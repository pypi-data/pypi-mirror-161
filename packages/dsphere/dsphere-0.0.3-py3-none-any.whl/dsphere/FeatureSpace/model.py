from dsphere.FeatureSpace.feature_structures.feature_data import FeatureData
from dsphere.FeatureSpace.feature_structures.feature_set import FeatureSet
from dsphere.FeatureSpace.feature_structures.feature_model import FeatureModel
from dsphere.FeatureSpace.feature_structures.feature_matrix import FeatureMatrix
from dsphere.FeatureSpace.feature_structures.feature_view import FeatureView
from dsphere.FeatureSpace.feature_structures.feature_chart import FeatureChart

import os
import psycopg2
import logging
import pandas as pd
import numpy as np
import scipy.sparse as sp
#import json
import datetime
import dateutil.parser as date_parser
import shutil
import json
#import pickle
import dill
import gc
import dask
import dask.dataframe as dd
import pyarrow as pa
import pyarrow.parquet as pq
import sklearn
from sklearn import metrics
from pympler.asizeof import asizeof
import sys
import copy
from filelock import FileLock
import io
import pgpy


#############################################################################################
# TODO: Support more types of feature normalization
def normalize(self, X, norm='max'):
    if norm == 'max':
        X_max = np.maximum(np.max(X, axis=0),1.)
        return X/X_max
    else:
        return X

# Note: Pass in training_function if want to override standard training functions available in libraries like 'scikit-learn'
# training_data_label = string --> use the data in the given FeatureSet
# training_data_label = other formats (dataframe or numpy array) --> use the data passed here
def train(self, model_label, model, 
               training_data, 
               training_cols,
               actuals_label, actuals_vars, 
               #actuals_variant=None,  # enforcing this to be the same variant as the featurest 
               actuals_child=None,
               training_function=None,
               loss_function=None,
               percent_training=None,
               norm=None,
               fillna=None,
               **kwargs):

    variant = kwargs.get('variant', None)
    child = kwargs.get('child', None)
    kwargs.pop('variant', None)
    kwargs.pop('child', None)
    model_variant = kwargs.get('model_variant', variant)
    kwargs.pop('model_variant', None)

    # Reload the FeatureSpace first to make sure we load the latest files
    self.out("Reloading the FeatureSpace...")
    self._loadFeatureSetMetadata()

    # Get the input feature data
    #feature_data = self.Data(training_data_label, reload=True).compute().copy()
    #all_feature_cols = list(self.Features(training_data_label).feature_cols)
    #all_features_ready = feature_data[all_feature_cols]
    #print("feature cols:", all_features_ready.columns)
    if isinstance(training_data, str):
        if child is None:
            # Use the parent dataframe
            all_features_ready = self.Data(training_data, variant=variant, child=child, reload=True)[training_cols] #.copy()
        else:
            # Use the child matrix
            all_features_ready = self.Data(training_data, variant=variant, 
                                           child=child, reload=True).getColumns(training_cols)
    else:
        all_features_ready = training_data

    # Added 7/26/21: Look for a FeatureMatrix as the child
    if hasattr(all_features_ready, '__feature_type__') and \
                all_features_ready.__feature_type__=='FeatureMatrix':
        all_features_ready = all_features_ready.getMatrix()


    # Added on 8/1/19: Proactively auto-correct for the input FeatureMatrix being in sparse COO format by converting to CSR
    if isinstance(all_features_ready, sp.coo.coo_matrix):
        all_features_ready = all_features_ready.tocsr()

    # Added 7/26/21: Sort the indices for a CSR matrix to allow it to pass into tensorflow mode
    if isinstance(all_features_ready, sp.csr.csr_matrix):
        all_features_ready.sort_indices()

    # Get the training labels
    if actuals_child is None:
        # Note: Assuming child=None for the labels
        actuals_df = self.Data(actuals_label, variant=variant, child=None) #.compute()
        print("actuals_df: ", actuals_df.shape)
        actuals_array = actuals_df[actuals_vars].values
        print("actuals_array: ", actuals_array.shape)
    else:
        actuals_matrix = self.Data(actuals_label, variant=variant, child=actuals_child)
        if actuals_vars is not None:
            # If a subset of the labels columns is specified, only use those
            actuals_array = actuals_matrix.getColumns(actuals_vars)
        else:
            # Otherwise use all label columns in the given child matrix
            actuals_array = actuals_matrix.getMatrix()

    if percent_training is not None:
        # Create random split of training/test data, if instructed
        num_rows = all_features_ready.shape[0]
        training_size = np.floor(num_rows * percent_training).astype(int)
        print("Training size: ", training_size)
        test_size = num_rows - training_size
        print("Test size: ", test_size)
        training_idx = np.random.randint(num_rows, size=training_size)
        test_idx = np.random.randint(num_rows, size=test_size)
        X_train, X_test = all_features_ready.loc[training_idx,:], all_features_ready.loc[test_idx,:]
        y_train, y_test = actuals_array[training_idx], actuals_array[test_idx]
    else:
        # Use the entire training dataset for training
        X_train = np.nan_to_num(all_features_ready) if fillna is not None else all_features_ready
        y_train = actuals_array

        # Can fill nulls 
        if fillna is not None:
            y_train[y_train == -np.inf] = fillna
            y_train = np.nan_to_num(y_train, fillna)
    print("X_train:", X_train.shape, type(X_train))
    print("y_train:", y_train.shape, type(y_train))


    # TODO: Support various types of feature normalization 
    if norm is not None:
        print("Applying '{}' normalization to the features".format(norm))
        X_train = self.normalize(X_train, norm=norm)

    # Train the model using the input feature + labels data
    # If training_function is passed in, use that
    model_type = None
    if training_function is not None:
        training_history = training_function(model, X_train, y_train)
    else:
        if 'sklearn' in str(type(model)):
            print("fitting the sklearn model {} with parameters {}".format(type(model), kwargs))
            training_history = model.fit(X_train, y_train, **kwargs)
            model_type = 'sklearn'
        elif 'keras' in str(type(model)):
            print("fitting the keras model {} with parameters {}".format(type(model), kwargs))
            print("...using X_train={} {}, y_train={} {}".format(X_train.shape, type(X_train),
                                                                 y_train.shape, type(y_train)))
            training_history = model.fit(X_train, y_train, **kwargs)
            model_type = 'keras'

    # TODO: Auto-detect tensorflow, theano, keras, etc. and call corresponding training function for each

    # Then store the model in this FeatureSpace
    new_featuremodel = self.addData(model_label, model, datatype='model', variant=model_variant,
                                    model_type=model_type,
                                    training_cols=training_cols,
                                    training_function=training_function,
                                    loss_function=loss_function,
                                    **kwargs)

    # Store the columns in the FeatureModel
    #new_featuremodel.setTrainingColumns(training_cols)

    return training_history

    # TODO: Do evaluation of this trained model on the test data

#############################################################################################
# This forces the use of the same order of columns in the data used to train
# the given model with the test data used to make predictions
# Note: Pass in prediction_function if want to override standard prediction functions available in libraries like sklearn
def predict(self, predictions_label, model_featureset, test_data_label, 
            index_vars=None,
            class_vars=None, 
            classification_function=None,
            regression_vars=None, 
            regression_function=None,
            norm=None,
            fill_missing=0.0, # New 1/15/21: Fill a missing feature column with this (if not None)
            **kwargs):

    # Reload the FeatureSpace first to make sure we use the latest files
    self.out("Reloading the FeatureSpace...")
    self._loadFeatureSetMetadata()

    # Allow a variant and filename for the model to be passed different from the variant(s) for the data
    model_label = None
    model_filename = None
    variant_model = None
    if isinstance(model_featureset, str):
        model_label = model_featureset
    if 'model_variant' in kwargs:
        variant_model = kwargs['model_variant']
        kwargs.pop('model_variant', None)
    if 'model_filename' in kwargs:
        model_filename = kwargs['model_filename']
        kwargs.pop('model_filename', None)

    # Also check if the model_featureset is a dict containing the model label, variant, or filename
    # Note this will override passing in the model_variant or model_filename parameters
    if isinstance(model_featureset, dict):
        if 'featureset' in model_featureset:
            model_label = model_featureset['featureset']
        elif 'label' in model_featureset:
            model_label = model_featureset['label']
        if 'variant' in model_featureset:
            variant_model = model_featureset['variant']
        if 'filename' in model_featureset:
            model_filename = model_featureset['filename']

    # Throw an error if there's still no valid model featureset to use
    if model_label is None:
        self.out("ERROR: No valid model featureset label was provided in '{}'".format(model_featureset), type='error')
        raise
#         elif not self.exists(model_label, variant=variant_model):
#             self.out("ERROR: The given model featureset '{}' for variant {} does not exist in the FeatureSpace".format(model_label, variant_model), type='error')
#             raise

    variant = kwargs.get('variant', None)
    child = kwargs.get('child', None)
    index_child = kwargs.get('index_child', None) # This is the child containing the given index_vars

    # Optionally make predictions in chunks if the input matrix is sparse (since it needs to be converted to dense)
    default_chunk_size = 50000

    if variant == '*':
        self.out("ERROR! Cannot support variant='*' in predict() yet. Can only predict for one variant at a time. Exiting.",
                 type='error')
        raise

    # Get the trained ML model
    # 10/21/21: Now allows this to be a model trained in the past
    model_obj = self.Features(model_label, variant=variant_model, filename=model_filename, datatype='model') #, variant=variant_model)
    #model = self.Data(model_label, datatype='model', variant=variant_model)
    model = model_obj.getData(variant=variant_model) #[variant_model]
    model_type = str(type(model))
    print("Predicting using model type", model_type)

    # Also get the ordered list of feature cols used to train
    # which we need to use in the inputted test data too
    #training_data_cols = self.Features(model_label, **kwargs).training_data_cols
    training_data_cols = model_obj.feature_cols
    print("Using {} training data cols (type:{})".format(len(training_data_cols), type(training_data_cols)))

    # TODO: Store the feature cols in the object and use those
    # Pull the test data using the variant (if given)
    test_data = self.Data(test_data_label, reload=True, variant=variant, child=child) #.copy()
    all_features_ready = None
    if isinstance(test_data, dd.DataFrame) or isinstance(test_data, pd.DataFrame):
        # Convert to pandas if the data is dask
        test_data = test_data.compute() if isinstance(test_data, dd.DataFrame) else test_data
        test_data_cols = test_data.columns

        # Subset the training data cols from the test data
        all_features_ready = test_data[training_data_cols]
        # TODO: Handle case of column from training_data_cols that's missing in the test data --> use default missing value
        print("Prediction columns: ", all_features_ready.columns)

    elif hasattr(test_data, '__feature_type__') and test_data.__feature_type__=='FeatureMatrix':
        # Support FeatureMatrix as the test data
        test_data_cols = test_data.columns()
        test_matrix_type = test_data.matrix_type

        # Note: Changed on 8/1/19 *not* to convert from sparse to dense...let the user control that b/c of memory usage
        # Convert the matrix into dense (if it's not already)
        test_data = test_data.getMatrix() #type='dense')

        # Changed on 8/1/19: Instead if the matrix is sparse COOMatrix, need to convert to CSR format to continue
        # (also do this during training)
        print("TYPE:", type(test_data))
        if isinstance(test_data, sp.coo.coo_matrix):
            print("WARNING: Converting the inpute FeatureMatrix to sparse CSR format instead of COO in order to continue")
            test_data = test_data.tocsr()

        # New on 1/15/21: If fill_missing is not None, fill-in any missing feature columns need by the model
        if fill_missing is not None:
            num_missing_cols = 0
            for training_col in training_data_cols:
                if training_col not in test_data_cols:
                    # Create a column of the fill_missing value (usually 0)
                    test_data_cols.append(training_col)
                    num_missing_cols += 1

            # If any are missing
            if num_missing_cols > 0:
                print("...creating {} columns with {} values for missing training cols".format(num_missing_cols, 
                                                                                               fill_missing))
                print("...current test matrix:", test_data.shape)
                matrix_num_rows = test_data.shape[0]
                # Create matrix of the default value
                zeros = np.zeros((matrix_num_rows,
                                  num_missing_cols), dtype=np.float16) + fill_missing
                if test_matrix_type=='sparse':
                    # If sparse, convert it to sparse and concat
                    zeros_sp = sp.csr_matrix(zeros)
                    test_data = sp.hstack((test_data, zeros_sp)).tocsr()
                else:
                    test_data = np.hstack((test_data, zeros))
                print("...current test matrix:", test_data.shape, "{} with {} columns".format(type(test_data),
                                                                                              len(test_data_cols)))

        # Re-order the features according to training_data_cols
        #print("training_data_cols:", len(training_data_cols), training_data_cols[:20])
        #print("test_data_cols:", len(test_data_cols))
        training_col_indexes = [training_data_cols.index(col) for col in test_data_cols if col in training_data_cols]
        #print("training_col_indexes:", training_col_indexes)

        # Check if there is any re-ordering of the columns to do
        last_i = None

        # Will need to reorder the columns if there is a subset or the columns have different order
        if len(test_data_cols) > len(training_data_cols):
            training_col_indexes_in_test = [test_data_cols.index(col) for col in training_data_cols]
            print("Pulling {} columns used to train the model out from the given test set (which has {} columns), found {} columns".format(len(training_data_cols), len(test_data_cols), len(training_col_indexes_in_test)))
            all_features_ready = test_data[:,training_col_indexes_in_test]
        else:
            is_reordered = False
            for i in training_col_indexes:
                if last_i is not None and i!=last_i+1:
                    is_reordered=True
                last_i = i

            # If so, produce a re-ordered version of this matrix (CAREFUL! Requires lots of RAM)
            if is_reordered:
                test_data_cols_resorted = np.argsort(training_col_indexes)
                all_features_ready = test_data[:,test_data_cols_resorted]
                print("Reshuffled columns in input test data matrix:", test_data_cols[:34])
                print("...to be ordered the same as the feature data used to train this model:", np.array(test_data_cols)[test_data_cols_resorted][:34])
                print("...new columns to input into the model:", [test_data_cols[col] for col in test_data_cols_resorted[:34]])
            else:
                all_features_ready = test_data
                print("Using columns of input test data matrix as-is, no re-ordering needed")
    else:
        print("for Data({}, reload=True, variant={}, child={}) got type {}".format(test_data_label, 
                                                                                   variant, child, type(test_data)))
        # TODO: Support other input datasets like numpy array here
        test_data_cols = test_data.columns
        all_features_ready = test_data

    # Look for training data columns not in the test set
    missing_training_data_cols = [x for x in training_data_cols if x not in test_data_cols]
    if len(missing_training_data_cols)>0:
        print("...{} training cols are missing in the test data: {}".format(len(missing_training_data_cols), missing_training_data_cols))
        print("...training cols:", training_data_cols)
        print("...test data set cols:", test_data_cols)


    # If index_vars are given, then add them as column(s)
    predictions_df = None
    if index_vars is not None:
        # Get the child dataset containing the given index_vars
        index_data = self.Data(test_data_label, variant=variant, child=index_child)
        # TODO: Support the index_child being something other than pandas/dask here
        predictions_df = index_data[index_vars].reset_index(drop=True)
        if isinstance(predictions_df, dd.Series) or isinstance(predictions_df, dd.DataFrame):
            predictions_df = predictions_df.compute()
        print("predictions_df:", predictions_df.head())

    # TODO: Support various types of feature normalization
    if norm is not None:
        print("Applying '{}' normalization to the features".format(norm))
        feature_matrix = self.normalize(all_features_ready, norm=norm)
    else:
        feature_matrix = all_features_ready

    # Classify using either the custom classification function (if given)
    # or auto-detect the classification function to use (if not)
    classes = None
    values = None

    # If a custom classification/regression lambda function is provided, use it
    if classification_function is not None:
        print("...have custom classification function")
        classes = classification_function(model, feature_matrix)

    if regression_function is not None:
        print("...have custom regression function")
        values = regression_function(model, feature_matrix)

    # keras NN
    if 'keras' in model_type:
        # If the matrix is sparse, need to iterate through and convert the chunks into dense
        if regression_function is None:
            if isinstance(feature_matrix, sp.coo.coo_matrix) or isinstance(feature_matrix, sp.csr.csr_matrix):
                total_num_rows = feature_matrix.shape[0]
                num_chunks = (np.floor(total_num_rows/default_chunk_size)+1).astype(int)
                temp_values = None
                for chunk_num in range(num_chunks):
                    # Predict for just this chunk
                    start_row = chunk_num * default_chunk_size
                    end_row = min(start_row+default_chunk_size, total_num_rows)
                    if end_row>start_row:
                        feature_matrix_chunk = feature_matrix[start_row:end_row,:].todense()
                        values_chunk = model.predict(feature_matrix_chunk)
                        print("Calculated NN outputs for chunk of rows {}-{}: {}".format(start_row, end_row, values_chunk.shape))
                        # Append onto the bottom of the stack of probabilities
                        temp_values = values_chunk if temp_values is None else np.vstack([temp_values, values_chunk])
                        del(feature_matrix_chunk)
                        gc.collect()
                self.out("Finished with total NN outputs:", temp_values.shape)

            else:
                # Use the whole feature matrix
                temp_values = model.predict(feature_matrix)

            # Only store these outputs if instructed to do so
            if regression_vars is not None:
                values = temp_values

        # Calculate binary classes by rounding (if didn't already get a classification lambda fn)
        if class_vars is not None and classification_function is None:
            # Handle case of custom regression function (to determine values) but no custom classification_function
            if temp_values is None:
                temp_values = model.predict(feature_matrix)
            classes = np.round(temp_values)


    # scikit-learn
    elif 'sklearn' in model_type:
        if class_vars is not None and classification_function is None:
            print("Using sklearn to predict for feature matrix: {}".format(feature_matrix.shape))
            classes = model.predict(feature_matrix)

        if regression_vars is not None and regression_function is None:
            if 'Classifier' in model_type:
                values = model.predict_proba(feature_matrix)
            else:
                self.out("ERROR: Cannot predict regression vars {} for the given model of type {}".format(regression_vars, 
                                                                                                          model_type), 
                         type='error')

    else:
        self.out("ERROR: Currently do not support predict() using given model with model_type='{}', only support 'sklearn' and 'keras', or a custom lambda function".format(model_type), type='error')
        return None

    # Store the outputs of the NN
    regression_df = None
    classes_df = None
    if values is not None:
        regression_cols = [regression_vars] if isinstance(regression_vars, str) else regression_vars
        if isinstance(values, list):
            regression_df = pd.DataFrame(np.hstack(values), columns=regression_cols).reset_index(drop=True)                
        else:
            regression_df = pd.DataFrame(values, columns=regression_cols).reset_index(drop=True)

    if class_vars is not None:
        classes_df = pd.DataFrame(classes, columns=[class_vars] if isinstance(class_vars, str) \
                                                                        else class_vars).reset_index(drop=True)

    # Create the final output dataframe
    if regression_df is not None:
        predictions_df = pd.concat([predictions_df, regression_df], axis=1)

    if classes_df is not None:
        predictions_df = pd.concat([predictions_df, classes_df], axis=1)

    # Store the predictions (and maybe probabilities) dataframe, using the same variant as the input feature data
    print("Predictions_df:", type(predictions_df), predictions_df.head())

    # Default the child for the predictions to be None
    kwargs['child'] = None
    self.addData(predictions_label, predictions_df, datatype='dataframe', **kwargs) 

    del(test_data)
    del(all_features_ready)


#############################################################################################
# Returns a dict containing the overall evaluation of these predictions
# Also stores row-by-row comparison of predictions vs. labels in the FeatureSpace if you provide a comparison_label
# Note: Unlike in predict(), can only use one prediction var and one probability var at a time here
# TODO: Add support for multiclass predictions here, not just one at a time
# TODO: Allow actuals / predictions to be merged together using a given index var, rather than assumption that
# they are in-order and can be compared row-wise which is dangerous.
def evaluate(self, predictions_label, actuals_label, actuals_var,
             class_var=None,
             regression_label=None,
             regression_var=None,
             comparison_label=None, **kwargs):

    # Reload the FeatureSpace first to make sure we reload the latest files
    self.out("Reloading the FeatureSpace...")
    self._loadFeatureSetMetadata()

    variant = kwargs.get('variant', None)
    child = kwargs.get('child', None)
    actuals_child = kwargs.get('actuals_child', None)
    lift_top_scores = kwargs.get('lift', 'decile')

    if variant == '*':
        print("ERROR! Cannot support variant='*' in predict() yet. Can only predict for one variant at a time. Exiting.")
        return None

    # Get the dataframes for the predictions and labels
    actuals_df = self.Data(actuals_label, variant=variant, child=actuals_child)
    if hasattr(actuals_df, '__feature_type__') and actuals_df.__feature_type__=='FeatureMatrix':  
        actuals_matrix_columns = actuals_df.columns()
        print("...actuals_matrix_columns:", actuals_matrix_columns)
        actuals_matrix = actuals_df.getMatrix(type='dense')
        print("...actuals_matrix:", actuals_matrix.shape)
        actuals_var_index = actuals_matrix_columns.index(actuals_var)
        print("...actuals_var_index:", actuals_var_index)
        actuals_array = actuals_matrix[:,actuals_var_index]
        print("Actuals array is column #{}='{}' of the input matrix, with {} 1s out of {} rows".format(actuals_var_index, 
                                                                                                       actuals_var, 
                                                                                                       actuals_array.sum(),
                                                                                                    actuals_array.shape[0]))
    else:
        if isinstance(actuals_df, dd.DataFrame):
            actuals_df = actuals_df.compute()
        actuals_array = actuals_df[actuals_var].values
        print("Actuals:", actuals_df.columns, actuals_array.sum())

    stats = {}
    # Get the class predictions 
    predictions_df = self.Data(predictions_label, variant=variant, child=child)
    if isinstance(predictions_df, dd.DataFrame) or isinstance(predictions_df, dd.Series):
        predictions_df = predictions_df.compute()
    predicted_classes_array = None
    if isinstance(predictions_df, pd.DataFrame):
        print("Predictions:", predictions_df.columns)
        if class_var is not None:
            predicted_classes_array = predictions_df[class_var]
    elif isinstance(predictions_df, pd.Series) or isinstance(predictions_df, np.ndarray):
        print("Predictions is of type ", type(predictions_df))
        predicted_classes_array = predictions_df
    else:
        print("ERROR: Unknown type of predictions here:", type(predictions_df))
        return None
    print("Have {} predictions (with {} 1s)".format(predicted_classes_array.shape[0], predicted_classes_array.sum()))

    # If given, compare the predicted classes to the actuals
    if predicted_classes_array is not None:
        stats['accuracy'] = sklearn.metrics.accuracy_score(actuals_array, predicted_classes_array)
        stats['F1'] = sklearn.metrics.f1_score(actuals_array, predicted_classes_array)
        stats['precision'] = sklearn.metrics.precision_score(actuals_array, predicted_classes_array)
        stats['recall'] = sklearn.metrics.recall_score(actuals_array, predicted_classes_array)
        stats['confusion_matrix'] = sklearn.metrics.confusion_matrix(actuals_array, predicted_classes_array)

    # Get the regression values too
    regression_df = self.Data(predictions_label if regression_label is None else regression_label, 
                              variant=variant, child=child)
    if isinstance(regression_df, dd.DataFrame) or isinstance(regression_df, dd.Series):
        regression_df = regression_df.compute()
    predicted_values_array = None
    if isinstance(regression_df, pd.DataFrame):
        print("Predicted values:", regression_df.columns)
        if regression_var is not None:
            predicted_values_array = regression_df[regression_var]
    elif isinstance(regression_df, pd.Series) or isinstance(regression_df, np.ndarray):
        print("Predicted values are of type ", type(regression_df))
        predicted_values_array = regression_df
    else:
        print("ERROR: Unknown type of predictions here:", type(regression_df))
        return None

    # If given, also compare the predicted values (i.e. regression or probabilities) vs. actuals
    if predicted_values_array is not None:
        stats['MSE'] = sklearn.metrics.mean_squared_error(actuals_array, predicted_values_array)
        stats['RMSE'] = np.sqrt(stats['MSE'])
        stats['MAE'] = sklearn.metrics.mean_absolute_error(actuals_array, predicted_values_array)
        stats['explained_variance'] = sklearn.metrics.explained_variance_score(actuals_array, predicted_values_array)
        stats['r2'] = sklearn.metrics.r2_score(actuals_array, predicted_values_array)
        stats['cross_entropy_loss'] = sklearn.metrics.log_loss(actuals_array, predicted_values_array, labels=[0,1])
        num_samples = actuals_array.shape[0]

        # Calculate lift using the given groups ('decile', 'deciles', 10000, etc.)
        all_lift_num_scores = []
        if lift_top_scores == 'decile':
            one_decile = int(np.round(num_samples/10))
            all_lift_num_scores.append((0, one_decile, 'top_decile'))
        elif lift_top_scores == 'deciles':
            one_decile = int(np.round(num_samples/10))
            decile_start = 0
            for decile_num in range(10):
                decile_end = decile_start + one_decile
                all_lift_num_scores.append((decile_start, decile_end, f'decile_{(decile_num+1)}'))
                decile_start = decile_end+1
        elif isinstance(lift_top_scores, int):
            all_lift_num_scores.append((0, lift_top_scores, f'top_{lift_top_scores}'))

        # Iterate through each range of scores to calculate the lift on
        for top_scores_start, top_scores_end, top_scores_label in all_lift_num_scores:
            # Then calculate lift for the top-N
            top_scores_end_max = np.minimum(top_scores_end, num_samples)
            sort_indices_topdown = np.argsort(predicted_values_array)[::-1]
            actuals_array_sorted = actuals_array[sort_indices_topdown]
            num_top_scores = top_scores_end - top_scores_start
            true_positives_in_top_scores = actuals_array_sorted[top_scores_start:top_scores_end_max].sum()
            num_total_positives = actuals_array.sum()

            lift = (true_positives_in_top_scores/num_top_scores) / (num_total_positives/num_samples)
            stats['lift_rate_{}'.format(top_scores_label)] = lift
            stats['lift_num_scores_{}'.format(top_scores_label)] = num_top_scores

    return stats

