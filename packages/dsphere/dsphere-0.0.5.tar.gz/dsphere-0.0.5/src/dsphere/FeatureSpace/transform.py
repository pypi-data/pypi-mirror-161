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
# Pass feature_cols='*' if you want *all* columns not explicitly set as index/label cols to be feature cols
# Leave feature_cols null if you want to carry forward the feature cols of the input feature sets into the output
# Only allowing transforms on one child dataset at a time...might need to change that 
# Can pass child='child1' or leave child blank to indicate child=None (to use primary dataset)
# TODO: Support child='*' somehow so can make that the default...or just keep that specific to each function calling this
# Note: Passing 'data_types' overrides in the output any stored data types of columns in the input feature sets
# Note: Also the forced data type of a column is determined by the first input feature set in this list, if repeated
# (for instance merge() contains [fs1, fs2] and fs1 defined 'col1' as 'str' where fs2 defined 'col1' as 'int' --> 'str' wins
# TODO: Remove parameter engine here. Should not be transparent to the data scientist.
# Added on 2/6/21: 
# - Can now allow variant params to force the combinations to use, either using a dict for input_labels
# like {'featureset1':['var1'], 'featureset2':['var2']} or by passing in a dict to define the featureset
# like [{'label':'featureset1', 'variant':['var1']}, 'featureset2']
# - Can now combine input_labels=['featureset1', 'featureset2'] with variant=[['var1'],['var2']] (list of lists)
# - Using variant=['var1', 'var2'] constrains the list of combinations of variants to only those two, even if the input
# featuresets have more variants in memory.
# - However variant=[[None],[None,'training']] will still only use [None, None] as the combination (because a list of
# variants currently means "use any of these variants" not "use all of these variants". To achieve the combinations
# [[None, None],[None, 'training']] the user should explicitly pass in those combinations in two separate calls to the transform.
# - Now allow both "variant" or "variants" parameters (if both are passed, "variant" will win)
# - Now allow both "output_variant" or "output_variants" parameters (if both are passed, "output_variant" will win)
# - 10/20/2011 (William turns 10!): Now allow any of the input featuresets to be dict structures with 'label' or 'featureset'
#   (required) + 'variant' or 'variants' (optional) + 'filename' (optional) in it
#   Note: Unknown behavior will occur if you pass in a mix of variants in a featureset dict + variant in the transform
#   like: input_featureset = [{'label':'featureset_1', 'variant':'var1'}, 'featureset_2'] + variant=['var1', 'var2']
def _transform(self, output_label, transformer_function, input_featuresets, *args, **kwargs):
    self.out("\nInside _transform({}, transformer_function={}, input_featuresets={}, args={}, kwargs={})".format(output_label, transformer_function, input_featuresets, [arg for arg in args if isinstance(arg, str)], kwargs))
    output_featureset = None
    engine = kwargs.get('engine', self.default_engine)
    batch = kwargs.get('batch', self.default_batch)
    variant = kwargs.get('variant', kwargs.get('variants', '*')) # self.default_variant) Note: Changed on 4/3/19
    child = kwargs.get('child', None)
    if child == '*':
        self.out("ERROR! Currently do not support child='*' in this _transform() call", type='error')
        return None
    #target_variant_list = [variant] if variant is None or isinstance(variant, str) else variant

    # Update on 2/6/21: '*' is now the keyword meaning "infer the output variants from the combinations of input variants"
    # since output_variant=[None] or output_variant=None should indicate the output_variant should just be None
    output_variant = kwargs.get('output_variant', kwargs.get('output_variants', '*'))
    kwargs.pop('output_variant', None)
    kwargs.pop('output_variants', None)
    index_cols = kwargs.get('index_cols', None)
    kwargs.pop('index_cols', None)
    feature_cols = kwargs.get('feature_cols', None)
    kwargs.pop('feature_cols', None)
    label_cols = kwargs.get('label_cols', None)
    kwargs.pop('label_cols', None)
    fillna = kwargs.get('fillna', False)  # Note: On 8/30/19 changed the default to False (more neutral/intuitive)
    kwargs.pop('fillna', None)
    data_types = kwargs.get('data_types', {})
    if data_types is None:
        data_types = {}    

    # Set this flag to False so addData (below) does not create another copy of this on disk
    # save_to_disk = False if engine=='parquet' else True
    save_to_disk = kwargs.get('save_to_disk', engine!='parquet') # Added 6/22/20 to allow calling function to decide

    # Check whether this transform creates new rows or cols (default=True for both)
    new_rows = kwargs.get('new_rows', True)
    new_cols = kwargs.get('new_cols', '*')
    self.out("...using new_rows={}, new_cols={}".format(new_rows, new_cols))

    # If the caller says to overwrite, then do so
    overwrite = kwargs.get('overwrite', False)

    # Reload the FeatureSpace metadata first to make sure we reload the latest files
    self.out("Reloading the FeatureSpace...")
    self._loadFeatureSetMetadata()

    # First transform the input_featuresets and variants (if provided) based on their format
    input_labels = []
    target_variant_list = None
    input_filenames = {}  # If any featureset should use a previous filename
    if isinstance(input_featuresets, dict):
        # {'featureset_1':['var1', 'var2'], 'featureset_2':'var1'}
        input_labels = list(input_featuresets.keys())

        # Use the variants for each input if provided in the dict structure
        target_variant_list = [([val] if isinstance(val, str) or val is None else val) for key, val in input_featuresets.items()]

    elif isinstance(input_featuresets, str):
        # Convert a single input label to a list, so can be treated below same as with >1 input labels
        input_labels = [input_featuresets]

    else:
        # Assume this is a list or tuple, then iterate through and check if each item is a string or dict
        for input_featureset_def in input_featuresets:
            if isinstance(input_featureset_def, str):
                input_labels.append(input_featureset_def)
            elif isinstance(input_featureset_def, dict):
                # Get the featureset/label parameter out of this element, and any variants too
                current_label = None
                if 'featureset' in input_featureset_def:
                    current_label = input_featureset_def['featureset']
                elif 'label' in input_featureset_def:
                    current_label = input_featureset_def['label']
                else:
                    self.out("ERROR: There must be a 'featureset' or 'label' property of the input featureset: {}".format(input_featureset_def), type='error')
                    raise
                input_labels.append(current_label)

                # Also get the variant(s) if provided here
                if 'variant' in input_featureset_def or 'variants' in input_featureset_def:
                    input_variants = input_featureset_def['variant'] if 'variant' in input_featureset_def \
                                     else input_featureset_def['variants']
                    if isinstance(input_variants, str):
                        input_variants = [input_variants]
                    if target_variant_list is None:
                        target_variant_list = [input_variants]
                    else:
                        target_variant_list.append(input_variants)

                # Check if a filename is provided, if so tag this to be used for this featureset
                if 'filename' in input_featureset_def:
                    input_filenames[current_label] = input_featureset_def['filename']

            else:
                self.out("ERROR: The input featureset must be a string or dict, but {} provided: {}".format(type(input_featureset_def), input_featureset_def), type='error')
                raise


    # Convert a single input label to a list, so can be treated below same as with >1 input labels
    #input_labels = [input_labels] if isinstance(input_labels, str) else input_labels

    self.out("...proceeding with engine={}, batch={}, variant={}, child={}, output_variant={}, index_cols={}, feature_cols={}, label_cols={}, overwrite={}, input_labels={}".format(engine, batch, variant, child, output_variant, index_cols, feature_cols, label_cols, overwrite, input_labels))

    # Free up memory if needed
    # Note: Now we can safely assume input_labels is a list of strings
    #if isinstance(input_labels, dict):
    #    self.freeUpMemory(list(input_labels.keys()) + [output_label])
    #else:
    if (self.memory_mode == 'low' or (self.dsphere is not None and self.dsphere.memory_mode=='low')) and save_to_disk:
        # Only remove unused featuresets from memory if in "low" memory_mode 
        # and this is a transform that will be saved to disk 
        # -- otherwise assume prior featuresets might be needed in future memory-only transforms
        self.out("LOW MEMORY MODE: Trying to free up space in memory:")
        self.freeUpMemory(input_labels+[output_label])

    # Get the list of combinations of variants to use for each input in input_labels
#         target_variant_list = []
    if variant=='*' and target_variant_list is None:
        # Don't override variant set above in any featuresets' dict structures
        target_variant_list = ['*']
    elif (isinstance(variant, str) and variant != '*') or variant is None:
        # Convert to list
        if target_variant_list is None:
            target_variant_list = []
        target_variant_list.append(variant)
        variant = [variant]            
    elif isinstance(variant, list):
        if target_variant_list is None:
            target_variant_list = variant
        else:
            target_variant_list += variant
    self.out("...target_variant_list={}".format(target_variant_list))

     # Commenting out on 2/6/21 because this could break the new getVariantCombinations() if target_variant_list=['*']
        # or target_variant_list=[[var1],[var2]]
#         if output_variant is not None:
#             if isinstance(output_variant, str):
#                 self.out("appending output variant ", output_variant)
#                 target_variant_list.append(output_variant)
#             elif isinstance(output_variant, list):
#                 for output_var in output_variant:
#                     if not output_var in target_variant_list:
#                         target_variant_list.append(output_var)
    self.out("calling _getVariantCombinations({}, {}, {}, {})".format(input_labels, 
                                                                      target_variant_list, 
                                                                      output_variant, 
                                                                      batch))
    all_input_variant_combos, all_output_variants = self._getVariantCombinations(input_labels, 
                                                                                 target_variant_list, 
                                                                                 output_variant, 
                                                                                 batch)

    # If no variant(s) were found in common, then exit the transform, can't continue
    # TODO: Improve this error message to indicate if this was because the given input featureset label is not there
    if all_input_variant_combos is None or len(all_input_variant_combos)==0:
        self.out("ERROR: Could not find any variant='{}' in common for all the input featuresets, cannot proceed. Exiting transform.".format(variant), type='error')
        return None

    # TODO Consider removing featureset.variants()
    self.out("combos: ", all_input_variant_combos)
    self.out("kwargs:", kwargs)

    # Retrieve the data sets for the given variant(s)
    kwargs.pop('variant', None)
    kwargs.pop('variants', None)

    # Iterate through the 1 or many datasets, running the transform on each
    num_variant_combos = len(all_input_variant_combos)
    transform_metadata = []
    for input_variant_combination, this_output_variant  in zip(all_input_variant_combos, all_output_variants):
        self.out("\nRunning Transformation {} on inputs {} using variants {} producing output with variant {}...".format(transformer_function, input_labels, input_variant_combination, this_output_variant))
        # Pass-through each variant

        # If have multiple input featuresets, iterate through each of them
        all_input_dfs = []
        all_primary_dfs = []
        all_input_cols_set = set()
        input_feature_cols_set = set()
        input_index_cols_set = set()
        input_label_cols_set = set()
        all_input_col_types = {}
        ##all_input_statuses_true = True
        # Iterate through each variant for each input label in the current combination
        input_labels_with_variants = list(zip(input_labels, input_variant_combination))
        for (input_label, input_variant) in input_labels_with_variants:
            self.out("Gathering input FeatureSet '{}' with variant '{}' and child='{}'".format(input_label, 
                                                                                            input_variant, 
                                                                                            child))
            kwargs['variant'] = input_variant
            kwargs['filename'] = input_filenames.get(input_label, None)
            input_featureset = self.Features(input_label, **kwargs)

            # Get the data for this child/variant
            input_data = input_featureset.getData(variant=input_variant, child=child) #[child]

            # If the child is not None, pass its primary dataset (child=None) too
            # Note: Passing by reference here, not making a copy. Better for memory mgmt. But be careful about modifying it.
            all_primary_dfs.append(input_featureset.getData(variant=input_variant, child=None) if child is not None else None)

            #all_input_data[input_variant]
            # TODO: Move this into FeatureData.getData
            if isinstance(input_data, dict) and len(input_data)==1 and None in input_data:
                input_data = input_data[None]
            #print("Input data:", input_data)

            # Exit if this variant could not be found
            if input_data is None:
                self.out("ERROR: Cannot find data set with label={}, variant={}, kwargs={}...canceling transform".format(input_label, input_variant, kwargs), type='error')
                return None

            # Persist the forced column data types of each input FeatureSet (unless overridden in the transform call)
            # Also note this uses the forced type the first time it's defined in order of feature sets
            # (if two input feature sets both define the same column type)
            input_data_types = input_featureset.types
            for input_type_col in input_data_types:
                input_data_type_tuple = input_data_types[input_type_col]
                if input_data_type_tuple[1] == FeatureSet._COL_TYPE_FLAGS_FORCED:
                    # Look at any forced data types in the input FeatureSet 
                    if input_type_col not in data_types:
                        # If it's not provided a forced type in this transform call
                        data_types[input_type_col] = input_data_type_tuple[0]

                        # New 5/31/20: Also keep track of this previously-defined typing
                        all_input_col_types[input_type_col] = input_data_type_tuple

                        self.out("...persisting col type '{}'='{}'".format(input_type_col, input_data_type_tuple[0]), type='debug')

                    else:
                        # Otherwise keep track of the newly-forced datatype
                        all_input_col_types[input_type_col] = data_types[input_type_col]
                elif input_type_col not in all_input_col_types:
                    # Store the previously-inferred data type for each col
                    # Note this will use the first inferred type per column name
                    all_input_col_types[input_type_col] = input_data_type_tuple

            if engine == 'pandas':
                # TODO: Handle conversion of a FeatureMatrix to pandas

                # If the input dataset is dask, convert it to pandas to do the transform
                if isinstance(input_data, dd.DataFrame):
                    # Convert dataframe to pandas to execute the transform, and reset the indexes (to remove duplicate indexes)
                    self.out("Since engine=pandas, running compute() on the input_data")
                    input_df_dtypes = input_data.dtypes
                    input_df_copy = input_data.compute().reset_index(drop=True, inplace=False).copy()
                    self.out("...done")

                    # Convert columns in the pandas dataframe back to int type with 0s filled-in for nulls
                    # (since .compute() coerces those columns to float64 if there are nulls)
                    for col, coltype in input_df_dtypes.iteritems():
                        if coltype==np.int64:
                            input_df_copy[col] = input_df_copy[col].fillna(0).astype(int)

                    # Keep track of columns in the input feature set(s)
                    input_cols_set = set(input_df_copy.columns)

                    # Transform a copy of the input FeatureSet (so the original input data aren't changed)
                    #input_df_copy = input_df_pandas.copy() # if engine=='pandas' else input_data.copy()

                elif isinstance(input_data, pd.DataFrame):
                    self.out("...retrieved dataframe of type:{}, shape:{}".format(type(input_data), input_data.shape))
                    #self.out("...retrieved dataframe of type:{}, shape:{}, max index:{}".format(type(input_data), input_data.shape, input_data.index.max()))
                    # If the input data is already a pandas dataframe
                    input_df_copy = input_data.copy()
                    self.out("...copy:", input_df_copy.index.max())
                    input_cols_set = set(input_df_copy.columns)

                elif hasattr(input_data, '__feature_type__') and input_data.__feature_type__=='FeatureMatrix':
                    # If the input is a FeatureMatrix, then convert it to a dense pandas dataframe
                    # Note: Cannot do this yet because it causes downstream bugs
                    # TODO: Support >1 child that's pandas in the same folder
                    #input_df_copy = input_data.dataframe(type='pandas').copy()
                    input_df_copy = input_data.copy()
                    #input_df_copy = input_df_pandas.copy()
                    self.out("created new version of the FeatureMatrix as type '{}'".format(type(input_df_copy)))
                    input_cols_set = set(input_df_copy.columns())

                else:
                    # If the input data is a pandas Series (or otherwise)
                    input_df_copy = input_data.copy()
                    input_cols_set = set()
            else:
                #input_cols_set = set(input_data.columns)
                input_cols_set = set(input_featureset.columns(variant=input_variant, child=child))
                input_df_copy = input_data.copy()

            all_input_dfs.append(input_df_copy)

            #input_feature_set = self.Features(input_label, **kwargs)
            all_input_cols_set |= input_cols_set
            input_feature_cols_set |= set(input_featureset.feature_cols)
            input_index_cols_set |= set(input_featureset.index_cols)
            input_label_cols_set |= set(input_featureset.label_cols)
            self.out("So far have {} index cols ({}), {} feature cols, {} label cols".format(len(input_index_cols_set), input_index_cols_set, len(input_feature_cols_set), len(input_label_cols_set)))
            #print("...feature cols: {}".format(input_feature_cols_set))


        # Take out keyword parameters that shouldn't be passed-through to the transformer
        kwargs_transformer = copy.deepcopy(kwargs)
        kwargs_transformer.pop('engine', None)
        kwargs_transformer.pop('variant', None)
        kwargs_transformer.pop('reset_data', None)
        kwargs_transformer.pop('overwrite', None)
        #kwargs_transformer.pop('child', None)

        # Pass the primary datasets too, in case they're needed by the transformer
        kwargs_transformer['primary_datasets'] = all_primary_dfs

        #args_transformer = tuple(all_input_dfs) + args
        # Note that args is a tuple, so by definition immutable. But if any of its members points to a var 
        # that changes inside of the transformer_function, that var will change here too.
        # Would need to do a "deep copy" to prevent that from ever happening.
        args_transformer = args

        # Send the input dataframes + any args/kwargs provided in this _transform() call into the given transform_function
        num_input_dfs = len(all_input_dfs)
        self.out("...sending in {} dataframes to the transformer function with args: {} and kwargs: {}".format(num_input_dfs, args_transformer, kwargs_transformer.keys()))

        # Replaced on 8/30/19: Allow variable type of output from the transformer
        transform_result = transformer_function(all_input_dfs[0] if num_input_dfs<=1 else all_input_dfs, 
                                                *args_transformer, 
                                                **kwargs_transformer)
        if isinstance(transform_result, dict):
            transform_df = transform_result['dataframe']
            new_index_cols = transform_result['index_cols']
            self.out("New index cols created during transform:{}".format(new_index_cols), type='debug')
        else:
            transform_df = transform_result
            new_index_cols = None
        self.out("Completed transform -- resulted in dataframe with type {} and new index cols: {}".format(type(transform_df), new_index_cols))

        # Check if there was an error during the transform
        if transform_df is None:
            self.out("ERROR! Running transform {} on {} returned None, so not proceeding.".format(transformer_function, input_label), type='error')
            del(input_df_copy)
            del(input_data)
            #if engine == 'pandas':
            #    del(input_df_pandas)
            return

        # Set up the output parameters
        kwargs_output = copy.deepcopy(kwargs) ## Should contain child
        # Update on 2/6/21: This is no longer needed here, since the output_variants are calculated in getVariantCombinations
        #this_output_variant = self._getOutputVariant(input_variant_combination, output_variant, num_variant_combos)
        kwargs_output['variant'] = this_output_variant

        # If the output feature set label and variant are the same as for any one of the input feature sets
        # then overwrite the old copy of the featureset with the new one
        # (for example, if this transform is adding new columns to a dataframe, we may only need to keep the new copy)
        if (output_label, this_output_variant) in list(zip(input_labels, input_variant_combination)):
            kwargs_output['overwrite'] = True
            self.out("Setting overwrite=True because output feature_set '{}' and variant '{}' are same as one of the inputs".format(output_label, this_output_variant))

        # TODO: Change this to make sure *all* children for this label/variant are the same, otherwise we'll 
        # inadvertently overwrite children when modifying another child

        #print("Calling addData000 for type", type(transform_df), transform_df.columns)

        # Convert the dataframe to another format based on the 'engine' value
        if engine is not None:
            if isinstance(transform_df, pd.DataFrame) or isinstance(transform_df, pd.Series):
                if engine == 'dask':
                    transform_df = dd.from_pandas(transform_df, chunksize=DEFAULTS._DEFAULT_CHUNK_SIZE, sort=False)
                # Before adding the transformed dataset to the output FeatureSet, unify its datatypes
                # TODO: Allow some columns not to be unified, like an index col generated by merge()
                # TODO: Allow fillna=False to be passed into here 

            elif isinstance(transform_df, dd.DataFrame) or isinstance(transform_df, dd.Series):
                if engine == 'pandas':
                    transform_df = transform_df.compute()

            elif isinstance(transform_df, np.ndarray):
                if engine == 'dask':
                    transform_df = dd.from_array(transform_df, chunksize=DEFAULTS._DEFAULT_CHUNK_SIZE)
                elif engine == 'pandas':
                    transform_df = pd.DataFrame(transform_df)

        # Infer the index/feature/label cols from the output of the transform (if not a numpy array)
        #if not isinstance(transform_df, np.ndarray) and not isinstance(transform_df, pd.Series):

        # Use the columns if available
        output_index_cols_set = None
        output_feature_cols_set = None
        output_label_cols_set = None
        transform_df_cols_set = None
        if isinstance(transform_df, pd.DataFrame) or isinstance(transform_df, dd.DataFrame):
            # Infer feature/index/label cols for the output FeatureSet based on input FeatureSet
            transform_df_cols_set = set(transform_df.columns)
        elif hasattr(transform_df, '__feature_type__') and transform_df.__feature_type__=='FeatureMatrix':
            transform_df_cols_set = set(transform_df.columns())
            self.out("...transform returned FeatureMatrix with {} columns".format(len(transform_df_cols_set)))

            # TODO Make sure all set operations work with >1 input feature sets too

        if transform_df_cols_set is not None:
            # If index/feature/label cols are passed in, use those. Otherwise infer them.
            if index_cols is not None:
                if index_cols == '*':
                    # Placeholder '*' tells _transform() to treat *all* the columns in the output set as index cols
                    output_index_cols_set = transform_df_cols_set
                else:
                    output_index_cols_set = set([index_cols] if isinstance(index_cols, str) else index_cols)
            else:
                # Default behavior is to pull the index cols from the input to be the index cols of the output (if still there)
                output_index_cols_set = input_index_cols_set & transform_df_cols_set

                # New on 8/30/19: Also keep track of index columns generated inside the transform
                if new_index_cols is not None:
                    output_index_cols_set |= set(new_index_cols)

            if label_cols is not None:
                output_label_cols_set = set([label_cols] if isinstance(label_cols, str) else label_cols)
            else:
                output_label_cols_set = input_label_cols_set & transform_df_cols_set

            # Feature cols in the output = new cols created in transform + input feature cols also in the transformed data
            if feature_cols is not None:
                if feature_cols == '*':
                    # Placeholder '*' tells _transform() to treat *all* the columns in the output set as features (if they're not index/label cols)
                    output_feature_cols_set = transform_df_cols_set - output_index_cols_set - output_label_cols_set
                    self.out("Here with output features: ", output_feature_cols_set)
                else:
                    # If a column or list of cols is provided, use them as the feature cols
                    output_feature_cols_set = set([feature_cols] if isinstance(feature_cols, str) else feature_cols)
                    # TODO: Make sure no col is in both index & features & labels
            else:
                # If nothing passed in, default is to treat any *new* columns created by the transform + any feature columns in the input set as features in the output (removing index/label cols)
                output_feature_cols_set = ((transform_df_cols_set - all_input_cols_set) | (input_feature_cols_set & transform_df_cols_set)) - output_index_cols_set - output_label_cols_set

            # Note: This will leave untouched any cols that are *not* feature/index/label cols
            # Also note: This will resolve any errors in cols classified as both feature+index in the input

            self.out("Output set has {} index cols ({}), {} feature cols, {} label cols".format(len(output_index_cols_set), output_index_cols_set, len(output_feature_cols_set), len(output_label_cols_set)))

        # Unify the columns and reset the index if the output is a dataframe
        # Note 8/30/19: Now we will not unify the index columns (as they accumulate)
        if isinstance(transform_df, pd.DataFrame) or isinstance(transform_df, dd.DataFrame):
            # If data_types contains columns with new types different from the previous types, treat those columns as "new"
            self.out("...testing2 new_cols={}".format(new_cols))

            # If some columns are new, but not all
            if new_cols != '*': 
                for data_type_col, new_data_type in data_types.items():
                    if data_type_col in all_input_col_types:
                        old_data_type = all_input_col_types[data_type_col][0]
                        if old_data_type != new_data_type:
                            if new_cols is None:
                                new_cols = [data_type_col]
                            elif isinstance(new_cols, str) and new_cols!=data_type_col:
                                new_cols = [new_cols, data_type_col]
                            else:
                                new_cols.append(data_type_col)
                            self.out("...going to unify column {} since it has a new forced data type: {}".format(data_type_col, new_data_type))

            # Only unify and infer types if new rows or new columns were added
            self.out("...testing not new_rows={}".format(not new_rows))
            self.out("...testing new_cols={}, {}".format(not new_cols, new_cols))
            all_cols = transform_df.columns
            if not new_rows and not new_cols:
                # Otherwise keep the existing types, which combine the inferred/forced types from all input featuresets
                #kwargs_output['forced_types'] = data_types
                #kwargs_output['inferred_types'] = all_input_col_types
                self.out("all_input_col_types: {}".format(all_input_col_types), type='debug')
                kwargs_output['forced_types'] = {**{col:type_tuple[0] for col, type_tuple in all_input_col_types.items() 
                                                    if type_tuple[1]==FeatureSet._COL_TYPE_FLAGS_FORCED}, 
                                                 **(data_types or {})
                                                }
                kwargs_output['inferred_types'] = {col:type_tuple[0] for col, type_tuple in all_input_col_types.items() 
                                                   if (data_types is None or col not in data_types) 
                                                   and type_tuple[1]==FeatureSet._COL_TYPE_FLAGS_INFERRED}
                self.out("NO NEW ROWS OR COLUMNS, NOT UNIFYING COLUMNS AGAIN", type='debug')
                self.out("...using forced_types: {}".format(kwargs_output['forced_types']), type='debug')
                self.out("...using inferred_types: {}".format(kwargs_output['inferred_types']), type='debug')
                #self.out("...existing columns have types: {}".format(all_input_col_types), type='debug')
            else:
                if new_rows or new_cols=='*':
                    # ...then unify all columns except the index cols
                    cols_to_exclude = list(output_index_cols_set)
                    self.out("Will exclude these columns from unifying: {}".format(output_index_cols_set), type='debug')
                elif isinstance(new_cols, str) or isinstance(new_cols, list) or isinstance(new_cols, set):
                    # ...then unify only the given new columns
                    not_new_cols_set = set(all_cols) - set(new_cols)
                    cols_to_exclude = list(output_index_cols_set | not_new_cols_set)

                self.out("UNIFY START:{}".format(datetime.datetime.now()), type='debug')
                self.out("...excluding cols: {}".format(cols_to_exclude), type='debug')
                self.out(os.popen('free').read(), type='debug')

                # Unify the columns needed
                transform_df, unified_types = FeatureSet._unifyDataTypes(transform_df, fillna=fillna, 
                                                                          debug=(self.output_mode=='debug' or (self.dsphere is not None and self.dsphere.output_mode=='debug')),
                                                                        cols_to_exclude=cols_to_exclude,
                                                                        #cols = cols_to_unify,
                                                                        forced_types=data_types)
                self.out("UNIFY FINISH:{}".format(datetime.datetime.now()), type='debug')
                self.out(os.popen('free').read(), type='debug')
                kwargs_output['forced_types'] = data_types
                kwargs_output['inferred_types'] = unified_types
                self.out("...finished unifyDataTypes()", type='debug')

            # Also reset the index (for instance if this was a subset transform)
            # Note: In Dask this index can include repeats across partitions (i.e. each partitions starts with 0)
            if isinstance(transform_df, pd.DataFrame):
                transform_df.reset_index(drop=True, inplace=True)
            elif isinstance(transform_df, dd.DataFrame):
                transform_df = transform_df.reset_index(drop=True)
            self.out("RESET INDEX FINISH:{}".format(datetime.datetime.now()), type='debug')                
            self.out("Calling addData for type: {}, columns: {}, shape: {}".format(type(transform_df), 
                                                                                   len(transform_df.columns), 
                                                                                   transform_df.shape))

            # Take out lingering data types for columns now dropped
            if 'forced_types' in kwargs_output and kwargs_output['forced_types'] is not None:
                new_forced_types = {col:kwargs_output['forced_types'][col] \
                                    for col in kwargs_output['forced_types'] if col in all_cols}
                if len(new_forced_types)<len(kwargs_output['forced_types']):
                    dropped_types = list(set(kwargs_output['forced_types'].keys()) - set(new_forced_types))
                    self.out(f"...dropped forced_types for columns no longer present: {dropped_types}")
                    kwargs_output['forced_types'] = new_forced_types

            if 'inferred_types' in kwargs_output and kwargs_output['inferred_types'] is not None:
                new_inferred_types = {col:kwargs_output['inferred_types'][col] \
                                    for col in kwargs_output['inferred_types'] if col in all_cols}
                if len(new_inferred_types)<len(kwargs_output['inferred_types']):
                    dropped_types = list(set(kwargs_output['inferred_types'].keys()) - set(new_inferred_types))
                    self.out(f"...dropped inferred_types for columns no longer present: {dropped_types}")
                    kwargs_output['inferred_types'] = new_inferred_types
        else:
            kwargs_output['forced_types'] = data_types
            kwargs_output['inferred_types'] = None

        # 6/22/20: Moved this up to top of _transform()
        # Set this flag to False so addData (below) does not create another copy of this on disk
        # save_to_disk = False if engine=='parquet' else True

        # Set up the new FeatureSet with the transformed data and new feature/index/label col 
        #print("kwargs_output:", kwargs_output)
        self.out("Calling addData for type", type(transform_df))
        output_featureset = self.addData(output_label, transform_df, datatype='dataframe',
                                         index_cols=output_index_cols_set, 
                                         feature_cols=output_feature_cols_set, 
                                         label_cols=output_label_cols_set,
                                         #overwrite=overwrite,
                                         #save_to_disk=save_to_disk,
                                         view_output=False,
                                         **kwargs_output)

        self.out("New feature set '{}', batch '{}', variant '{}' has shape: {}".format(output_label, batch, kwargs_output['variant'], output_featureset.shape(kwargs_output['variant'], child='*')))
        output_featureset._printColumnTypes()

        # Set up dependency so we can know when updates need to happen
        # Store the transformer in an encapsulated object
        transformer_obj = {'type': 'transform',
                           'class': transformer_function.__class__ if hasattr(transformer_function, '__class__') else None,
                           #'function': transformer_function.__func__ if hasattr(transformer_function, '__func__') else None,
                           'args': args, 
                           #'kwargs': kwargs_transformer
                          }

        # TODO Handle dependency on either >1 input feature sets, rather than separating into two dependencies            
        for input_label in input_labels:
            self.out("Setting dependency '{}' --> '{}' via transform: {} with {} args, kwargs={}, kwargs_output={}".format(input_label, output_label, transformer_function, len(args), kwargs.keys(), kwargs_output.keys())) 
            self._setDependency(output_label, input_label, transformer_obj, **kwargs_output) 
        #self._updateFeatureSetMetadata()

        # Keep track of all input / output variants and new index cols created
        if input_labels_with_variants is not None and len(input_labels_with_variants)>0:
            new_index_cols_list = new_index_cols or [[] for a in range(len(input_labels_with_variants))]
        else:
            new_index_cols_list = input_labels_with_variants
        transform_metadata.append({'output_featureset':output_label, 
                                   'output_variant':this_output_variant,
                                   'inputs':[{'input_featureset':input_label,
                                              'input_variant':input_variant,
                                              'input_child':child,
                                              'index_col':new_index_col}
                                             for ((input_label,input_variant),new_index_col) in 
                                                 zip(input_labels_with_variants, new_index_cols_list)
                                            ]
                                  })

        # Free up memory by deleting references and deleting the copy
        # TODO Delete >1 input feature sets too
        del(input_data)
        del(input_df_copy)
        del(transform_df)
        gc.collect()

        self.out("Feature Set '{}': {}".format(output_featureset.label, output_featureset.shape()))
        self.out("===============================================================")

    # New on 6/7/20: Pass this "metadata" back out of the transform so the calling function knows what took place
    return transform_metadata

#############################################################################################
# new_col_function: lambda function to create the new column either:
# - row-wise, where the lambda function takes one row at a time as the input "x", e.g.
#   lambda x: x['col_1'] + x['col_2'] if x['col_1']==x['col_1'] else 0
# - column-wise, where the lambda function takes one column and operates on it all at once (much more efficient):
#   lambda x: max(x, 0.0) --> here the 'on' parameter must be passed in specifying the column to run this function on
# - column-wise with >1 columns to operate on:
#   lambda x: np.mean(x[0], x[1]) --> here the 'on' parameter should contain a list of the 2 columns that will become
#   the two parts of the tuple x[0] and x[1] (and it requires this tuple-style format of the function)
# or alternatively pass 
# on: the column that should be inputted to the new_col_function (optional) in a vectorized way, not using apply
# Note: Use the on var whenever possible and reduce the function to just operate on one col at a time --
# map() is much faster than apply()
def addColumn(self, input_label, new_column, new_col_function, on=None, view_output=True, **kwargs):

    def add_column(df, on_col=None, **kwargs):
        self.out("ADD COLUMN START:{}".format(datetime.datetime.now()), type='debug')
        self.out(os.popen('free').read(), type='debug')
        if df.shape[0]==0:
            # If the dataframe is empty, just insert the column as null, don't try the mapping function below
            df[new_column] = None
            self.out("Dataframe is empty, inserting null column '{}'".format(new_column))
        elif on_col is not None:
            self.out("Using map()...")
            if isinstance(on_col, str): 
                df[new_column] = df[on_col].map(new_col_function)
            elif isinstance(on_col, list):
                #temp_col = "TEMP::{}".format('_'.join(on_col))
                self.out("...multiple on columns...creating a temp column containing the tuple")
                #df[temp_col] = tuple([df[one_on_col] for one_on_col in on_col])
                temp_tuple_col = pd.Series(list(df[on_col].itertuples(index=False, name=None)))
                print("...created tuples")
                df[new_column] = temp_tuple_col.map(new_col_function)
                del(temp_tuple_col)
        else:
            try:
                self.out("Trying column-wise function...")
                df[new_column] = new_col_function(df)
            except:
                self.out("...didn't work, trying row-wise apply()...")
                df[new_column] = df.apply(new_col_function, axis=1)
            #df[new_column] = df.applymap(new_col_function)
#             new_col_list = []
#             for _, row in df.iterrows():
#                 new_col_list.append(new_col_function(row))
        #new_col_df = pd.DataFrame({'new_column': new_col_list})
        self.out("ADD COLUMN FINISH:{}".format(datetime.datetime.now()), type='debug')
        self.out(os.popen('free').read(), type='debug')
        return df

    self._transform(input_label, add_column, input_label, on_col=on, new_rows=False, new_cols=[new_column], **kwargs)
    if view_output:
        self.view(input_label, 'shape', child=None)

#############################################################################################
# Note: If passing in agg_functions=['size'] or 'size', then can leave agg_vars as None
# TODO: Implement the conditions on '*' to perform agg_functions only on the right types of vars.  (i.e. sum --> only numeric, max --> numeric, dates, and strings)
# TODO: Make children opaque altogether?  Don't allow the user to control what happens inside children.  Just find column labels.
# TODO: This still requires knowing which child 'var1' is in. Should allow lookup of which child 'var1' is in.
# TODO: Make sure each var name can only be in one child data set. Else this lookup is tricky.
def aggregate(self, output_label, input_label, index_vars=None, agg_functions=None, agg_vars=None, agg_var_names=None, view_output=True, **kwargs):
    """Aggregate data together in a given FeatureSet -- such as to find the sum, average, count, min, max, or other calculation on each unique group of the given index variable(s) -- and saves the results into a new FeatureSet in the FeatureSpace. 

    * Parameters:
        1. **output_label**: Label of the new FeatureSet where results of this aggregation will be saved
        2. **input_label**: FeatureSet which we will perform the aggregation on

        - **index_vars**: (optional, default=None) Unique values of this variable(s) will be aggregated together and each have one row in the output FeatureSet. For instance, 'patient_id' means the aggregation will be performed across all rows in the input FeatureSet with the same 'patient_id', and that 'patient_id' value will get one row in the output. Either:
            - None: Perform the aggregations across all rows of the input FeatureSet, and the output will have just 1 row
            - String: Name of one column in the input FeatureSet to treat as the index variable (e.g. 'patient_id')
            - List: List of columns to use together as index variables, where each unique *combination* of values for all index variables will be grouped together and given one row in the output FeatureSet (e.g. ['patient_id', 'year'] will calculate teh agg_functions on each patient per year.)

        - **agg_functions**: (optional, default=None) Which calculations or aggregations should be performed across rows for each unique index, provided as either a string (just one operation such as 'sum') or a list of operations (e.g. ['sum', 'count']) which will all be performed on all **agg_vars**.  The full list of supported operations is:
            - 'sum' (total across the group++)
            - 'min' (minimum value in the group)
            - 'max' (maximum value in the group)
            - 'mean' (average of the group++)
            - 'median' (median of the group++)
            - 'count' (how many non-null values are in the group)
            - 'size' (how many rows are in each group, regardless of nulls or non-nulls)
            - 'nunique' (how many unique values are in the group)
            - 'std' (standard deviation of the group++)
            - 'var' (statistical variance of the group++)
            - 'sem' (standard error from the mean within each group++)
            - 'first' (first row of each group using the order of rows in the input FeatureSet)
            - 'last' (last row of each group using the order of rows in the input FeatureSet)
            - *custom lambda*: you may provide a custom lambda function to perform any calculation across the rows for a single variable (i.e. it must be univeriate, such as my_function(x), and not require any additional inputs)

            ++ only applicable to numeric variables

        - **agg_vars**: (optional, default=None) The variable(s) that will be aggregated together using the **agg_functions**, either:
            - None: Only allowed if **agg_functions** = ['size'] because there is no need to choose variables if we are only counting rows
            - String: Aggregate only this variable
            - '*': Perform the aggregations on *all* variables in the **input_label** FeatureSet except the **index_vars**. 
                - Note: Currently this may break if you try to perform aggregation functions on the wrong variable types, such as 'sum' on a string variable.
            - List: List of variables (e.g. ['var1', 'var2']), all of which we will perform *all* the **agg_functions**, resulting in len(**agg_vars**)*len(**agg_functions**) aggregated variables.
            - Dict: Definition of which agg_vars to aggregate within each "child" of the input FeatureSet (e.g. {None: ['var1', 'var2'], 'child1':'*', 'child2:'var3'} --> perform all **agg_functions** on 'var1' and 'var2' in the parent dataframe, on *all* variables in 'child1', and on 'var3' in 'child2').
                - Note: Passing in a dict here will override passing in child to the overall aggregate() call.

         - **agg_var_names**: (optional, default=None) The names of the outputted aggregated variables, if you'd like to customize these names rather than allow aggregate() to decide how to name the variables. Options:
             - None: aggregate() will name the calculated aggregate variables as {agg_var}_{agg_function}, e.g. 'var_1_sum'
             - String: If there is only one function in **agg_functions** and one variable in **agg_vars** then this can be the name of the single output variable. Otherwise throws an error.
             - List: Names to give to each of the output aggregate variables in the output FeatureSet.  Must have the same length as len(**agg_vars**)*len(**agg_functions**) or else throws an error.

    * Returns: *Nothing returned*

    """
    # Note: On 12/14/20 added dropna=False into the groupby statements so null values are now kept in the index_vars
    self.out("\nStarting aggregate({}, {}, agg_vars={}, agg_functions={}, index_vars={}, agg_var_names={}, kwargs={})".format(output_label, input_label, agg_vars, agg_functions, index_vars, agg_var_names, kwargs), type='progress')

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def agg_function(input_dataset, index_vars, agg_vars, agg_functions, agg_var_names, primary_datasets=None, **kwargs):
        self.out("\nCalling agg_function({}, index_vars={}, agg_vars={}, agg_functions={}, agg_var_names={}, primary_datasets={}, kwargs={})".format(type(input_dataset), index_vars, agg_vars, agg_functions, agg_var_names, type(primary_datasets), kwargs))  
        child = kwargs.get('child', None)
        if isinstance(agg_var_names, str):
            agg_var_names = [agg_var_names]

        # If just one agg_var provided in a list, convert it to a string
        if (isinstance(agg_vars, list) or isinstance(agg_vars, tuple) or isinstance(agg_vars, set)) and len(agg_vars)==1:
            agg_vars = agg_vars[0] 

        self.out("...using child={}, agg_var_names={}, agg_vars={}".format(child, agg_var_names, agg_vars))

            # If agg_functions is just 'count' and agg_vars is None, use the index_vars as the agg_vars
        dummy_var = '---DUMMYVAR---'
        if agg_vars is None:
            #if (agg_functions == ['count'] or agg_functions == 'count') \
            if (agg_functions == ['size'] or agg_functions == 'size') \
                and (isinstance(input_dataset, pd.DataFrame) or isinstance(input_dataset, dd.DataFrame)):
                if index_vars is not None:
                    input_cols_no_index = set(input_dataset.columns) - set(index_vars)
                else:
                    input_cols_no_index = set(input_dataset.columns)
                if len(input_cols_no_index)>0:
                    # TODO: Fix this! This picks a semi-random column, which is not 
                    agg_vars = input_cols_no_index.pop()
                    self.out("agg_vars=", agg_vars)
                else:
                    agg_vars = dummy_var
                    input_dataset[dummy_var] = 1
                if agg_var_names is None:
                    #agg_var_names = ['count']
                    agg_var_names = ['size']
            elif not isinstance(input_dataset, pd.Series):
                self.out("ERROR: No aggregation vars provided in aggregate()", type='error')
                return None

        # Make sure the agg_functions are iterable
        if not isinstance(agg_functions, list) and not isinstance(agg_functions, set):
            #isinstance(agg_functions, str) or (callable(agg_functions) and agg_functions.__name__ == "<lambda>"):
            agg_functions = [agg_functions]

        # De-dup the agg_functions, since it breaks below when there are dups (but keep order the same)
        # Thanks to: 
        # https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order
        agg_function_set = set()
        agg_function_set_add_fn = agg_function_set.add
        agg_functions = [fn for fn in agg_functions if not (fn in agg_function_set or agg_function_set_add_fn(fn))]
        self.out("Using agg_functions: {}".format(agg_functions))

        #########################
        # Need to handle nunique slightly differently to produce a Dataframe not a Series
        if hasattr(input_dataset, '__feature_type__') and input_dataset.__feature_type__=='FeatureMatrix':
            # Handle when child is a FeatureMatrix
            self.out("Trying to aggregate a FeatureMatrix...")

            # Need to create a matrix representing the index cols
            index_dataset = primary_datasets[0].copy()
            #index_dataset = index_dataset.assign(__DUMMY__ = lambda x: 1)
            index_dataset['__DUMMY__'] = 1
            if isinstance(index_vars, list) and len(index_vars)>1:
                # Need to handle multiple index vars differently
                temp_index_col = _get_index_col(index_vars)
                index_counts_multivar = index_dataset.groupby(index_vars, 
                                                              as_index=False, 
                                                              dropna=False,
                                                              observed=True)['__DUMMY__'].count()
                index_counts_multivar_sorted = index_counts_multivar.sort_values(index_vars)[index_vars]
                index_counts_multivar_sorted[temp_index_col] = index_counts_multivar_sorted.index
                index_unique_list = index_counts_multivar_sorted[temp_index_col].values
                index_cols_df = index_dataset[index_vars]
                index_cols_df_with_indices = index_cols_df.merge(index_counts_multivar_sorted, on=index_vars, how='left')
                all_index_values = index_cols_df_with_indices[[temp_index_col]].values
                # TODO: Should we replace nulls in multiple index vars too?
            else:
                #index_counts = index_dataset.groupby(index_vars, dropna=False)['__DUMMY__'].count()
                if isinstance(index_dataset, dd.DataFrame):
                    #index_unique_list = np.sort(list(index_counts.compute().index))
                    index_cols_df = index_dataset[index_vars].compute()
                    #all_index_values = index_dataset[index_vars].compute().values
                else:
                    #index_unique_list = np.sort(list(index_counts.index))
                    index_cols_df = index_dataset[index_vars]
                    #all_index_values = index_dataset[index_vars].values

                # Fill in nulls efficiently in the full (unsorted) index vars list 
                # with the corresponding blank/0 value based on the column type
                all_var_types = kwargs['all_data_types']
                index_var_types = [all_var_types[x][0] if x in all_var_types else 'str' for x in index_vars]
                for index_var, index_var_type in zip(index_vars, index_var_types):
                    null_indexes = index_cols_df[index_cols_df[index_var]!=index_cols_df[index_var]].index
                    if len(null_indexes)>0:
                        blank_val = 0
                        if index_var_type=='str':
                            blank_val = ''
                        elif index_var_type=='float':
                            blank_val = 0.0
                        elif index_var_type=='int':
                            blank_val = 0
                        elif index_var_type=='date':
                            blank_val = 0
                        self.out("...filling in {} nulls in index column '{}' ({}) with value {}".format(len(null_indexes),
                                                                                                      index_var, 
                                                                                                      index_var_type, 
                                                                                                      blank_val))
                        index_cols_df.loc[null_indexes, index_var] = blank_val

                    else:
                        self.out("...no nulls found in index column '{}'".format(index_var))


                all_index_values = index_cols_df.values

                # Get the list of unique index var combinations (after filling in nulls)
                index_counts = index_cols_df.groupby(index_vars, dropna=False, observed=True).count()
                print("...index_counts shape:", index_counts.shape, index_counts.index.map(type).value_counts())

                # Get a sorted list of the index values as a numpy array (and if strings, sort it a different way)
                from pandas.api.types import is_string_dtype
                if is_string_dtype(index_counts.index):
                    index_unique_list = np.array(index_counts.sort_index(na_position='first').index)
                else:
                    index_unique_list = np.sort(list(index_counts.index))

            num_index_values = all_index_values.shape[0]
            self.out("Found {} index values ({} uniques) using index vars: {}".format(num_index_values, 
                                                                                   index_unique_list.shape[0], 
                                                                                   index_vars))
            num_null_index_vals = len([val for val in all_index_values.flatten() if val is None or val!=val])
            self.out("...{} null values in index values".format(num_null_index_vals))

            if num_null_index_vals>0:
                # Note: Currently we shouldn't hit this error case if there's one index var, because
                # the above code replaces the nulls automatically.  Only if >1 index var and any has nulls.
                print("ERROR: Cannot run aggregate() with null values in the index vars")
                raise

            # https://stackoverflow.com/questions/7632963/numpy-find-first-index-of-value-fast/7654768
            index_locations = np.searchsorted(index_unique_list, all_index_values, side='left')
            #print(np.max(index_unique_list))
            #print(all_index_values.max())
            self.out("...found {} locations".format(index_locations.shape))

            dtype_to_use = constants.getDtype(num_index_values)
            rows = np.arange(num_index_values, dtype=dtype_to_use)
            #print("rows:", rows.shape)
            #print("cols:", len(cols), cols[0])
            vals = np.ones((num_index_values,), dtype=dtype_to_use)
            #print("vals:", vals.shape)
            #cols_array = np.asarray(cols).flatten()
            cols_array = index_locations.flatten()
            #print("cols_array:", cols_array.shape, cols_array[:10], cols_array.max())

            #index_onehot_sparse = sp.csr_matrix((vals, (rows, cols)))
            index_onehot_sparse = sp.csr_matrix((vals, (rows, cols_array)))
            self.out("Created sparse one-hot matrix representing the indexes:", index_onehot_sparse.shape, type(index_onehot_sparse))

            # Handle multiple possible column lists
            if isinstance(agg_vars, str):
                if agg_vars=='*':
                    # '*' --> use all columns in the FeatureMatrix
                    agg_vars_list = input_dataset.columns()
                else:
                    # Or a single column
                    agg_vars_list = [agg_vars]
            else:
                # Or a list of columns
                agg_vars_list = agg_vars

            # Get numpy matrix representing 1/0 for each index (col) in each row
            input_dataset_matrix = input_dataset.getMatrix()
            input_dataset_cols = input_dataset.columns()
            agg_var_col_nums = [input_dataset_cols.index(input_col) for input_col in agg_vars_list]

            all_matrix_cols = None
            matrix_column_names = []
            # Iterate through each agg_function
            for agg_fn in agg_functions:
                if agg_fn=='sum':
                    # Use matrix multiplication to solve this for us quickly
                    self.out("Summing child FeatureMatrix '{}' with shape {} along {} columns".format(child, input_dataset_matrix.shape, len(agg_var_col_nums)))
                    agg_var_matrix = input_dataset_matrix.tocsr()[:,agg_var_col_nums]
                    print("...got agg var matrix: {}".format(agg_var_matrix.shape))

                    # Multiply the index matrix by the (single) agg var column
                    all_matrix_cols = index_onehot_sparse.T * agg_var_matrix
                    #agg_var_x_index = index_onehot_sparse.multiply(agg_var_matrix)
                    print("...multiplied index matrix ({}) X agg var matrix ({}) = all_matrix_cols ({})".format(index_onehot_sparse.shape, agg_var_matrix.shape, all_matrix_cols.shape))                                             

                    # Append another column name based on the agg_var and the agg_fn
                    matrix_column_names = ['{}_{}'.format(agg_var, agg_fn) for agg_var in agg_vars_list]

                elif agg_fn=='max' or agg_fn=='min':
                    # Iterate through each agg_var and create a column, then concat them together
                    #for agg_var in agg_vars_list:
                    print("...calculating the {} of each column in matrix with {} columns".format(agg_fn, 
                                                                                                  len(agg_vars_list)))
                    #all_stacked_cols = []
                    for agg_var, agg_var_num in zip(agg_vars_list, agg_var_col_nums):
                        #self.out("Trying to aggregate just '{}' (col #{}) in a FeatureMatrix".format(agg_var, agg_var_num))
                        #agg_var_matrix = input_dataset.getMatrix(col=agg_var)
                        agg_var_matrix = input_dataset_matrix.getcol(agg_var_num)
                        #self.out("...got agg var matrix: {}".format(agg_var_matrix.shape), type='debug')

                        # Multiply the index matrix by the (single) agg var column
                        agg_var_x_index = index_onehot_sparse.multiply(agg_var_matrix)
                        #self.out("...multiplied index matrix ({}) X agg var matrix ({}) = agg_var_x_index ({})".format(index_onehot_sparse.shape, agg_var_matrix.shape, agg_var_x_index.shape), type='debug')


                        if agg_fn == 'max':
                            agg_x_index = agg_var_x_index.max(axis=0).transpose()
                            #print("...took max of each row: {}".format(agg_x_index.shape))
                        elif agg_fn == 'min':
                            agg_x_index = agg_var_x_index.min(axis=0).transpose()
                            #print("...took min of each row: {}".format(agg_x_index.shape))
#                             elif agg_fn == 'sum':
#                                 agg_x_index = agg_var_x_index.sum(axis=0).transpose()
#                                 print("...took sum of each row: {}".format(agg_x_index.shape))
#                             else:
#                                 # TODO: Implement more functions
#                                 self.out("DON'T KNOW HOW TO EXECUTE THIS AGG FUNCTION! '{}'".format(agg_fn), type='error')
                        agg_x_index_sparse = sp.coo_matrix(agg_x_index)
                        #all_stacked_cols.append(agg_x_index_sparse)
                        if all_matrix_cols is None:
                            all_matrix_cols = agg_x_index_sparse
                        else:
                            # Otherwise stack the columns together horizontally
                            all_matrix_cols = sp.hstack([all_matrix_cols, agg_x_index_sparse])

                        # Append another column name based on the agg_var and the agg_fn
                        matrix_column_names.append('{}_{}'.format(agg_var, agg_fn))
                    #all_matrix_cols = sp.hstack(all_stacked_cols)
                    print("...stacked columns together, now have matrix of shape {}".format(all_matrix_cols.shape))

                    # Construct new column names using the aggregate function
                    #agg_fn = agg_functions if isinstance(agg_functions, str) else agg_functions[0]
                    #matrix_column_names = ['{}_{}'.format(agg_var, agg_fn) for agg_var in agg_vars_list]

                else:
                    # TODO: Implement more functions
                    self.out("DON'T KNOW HOW TO EXECUTE THIS AGG FUNCTION! '{}'".format(agg_fn), type='error')
                    raise

            # Use the provided agg_var_names if they have the right length
            num_matrix_columns = len(matrix_column_names)
            if agg_var_names is not None:
                if (isinstance(agg_var_names, str) and num_matrix_columns==1) or num_matrix_columns==len(agg_var_names):
                    column_names = agg_var_names
                else:
                    self.out("WARNING! The agg_var_names provided has length {}, but there are {} agg vars created here. Ignoring the provided agg_var_names to continue execution.".format(len(agg_var_names), num_matrix_columns), type='warning')
                    column_names = matrix_column_names
            else:
                column_names = matrix_column_names

            # Transpose so this is a column array, and store that as a FeatureMatrix object
            self.out("Creating FeatureMatrix with matrix:{}".format(all_matrix_cols.shape))
            return FeatureMatrix(label=child, 
                                 matrix=all_matrix_cols, 
                                 columns=column_names, 
                                 mappings=input_dataset.getMappings())

            # TODO: Save the column for the index as its own DataFrame in child=None

        # IF no index vars passed in (and it's a dask/pandas dataframe)
        elif index_vars is None:
            # TODO: Handle agg_vars='*'
            if isinstance(agg_vars, str):
                temp_df = input_dataset[[agg_vars]]
                temp_df[dummy_var] = 1
                # Note this dropna=False needs pandas==1.1.0 or later:
                # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html
                agg_df = temp_df.groupby(dummy_var, 
                                         dropna=False, 
                                         observed=True)[agg_vars].agg(agg_functions).reset_index().drop(dummy_var, axis=1) 
                agg_df.columns = ['{}_{}'.format(agg_vars, col) for col in agg_df.columns.values]
            else:
                temp_df = input_dataset[agg_vars]
                temp_df[dummy_var] = 1
                agg_df = temp_df.groupby(dummy_var, 
                                         dropna=False, 
                                         observed=True)[agg_vars].agg(agg_functions).reset_index().drop(dummy_var, axis=1)
                agg_df.columns = ['_'.join(col).strip() if col[0] in agg_vars else col[0] for col in agg_df.columns.values]

        # Handle a pandas DataFrame
        elif isinstance(input_dataset, pd.DataFrame):     
            if isinstance(agg_vars, str):
                if agg_vars=='*':
                    agg_df = input_dataset.groupby(index_vars, 
                                                   as_index=False, 
                                                   dropna=False,
                                                   observed=True).agg(agg_functions).reset_index()
                else:
                    # Handle when child is a pandas DataFrame 
                    agg_df = input_dataset.groupby(index_vars, 
                                                   as_index=False, 
                                                   dropna=False,
                                                   observed=True).agg({agg_vars: (agg_functions)})   
            else:
                # Handle when child is a pandas DataFrame
                agg_df = input_dataset.groupby(index_vars, 
                                               as_index=False, 
                                               dropna=False,
                                               observed=True)[agg_vars].agg(agg_functions).reset_index()

        # Handle a pandas Series
        elif isinstance(input_dataset, pd.Series):
            # Check for aggregate() calls that cannot be run on a Series
            if agg_vars is not None:
                self.out("ERROR: Running aggregate() on a pandas Series cannot accept agg_vars={}".format(agg_vars), type='error')
                return None
            if index_vars is not None:
                if (isinstance(index_vars, str) and index_vars != input_dataset.name) or \
                   (isinstance(index_vars, list) and len(index_vars)==1 and index_vars[0] != input_dataset.name):
                    self.out("ERROR: Cannot run aggregate() using index_vars={} on pandas Series with one column named '{}'".format(index_vars, input_dataset.name), type='error')
                    return None

            agg_df = input_dataset.groupby(input_dataset, 
                                           dropna=False,
                                           observed=True).agg(agg_functions)

        # Handle a Dask dataframe (and anything else)
        else:
            # Note edge case: This will break if you pass in ['nunique','nunique']
            if isinstance(agg_vars, str):
                if agg_vars=='*':
                    agg_df = input_dataset.groupby(index_vars, 
                                                   dropna=False).agg(agg_functions).reset_index()   
                else:
                    # Otherwise assume the child is a dask DataFrame
                    agg_df = input_dataset.groupby(index_vars, dropna=False).agg({agg_vars: (agg_functions)}).reset_index()
            else:
                # Otherwise assume child is a dask DataFrame
                agg_df = input_dataset.groupby(index_vars, dropna=False)[agg_vars].agg(agg_functions).reset_index()

        # Rename the columns of the output aggregated results
        if agg_var_names is not None:
            if index_vars is not None:
                agg_df.columns = index_vars + agg_var_names
            else:
                agg_df.columns = agg_var_names
        elif index_vars is not None:
            if isinstance(agg_df, pd.DataFrame) or isinstance(agg_df, dd.DataFrame): 
                agg_df.columns = ['_'.join(col).strip() if col[0] in agg_vars else col[0] for col in agg_df.columns.values]

        return agg_df
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # Efficient way to calculate nuniques on a Dask dataframe
    # Courtesy of: https://stackoverflow.com/questions/45922884/dask-nunique-method-on-dataframe-groupby 

    # First map each partition to a unique list
    def chunk(s):
        return s.apply(lambda x: list(set(x)))

    # Then reduce by aggregating across partitions
    def agg(s):
        s = s._selected_obj    
        return s.groupby(level=list(range(s.index.nlevels))).sum()

    # Optional function to apply across the agg functions 
    def finalize(s):
        return s.apply(lambda x: len(set(x)))

    nunique_fn = dd.Aggregation('nunique', chunk, agg, finalize)

    # Automically include the index_vars for this aggregate() call in the index_cols of the resulting feature set
    #index_cols = kwargs.get('index_cols', [])
    #index_cols = [index_cols] if isinstance(index_cols, str) else index_cols
    if index_vars is not None:
        index_vars = [index_vars] if isinstance(index_vars, str) else index_vars
        #index_cols += [index_var for index_var in index_vars if index_var not in index_cols]
    #kwargs['index_cols'] = index_cols
    #self.out("Received index_vars={} --> sending in index_cols={} to the transform".format(index_vars, index_cols))

    # TODO: Check if the index_vars are in the child=None (primary) FeatureSet, if not flag an error
    # Otherwise we're just assuming the index vars are there in child=None


    # Check if agg_vars is a dict --> Need to pull vars out of each child/column tag one at a time
    # Note: Here the child's label and the "tagging" of a group of columns are synonymous.
    child_cols_to_aggregate = {}
    if isinstance(agg_vars, dict):
        child_cols_to_aggregate = agg_vars

        # Remove any value of child passed into the fs.aggregate() call, which is now overriden by the dict
        kwargs.pop('child', None)

        # Iterate through each child/tag name and pull out the corresponding vars 
        #for column_tag in agg_vars:
        #    column_list = agg_vars[column_tag]

        # TODO: If '*', then need to look up all the vars for that child

        # Create a dict to iterate through below

        # Handle if child is not None --> need to somehow pass those into the self._transform() call

    else:
        # Mimic that dict/list structure with just child=None in it, to iterate through below
        child_cols_to_aggregate[None] = agg_vars

        # TODO: Fix this so that agg_vars='*' means repeat child:['*'] for all children


    # Replace any 'nunique' agg function with the function object nunique_fn (dask only)
    engine = kwargs.get('engine', None)
    self.out("Using engine={}".format(engine))
    if engine == 'dask':
        if isinstance(agg_functions, str) and agg_functions=='nunique':
            agg_functions = [nunique_fn]
        elif agg_functions is not None:
            for agg_index, agg_fn in enumerate(agg_functions):
                if agg_fn == 'nunique':
                    agg_functions[agg_index] = nunique_fn
        else:
            self.out("ERROR! No aggregation functions provided, cannot proceed.", type='error')
            return None

    # Need to overwrite the whole FeatureSet here
    # TODO: Will overwrite variants too! 
    #kwargs['overwrite'] = True

    # Transition to iterating through the structure above (even if only one data set to run on)
    is_first_child = True
    has_parent = False
    for child_label in child_cols_to_aggregate:
        # Pull out the list of columns to aggregate for this child (or '*')
        child_agg_vars = child_cols_to_aggregate[child_label]
        kwargs['child'] = child_label

        # Keep track of whether any of the children is the parent (child=None)
        if child_label is None:
            has_parent = True

        # After the first child, set overwrite to True to tell transform -> addData -> save to overwrite the previous copy
        if not is_first_child:
            kwargs['overwrite'] = True

        # If the child is not the primary (child=None) and it's a FeatureMatrix, then create an index matrix to pass in
        #if child_label is not None:

        # New 6/2/20: Pass-in the inferred/forced types for all vars
        all_var_types = self.Features(input_label).types
        kwargs['all_data_types'] = all_var_types

        self.out("Running aggregation transform on '{}', child='{}' --> pushing result into '{}'...".format(input_label, child_label, output_label)) 
        self._transform(output_label, agg_function, input_label, 
                       index_vars=index_vars, 
                       agg_vars=child_agg_vars, agg_functions=agg_functions, agg_var_names=agg_var_names,
                       reset_data=is_first_child,
                       **kwargs)
        is_first_child = False

    # Handle edge-case where none of the given children to aggregate is the parent (child=None)
    # So we need to manually create the parent with just the index cols
    if not has_parent:
        index_dfs_all_variants = self.Features(input_label).getData(variant='*', child=None)
        # Convert into a dict if just one variant=None
        if not isinstance(index_dfs_all_variants, dict):
            index_dfs_all_variants = {None: index_dfs_all_variants}

        # Iterate through each variant
        for this_variant in index_dfs_all_variants:
            # Repeating code inside agg_function above...
            index_dd = index_dfs_all_variants[this_variant].copy()
            index_dd['__DUMMY__'] = 1
            if isinstance(index_vars, list) and len(index_vars)>1:
                # If multiple index vars
                index_counts_multivar = index_dd.groupby(index_vars, as_index=False, dropna=False)['__DUMMY__'].count().drop('__DUMMY__', axis=1)
                if isinstance(index_dd, dd.DataFrame):
                    index_counts_multivar = index_counts_multivar.compute()
                index_uniques = index_counts_multivar.sort_values(index_vars)[index_vars]

            else:
                # Single index var
                #index_uniques = index_dd.groupby(index_vars)['__DUMMY__'].count().compute()
                #index_counts = index_dd.groupby(index_vars)['__DUMMY__'].count().reset_index().drop('__DUMMY__', axis=1)
                index_uniques = index_dd.groupby(index_vars, dropna=False)['__DUMMY__'].count().reset_index().drop('__DUMMY__', axis=1).compute().sort_values(index_vars).reset_index(drop=True) if isinstance(index_dd, dd.DataFrame) else index_dd.groupby(index_vars, dropna=False)['__DUMMY__'].count().reset_index().drop('__DUMMY__', axis=1).sort_values(index_vars).reset_index(drop=True)

            #index_unique_list = np.sort(list(index_counts.index))                
            self.out("No parent in the output, so going to save index cols {} as a dataframe {} to be child=None for variant={}".format(index_vars, index_uniques.shape, this_variant), type='warning')
            #print(index_dd.head())
            kwargs_parent = {'overwrite':True, 'child':None, 'variant':this_variant, 'engine':engine}
            output_featureset = self.addData(output_label, index_uniques, datatype='dataframe',
                             #index_cols=index_vars, 
                             **kwargs_parent)
            self.out("Added parent to data set '{}', variant '{}' --> new shape: {}".format(output_label, kwargs_parent['variant'], output_featureset.shape(kwargs_parent['variant'], child='*')))

    if view_output:
        self.view(output_label)
#        self._transform(output_label, agg_function, input_label, index_vars=index_vars, agg_vars=agg_vars, agg_functions=agg_functions, agg_var_names=agg_var_names, **kwargs)


#############################################################################################
# Basically a wrapper around a certain call to aggregate() to de-duplicate the rows of a dataframe
# how = 'last', 'first', 'max', 'min', or even aggs like 'sum' (which would probably break for text fields)
def dedup(self, output_label, input_label, *args, index_vars=None, how=None, view_output=True, **kwargs):

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def dedup_function(input_dataset, index_vars, how, primary_datasets=None, **kwargs):
        self.out("\nCalling dedup_function({}, index_vars={}, how={}, primary_datasets={}, kwargs={})".format(type(input_dataset), index_vars, how, type(primary_datasets), kwargs))  
        # Treat ['var1'] as 'var1'
        if isinstance(index_vars, list) and len(index_vars)==1:
            index_vars = index_vars[0]

        # See here: https://stackoverflow.com/questions/13035764/remove-rows-with-duplicate-indices-pandas-dataframe-and-timeseries
        input_deduped = input_dataset[~input_dataset[index_vars].duplicated(keep=how)]
        return input_deduped
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++


    if how in ['last', 'first']:
        # For first/last use dedup transform here
        self._transform(output_label, dedup_function, input_label, *args, index_vars=index_vars, how=how, 
                       new_rows=False, new_cols=None,
                       # 11/28/20: No need to unify here
                       **kwargs)

    elif how in ['max', 'min', 'sum']:
        # For min/max/sum use aggregate
        if isinstance(how, str):
            how = [how]

        self.aggregate(output_label, input_label, agg_vars='*', agg_functions=how, index_vars=index_vars, **kwargs)

    if view_output:
        self.view(output_label, 'shape')


#############################################################################################
# Subset the data by rows (given a row_filter function that outputs a boolean on each row) or columns (given a list of columns or a column filter boolean function)
# Note: For now row_filter can only be a function that can operate on an entire dataframe.  It cannot be a complex
# function that needs to run on each row of the dataframe (like using .apply).  So for instance:
#   - lambda x: x['col1']==1 is okay because it operates in a vectorized way over the entire dataframe
#   - lambda x: x['col1']==1 and x['col2']==1 is not okay, because it evaluates as an "and" between two Series of boolean values...how would that be calculated? (row-wise or col-wise?)
#   - if you want to do boolean operations combining multiple series, use the pandas boolean operators & | ~
#     e.g. lambda x: (x['col1']==1) & (x['col2']==1) 
def subset(self, output_label, input_label, *args, row_filter=None, var_to_subset=None, var_list=None, 
           cols_list=None, cols_filter=None, view_output=True, **kwargs):
    self.out("\nCalling subset({}, {}, args={}, row_filter={}, var_to_subset={}, var_list={}, cols_list={}, cols_filter={}, kwargs={})".format(output_label, input_label, args, row_filter, var_to_subset, var_list, cols_list, cols_filter, kwargs), 
             type='progress')

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def subset_function(df, new_index_col, **kwargs):
        self.out("...in subset transformer function with df={}, kwargs={}".format(type(df), kwargs))

        # Note: Moved this out to calling function 6/7/20
#             feature_set_df_num_rows = df.shape[0]
#             df[new_index_col] = np.arange(feature_set_df_num_rows)
#             self.out("...Created index col '{}' in feature set '{}'".format(new_index_col, input_label))

        df_subset = df

        # If a row_filter is provided use it to filter rows to keep based on which return true
        if row_filter is not None:
            row_mask = row_filter(df_subset) #apply(row_filter, axis=1) <-- apply is too slow, need to vectorize
            # See: https://engineering.upside.com/a-beginners-guide-to-optimizing-pandas-code-for-speed-c09ef2c6a4d6
            df_subset = df_subset[row_mask]

        # Can set a particular var to be subsetted if in a given list of values
        if var_to_subset is not None and var_list is not None:
            row_mask = df_subset[var_to_subset].isin(var_list)
            df_subset = df_subset[row_mask]
        elif var_to_subset is not None:
            self.out("WARNING: FeatureSpace.subset() received a var_to_subset but no var_list parameter. Try using row_filter instead (e.g. row_filter=lambda x: x[var] ... [some filter you want to apply])", type='warning')
        elif var_list is not None:
            self.out("WARNING: FeatureSpace.subset() received a var_list but no var_to_subset. Without knowing which var to subset based on the given list, we cannot apply this filter. Ignoring var_list.", type='warning')

        self.out(f"...cols_list={cols_list}")
        self.out(f"...df_subset cols={df_subset.columns}")
        if cols_list is not None:
            df_subset = df_subset[cols_list]
            cols_subset = set(cols_list)

        if cols_filter is not None:
            cols_subset = [col for col in df_subset.columns if cols_filter(col)]
            df_subset = df_subset[cols_subset]

        #return df_subset
        return {'dataframe': df_subset,
                'index_cols': [new_index_col]
               }

    # Check if there are children or not
    new_index_col = "IX::TEMP::{}".format(input_label) #_get_index_col(input_label)
    variant = kwargs.get('variant', '*')
    child = kwargs.get('child', '*')
    data_types = kwargs.get('data_types', None)
    children = self.Features(input_label).children(variant=variant)
    if isinstance(children, dict):
        # If variant=='*' then children may return a dict with the list of children for 1+ variants
        has_children = False
        for one_var in children:
            # Check all variants
            one_var_children = children[one_var]
            if len([child for child in one_var_children if child is not None])>0:
                has_children = True
    else:
        # Assume children is a list
        has_children = len([child for child in children if child is not None])>0
    self.out("Has children?", has_children)

    # Trying to fix again on 11/15/20 to prevent entering this loop when the only child is None
    if has_children and child is not None and (row_filter is not None or var_to_subset is not None):
    # Fixed on 11/10/19 because variant='*' was not entering this loop ever
    #if child is not None and (row_filter is not None or var_to_subset is not None):
    #if child is not None and len(children)>1 and (row_filter is not None or var_to_subset is not None):
        # If there are children and we are going to subset rows...
        self.out("Found children! for '{}', args={}, kwargs={}".format(input_label, args, kwargs))

        # Add the index column to the input dataset (for each variant)
        # TODO Push this into self.addColumn() once we can pass in a Series/numpy array, not just a lambda
        # TODO check if this new_index_col is already there and rename it if needed (like merge)
        input_df = self.Data(input_label, child=None, variant=variant)
        print(f"Called Data({input_label}, child=None, variant={variant}), got:", type(input_df))
        if isinstance(input_df, dict):
            for one_var in input_df:
                input_df_num_rows = input_df[one_var].shape[0]
                # Note this will cover up to 4,294,967,295 rows
                input_df[one_var][new_index_col] = np.arange(input_df_num_rows, dtype=np.uint32)

                # Store the new dataframe back into the featureset
                self.addData(input_label, input_df[one_var], child=None, variant=one_var)
        else:
            # If Data did not return a dataframe, there must have been a single variant
            one_var = self.Features(input_label, child=None).variants()[0] if variant=='*' else variant
            input_df_num_rows = input_df.shape[0]
            input_df[new_index_col] = np.arange(input_df_num_rows, dtype=np.uint32)
            # Store the new dataframe back into the featureset
            self.addData(input_label, input_df, child=None, variant=one_var)

        self.out("...Created index col '{}' in feature set '{}' for variant={}".format(new_index_col, input_label, variant))
        # Next subset the parent dataframe based on the given conditions to subset rows
        # and only save the resulting index column into a new temporary dataframe
        temp_output_label = output_label + '[[TEMP]]'
        variant = kwargs.get('variant', '*') 
        output_variant = kwargs.get('output_variant', '*')
        subset_metadata = self.subset(temp_output_label, input_label, child=None, variant=variant,
                                       row_filter=row_filter, var_to_subset=var_to_subset, var_list=var_list,
                                       cols_list=[new_index_col], data_types=data_types, output_variant=output_variant,
                                       #new_rows=False, new_cols=None, # Commenting out on 11/28/20...redundant now
                                      view_output=view_output) 



        # Apply the subset to the children by merging the TEMP index dataframe back with the original FeatureSet
        # i.e. X_parent_subset_index > X_parent+X_child = X_parent_subset + X_child_subset
        # NOTE: One bad practice here is that this works because the merge() function also creates the same index col
        # so ideally we wouldn't make that assumption, instead we'd create that column here first
        # TODO: Clean this up when we clean up merge() too
        self.out(f"\nMerge the children onto the subsetted rows in the parent: self.merge(output_label, [{temp_output_label}, {input_label}], {new_index_col}, fillna=False, data_types={data_types}, variant=[[{output_variant}],[{variant}]], output_variant={output_variant}, view_output={view_output})")
        self.merge(output_label, 
                   [temp_output_label, input_label],
                   new_index_col,
                   fillna=False, data_types=data_types, variant=[[output_variant],[variant]], output_variant=output_variant,
                   # new_rows=False, new_cols=None, # 11/28/20: Commenting out since this is default in merge() now 
                   view_output=view_output)
        # If this subset call had columns to choose, re-apply that to the resulting dataframe
        if cols_list is not None or cols_filter is not None:
            self.out("WARNING: Not yet supporting cols_list or cols_filter for calls to subset() with children",
                     type='error')
            # self.subset(output_label, output_label, variant=variant, cols_list=cols_list, cols_filter=cols_filter)
    else:
        # If there are no children to merge, or if we are just subsetting columns, then proceed the simple way
        variant = kwargs.get('variant', '*') 
        self.out("\nNo children for variant={}.".format(variant))
        output_variant = kwargs.get('output_variant', '*')

        # Next subset the parent dataframe based on the given conditions
        self.out(f"...going to run self._transform({output_label}, subset_function, {input_label}, {new_index_col}, {args}, new_rows=False, new_cols=None, variant={variant}, output_variant={output_variant})")
        self._transform(output_label, subset_function, input_label, new_index_col, *args, 
                       new_rows=False, new_cols=None,
                       variant=variant, output_variant=output_variant,
                       #**kwargs
                       )
                       # 11/28/20: Moved this to here so it catches all cases 
                       # New 5/31/20: Tell transform to use existing column types

    if view_output:
        self.view(output_label, '', child=None)

#############################################################################################
# index_var = the var that defines each unique row in the resulting pivoted table -- str
# pivot_var = the var that should be "pivoted" from multiple rows (per index_var) to multiple columns (per index_var) -- str
# values = the variable or list of variables that should be kept in the pivoted table
# (optional) value_names = the column label or list of column labels that should be created after the pivot,
#    where the length of this list must match the *values* input
# collate = whether to re-order the columns according to the pivot_var or the values:
#  - collate=False --> values1_pivot1, values1_pivot2, values2_pivot1, values2_pivot2  
#  - collate=True  --> values1_pivot1, values2_pivot1, values1_pivot2, values2_pivot2  
# (only relevant if >1 values provided here)    
def pivot(self, output_label, input_label, index_var, pivot_var, values, value_names=None, collate=False, **kwargs):

    def pivot_function(df, index_var, pivot_var, values, value_names=None, **kwargs):
        # Let pandas do the pivot
        df_pivot = df.pivot(index_var, pivot_var, values).reset_index()

        # Get the multi-index columns created by pandas (in whatever order it determines)
        df_pivot_cols = list(df_pivot.columns)
        print("Pandas pivot cols:", df_pivot_cols)

        # Make sure only pivoting on one var at a time
        # (since the below code assumes each col_tuple has exactly two parts)
        if isinstance(pivot_var, list) and len(pivot_var)>1:
            self.out("ERROR: Cannot run pivot() on multiple pivot_vars yet.", type='error')
            raise

        # Map values -> value_names if provided
        if value_names is not None:
            if not isinstance(value_names, list) or len(value_names)!=len(values):
                self.out("ERROR: value_names must have the same length as values in pivot()", type='error')
                raise
            pivot_col_map = {val:val_name for val, val_name in zip(values, value_names)}

        # Create a new set of tuples to include the modified column names
        new_index_cols = []
        new_pivot_col_tuples = []
        for col_tuple in df_pivot_cols:
            if (isinstance(index_var, str) and col_tuple[0]==index_var) or \
               (isinstance(index_var, list) and col_tuple[0] in index_var):
                # Include this as an index var
                new_index_cols.append(col_tuple[0])
            else:
                # Map the new pivot column name
                new_col = pivot_col_map[col_tuple[0]]+'_'+str(col_tuple[1]) if value_names is not None \
                          else '_'.join([str(col) for col in col_tuple]).strip()
                # Get the sort order of the value column
                value_order = values.index(col_tuple[0])

                # Keep tuples: 0=new column, 1=value column, 2=value col order, 3=pivot_var is None, 4=pivot_var as string
                # (to use below if re-shuffling these columns to collate)
                new_pivot_col_tuples.append(tuple([new_col, 
                                                   col_tuple[0], 
                                                   value_order, 
                                                   col_tuple[1] is None or pd.isnull(col_tuple[1]), 
                                                   str(col_tuple[1])]))
        new_pivot_cols = [col_tuple[0] for col_tuple in new_pivot_col_tuples]

        # Rename the columns -- Note this assumes pandas pivot() keeps the index cols first
        df_pivot.columns = new_index_cols + new_pivot_cols
        print("df_pivot after:", df_pivot.columns)

        # Reorder the columns (if collate=True and there are >1 values)
        if collate and len(values)>1:
            # Sort the new columns on first the pivot_var then second on the original order of the value cols
            new_pivot_col_tuples_resorted = sorted(new_pivot_col_tuples, key=lambda x: (not x[3], x[4], x[2]))
            new_pivot_cols_resorted = [new_pivot_col_tuple[0] for new_pivot_col_tuple in new_pivot_col_tuples_resorted]
            df_pivot = df_pivot[new_index_cols + new_pivot_cols_resorted]
            print("...after collating:", df_pivot.columns)

        return df_pivot

    self._transform(output_label, pivot_function, input_label, 
                   index_var=index_var, 
                   pivot_var=pivot_var, 
                   values=values, 
                   value_names=value_names,
                   **kwargs)
    self.view(output_label, child=None)


#############################################################################################
# pivot_vars is a list of dicts, where each dict is a set of vars that should be unpivoted together and renamed
# such as [{'constituent_code_1':'constituent_code',
#           'code_1_date_from':'code_date_from',
#           'code_1_date_to':'code_date_to'},
#          {'constituent_code_2':'constituent_code',
#           'code_2_date_from':'code_date_from',
#           'code_2_date_to':'code_date_to'},
#          {'constituent_code_3':'constituent_code',
#           'code_3_date_from':'code_date_from',
#           'code_3_date_to':'code_date_to'}]
# Note: If None is the key for any column in this dict, it will be ignored
# which will result in the unpivoted dataframe having constituent_code, code_date_from, and code_date_to columns
# with one row for each of those three sets of columns stacked on top of each other
# drop can be a lambda function to run on each row, returning True if that row should be ignored from the unpivoted df
# such as: lambda x: x['var_name']==''
# keep_pivot_vars = False (default) or True if the unpivoted df should contain the labels of the columns provided as pivot_vars 
def unpivot(self, output_label, input_label, index_vars, pivot_vars, **kwargs):

    def unpivot_function(pivoted_df, index_vars, pivot_vars, **kwargs):
        drop_condition = kwargs.get('drop', None)
        keep_pivot_vars = kwargs.get('keep_pivot_vars', False)

        unpivoted_df = None
        for pivot_var_set in pivot_vars:
            # Grab the right set of pivoted vars
            pivot_cols_this_set = []
            pivot_vars_this_set = []
            for col, var in pivot_var_set.items():
                if col is not None:
                    pivot_cols_this_set.append(col)
                    pivot_vars_this_set.append(var)
            pivoted_cols = list(index_vars) + list(pivot_cols_this_set)
            one_df = pivoted_df[pivoted_cols]

            # Change their column labels
            one_df.columns = list(index_vars) + list(pivot_vars_this_set)

            # Drop according to the given condition
            if drop_condition is not None:
                print("Have {} rows with columns:".format(one_df.shape[0]), one_df.columns)
                one_df = one_df[~one_df.apply(drop_condition, axis=1)]
                print("...Have {} rows in one set of pivot vars after dropping blanks".format(one_df.shape[0]))

            # If keep_pivot_vars=True, store the pivot var columns in their own columns in the unpivoted dataframe
            if keep_pivot_vars:
                for pivot_var, unpivoted_var in pivot_var_set.items():
                    pivot_col_label = f'_SOURCE_{unpivoted_var}'
                    one_df[pivot_col_label] = pivot_var

            # Stack the results
            if one_df is not None and one_df.shape[0]>0:
                if unpivoted_df is None:
                    unpivoted_df = one_df
                else:
                    unpivoted_df = pd.concat([unpivoted_df, one_df], axis=0, join='outer', sort=False).reset_index(drop=True)
            print("...{} total rows so far".format(unpivoted_df.shape if unpivoted_df is not None else 0))

        return unpivoted_df

    self._transform(output_label, unpivot_function, input_label, 
                   index_vars=index_vars, 
                   pivot_vars=pivot_vars, 
                   **kwargs)
    self.view(output_label, child=None)

#############################################################################################
# cols = column or set of columns to run through this 'clean' function, either:
# - 'col1' = a single column label
# - '*' --> all columns in the input data [not supported yet for how='remove' until implement '*' in subset())
# - ['col1', 'col2', etc.] = list of columns to clean
# - 'type:date', 'type:str', 'type:numeric' --> all columns with the given data type (according to ____) [not supported yet]
#
# when = when should the cleaning be done, either:
# - a constant value like '', 0, or 3.5
# - a list of values like [0, 1000000]  Note: Cannot include 'null' in the list currently
# - 'null' --> when any form of null value is reached, including np.NaN, np.NaT, None, etc.
# - lambda function returning True when each col should be cleaned up (i.e. lambda x: x>10000, where x is one value)
#
# how = what should be done when the "when" condition is true, either:
# - a constant value like '' or 0 (for instance to fill nulls with '')
# - a lambda function to modify the value being cleaned
def clean(self, output_label, input_label, cols, when, how, *args, cleaned_rows_label=None, **kwargs):

    # Expects a col, '*', or list of cols for "cols", a lambda fn for when_to_clean, and a value or lambda fn for cleaned_value
    def clean_function(df, cols, clean_lambda, **kwargs):            
        # First establish the list of columns to clean
        cols_to_clean = [] # TODO
        if cols == '*':
            cols_to_clean = list(df.columns)
        elif isinstance(cols, str):
            # TODO: Check for "type:" at beginning of string
            cols_to_clean = [cols]
        else:
            cols_to_clean = cols

        # Iterate through each column to clean
        for col_to_clean in cols_to_clean:
            if col_to_clean not in df.columns:
                self.out("ERROR! Cannot find column '{}' to clean".format(col_to_clean), type='error') 
                return None
            df[col_to_clean] = df[col_to_clean].apply(clean_lambda)

        return df

    # Create the lambda function to output values (cleaning when certain conditions are true)
    clean_lambda = None # TODO
    if when == 'null':
        clean_lambda = lambda x, clean_constant=how: clean_constant if x!=x or pd.isnull(x) else x
    elif isinstance(when, str) or isinstance(when, int) or isinstance(when, float):
        clean_lambda = lambda x, dirty_constant=when, clean_constant=how: clean_constant if x==dirty_constant else x
    elif isinstance(when, list):
        clean_lambda = lambda x, dirty_constant_list=when, clean_constant=how: clean_constant if x in dirty_constant_list else x
    elif callable(when):
        # this is if a lambda function was passed into clean
        self.out("Found lambda function passed in for 'when'")
        if callable(how):
            self.out("...also lambda function passed in for 'how'")
            clean_lambda = lambda x, when_lambda=when, clean_fn=how: clean_fn(x) if when_lambda(x) else x
        else:
            clean_lambda = lambda x, when_lambda=when, clean_constant=how: clean_constant if when_lambda(x) else x 
    else:
        self.out("ERROR: Do not know how to handle 'when' value {} provided to clean(). Exiting.".format(when), 
                 type='error')
        return None

    # Otherwise pass the 'how' value/function through to be used inside the transformer
    self._transform(output_label, clean_function, input_label, cols, clean_lambda, *args, 
                   cleaned_rows_label=cleaned_rows_label, **kwargs)
    self.view(output_label, child=None)



#############################################################################################
# Find unique matches between rows in two featuresets based on a given set of matching criteria
# name_set can be a list of two featuresets to match, or a dict with variants like:
# {'name_set-1':'var1', 'name_set-2':'var2'}
# match_conditions is a list of pairs of tuples, where the first tuple is the vars used for matching
# Currently only supporting one index_var per name_set
# in the first name set, second is the vars to match in teh second name set (must be equal length)
# such as: [[('var1', 'var2'), ('var1b', 'var2b')], 
#          [('var1', 'var2', 'var3'), ('var1b', 'var2b', 'var3b')]]
# can also pass into kwargs: 'exclude'= list of values to exclude from matching (like None, '')
def findMatches(self, output_label, name_sets, index_vars=None, match_conditions=None, 
#                     data_types=None, 
                **kwargs):

    def find_matches_function(name_set_dfs, name_sets, index_vars, match_conditions, **kwargs):            
    # Get the 2 feature sets to match
        if isinstance(name_set_dfs, list) and isinstance(name_sets, list):
            if len(name_set_dfs)!=2 or len(name_sets)!=2:
                self.out("ERROR: Can only take a list of two sets to match", type='error')
                raise
            names_1, names_2 = tuple(name_set_dfs)
            name_set_1, name_set_2 = tuple(name_sets)

        else:
            self.out("ERROR: Can only take a list for name_sets", type='error')
            raise


        # Get the index vars
        if index_vars is not None and isinstance(index_vars, list) and len(index_vars)==2:
            index_set_1, index_set_2 = tuple(index_vars)
        else:
            self.out("ERROR: Must pass in two index_vars in a list, corresponding to the two faeturesets",
                     type='error')
            raise

        exclude_vals = kwargs.get('exclude', [None, ''])
        unique_flag = True # Currently this isn't used anywhere

        # Iterate through each match condition
        all_mappings = None
        for match_cols_1, match_cols_2 in match_conditions:
            if isinstance(match_cols_1, str):
                match_cols_1 = [match_cols_1]
            if isinstance(match_cols_2, str):
                match_cols_2 = [match_cols_2]  
            print("\nTrying to match on {} in {} <--> {} in {}".format(match_cols_1, 
                                                                        name_set_1, 
                                                                        match_cols_2, 
                                                                        name_set_2))
            # If there are prior mappings, take them out before trying this match
            name_set_1_nonblank = names_1
            name_set_2_nonblank = names_2
            if all_mappings is not None:
                # Take these mapped ones out of the remaining rows to try matching
                # Note this might break if index_set_1 is already in name_set_2 or vice versa
                name_set_1_nonblank = name_set_1_nonblank.merge(all_mappings,
                                                                on=index_set_1,
                                                                how='left')
                name_set_1_nonblank = name_set_1_nonblank[name_set_1_nonblank[index_set_2]!=name_set_1_nonblank[index_set_2]]
                name_set_1_nonblank.drop(index_set_2, inplace=True, axis='columns')
                print("...{} rows of {} remain after taking out {} previously mapped {} values".format(name_set_1_nonblank.shape[0],
                                                                                                       name_set_1,
                                                                                                       all_mappings.shape[0],
                                                                                                       index_set_2))
                name_set_2_nonblank = name_set_2_nonblank.merge(all_mappings,
                                                                on=index_set_2,
                                                                how='left')
                print("...{} rows in {} when merging with prior mappings".format(name_set_2_nonblank.shape[0],name_set_2))
                name_set_2_nonblank = name_set_2_nonblank[name_set_2_nonblank[index_set_1]!=name_set_2_nonblank[index_set_1]]
                name_set_2_nonblank.drop(index_set_1, inplace=True, axis='columns')
                print("...{} rows of {} remain after taking out {} previously mapped {} values".format(name_set_2_nonblank.shape[0],
                                                                                                       name_set_2,
                                                                                                       all_mappings.shape[0],
                                                                                                       index_set_2))

            # Remove exclude vals from name set 1
            print("\nStarting with {} rows in {}".format(name_set_1_nonblank.shape[0], name_set_1))
            for match_index in match_cols_1:
                print("...removing rows where {} in {} from {}".format(match_index, exclude_vals, name_set_1))
                name_set_1_nonblank = name_set_1_nonblank[name_set_1_nonblank[match_index].apply(lambda x: x not in exclude_vals)]
                print("...{} rows remaining".format(name_set_1_nonblank.shape[0]))

            # Remove exclude vals from name set 2
            print("\nStarting with {} rows in {}".format(name_set_2_nonblank.shape[0], name_set_2))
            for match_index in match_cols_2:
                print("...removing rows where {} in {} from {}".format(match_index, exclude_vals, name_set_2))
                name_set_2_nonblank = name_set_2_nonblank[name_set_2_nonblank[match_index].apply(lambda x: x not in exclude_vals)]
                print("...{} rows remaining".format(name_set_2_nonblank.shape[0]))

            # Try to match using this match condition
            print("Name set 1: ", name_set_1_nonblank.columns)
            print("...match_cols_1:", list(match_cols_1))
            print("...index_set_1:", index_set_1)
            name_set_1_nonblank_matchcols = name_set_1_nonblank[list(match_cols_1)+[index_set_1]]
            name_set_2_nonblank_matchcols = name_set_2_nonblank[list(match_cols_2)+[index_set_2]]
            name_matches = name_set_1_nonblank_matchcols.merge(name_set_2_nonblank_matchcols,
                                                     left_on=match_cols_1,
                                                     right_on=match_cols_2,
                                                     how='inner')
            print("\nHave {} rows matching".format(name_matches.shape[0]))

            # Get the unique matches
            all_match_cols = list(set(match_cols_1)|set(match_cols_2))
            print("...all match cols: {}".format(all_match_cols))
            dummy_col = '[[DUMMY]]'
            name_matches[dummy_col] = 1
            name_matches_counts = name_matches.groupby(all_match_cols, 
                                                       as_index=False,
                                                       observed=True)[dummy_col].count()
            name_matches_counts_equal_1 = name_matches_counts[name_matches_counts[dummy_col]==1]
            print("...{} rows match uniquely".format(name_matches_counts_equal_1.shape[0]))

            # Store the match indexes of the unique matches
            name_matches_unique = name_matches.merge(name_matches_counts_equal_1,
                                                     on=all_match_cols,
                                                     how='inner')
            print("...{} rows (double-check the same)".format(name_matches_unique.shape[0]))
            if name_matches_unique is not None and name_matches_unique.shape[0]>0:
                new_mappings = name_matches_unique[[index_set_1, index_set_2]]
                if all_mappings is None:
                    all_mappings = new_mappings
                else:
                    all_mappings = pd.concat([all_mappings, new_mappings], axis=0)
            if all_mappings is not None:
                print("Have {} mappings of {} <--> {} so far".format(all_mappings.shape[0],
                                                                     index_set_1,
                                                                     index_set_2))

        # Get the unique list of mappings
        if all_mappings is not None:
            all_mappings_unique = all_mappings.groupby([index_set_1, index_set_2], 
                                                observed=True).size().reset_index(drop=False)\
                                                .drop(0, axis='columns')
            return all_mappings_unique
            # Save to the FeatureSpace
            #self.addData(output_mapping_set, all_mappings_unique, data_types=data_types)
        else:
            print("No matches found!")
            return None


    # Otherwise pass the 'how' value/function through to be used inside the transformer
    self._transform(output_label, find_matches_function, name_sets, name_sets, index_vars, match_conditions,
                   **kwargs)
    self.view(output_label)

#############################################################################################
# Split the data into multiple subsets by rows, either randomly, given a fixed number of rows, or given a boolean function to use to split 
# The output_splits var should contain dicts for each of the splits (i.e. 2, 3, or more), each of which can contain these params:
# {'label': label of the output feature set,
#  'percent': random percent of the rows to be split off,
#  'rows': number of rows to be split off,
#  'filter': lambda function that outputs a boolean given each row [NOTE NOT YET IMPLEMENTED]
# } 
# Notes:
# - Currently as implemented, 'rows' does not get exact number of rows, because of the statistical distribution of random values (and how I kept it fast by not sorting)
# - If you provide more than one way to do a single split, then we will choose percent, then rows, then filter
# - If random is True, then these are done randomly. If False, then these are done in order.
# - If all_rows is True, then we will assume all rows of the input dataset should be used (and override by making the last split larger/smaller 
#   if percents for all splits don't add up to 100% or if the rows for all splits don't add up to the number of rows)
# - If all_rows is False and the split percents add up to <100%, then <100% rows will be split off. If they add up to >100%, then only 100% rows will be split.
# TODO: Find way to get 'rows' to get exact number of rows (by sorting the sample vals then finding the argsort)
def split(self, output_splits, input_label, *args, random=True, all_rows=True, index_cols=None, feature_cols=None, label_cols=None, **kwargs):
#         reload = kwargs.get('reload', self.default_reload)
#         batch = kwargs.get('batch', self.default_batch)
#         variant = kwargs.get('variant', self.default_variant)


    # Reload the FeatureSpace metadata first to make sure we reload the latest files
    self.out("Reloading the FeatureSpace...")
    self._loadFeatureSetMetadata()

    input_featureset = self.Features(input_label, **kwargs)
    ##input_status = input_featureset.getStatus()

    # Convert the dask dataframe (temporarily) into a pandas dataframe
    # Note: This will store it in memory
    # Convert from a dask dataframe to pandas dataframe
    input_df_dask = self.Data(input_label, **kwargs)
    input_df_dask_dtypes = input_df_dask.dtypes
    input_df_pandas = input_df_dask.compute()        
    num_rows = len(input_df_pandas)
    self.out("\nSplitting FeatureSet {} with {} rows, random={}:".format(input_label, num_rows, random))
    self.out("...duplicate index rows: ", input_df_pandas.index.duplicated().sum())

    # Convert columns in the pandas dataframe back to int type with 0s filled-in for nulls
    # (since .compute() coerces those columns to float64 if there are nulls)
    for col, coltype in input_df_dask_dtypes.iteritems():
        if coltype==np.int64:
            input_df_pandas[col] = input_df_pandas[col].fillna(0).astype(int)

    # Create a mask to track whether each row has been put into a split yet
    all_rows_mask = np.zeros(num_rows)

    # Create a random set of values used to choose rows (if random is True), otherwise use the row numbers normalized to [0,1]
    if random:
        all_rows_sample_vals = np.random.rand(num_rows)
    else:
        all_rows_sample_vals = np.linspace(0.0, 1.0, num=num_rows)

    # Iterate through each given split
    num_splits = len(output_splits)
    split_num = 0
    total_percent_split_so_far = 0.0 
    for split in output_splits:
        split_num += 1
        output_label = split['label']

        # If this is the final split and all_rows is True, then this split should just get all remaining rows
        if split_num == num_splits and all_rows:
            split_mask = all_rows_mask == 0
            split_rows = input_df_pandas[split_mask]
            all_rows_mask[split_mask] = 1
            self.out("...split #{} is the last split (and all_rows=True), so it gets all rows not split off yet = {} rows".format(split_num, len(split_rows)))
            self.out("...duplicate index rows: ", split_rows.index.duplicated().sum())

        # If percent is provided, then use this to randomly choose a set of rows
        elif 'percent' in split or 'rows' in split:
            if 'percent' in split:
                sample_val_cutoff = split['percent'] + total_percent_split_so_far
                self.out("...split #{}: {}% using sample cutoff {}".format(split_num, split['percent'], sample_val_cutoff))
            elif 'rows' in split:
                sample_val_cutoff = split['rows']/num_rows + total_percent_split_so_far
                self.out("...split #{}: {} rows using sample cutoff {}".format(split_num, split['rows'], sample_val_cutoff))
            total_percent_split_so_far = sample_val_cutoff
            split_mask = (all_rows_sample_vals <= sample_val_cutoff) & (all_rows_mask == 0)
            split_rows = input_df_pandas[split_mask]
            all_rows_mask[split_mask] = 1
            self.out("......split gets {} rows".format(len(split_rows)))
            self.out("......duplicate index rows: ", split_rows.index.duplicated().sum())


        # Convert the pandas dataframe back to dask dataframe before saving it
        split_rows_dd = dd.from_pandas(split_rows, chunksize=DEFAULTS._DEFAULT_CHUNK_SIZE, sort=False) #npartitions=10)

        # Create the new feature set with the same column types as the input feature set
        output_featureset = self.addData(output_label, split_rows_dd, datatype='dataframe', 
                                         ##status=input_status, 
                                         index_cols=input_featureset.index_cols, 
                                         feature_cols=input_featureset.feature_cols, 
                                         label_cols=input_featureset.label_cols,
                                         **kwargs)
        output_featureset._printColumnTypes()
        self._setDependency(output_label, input_label, {'split': split}, **kwargs)

    del(input_df_pandas)
    del(input_df_dask)
    self.view(output_label)
# TODO: Support two-column cross within one dataframe


#############################################################################################
def cross(self, new_label, varsToCross, **kwargs):
#         reload = kwargs.get('reload', self.default_reload)
#         batch = kwargs.get('batch', self.default_batch)

    # Reload the FeatureSpace metadata first to make sure we reload the latest files
    self.out("Reloading the FeatureSpace...")
    self._loadFeatureSetMetadata()

    all_crosses = None
    all_input_sets = set()
    for var_def in varsToCross:
        label = var_def['label']
        var = var_def['var']
        minVar = var_def['min'] if 'min' in var_def else None
        maxVar = var_def['max'] if 'max' in var_def else None
        useMinMaxRangeInData = var_def['min_max_from_data'] if 'min_max_from_data' in var_def else False
        if isinstance(var, str):
            var_list = [var]
        else:
            var_list = var
            if useMinMaxRangeInData:
                useMinMaxRangeInData = False
                print("WARNING! cross() cannot handle 'min_max_from_data'=True if 'var' is a list (not a string). Defaulting to treat 'min_max_from_data' as False.")

        print('Crossing var {} from df {} using min {}, max {} (pulling min/max from data {})'.format(var, label, minVar, maxVar, useMinMaxRangeInData))
        feature_set_to_cross = self.Features(label, **kwargs)
        feature_set_to_cross_df = self.Data(label, **kwargs)
        # TODO: Don't call these twice, redundant
        if feature_set_to_cross_df is None:
            print("ERROR: Could not find FeatureSet {}...exiting cross.".format(label))
            return None

        # Create a dataframe with the right range of values
        if useMinMaxRangeInData:
            if minVar is None:
                #minVar = np.min(feature_set_to_cross_df[var])
                minVar = feature_set_to_cross_df[var].min().compute()
            if maxVar is None:
                #maxVar = np.max(feature_set_to_cross_df[var])
                maxVar = feature_set_to_cross_df[var].max().compute()
            #var_allvals = pd.DataFrame(np.arange(minVar, maxVar+1), columns=[var])
            var_allvals = dd.from_array(np.arange(minVar, maxVar+1)).to_frame()
            #var_allvals = dd.DataFrame(np.arange(minVar, maxVar+1)) #, columns=[var])
            var_allvals.columns = [var]
        else:
            #var_allvals = feature_set_to_cross_df.groupby(var_list, as_index=False).count()[var_list]
            var_allvals = feature_set_to_cross_df.groupby(var_list, 
                                                          dropna=False,
                                                          observed=True).count().reset_index()
            #var_allvals.columns = var_list

            #var_allvals = pd.DataFrame(feature_set_to_cross_df[var].unique(), columns=[var])

        print("...have {} unique values of {} to cross -- columns: {}".format(len(var_allvals), var, var_allvals.columns)) 

        # Create dummy var to use to merge
        var_allvals['dummy'] = 1

        # Cross the previous crosses (if have any) with the new range of values
        if all_crosses is None:
            all_crosses = var_allvals
        else:
            #all_crosses = pd.merge(all_crosses, var_allvals, on='dummy', how='left')
            all_crosses = dd.merge(all_crosses, var_allvals, on='dummy', how='left')

        # Keep track of the list of data sets used to create the cross
        all_input_sets.add(label)

    all_crosses = all_crosses.drop(['dummy'], axis=1) #, inplace=True)

    # Create the new FeatureSet with the merged data and feature/index/label columns
    new_index_cols = set(all_crosses.columns)
    new_featureset = self.addData(new_label, all_crosses, 
                                  datatype='dataframe', 
                                  ##status=True, 
                                  index_cols=new_index_cols, 
                                  **kwargs)
    new_featureset._printColumnTypes()

    # Track dependencies
    for input_set in all_input_sets:
        self._setDependency(new_label, input_set, 'cross', **kwargs)

    self.view(new_label)
    #return all_crosses


#############################################################################################
# Merge will bring the children of each of the input datasets in too
# But note that this assumes all the mergeVars are in the parents (child=None)
# Also this only works for variant=None!!
def merge(self, new_label, featureSetsToMerge, mergeVars, join='left', view_output=True, **kwargs):
    """Merges the given data sets on a given set of merge variables, and saves the resulting FeatureData set into the FeatureSpace.

    * Parameters:
        1. **new_label**: Label of the output FeatureSet to be saved in the FeatureSpace
        2. **featureSetsToMerge**: Ordered list of labels of the FeatureSets to be merged together (e.g. ['my_dataset_1', 'my_dataset_2']). Must contain >1 FeatureSet.
        3. **mergeVars**: The variable(s) to use to merge the FeatureSets together, either:
            - a string for the one var to use to merge all feature sets together (i.e. 'person_id')
            - a list for the set of vars to use to merge all feature sets together (i.e. ['first_name', 'last_name'])
            - a list of lists corresponding to the set of merge vars to use for each corresponding FeatureSet in **merge_sets**, (e.g. [['first_name', 'last_name'], ['your_first_name', 'your_last_name']] --> join rows if 'first_name' in 'my_dataset_1' equals 'your_first_name' in 'my_dataset_2' **and** 'last_name' in 'my_dataset_1' equals 'your_last_name' in 'my_dataset_2')
            - Note the **merge_vars** are assumed to be in the "parent" datasets, not in the "children" (todo)

        - **join**: Either 'left' for left-join, 'inner' for inner-join, 'right' for right-join, 'outer' for outer-join, or 'left-outer' for a left outer join. (optional, default='left')  
            - Note each successive FeatureSet is merged according to the left-to-right ordering of **featureSetsToMerge**.  
            - Cannot yet support different left/inner joins for different FeatureSets in **featureSetsToMerge**.  (If desired, you should instead make separate calls to merge() with different **join** values.)
        - **fillna**: Either True to replace nulls with default values for each column-type, or False to leave nulls in place (optional, default=False)
            - We try to preserve the data type most frequently found in each column, as follows:
            - If fillna=True, then np.int64 or np.float64 have null values filled with 0s, object-type columns are filled with '' if strings are detected anywhere in the column, and datetime columns are left filled with NaT values (because there is no "default" date to fill-in).
            - If fillna=False, then np.nan is inserted into np.int64 or np.float64 type columns, object-type columns are kept with NaN or NaT values (as-is), and datetime columns are kept with NaT values.
            - Note: 5/3/2020 Added support for left-outer joins which does left join then keeps only nulls (non-matches) on the right side


    * Returns: *Nothing returned*
    """
    #print("fillna: ", fillna)
    self.out("kwargs: ", kwargs)
    engine = kwargs.get('engine', None)

    # Check errors in given parameters
    if not isinstance(featureSetsToMerge, list) and not isinstance(featureSetsToMerge, dict):
        self.out("ERROR: Must provide a list or dict of featuresets to merge", 
                 type='error')
        raise
    elif len(featureSetsToMerge)<=1:
        self.out("ERROR: Must provide more than one featureset to merge",
                 type='error')
        raise

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Use this to have consistent mapping to an index column name
#         def _get_index_col(label):
#             return 'IX::{}'.format(label)

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def merge_child_function(input_dataset, input_label, index_col, **kwargs):
        self.out("Inside merge_child_function...")
        self.out("input_dataset:", input_label, type(input_dataset))
        #self.out("shape:", input_dataset.shape)
        child = kwargs.get('child', None)
        self.out("child:", child)
        parent = kwargs.get('parent', None)
        self.out("parent:", parent)
        self.out("index col:", index_col.shape, index_col.max())

        if hasattr(input_dataset, '__feature_type__') and input_dataset.__feature_type__=='FeatureMatrix':
            # Handle when child is a FeatureMatrix
            input_child_matrix = input_dataset.getMatrix()
            self.out("have input_child_matrix:", input_child_matrix)
            self.out("Trying to merge a FeatureMatrix...shape:{}".format(input_child_matrix.shape))
            input_matrix_columns = input_dataset.columns()
            num_input_columns = input_child_matrix.shape[0]
            num_output_rows = index_col.shape[0]

            # Only proceed if there are any rows to output to matrix
            if input_dataset.isEmpty() or num_output_rows==0:
                self.out(f"WARNING! Feature Matrix '{child} is empty or missing so cannot merge it.", type='error')
                #raise

            else:
                # Need to create a one-hot matrix representing the index col
                num_index_values = index_col.shape[0]
                self.out("Found {} index values in the given index col".format(num_index_values))

                # https://stackoverflow.com/questions/7632963/numpy-find-first-index-of-value-fast/7654768
                dtype_to_use = constants.getDtype(num_index_values)
                rows = []
                cols = []
                for output_index, input_index in enumerate(index_col.values):
                    # Only insert values if this is not null
                    if input_index is not None and input_index==input_index:
                        rows.append(int(output_index))
                        cols.append(int(input_index))
                highest_index_col = np.max(index_col)
                #list(index_col.values)
                #rows = np.arange(num_index_values, dtype=dtype_to_use)
                num_vals = len(rows)
                self.out("rows:", num_vals)

                # Make sure some values actually merged
                if num_vals==0:
                    self.out(f"ERROR! 0 rows in the Feature Matrix '{child}' were successfully merged, exiting merge().",
                             type='error')
                    raise

                else:
                    # Only proceed to create the child matrix if there are any rows to merge
                    vals = np.ones((num_vals,), dtype=dtype_to_use)
                    self.out("cols:", len(cols))
                    cols_array = np.asarray(cols).flatten()
                    self.out("cols_array:", cols_array.shape, cols_array.max())
                    self.out("vals:", vals.shape)
                    self.out("shape of new sparse matrix: ({}, {})".format(num_output_rows, num_input_columns))
                    index_onehot_sparse = sp.csr_matrix((vals, (rows, cols_array)), shape=(num_output_rows, num_input_columns))
                    # print("shape of new sparse matrix: ({}, {})".format(num_output_rows, highest_index_col+1))
                    # index_onehot_sparse = sp.csr_matrix((vals, (rows, cols_array)), shape=(num_output_rows, highest_index_col+1))
                    self.out("Created sparse one-hot matrix representing the indexes:", index_onehot_sparse.shape)

                    merge_child_spread = index_onehot_sparse.dot(input_child_matrix)
                    self.out("Dot product with input child dataset: ", merge_child_spread.shape)

                    # Transpose so this is a column array, and store that as a FeatureMatrix object
                    self.out("Creating FeatureMatrix with matrix:{} and columns={}".format(merge_child_spread.shape, input_matrix_columns))
                    # TODO: Make sure this child name isn't duplicated for the same child name in >1 merge input sets
                    return FeatureMatrix(label=child, 
                                         parent_label=parent,
                                         matrix=merge_child_spread, 
                                         columns=input_matrix_columns, 
                                         mappings=input_dataset.getMappings())

                #return merge_child_spread

        return None

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def merge_function(input_dfs, input_labels, mergeVars, **kwargs):
        merge_df = None
        self.out("Inside merge_function with input_dfs={}, input_labels={}, mergeVars={}, kwargs={}".format(type(input_dfs), input_labels, mergeVars, kwargs.keys()))

        # Detect whether to use the same mergeVar(s) for all input feature sets, or to vary for each one
        use_same_merge_vars = True
        if isinstance(mergeVars, str) or (isinstance(mergeVars, list) and isinstance(mergeVars[0], str)):
            use_same_merge_vars = True
        elif isinstance(mergeVars[0], list):
            use_same_merge_vars = False

        # TODO: Don't assume we're only merging the None child here...need to merge the children too

        # Iterate through the dataframes and their labels to merge together
        num_feature_sets_to_merge = len(input_labels)
        merged_dataset_types = None
        new_index_cols = []
        for feature_set_num, (featureSetToMerge, feature_set_to_merge_df) in enumerate(zip(input_labels, input_dfs)):
            # Add an index column to track where each row goes in the merge
            new_index_col = _get_index_col(featureSetToMerge)
            suffix = featureSetToMerge
            if isinstance(featureSetToMerge, dict):
                self.out(f"...looking for 'featureset' in dict {featureSetToMerge} to use as suffix")
                suffix = featureSetToMerge.get('featureset', featureSetToMerge.get('label', 'merge'))
                self.out(f"...found suffix={suffix}")

            # Note: On 6/7/20 added check for whether this IX column already exists, in which case append "_1", "_2", etc.
            # and also append this to the suffix used in the merge to avoid duplicate columns
            # (this avoids bugs if you merge the same featureset twice)
            if merge_df is not None:
                extra_suffix_digit = 1
                check_new_index_col = new_index_col
                check_new_suffix = suffix
                while check_new_index_col in merge_df.columns:
                    check_new_index_col = "{}_{}".format(new_index_col, extra_suffix_digit)
                    check_new_suffix = "{}_{}".format(suffix, extra_suffix_digit)
                    extra_suffix_digit += 1
                new_index_col = check_new_index_col
                suffix = check_new_suffix

            feature_set_df_num_rows = feature_set_to_merge_df.shape[0]
            # Note: 6/17/19 Switching to numpy arange since dask can repeat indexes across partitions
            feature_set_to_merge_df[new_index_col] = np.arange(feature_set_df_num_rows)
            #feature_set_to_merge_df[new_index_col] = feature_set_to_merge_df.index
            self.out("Created index col {} in feature set '{}' during merge_function".format(new_index_col, featureSetToMerge))
            new_index_cols.append(new_index_col)

            #print("...test66:", feature_set_to_merge_df.shape, feature_set_to_merge_df[new_index_col].max())
            if merge_df is None:
                merge_df = feature_set_to_merge_df #.copy() # Commenting out the copy() on 1/21/21
                merged_dataset_types = 'dask' if isinstance(feature_set_to_merge_df, dd.DataFrame) else \
                                       'pandas' if isinstance(feature_set_to_merge_df, pd.DataFrame) else 'other'
                self.out("Copying first merge set: ", featureSetToMerge, type(feature_set_to_merge_df))

                # If the merge vars change for each feature set, keep track of the first set
                if not use_same_merge_vars:
                    previous_merge_vars = mergeVars[feature_set_num]

            else:
                self.out("Merging in next merge set: ", featureSetToMerge, type(feature_set_to_merge_df))

                # Need to make sure the merged datasets are of the same type
                if merged_dataset_types=='pandas' and isinstance(feature_set_to_merge_df, dd.DataFrame):
                    # Convert the next set to pandas if any of the previous ones were
                    feature_set_to_merge_df = feature_set_to_merge_df.compute()
                elif merged_dataset_types=='dask' and isinstance(merge_df, dd.DataFrame) and \
                    isinstance(feature_set_to_merge_df, pd.DataFrame):
                    # Then need to convert the previous set to pandas
                    merge_df = merge_df.compute()
                    merged_dataset_types = 'pandas'

                if use_same_merge_vars:
                    # Check if we are merging on a single var or a list of vars
                    self.out("...merge vars=", mergeVars)

                    if join=='left outer' or join=='left-outer':
                        # First do left join
                        self.out("...executing left outer join with suffix '{}'".format(suffix))
                        merge_df = merge_df.merge(feature_set_to_merge_df, 
                                                  on=mergeVars, 
                                                  how='left',
                                                  suffixes=('', '_'+suffix)
                                                 )
                        self.out("...left join produces {} rows".format(merge_df.shape[0]))

                        # Then keep only nulls (non-matches) on the right side
                        merge_df = merge_df[merge_df[new_index_col]!=merge_df[new_index_col]]
                        self.out("...left outer join produces {} rows after removing matches".format(merge_df.shape[0]))

                    else:
                        # Otherwise do 'inner', 'left', 'right', or 'outer' join 
                        self.out("...executing {} join with suffix '{}'".format(join, suffix))
                        merge_df = merge_df.merge(feature_set_to_merge_df, 
                                                  on=mergeVars, 
                                                  how=join,
                                                  suffixes=('', '_'+suffix)
                                                 )
                else:
                    # Or if we are given a list of lists, then use each feature set's sub-list of merge vars 
                    current_merge_vars = mergeVars[feature_set_num]
                    self.out("...left merge vars=", previous_merge_vars)
                    self.out("...right merge vars=", current_merge_vars)
                    if join=='left outer' or join=='left-outer':
                        # First do left join
                        self.out("...executing left outer join with suffix '{}'".format(suffix))
                        merge_df = merge_df.merge(feature_set_to_merge_df, 
                                                  left_on=previous_merge_vars,
                                                  right_on=current_merge_vars, 
                                                  how='left',
                                                  suffixes=('', '_'+suffix)
                                                 )
                        self.out("...left join produces {} rows".format(merge_df.shape[0]))

                        # Then keep only nulls (non-matches) on the right side
                        merge_df = merge_df[merge_df[new_index_col]!=merge_df[new_index_col]]
                        self.out("...left outer join produces {} rows after removing matches".format(merge_df.shape[0]))

                    else:
                        # Otherwise do 'inner', 'left', 'right', or 'outer' join 
                        self.out("...executing {} join with suffix '{}'".format(join, suffix))
                        merge_df = merge_df.merge(feature_set_to_merge_df, 
                                                  left_on=previous_merge_vars,
                                                  right_on=current_merge_vars, 
                                                  how=join,
                                                  suffixes=('', '_'+suffix)
                                                 )

                    # TODO: Create index matrix for the merge vars in the *output* of the merges on the None child
                    # i.e. C = A > B --> take C[merge vars] and create index matrix
                    # --> ??? multiply that by each FeatureMatrix child
                    # Can this be done using agg?

                    previous_merge_vars = current_merge_vars

            # Unify the columns in the newly merged dataframe (but not the index col)
            #cols_to_unify = list(feature_set_to_merge_df.columns)
            #if new_index_col in cols_to_unify: 
            #    cols_to_unify.remove(new_index_col)
            #merge_df = unify_dataframe(merge_df, cols_to_unify, fillna=fillna)


        del(feature_set_to_merge_df)

        #return merge_df
        return {'dataframe': merge_df,
                'index_cols': new_index_cols
               }
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # Run the transform using this merge function (on the parents only)
    # TODO: Turn this into multiple transforms for each input feature set (including children)
    # Note: This assumes the parents contain the merge vars
    self.out("Going to merge the FeatureSets together {} to produce '{}'".format(featureSetsToMerge, new_label))
    merge_metadata = self._transform(new_label, merge_function, featureSetsToMerge, featureSetsToMerge, mergeVars, 
                                    new_rows=False, new_cols=None, 
                                    # 11/28/20: No new columns created in a merge so not re-unifying column types
                                    # Note this might cause problems by introducing nulls...need to debug if so
                                    **kwargs)
    self.out("...done")
    self.out("...merge metadata:{}".format(merge_metadata))

    # Iterate through the list of variants for the merged FeatureSet just created
    output_featureset = self.Features(new_label, reload=False)
    #input_featureset.getData(variant=input_variant, child=child)
    merge_variants = copy.deepcopy(self.Features(new_label).variants())
    self.out("...merge variants:{}".format(merge_variants))
    self.out(self.feature_set_metadata[new_label])

    # Replicating functionality normally inside fs._transform() to figure out what variants were used on the inputs
#         target_variant = kwargs.get('variant', '*')
    batch = kwargs.get('batch', self.default_batch)

    # If a 'child' kwarg was passed, then use it to determine which children to merge
    children_to_merge = kwargs.get('child', '*')
    children_to_merge_list = None if children_to_merge=='*' else [None] if children_to_merge is None else [children_to_merge] if isinstance(children_to_merge, str) else children_to_merge

    #for (curr_variant, input_variants) in zip(merge_variants, all_input_variant_combos):
    for one_merge_metadata in merge_metadata:
        curr_variant = one_merge_metadata['output_variant']
        input_variant_metadata = one_merge_metadata['inputs']
        self.out("Going to merge the children '{}' for '{}' variant={} using input variants {}".format(children_to_merge, new_label, curr_variant, input_variant_metadata))
        # Now iterate through each featureSetsToMerge and look for its children
        # If it has children, then map them to rows based on the IX::{} vars
        # that were created for each feature set

        # Keep list of index cols created for each feature set (for each variant)
        feature_set_index_cols = []

        # Get the output variant for this combo, to pass-into the transform below
        # TODO: Push all this into _transform() to handle iterating through multiple variants
#             output_variant = kwargs.get('output_variant', None)
#             num_variant_combos = len(input_variants)
#             this_output_variant = self.getOutputVariant(input_variants, output_variant, num_variant_combos)

        # Iterate through each input feature set with its variant
        #for (feature_set_label, input_variant) in zip(featureSetsToMerge, input_variants):

        for one_merge_input_metadata in input_variant_metadata:
            feature_set_label = one_merge_input_metadata['input_featureset']
            input_variant = one_merge_input_metadata['input_variant']
            self.out("Checking for children in {} using variant {}...".format(feature_set_label, input_variant))
            input_feature_set_obj = self.Features(feature_set_label)
            input_feature_set_data = input_feature_set_obj.getData(variant=input_variant, child=None)
            #input_feature_set_data = self.Data(feature_set_label, variant=input_variant, child=None)
            output_feature_set_data = output_featureset.getData(variant=curr_variant, child=None)
            #output_feature_set_data = self.Data(new_label, variant=curr_variant, child=None)
            self.out("output feature set data for '{}' from variant={}, child=None, shape {}".format(new_label, curr_variant, 
                        output_feature_set_data.shape))
            input_feature_set_children = copy.deepcopy(input_feature_set_obj.children(variant=input_variant))
            self.out("...input feature set children:", input_feature_set_children)

            # Figure out the name of the column created for this input feature set
            input_feature_set_index_col = one_merge_input_metadata['index_col'] #_get_index_col(feature_set_label)
            feature_set_index_cols.append(input_feature_set_index_col)

            # Iterate through each child, look for the non-None ones
            all_children_to_merge = children_to_merge_list or input_feature_set_children
            all_children_to_merge_nonone = [child for child in all_children_to_merge if child is not None]
            last_child_to_merge = all_children_to_merge_nonone[-1] if len(all_children_to_merge_nonone)>0 else None

            #for feature_set_child in input_feature_set_children:
            for feature_set_child in all_children_to_merge_nonone:
            # Only merge non-None children (and in the given 'child' list, if any given)
                #if feature_set_child is not None and (children_to_merge_list is None or feature_set_child in children_to_merge_list):
                self.out("Need to merge child='{}' for feature set='{}', variant='{}'".format(feature_set_child, feature_set_label, input_variant))

                # Added 9/22/20: Only save the final child, to avoid repetitive saving of all intermediate children N^2 times
                save_to_disk = (feature_set_child == last_child_to_merge)
                self.out("...save_to_disk for child '{}' = {}".format(feature_set_child, save_to_disk))

                # TODO: Need to check if this is indeed dask                            
                new_index_rows = output_feature_set_data[input_feature_set_index_col].compute() if isinstance(output_feature_set_data, dd.DataFrame) else output_feature_set_data[input_feature_set_index_col]
                self.out("...index col found '{}' with shape {}, {} nulls, max value={}".format(input_feature_set_index_col, new_index_rows.shape, new_index_rows.isna().sum(), new_index_rows.max()))

                # Pass this column of the rows new index into a transform function
                kwargs['child'] = feature_set_child
                kwargs['variant'] = input_variant
                kwargs['output_variant'] = curr_variant # Added on 6/10/19
                kwargs['parent'] = new_label
                kwargs['overwrite'] = True # Added on 7/24/19
                kwargs['save_to_disk'] = save_to_disk # Added on 9/22/20

                # Note: Commenting this out until can also support conversion of children to pandas inside _transform()
                # This is to handle the fact that _transform() will change the FeatureMatrix children to pandas dfs
                #if engine=='pandas' or engine is None:
                #    self._transform(new_label, merge_function, [new_label, feature_set_label], [feature_set_label], 
                #                   mergeVars, **kwargs)
                #else:
                self._transform(new_label, merge_child_function, 
                               feature_set_label, feature_set_label, new_index_rows, **kwargs)

        self.out('...finished merging child', type='debug')
        self.out(self.feature_set_metadata[new_label])

        # Then remove those index columns for this variant on the parent (child=None)
        # TODO: Uncomment this when subset works with children
        subset_kwargs = {'batch':batch, 'variant':curr_variant, 'child':None, 'overwrite':True}
        #self.subset(new_label, new_label, cols_filter=lambda x: x not in feature_set_index_cols)

    if view_output:
        self.view(new_label, 'shape')        

#############################################################################################
# Concatenates multiple data sets together into a new one
# axis=0 --> concat rows together
# axis=1 --> concat columns together (just like pandas) along with any children
# keep_all_columns=True --> keep all columns from all data sets, fill with None if the column is missing for that row
# keep_all_columns=False --> only keep the columns that are in all the input datasets (only applicable if axis=0)
# Note: Currently doesn't support concating children for axis=0 (even if all the children are the same types) 
def concat(self, output_label, input_labels, axis=0, keep_all_columns=False, reset_index=True, **kwargs):
    # Default action is to not modify the children to become dask/pandas
    engine = kwargs.get('engine', None)
    variant = kwargs.get('variant', '*')
    child = kwargs.get('child', '*')
    batch = kwargs.get('batch', self.default_batch)

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # TODO: Respect reset_index=False (what would that mean?)
    def concat_function(concat_dfs, concat_labels, axis=0, keep_all_columns=True, reset_index=True, **kwargs):
        if isinstance(concat_dfs, list):
            print("In concat_function, received {} concat dfs: {} with labels: {}, axis={}, keep_all_columns={}".format(len(concat_dfs), [type(x) for x in concat_dfs], concat_labels, axis, keep_all_columns))
#                 if len(concat_dfs)>2:
#                     print("ERROR! Currently cannot support >2 dataframes to concat at once inside concat_function. Exiting.")
#                     return None

            # Iterate through the dataframes and their labels to merge together
            num_feature_sets_to_concat = len(concat_labels)
            all_concat_df = None

            #previous_concat_label = None
            all_previous_concat_labels = []
            for feature_set_num, (featureSetToConcat, feature_set_to_concat_df) in enumerate(zip(concat_labels, 
                                                                                                 concat_dfs)):
                if all_concat_df is None:
                    # For the first one, just copy it
                    all_concat_df = feature_set_to_concat_df #.copy() # Commenting out the copy() on 1/21/21
                    concat_dataset_types = 'dask' if isinstance(feature_set_to_concat_df, dd.DataFrame) else \
                                           'pandas' if isinstance(feature_set_to_concat_df, pd.DataFrame) else 'other'
                    self.out("Copying first concat set: ", featureSetToConcat, type(feature_set_to_concat_df))
                else:
                    # For the others, concat them to the previous ones
                    if axis==0:
                        # Concat vertically
                        # TODO: Handle case where this is not Dask
                        if keep_all_columns:                                
                            all_concat_df = all_concat_df.append(feature_set_to_concat_df)
                        else:
                            overlapping_cols = list(set(all_concat_df.columns) & 
                                                    set(feature_set_to_concat_df.columns))
                            print("...since keep_all_columns=False and axis=0, output trimmed down to {} cols"\
                                  .format(len(overlapping_cols)))
                            all_concat_df_cols = all_concat_df[overlapping_cols]
                            new_concat_df_cols = feature_set_to_concat_df[overlapping_cols]
                            all_concat_df = all_concat_df_cols.append(new_concat_df_cols)
                        print("After concatting {} rows, have output with shape:".format(feature_set_to_concat_df.shape[0]), 
                              all_concat_df.shape)
                    else:
                        # Join the dataframes to put them together column-wise (horizontally)
                        next_concat_label = featureSetToConcat
                        i = 1
                        if next_concat_label in all_previous_concat_labels:
                            while next_concat_label+'_{}'.format(str(i)) in all_previous_concat_labels and i<100:
                                i += 1
                            next_concat_label = next_concat_label+'_{}'.format(str(i))
                        all_concat_df = all_concat_df.join(feature_set_to_concat_df.reset_index(drop=True),
                                                           #lsuffix='_{}'.format(output_label),
                                                           rsuffix='_{}'.format(next_concat_label)
                                                          )
                        all_previous_concat_labels.append(next_concat_label)
                        #previous_concat_label = next_concat_label
                        print("After concatting dataframe {}, have output with shape:".format(feature_set_to_concat_df.shape), 
                              all_concat_df.shape)

                #previous_concat_label = featureSetToConcat

            return all_concat_df
        return None

#                 curr_df = concat_dfs[0]
#                 concat_df = concat_dfs[1]

#                 if axis==0:

#                 else:
#                     # Join the dataframes to put them together column-wise (horizontally)
#                     if len(concat_labels)>1:
#                         print("...concat_labels:", concat_labels)
#                         first_concat_label = concat_labels[0]
#                         print("...first concat_label:", first_concat_label)
#                         second_concat_label = concat_labels[1]
#                         print("...second concat_label:", second_concat_label)
#                         output_df = curr_df.join(concat_df.reset_index(drop=True), 
#                                                    lsuffix='_{}'.format(first_concat_label), 
#                                                    rsuffix='_{}'.format(second_concat_label))
#                     else:
#                         output_df = curr_df.join(concat_df.reset_index(drop=True), 
#                                                    rsuffix='_{}'.format(concat_labels[0]))                        
#                     print("After concatting cols, have output with shape:", output_df.shape)
#                     return output_df

#             else:
#                 #print("In concat_function, received 1 concat df: {}".format(concat_dfs))
#                 return concat_dfs

        #return None
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def concat_child_function(input_dataset, input_label, current_child, axis=0, keep_all_columns=True, **kwargs):
        self.out("Inside concat_child_function...")
        self.out("current_child:", current_child)
        self.out("input_dataset:", input_label, type(input_dataset))
        child = kwargs.get('child', None)
        self.out("child:", child)
        parent = kwargs.get('parent', None)
        self.out("parent:", parent)
        fillna = kwargs.get('fillna', True)
        #self.out("index col:", index_col.shape, index_col.max())

        if hasattr(input_dataset, '__feature_type__') and input_dataset.__feature_type__=='FeatureMatrix':
            # Get the input matrix
            input_child_matrix = input_dataset.getMatrix()
            self.out("have input_child_matrix:", input_child_matrix)
            self.out("Trying to concat a FeatureMatrix...shape:{}".format(input_child_matrix.shape))
            input_matrix_columns = input_dataset.columns()
            num_input_columns = input_child_matrix.shape[1]
            num_input_rows = input_child_matrix.shape[0]
            input_matrix_type = input_dataset.matrix_type

            # Handle when child is a FeatureMatrix
            if current_child is None:
                # Just use the input child matrix
                                    # Transpose so this is a column array, and store that as a FeatureMatrix object
                self.out("Saving FeatureMatrix with matrix:{} and columns={}".format(input_child_matrix.shape, 
                                                                                       input_matrix_columns))
                # TODO: Make sure this child name isn't duplicated for the same child name in >1 merge input sets
                return FeatureMatrix(label=child, 
                                     parent_label=parent,
                                     matrix=input_child_matrix, 
                                     columns=input_matrix_columns, 
                                     mappings=input_dataset.getMappings())
            else:
                # Concat input child onto current child 
                self.out("Checking current_child {}: {}".format(current_child.label, current_child))
                # Make sure the current child is a FeatureMatrix too (combining dataframe+matrix not supported yet)
                if not hasattr(current_child, '__feature_type__') or not current_child.__feature_type__=='FeatureMatrix':
                    self.out("ERROR: Attempting to concat FeatureMatrix for child '{}' onto a dataframe.  Cannot do this.".format(current_child.label), type='error')
                    raise

                # Get the current matrix
                current_child_matrix = current_child.getMatrix()
                current_child_columns = current_child.columns()
                num_current_columns = current_child_matrix.shape[1]
                num_current_rows = current_child_matrix.shape[0]
                current_matrix_type = current_child.matrix_type

                # Only proceed if there are any rows to output to matrix
                if num_input_rows > 0 and num_input_columns > 0:
                    if axis==0:
                        # Check for the same # of columns, if not throw an error
                        if num_current_columns != num_input_columns:
                            if keep_all_columns:
                                print("Going to concat {} columns with {} new columns".format(num_input_columns,
                                                                                              num_current_columns))
                                # Need to line up the columns manually, since they don't match up
                                current_child_matrix_coo = current_child_matrix.tocoo()
                                input_child_matrix_coo = input_child_matrix.tocoo()

                                # Create a mapping of the column indexes in the current matrix to their 
                                # new column index in the concatted matrix
                                new_concat_cols = input_matrix_columns
                                new_current_col_index_map = {}
                                next_new_col_index = num_input_columns
                                for i, col in enumerate(current_child_columns):
                                    if col in input_matrix_columns:
                                        new_current_col_index_map[i] = input_matrix_columns.index(col)
                                    else:
                                        new_current_col_index_map[i] = next_new_col_index
                                        new_concat_cols.append(col)
                                        next_new_col_index += 1
                                num_concat_cols = next_new_col_index
                                print("...have {} overall columns".format(num_concat_cols))

                                # Apply this mapping to the columns of the elements in the second matrix to concat
                                new_current_child_matrix_cols = np.array([new_current_col_index_map[i] for i in \
                                                                          current_child_matrix_coo.col])
                                print("...mapped {} columns".format(new_current_child_matrix_cols.shape[0]))

                                # Shift the rows of the second matrix down
                                new_current_child_matrix_rows = current_child_matrix_coo.row + num_input_rows

                                # Build a new COO Matrix using the original matrix combined with the new mapped matrix
                                new_concat_matrix_data = np.hstack((input_child_matrix_coo.data,
                                                                   current_child_matrix_coo.data))
                                new_concat_matrix_rows = np.hstack((input_child_matrix_coo.row,
                                                                   new_current_child_matrix_rows))
                                new_concat_matrix_cols = np.hstack((input_child_matrix_coo.col,
                                                                   new_current_child_matrix_cols))
                                new_concat_matrix_numrows = num_input_rows + num_current_rows
                                new_concat_matrix_numcols = num_concat_cols

                                concat_matrix = sp.coo_matrix((new_concat_matrix_data, 
                                                                   (new_concat_matrix_rows, new_concat_matrix_cols)), 
                                                          shape=(new_concat_matrix_numrows, new_concat_matrix_numcols))
                                print("...new sparse concat matrix:", concat_matrix.shape)
                                concat_matrix_columns = new_concat_cols

                            else:
                                self.out("ERROR: Child matrix '{}' has {} columns != {} columns in input matrix.  To allow these to be concatted, pass in keep_all_columns=True.".format(current_child.label, num_current_columns, num_input_columns, input_dataset.label),
                                         type='error')
                                raise
                        else:
                            # Columns line up exactly, so just need to vertical-stack them
                            if input_matrix_type=='sparse' and current_matrix_type=='sparse':
                                concat_matrix = sp.vstack([current_child_matrix, input_child_matrix])
                            else:
                                concat_matrix = np.vstack([current_child_matrix, input_child_matrix])
                            concat_matrix_columns = current_child_columns
                    else:
                        # Check for the same # of rows, if not throw an error
                        if num_current_rows != num_input_rows:
                            self.out("ERROR: Child matrix '{}' has {} rows != {} rows in input matrix".format(current_child.label, num_current_rows, num_input_rows, input_dataset.label),
                                     type='error')
                            raise

                        # Stack the matrices horizontally
                        if input_matrix_type=='sparse' and current_matrix_type=='sparse':
                            concat_matrix = sp.hstack([current_child_matrix, input_child_matrix])
                        else:
                            concat_matrix = np.hstack([current_child_matrix, input_child_matrix])
                        # Create a list of all the columns in both current and input children, with no overlapping col names
                        concat_matrix_columns = current_child_columns
                        col_overlap = list(set(concat_matrix_columns)&set(input_matrix_columns))
                        for input_col in input_matrix_columns:
                            if input_col in col_overlap:
                                # Note this will result in _1_1_1 if the same column appears in repeated transforms
                                concat_matrix_columns.append(input_col+'_1')
                            else:
                                concat_matrix_columns.append(input_col)

                    # Transpose so this is a column array, and store that as a FeatureMatrix object
                    self.out("Creating FeatureMatrix with matrix:{} and columns={}".format(concat_matrix.shape, 
                                                                                           concat_matrix_columns))
                    # TODO: Make sure this child name isn't duplicated for the same child name in >1 merge input sets
                    return FeatureMatrix(label=child, 
                                         parent_label=parent,
                                         matrix=concat_matrix, 
                                         columns=concat_matrix_columns, 
                                         mappings=input_dataset.getMappings())


        return None


    # Iterate through each input label
#         is_first_input = True
#         for input_label in input_labels:
        # After the first concat, set overwrite to True to tell transform -> addData -> save to overwrite the previous copy
#             if not is_first_input:
#                 kwargs['overwrite'] = True

        # On the first iteration just "concat" the first data set alone
#             concat_labels = [output_label, input_label] if not is_first_input else input_label
#             concat_metadata = self.transform(output_label, concat_function, concat_labels, concat_labels, 
#                            axis=axis, keep_all_columns=keep_all_columns, reset_index=reset_index, 
#                            new_rows=(axis==0), # Only unify if concatting rows 
#                            new_cols=None, 
#                            **kwargs)
#             is_first_input = False

#             # Replicating functionality normally inside fs.transform() to figure out what variants were used on the inputs
#     #         target_variant = kwargs.get('variant', '*')
#             batch = kwargs.get('batch', self.default_batch)


#             #for (curr_variant, input_variants) in zip(merge_variants, all_input_variant_combos):

#                         # Added 9/22/20: Only save the final child, to avoid repetitive saving of all intermediate children N^2 times
#                         save_to_disk = (feature_set_child == last_child_to_merge)
#                         self.out("...save_to_disk for child '{}' = {}".format(feature_set_child, save_to_disk))

#                         # TODO: Need to check if this is indeed dask                            
#                         new_index_rows = output_feature_set_data[input_feature_set_index_col].compute() if isinstance(output_feature_set_data, dd.DataFrame) else output_feature_set_data[input_feature_set_index_col]
#                         self.out("...index col found '{}' with shape {}, {} nulls, max value={}".format(input_feature_set_index_col, new_index_rows.shape, new_index_rows.isna().sum(), new_index_rows.max()))

#                         # Pass this column of the rows new index into a transform function
#                         kwargs['child'] = feature_set_child
#                         kwargs['variant'] = input_variant
#                         kwargs['output_variant'] = curr_variant # Added on 6/10/19
#                         kwargs['parent'] = new_label
#                         kwargs['overwrite'] = True # Added on 7/24/19
#                         kwargs['save_to_disk'] = save_to_disk # Added on 9/22/20

#                         # Note: Commenting this out until can also support conversion of children to pandas inside transform()
#                         # This is to handle the fact that transform() will change the FeatureMatrix children to pandas dfs
#                         #if engine=='pandas' or engine is None:
#                         #    self.transform(new_label, merge_function, [new_label, feature_set_label], [feature_set_label], 
#                         #                   mergeVars, **kwargs)
#                         #else:
#                         self.transform(new_label, merge_child_function, 
#                                        feature_set_label, feature_set_label, new_index_rows, **kwargs)

#                 self.out('...finished merging child', type='progress')
#                 self.out(self.feature_set_metadata[new_label])

#                 # Then remove those index columns for this variant on the parent (child=None)
#                 # TODO: Uncomment this when subset works with children
#                 subset_kwargs = {'batch':batch, 'variant':curr_variant, 'child':None, 'overwrite':True}
#                 #self.subset(new_label, new_label, cols_filter=lambda x: x not in feature_set_index_cols)

#         if view_output:
#             self.view(new_label)            
#             concat_labels = [output_label, input_label] if not is_first_input else input_label
#             concat_metadata = self.transform(output_label, concat_function, concat_labels, concat_labels, 
#                            axis=axis, keep_all_columns=keep_all_columns, reset_index=reset_index, 
#                            new_rows=(axis==0), # Only unify if concatting rows 
#                            new_cols=None, 
#                            **kwargs)
#             is_first_input = False

    self.out("Going to concat the FeatureSets together {} to produce '{}'".format(input_labels, output_label))
    concat_metadata = self._transform(output_label, concat_function, input_labels, input_labels, axis=axis,
                                    keep_all_columns=keep_all_columns, reset_index=reset_index,
                                    new_rows=(axis==0), new_cols=None, 
                                    **kwargs)
    self.out("...done")
    self.out("...concat metadata:{}".format(concat_metadata))
    output_featureset = self.Features(output_label, reload=False)

    # If a 'child' kwarg was passed, then use it to determine which children to merge
    children_to_concat = kwargs.get('child', '*')
    children_to_concat_list = None if children_to_concat=='*' else [None] if children_to_concat is None else [children_to_concat] if isinstance(children_to_concat, str) else children_to_concat

    #if variant=='*' or isinstance(variant, list):
    # Figure out which children to concat for each variant
#         input_child_dict = self.Features(input_label).children(variant=variant)

#         # Convert to dict if the result is not a dict
#         if input_child_dict is None:
#             print("Could not find all variants {} in '{}', returning from concat()".format(variant, input_label))
#         elif isinstance(input_child_dict, list):
#             input_child_dict = {variant:input_child_dict}

#         output_featureset_obj = self.Features(output_label)
    # TODO: Generalize this since it's assuming the output variant is the same as all the input variants

    # To do so probably need to create iterator wrapper around transform that figures out all the combos
    # Also, note that the variant combos are created here in one-at-a-time fashion, rather than all at once

    self.out("concat_metadata:", concat_metadata)
    if concat_metadata is not None:
        for one_concat_metadata in concat_metadata:
            curr_variant = one_concat_metadata['output_variant']            
            input_variant_metadata = one_concat_metadata['inputs']
            self.out("Going to concat the children '{}' for '{}' variant={} using input variants {}".format(children_to_concat, output_label, curr_variant, input_variant_metadata), type='progress')

            # Now iterate through each featureSetsToMerge and look for its children

            # Get the output variant for this combo, to pass-into the transform below
            # TODO: Push all this into transform() to handle iterating through multiple variants
#             output_variant = kwargs.get('output_variant', None)
#             num_variant_combos = len(input_variants)
#             this_output_variant = self.getOutputVariant(input_variants, output_variant, num_variant_combos)

            # Iterate through each input feature set with its variant
            #for (feature_set_label, input_variant) in zip(featureSetsToMerge, input_variants):

            for one_merge_input_metadata in input_variant_metadata:
                feature_set_label = one_merge_input_metadata['input_featureset']
                input_variant = one_merge_input_metadata['input_variant']
                self.out("Checking for children in {} using variant {}...".format(feature_set_label, input_variant))
                input_feature_set_obj = self.Features(feature_set_label)
                input_feature_set_data = input_feature_set_obj.getData(variant=input_variant, child=None)
                #input_feature_set_data = self.Data(feature_set_label, variant=input_variant, child=None)
                output_feature_set_data = output_featureset.getData(variant=curr_variant, child=None)
                #output_feature_set_data = self.Data(new_label, variant=curr_variant, child=None)
                self.out("output feature set data for '{}' from variant={}, child=None, shape {}".format(output_label, 
                                                                                                         curr_variant,
                                                                                                         output_feature_set_data.shape))
                input_feature_set_children = input_feature_set_obj.children(variant=input_variant).copy()
                self.out("...input feature set children:", input_feature_set_children)

                # Iterate through each child, look for the non-None ones
                all_children_to_concat = children_to_concat_list or input_feature_set_children
                all_children_to_concat_nonone = [child for child in all_children_to_concat if child is not None]
                last_child_to_concat = all_children_to_concat_nonone[-1] if len(all_children_to_concat_nonone)>0 else None

                #for feature_set_child in input_feature_set_children:
                for feature_set_child in all_children_to_concat_nonone:
                # Only merge non-None children (and in the given 'child' list, if any given)
                    #if feature_set_child is not None and (children_to_merge_list is None or feature_set_child in children_to_merge_list):
                    self.out("Need to concat child='{}' for feature set='{}', variant='{}'".format(feature_set_child, feature_set_label, input_variant))


#             # Iterate through the list of variants which need to have concat run
#             for input_variant in input_child_dict:
#                 input_child_list = input_child_dict[input_variant]

#                 # Trim to just the list of children to actually concat
#                 if child=='*':
#                     # Just leaving this here for recordkeeping
#                     target_children = input_child_list
#                 elif isinstance(child, list) or isinstance(child, str) or child is None:
#                     target_child_list = [child] if isinstance(child, str) or child is None else child
#                     target_children = []
#                     for target_child in target_child_list:
#                         if target_child in input_child_list:
#                             target_children.append(target_child)
#                         else:
#                             print("ERROR! Cannot find child '{}' for variant '{}' in '{}'. Exiting concat.".format(target_child, input_variant, input_label))
#                             return None

#                 # Iterate through just the children specified
#                 last_child_to_concat = target_children[-1] if len(target_children)>0 else None
#                 for this_child in target_children:
#                     if this_child is not None:
#                         child_dataset = self.Data(input_label, variant=input_variant, child=this_child) #[child]
                    # Added 9/22/20: Only save the final child, to avoid repetitive saving of all intermediate children N^2 times
                    save_to_disk = (feature_set_child == last_child_to_concat)
                    self.out("...save_to_disk for child '{}' = {}".format(feature_set_child, save_to_disk))

                    # Pass this column of the rows new index into a transform function
                    kwargs['child'] = feature_set_child
                    kwargs['variant'] = input_variant
                    kwargs['output_variant'] = curr_variant
                    kwargs['parent'] = output_label
                    kwargs['overwrite'] = True
                    kwargs['save_to_disk'] = save_to_disk
                    kwargs['axis'] = axis
                    kwargs['keep_all_columns'] = keep_all_columns

                    # Get the current child matrix to concat onto
                    current_child = self.Data(output_label, child=feature_set_child, variant=curr_variant)

                    # Note: Commenting this out until can also support conversion of children to pandas inside transform()
                    # This is to handle the fact that transform() will change the FeatureMatrix children to pandas dfs
                    #if engine=='pandas' or engine is None:
                    #    self.transform(new_label, merge_function, [new_label, feature_set_label], [feature_set_label], 
                    #                   mergeVars, **kwargs)
                    #else:
                    #new_index_rows = None
                    self._transform(output_label, concat_child_function, 
                                   feature_set_label, feature_set_label, current_child, **kwargs)

    self.view(output_label)


#############################################################################################
def convolve(self, output_label, input_label, index_var, date_var, value_var, num_cols_per_window, date_unit,  add_differences=False, shift_zero_back=None, *args, **kwargs):
    batch = kwargs.get('batch', self.default_batch)
    input_labels = [input_label] if isinstance(input_label, str) else input_label

    # Get the list of combinations of variants to use for each input in input_labels
    variant = kwargs.get('variant', self.default_variant)
    output_variant = kwargs.get('output_variant', None)
    target_variant_list = [variant] if variant is None or isinstance(variant, str) else variant
    all_input_variant_combos, all_output_variants = self._getVariantCombinations(input_labels, 
                                                                                 target_variant_list, 
                                                                                 output_variant, 
                                                                                 batch)
    print("all combos", all_input_variant_combos)

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def createRollingTimeWindows(df, index_var, date_var, value_var, num_cols_per_window, date_unit, add_differences=False, shift_zero_back=None, save_directory=None, **kwargs):
        print("num_cols_per_window", num_cols_per_window)
        if isinstance(df, pd.DataFrame):
            df = dd.from_pandas(df, chunksize=100000) #npartitions=10)

        num_rows = len(df)
        print("Have {} input rows".format(num_rows))

        # Figure out number of columns we'll need to turn into rolling windows
        #date_var_describe = df[date_var].describe().compute()
        min_col = df[date_var].min() #date_var_describe['min'] #np.min(df[date_var]) #.astype(int)
        max_col = df[date_var].max() #date_var_describe['max'] #np.max(df[date_var]) #.astype(int)
        last_start_col = max(min_col, max_col-num_cols_per_window)
        num_cols = min(num_cols_per_window, max_col-min_col+1)

        if isinstance(index_var, str):
            index_var_list = [index_var]
            num_index_cols = 1
        else:
            index_var_list = index_var
            num_index_cols = len(index_var_list)  

        df_pandas = df.compute()
        merged_windows = None
        var_num = 1

        #for value_var in value_vars:
        df_pivot = df_pandas.pivot_table(index=index_var_list, values=value_var, columns=date_var).reset_index()
        df_pivot.columns = list(df_pivot.columns)
        #print("All pivot columns: ", df_pivot.columns.values, type(df_pivot))
        num_pivot_columns = len(df_pivot.columns) - num_index_cols

        if shift_zero_back is None:
            column_names = ['{}_back_{}_{}'.format(value_var, str(x), date_unit) for x in reversed(range(num_cols))]
        else:
            column_names = []
            for x in reversed(range(num_cols)):
                x_shifted = x - shift_zero_back
                if x_shifted >= 0:
                    column_names.append('{}_back_{}_{}'.format(value_var, str(x_shifted), date_unit))
                else:
                    column_names.append('{}_up_{}_{}'.format(value_var, str(x_shifted*-1), date_unit))
        print("new columns: {}".format(column_names))
        all_windows = None
        started_output = False

        concat_num = 0

        # say num_pivot_columns=100, num_cols_per_window=10, all col indexes: [0,99] --> 0-9, 1-10, 2-11, ..., 90-99
        last_col_index = max(num_pivot_columns-num_cols_per_window, 1)
        print("last_col_index:",last_col_index)
        for start_col_index in range(0, last_col_index):
            end_col_index = min(start_col_index + num_cols_per_window, num_pivot_columns)
            pivot_columns = df_pivot.columns[start_col_index+num_index_cols:end_col_index+num_index_cols]
            df_index_subset = df_pivot.loc[:,index_var_list]
            df_subset = df_pivot.loc[:,pivot_columns]
            df_subset.columns = column_names
            if shift_zero_back is None:
                zero_date_val = pivot_columns[-1]
                df_subset.loc[:,date_var] = zero_date_val
            else:
                zero_date_val = pivot_columns[-1*(1+shift_zero_back)]
                df_subset.loc[:,date_var] = zero_date_val

            # If told in the parameters, include a set of feature columns for the difference between each Nth and (N+1)th column
            if add_differences:
                num_new_columns = len(column_names)
                for new_column_order in range(num_new_columns-1):
                    new_column_name = column_names[new_column_order]
                    next_column_name = column_names[new_column_order+1]
                    new_diff_column = next_column_name + '_diff'
                    df_subset.loc[:,new_diff_column] = df_subset[next_column_name] - df_subset[new_column_name]

            # Concat the index cols back with the subset of pivoted cols
            df_subset_with_indexes = pd.concat([df_index_subset, df_subset], axis=1)

            # Now stack the complete dataframe with this new subset of rows
            if save_directory is not None:
                table = pa.Table.from_pandas(df_subset_with_indexes)
                if not started_output:
                    pqwriter = pq.ParquetWriter(save_directory, table.schema, compression='LZ4')
                pqwriter.write_table(table)
                started_output = True
            else:
                if all_windows is not None:
                    all_windows = dd.concat([all_windows, df_subset_with_indexes], axis=0, interleave_partitions=True)
                else:
                    all_windows = dd.from_pandas(df_subset_with_indexes, chunksize=100000) #npartitions=10)

            concat_num += 1
            if concat_num % 100 == 0 or concat_num == 1:
                gc.collect()
                print("...Concating from col #{}-#{}, {}={}, shape:{}".format(start_col_index, end_col_index, date_var, zero_date_val, len(df_subset_with_indexes)))            

        if save_directory is not None:
            pqwriter.close()
            all_windows = dd.read_parquet(save_directory, engine='pyarrow', index=None)

        del(df_pivot)
        return all_windows
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++



    # Create a blank FeatureSet where we can start to put the data from the convolution
    output_feature_set = FeatureSet(save_directory=self.base_directory, label=output_label, project=self.project_label, batch=batch, space=self)

    # Iterate through each variant, if we have more than one
    num_variant_combos = len(all_input_variant_combos)
    for variant_combo, this_output_variant in zip(all_input_variant_combos, all_output_variants):
        print("variant combo:", variant_combo)
        this_variant = variant_combo[0]

        # Set up the output parameters
        # No longer need this call here since this was included in _getVariantCombinations()
        #this_output_variant = self._getOutputVariant(variant_combo, output_variant, num_variant_combos)         
        # Even though the df is null, this will create a filename (with default filetype)
        # TODO: Don't hard-code the default filetype as parquet here, instead let the Constructor set it to determine the filepath
        output_feature_set.save(variant=this_output_variant, schema_changed=True)
        output_filename = output_feature_set.last_save_filenames[this_output_variant]
        output_folder = output_feature_set.getSaveDirectory(output_filename, variant=this_output_variant)
        output_path = os.path.join(output_folder, 'parts.pq')
        print("Have output_feature_set at {}".format(output_path))
        self._addFeatureSet(output_label, output_feature_set, batch=batch)

        # Send the output file location for the convolution into the transform
        # TODO: Don't fix this particular transform
        transform_kwargs = copy.deepcopy(kwargs)
        transform_kwargs['variant'] = this_variant
        #self._transform(output_label, DateTransformer.createRollingTimeWindows, input_label, 
        self._transform(output_label, createRollingTimeWindows, input_label, 
            index_var, date_var, value_var, num_cols_per_window, date_unit, 
            add_differences=add_differences, shift_zero_back=shift_zero_back, save_directory=output_path,
            *args, **transform_kwargs)

    self.view(output_label)



#############################################################################################
# Note: This method computes the dask dataframe into a pandas dataframe or numpy array, so is time/storage insensitive
# only_top_rows must be int -- choose the top # rows for the whole list (group_by=None) or within each group_by group
# rank_var creates a variable with value 1,2,3,... for the ordinal ranking of the sorted rows,
#    either within each grouping (if group_by provided) or within the whole sorted list (if no group_by provided)
def sort(self, output_label, input_label, sort_by_vars, ascending=False, 
         only_top_rows=None, group_by=None, special_var=None, rank_var=None, **kwargs):

    def sort_function(input_df, sort_vars, ascending_flags, only_top_rows=None, group_by=None, special_var=None, rank_var=None, **kwargs):
        # Create a pandas dataframe or numpy array to sort
        #input_df = self.Data(input_label, **kwargs).compute()
        print("In sort function")
        print(input_label)
        print(input_df.columns)

        # Convert dask dataframe to pandas dataframe
        # NOTE: This will crash things if you try to do it on a big dataset!
        if isinstance(input_df, dd.DataFrame):
            input_df = input_df.compute()

        # Check if there are columns to sort
        # (Note: As of 10/28/19, supporting no sorting rows, just selecting one row per group)
        if sort_vars is None:
            input_df_sorted = input_df
        else:
            # Sort if pandas dataframe
            if isinstance(input_df, pd.DataFrame):
                print("Sorting as a pandas dataframe")
                input_df_sorted = input_df.sort_values(by=sort_vars, 
                                                       axis=0, 
                                                       ascending=ascending_flags, 
                                                       inplace=False, 
                                                       na_position='last').reset_index(drop=True, inplace=False)

            # Or if numpy matrix
            elif isinstance(input_df, np.ndarray): 
                # TODO
                return None

        print("only top rows:", only_top_rows)
        print("group_by:", group_by)
        # If only_top_rows provided, then subset to only the top-N rows
        if only_top_rows is not None and isinstance(only_top_rows, int):
            if group_by is None:
                # Choose top rows from the overall data set
                input_df_sorted = input_df_sorted[:only_top_rows]
            elif special_var is not None:
                #appts = fs.Data('appointments_raw')[:1000000]
                num_total_rows = input_df_sorted.shape[0]
                latest_appt_per_patient_ix = input_df_sorted.groupby(group_by, 
                                                                     as_index=False, 
                                                                     dropna=False,
                                                                     observed=True)[special_var].idxmax(skipna=True)
                latest_appt_per_patient_ix_notna = latest_appt_per_patient_ix[~latest_appt_per_patient_ix.isna()]
                numrows_ones = latest_appt_per_patient_ix_notna.shape[0]
                ones = np.ones(numrows_ones)
                zeros = np.zeros(numrows_ones)
                #from scipy.sparse import csr_matrix
                ones_sp = sp.csr_matrix((ones, (latest_appt_per_patient_ix_notna, zeros)), 
                                        shape=(num_total_rows, 1), dtype=np.int16)
                ones_series = pd.DataFrame(ones_sp.todense())[0]
                input_df_sorted = input_df_sorted[ones_series==1]

            else:
                # Choose top rows within each group_by group
                input_df_sorted = input_df_sorted.groupby(group_by, 
                                                          sort=False, 
                                                          dropna=False,
                                                          observed=True).head(only_top_rows).reset_index(drop=True)

        # Create a ranking var if provided       
        if rank_var is not None:
            if group_by is None:
                num_rows = input_df_sorted.shape[0]
                input_df_sorted[rank_var] = np.arange(num_rows)+1
            else:
                one_sort_var = sort_vars if isinstance(sort_vars, str) else sort_vars[0]
                input_df_sorted[rank_var] = input_df_sorted.groupby(group_by, 
                                                                    sort=False, 
                                                                    dropna=False,
                                                                    observed=True)[one_sort_var].cumcount()+1

        return input_df_sorted

    # Handle both string and list inputs for sort_by and ascending
    sort_vars = [sort_by_vars] if isinstance(sort_by_vars, str) else sort_by_vars
    ascending_flags = [ascending] if isinstance(ascending, bool) else ascending
    print(sort_vars)

    # Run the transform using this merge function
    self._transform(output_label, sort_function, input_label, sort_vars=sort_vars, ascending_flags=ascending_flags, only_top_rows=only_top_rows, group_by=group_by, special_var=special_var, rank_var=rank_var, 
                   new_rows=False, new_cols=None,
                   # 11/28/20: No need to re-unify columns since no rows or columns are created here
                   **kwargs)
    self.view(output_label)


#############################################################################################
# todo: Allow control over the datatype (int64, int32, float32, float64, etc.)
# matrix_type = 'sparse' or 'dense' or 'array'
def createFeatureMatrix(self, output_features, input_dataset, 
                        index_vars=None, feature_cols=None, variant=None, 
                        feature_matrices='*',
                        matrix_label='matrix', child=None, matrix_type='sparse',
                        label_cols=None, label_child='labels',
                        label_matrices=None,
                        normalize='max', norm_label='matrix_norm',
                        fillna=None): #mean_encoding=None, fillna=False):

    # Reload the FeatureSpace metadata first to make sure we reload the latest files
    self.out("Reloading the FeatureSpace...")
    self._loadFeatureSetMetadata()

    if index_vars is None:
        self.out("ERROR: Cannot execute createFeatureMatrix() without index_vars. Exiting.", type='error')
        return
    elif feature_cols is None:
        self.out("ERROR: Cannot execute createFeatureMatrix() without feature_cols. Exiting.", type='error')
        return 

    # Create base training dataset (and fill nulls if indicated by fillna)
    training_data = self.Data(input_dataset, variant=variant, child=child, reload=True)
    if isinstance(feature_cols, str):
        feature_cols = [feature_cols]
    training_df = training_data[feature_cols] if fillna is None else training_data[feature_cols].fillna(fillna)
    if isinstance(training_data, dd.DataFrame):
        training_df = training_df.compute()
    self.out("Have training data set:", training_df.shape)

    # Choose index vars to keep in the parent dataframe
    if isinstance(index_vars, str):
        index_vars = [index_vars]
    ids_df = training_data[index_vars]
    self.out("Have dataframe for the ID columns '{}':".format(index_vars), ids_df.shape, type(ids_df))

    # Make the base training dataset into a sparse matrix
    training_matrix = None
    if matrix_type == 'sparse':
        training_matrix = sp.coo_matrix(training_df.values, dtype=np.float32)
        self.out("Created sparse feature matrix:", training_matrix.shape)
    else:
        # Otherwise if 'dense' or 'array' then use a numpy array
        training_matrix = training_df.values
        self.out("Created dense feature matrix:", training_matrix.shape)


    # Get the labels (if any)
    # Note: If any label columns are provided from the parent dataframe, the whole labels matrix will be numpy/dense below
    labels_array = None
    if label_cols is not None and len(label_cols)>0:
        label_cols = [label_cols] if isinstance(label_cols, str) else label_cols
        labels_df = training_data[label_cols] if fillna is None else training_data[label_cols].fillna(fillna)
        if isinstance(labels_df, dd.DataFrame):
            labels_df = labels_df.compute()
        print("Have labels data set:", labels_df.shape)
        labels_array = labels_df.values
        #self.addData(output_labels, labels_df, variant=output_variant)

    # Check memory footprints
    self.out("Training parent dataset:", training_df.memory_usage(index=True).sum())
    self.out("Training matrix:", asizeof(training_matrix))
    #print("Training parent dataset:", training_df.values.nbytes)
#         print("Training labels:", sys.getsizeof(labels_df))

    # Choose the child matrices to stack together horizontally
    if not self.exists(input_dataset):
        self.out(f"ERROR: Featureset '{input_dataset}' does not exist, cannot create a Features Matrix with it.",
                 type='error')
        raise
    features_overall = self.Features(input_dataset)
    if feature_matrices=='*':
        children = features_overall.children(variant=variant)
    else:
        children = feature_matrices
    self.out("Stacking children matrices together horizontally:", children)

    # Combine into a list of the children matrices
    all_children = []
    all_child_columns = []
    max_val = 0
    for child in children:
        self.out("...stacking child:{}".format(child))

        if child is not None:
            child_data = features_overall.getData(child=child, variant=variant)
            # Make sure this child exists
            if child_data is None:
                self.out(f"ERROR: Child matrix '{child}' for variant '{variant}' in the Featureset '{input_dataset}' does not exist, so cannot merge it into the Feature Matrix.",
                         type='error')
                raise

            # Assuming these children are all FeatureMatrix types 
            if hasattr(child_data, '__feature_type__') and child_data.__feature_type__=='FeatureMatrix':
                # Throw an error if one of them is empty so the user knows
                if child_data.isEmpty():
                    self.out(f"ERROR: Child matrix '{child}' for variant '{variant}' in the Featureset '{input_dataset}' is empty (shape={child_data.getShape()}), so cannot merge it into the Feature Matrix.",
                             type='error')
                    raise                
                child_matrix = child_data.getMatrix()
                child_columns = child_data.columns()

                # Store a list of the child matrices and their columns
                all_children.append(child_matrix)
                all_child_columns = all_child_columns + child_columns

                # Keep track of the max value found in all children
                child_max = child_matrix.max(axis=0).max()
                max_val = child_max if child_max > max_val else max_val

    # If there are label matrices, stack them too
    all_label_children = []
    all_label_columns = []
    if label_matrices is not None:
        if isinstance(label_matrices, str):
            label_matrices = [label_matrices]
        for one_label_child in label_matrices:
            label_data = features_overall.getData(child=one_label_child, variant=variant)
            label_matrix = label_data.getMatrix()
            label_columns = label_data.columns()

            # Store list of all label children and their columns
            all_label_children.append(label_matrix)
            all_label_columns = all_label_columns + label_columns

    # Figure out the smallest datatype needed
    #max_val = np.max([child.max(axis=0).max() for child in all_children])
    self.out("Max val is:", max_val)
    dtype = constants.getDtype(max_val)
    self.out("Using datatype for children:", dtype)

    # Stack together the base features + children as one big matrix (horizontally)
    if len(all_children)>0:
        children_stacked = sp.hstack(all_children, dtype=dtype) if matrix_type=='sparse' else np.hstack(all_children, dtype=dtype)
        if training_matrix is not None:
            all_features_stacked = sp.hstack([training_matrix, children_stacked]) if matrix_type=='sparse' else np.hstack([training_matrix, children_stacked])
        else:
            all_features_stacked = children_stacked
        self.out("Stacked children together:", children_stacked.shape)
    elif training_matrix is not None:
        # If no children...
        all_features_stacked = training_matrix

    # Stack the label children as a single numpy matrix (horizontally)
    if len(all_label_children)>0:
        self.out("Stacking all_label_children:", len(all_label_children), all_label_children)
        all_labels_stacked = None
        if labels_array is not None:
            all_labels_stacked = labels_array
        for one_label_child in all_label_children:
            if all_labels_stacked is None:
                all_labels_stacked = one_label_child
            elif sp.issparse(one_label_child):
                if sp.issparse(all_labels_stacked):
                    all_labels_stacked = sp.hstack([all_labels_stacked, one_label_child])
                else:
                    all_labels_stacked = np.hstack([all_labels_stacked, one_label_child.todense()])
            else:
                all_labels_stacked = np.hstack([all_labels_stacked, one_label_child])
        self.out("...Stacking label_children_stacked:", all_labels_stacked.shape, type(all_labels_stacked))
        #self.out("...with labels_array:", labels_array.shape if labels_array is not None else 'NONE')
        #all_labels_stacked = np.hstack([labels_array, label_children_stacked]) if labels_array is not None else label_children_stacked
        #self.out("...result:", all_labels_stacked.shape)
        all_label_columns = (label_cols or []) + all_label_columns
    else:
        all_labels_stacked = labels_array
        all_label_columns = label_cols or []

    # Stack the base feature data too (mind the resulting data type)
    all_feature_columns = feature_cols + all_child_columns
    self.out("All features:", all_features_stacked.shape)
    self.out("Have {} total columns: {}".format(len(all_feature_columns), all_feature_columns))
    self.out("Memory:", asizeof(all_features_stacked))

    # Store the IDs column as the parent FeatureSet
    self.addData(output_features, ids_df, variant=variant, child=None)

    # Create a FeatureMatrix to be the child and store that too
    feature_matrix = FeatureMatrix(label=matrix_label,
                                     parent_label=output_features,
                                     matrix=all_features_stacked, 
                                     columns=all_feature_columns)
    self.addData(output_features, feature_matrix, variant=variant, child=matrix_label)

    # If creating labels too, add that as another child
    if all_label_columns is not None and all_labels_stacked is not None:
        print(label_child, all_labels_stacked.__class__.__name__,
              output_features, all_labels_stacked.shape, len(all_label_columns))
        labels_matrix = FeatureMatrix(label=label_child,
                                     parent_label=output_features,
                                     matrix=all_labels_stacked, 
                                     columns=all_label_columns)
        self.out("Adding labels matrix '{}': {}".format(label_child, all_labels_stacked.shape))
        self.addData(output_features, labels_matrix, variant=variant, child=label_child)

    # Also can normalize the features
    if normalize is not None and norm_label is not None:
        self.out("Normalizing with '{}' and output label '{}'".format(normalize, norm_label))
        all_features_norm = None
        if normalize=='max':
            maxes = all_features_stacked.max(axis=0).todense()
            if matrix_type=='sparse':
                #norms = sp.csr_matrix(np.maximum(maxes, 1.0))
                norms = np.maximum(maxes, 1.0)
                # Use sparse diags instead of numpy diag to reduce memory footprint for large feature matrices
                norms_diag = sp.csr_matrix(sp.diags(np.array((1./norms).T).flatten(), 0), dtype=np.float32)
                #norms_diag = sp.csr_matrix(np.diag(np.array((1./norms).T).flatten()))
                all_features_norm = (all_features_stacked * norms_diag).astype(np.float32)
            else:
                norms = np.maximum(maxes, 1.0)
                all_features_norm = all_features_stacked/norms
            num_dims = norms.shape[1]
        elif normalize=='min_max':
            maxes = all_features_stacked.max(axis=0).maximum(0).todense()
            if matrix_type=='sparse':
                #norms = sp.csr_matrix(np.maximum(maxes, 1.0))
                norms = np.maximum(maxes, 1.0)
                # Use sparse diags instead of numpy diag to reduce memory footprint for large feature matrices
                norms_diag = sp.csr_matrix(sp.diags(np.array((1./norms).T).flatten(), 0), dtype=np.float32)
                #norms_diag = sp.csr_matrix(np.diag(np.array((1./norms).T).flatten()))
                all_features_norm = (all_features_stacked.maximum(0.0) * norms_diag).astype(np.float32)
            else:
                norms = np.maximum(maxes, 1.0)
                all_features_norm = np.maximum(all_features_stacked, 0.0)/norms
            num_dims = norms.shape[1]

        if all_features_norm is not None:
            norm_matrix = FeatureMatrix(label=norm_label,
                                        parent_label=output_features,
                                        matrix=all_features_norm,
                                        columns=all_feature_columns,
                                        mappings=feature_matrix.getMappings())
            self.addData(output_features, norm_matrix, variant=variant, child=norm_label)

    self.view(output_features, 'shape')

#############################################################################################
def update(self, output_label, into_label, from_label, index_vars, *args, upsert=False, **kwargs): 
    # Get index vars in common between the "from" and "into" featuresets
    if isinstance(index_vars, str):
        index_vars = [index_vars]
    self.subset(f"{into_label}[[TEMP_update_indexvarsonly]]", into_label, *args, cols_list=index_vars, 
                save_to_disk=False, **kwargs)
    self.subset(f"{from_label}[[TEMP_update_indexvarsonly]]", from_label, *args, cols_list=index_vars, 
                save_to_disk=False, **kwargs)
    self.merge(f"{into_label}_{from_label}[[TEMP_update_indexvars_overlap]]",
               [f"{into_label}[[TEMP_update_indexvarsonly]]",
                f"{from_label}[[TEMP_update_indexvarsonly]]"],
               index_vars, *args,
               join='inner',
               save_to_disk=False, **kwargs)

    # Left outer join to take out rows in the "into" featureset with those index vars
    self.merge(f"{into_label}[[TEMP_update_not_in_{from_label}]]",
               [into_label,
                f"{into_label}_{from_label}[[TEMP_update_indexvars_overlap]]"],
               index_vars, *args,
               join='left outer',
               save_to_disk=False, **kwargs)

    if upsert:
        # Concatenate that with the "from" featureset to get the combination of update + insert 
        self.concat(output_label, 
                    [f"{into_label}[[TEMP_update_not_in_{from_label}]]",
                     from_label],
                    *args,
                    axis=0, **kwargs)
    else:
        # Inner join to get the rows in the "from" featureset that overlap
        self.merge(f"{from_label}[[TEMP_update_overlap_with_{into_label}]]",
                   [from_label,
                    f"{into_label}_{from_label}[[TEMP_update_indexvars_overlap]]"],
                   index_vars, *args,
                   join='inner',
                   save_to_disk=False, **kwargs)

        # Concatenate those two sets vertically
        self.concat(output_label, 
                    [f"{into_label}[[TEMP_update_not_in_{from_label}]]",
                     f"{from_label}[[TEMP_update_overlap_with_{into_label}]]"],
                    *args,
                    axis=0, **kwargs)


#############################################################################################
def upsert(self, output_label, into_label, from_label, index_vars, *args, **kwargs):
    self.update(output_label, into_label, from_label, index_vars, *args, upsert=True, **kwargs)
    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Use this to have consistent mapping to an index column name
def _get_index_col(label):
    if isinstance(label, str):
        return 'IX::{}'.format(label)
    elif isinstance(label, list):
        return 'IX::{}'.format('::'.join(label))

