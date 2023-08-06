
def _GetModeler(DataStream=None, **kwargs):
    if 'TYPE' in kwargs:
        type_lower = kwargs['TYPE'].lower()
    elif 'type' in kwargs:
        type_lower = kwargs['type'].lower()
    else:
        print("ERROR: Cannot create Modeler with parameters {} since TYPE is not defined".format(kwargs))
        return None
    
    if type_lower=='predict':
        print("Created predict modeler...")
        return Prediction_Modeler(DataStream=DataStream, type=type_lower, **kwargs)
    #elif type_lower=='retrain':
    #    print("Created retrain modeler...")
    #    return Retrain_Modeler(DataStream=DataStream, type=type_lower, **kwargs)
    
##############################
### Parent Modeler class ###
class Modeler:
    modeler_params = None
    DataStream = None
    type = None # type can be 'predict'
    
    def __init__(self, DataStream=None, type=None, required=None, **kwargs):
        #self.featurespace = parameters.get('featurespace', None)
        #self.parameters = parameters
        self.DataStream = DataStream
        self.type = type
        print(kwargs)
        self.modeler_params = kwargs
        
        # If provided a list of required parameters, then confirm that each one is defined
        if required is not None:
            for param in required:
                if param not in self.modeler_params:
                    print("ERROR: Required parameter {} has not been defined for this modeler of type {}".format(param, 
                                                                                                                 type))
                    raise
        return None
        
    def predict(self):
        return None

    def train(self):
        return None
    
    def retrain(self):
        return None

    def test(self):
        return None

    def tune(self):
        return None

    def summary(self):
        return None

#######################################
### tensorflow/keras modeler ###
class Prediction_Modeler(Modeler):
    required_params = ['model',
                       'features']
    model_featureset = None
    features_featureset = None
    features_var = None
    features_child = None
    index_cols = None
    index_child = None
    label_cols = None
    labels_child = None
    predictions_featureset = None
    predictions_var = None
    predictions_child = None
    from tensorflow.keras.layers import Bidirectional, Concatenate, Permute, Dot, Input, LSTM, Multiply, Layer
    from tensorflow.keras.layers import RepeatVector, Dense, Activation, Lambda
    from tensorflow.keras.optimizers import Adam
    # from keras.utils import to_categorical
    from tensorflow.keras.models import load_model, Model, Sequential
    import tensorflow.keras.backend as K
    from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np

    def __init__(self, DataStream=None, type=None, **kwargs):
        Modeler.__init__(self, DataStream=DataStream, type=type, required=self.required_params, **kwargs)

#         {'TYPE': 'predict',
#          'predictions': {'featureset': 'final_predictions_after_training_nn',
#                            'var': 'training+past',
#                            'child': None},
#          'model': {'featureset': 'trained_nn_model_alldonors', 'type': 'tensorflow'},
#          'features': {'featureset': 'final_feature_matrix',
#                        'var': 'training+past',
#                        'child': 'feature_matrix_norm',
#                        'index_child': None,
#                        'index_cols': ['guarantor_mrn_list'],
#                        'label_cols': ['is_donor_future',
#                                        'is_large_donor_future',
#                                        'is_donor_6_months_future']}}
        
        # Get the ML model
        model = self.modeler_params.get('model', None)
        if model is not None:
            self.model_featureset = model.get('featureset', None)
            self.model_variant = model.get('variant', None)
            self.model_child = model.get('child', None)
            self.model_type = model.get('type', None) #'tensorflow'
            
        # Get the input features to use
        features = self.modeler_params.get('features', None)
        if features is not None:
            self.features_featureset = features.get('featureset', None)
            self.features_var = features.get('var', None)
            self.features_child = features.get('child', None)
            self.index_cols = features.get('index_cols', None)
            self.index_child = features.get('index_child', None)
            self.label_cols = features.get('label_cols', None)
            self.labels_child = features.get('labels_child', None)           
            
        # Get the output predictions to create
        predictions = self.modeler_params.get('predictions', None)
        if predictions is not None:
            self.predictions_featureset = predictions.get('featureset', None)
            self.predictions_var = predictions.get('var', None) # Not used for now
            self.predictions_child = predictions.get('child', None) # Not used for now
                    
    def predict(self):
        super().predict()
        #print(self.featurespace)
        
        # TODO: Look up the label_cols inside the given model...or let predict() figure it out
        print("Running predict() with parameters:", self.modeler_params)
        probability_vars = ['probability_'+var for var in self.label_cols]
        class_vars = ['class_'+var for var in self.label_cols]
        self.DataStream.FeatureSpace.predict(self.predictions_featureset, 
                                   self.model_featureset, 
                                   self.features_featureset,
                                   variant=self.features_var, child=self.features_child, 
                                   index_vars=self.index_cols, index_child=self.index_child,
                                   class_vars=class_vars,
                                   regression_vars=probability_vars
                                  )
        
    def train(self):
        super().train()
#     def train(self, model_label, model, 
#                    training_data, 
#                    training_cols,
#                    actuals_label, actuals_vars,
#                    training_function=None,
#                    loss_function=None,
#                    percent_training=None,
#                    norm=None,
#                    **kwargs):


        
        # TODO: Look up the label_cols inside the given model...or let predict() figure it out
        print("Running predict() with parameters:", self.modeler_params)
        probability_vars = ['probability_'+var for var in self.label_cols]
        class_vars = ['class_'+var for var in self.label_cols]
        self.DataStream.FeatureSpace.train(self.model_featureset,
                                self.predictions_featureset, 
                                   self.model_featureset, 
                                   self.features_featureset,
                                   variant=self.features_var, child=self.features_child, 
                                   index_vars=self.index_cols, index_child=self.index_child,
                                   class_vars=class_vars,
                                   regression_vars=probability_vars
                                  )
        
    def retrain(self):
        super().retrain()
        
        
        #features_fs = self.features_featureset #'final_feature_matrix' #'final_feature_data_norm_training'
        #features_child = self.features_child #'feature_matrix_norm' # 'normalized_features'
        feature_matrix = self.DataStream.FeatureSpace.Data(self.features_featureset, variant=self.features_var, child=self.features_child)
        X = feature_matrix.getMatrix().tocsr() #.todense().astype(np.float16)
        X_cols = feature_matrix.columns() #all_feature_cols

        #Y = labels_array.values
        import numpy as np
        Y_matrix = self.DataStream.FeatureSpace.Data(self.features_featureset, variant=self.features_var, child=self.labels_child)
        Y = np.nan_to_num(Y_matrix.getMatrix())#[:,0]).reshape(-1,1)
        Y_label_cols = Y_matrix.columns()

        print("Data set shape:")
        print(X.shape)
        print(Y.shape)
        print(len(X_cols))

        num_rows = X.shape[0]
        num_positives = np.count_nonzero(Y, axis=0)
        print("Data set num positives:\n" + str(num_positives) + "\n{}%".format(num_positives/num_rows*100.))
        print(Y_label_cols)
                               
                               
        # Seed the random number generator
        np.random.seed(3091)




        all_results = None

        
#         # Choose the hyperparameters of the model(s) to train
#         nodes_layer1 = 64  # Was 150 for May 2019
#         nodes_layer2 = 48   # Was 50 for May 2019
#         num_input_dimensions = X.shape[1]
        num_epochs = 20
        batch_size = 10000
#         k = 100
#         num_batches = (np.floor(X.shape[0]/batch_size)+1).astype(int)
#         print("Can use {} batches of size {} on {} rows".format(num_batches, batch_size, X.shape[0]))
#         num_labels = Y.shape[1]

#         # Train a new NN model

#         # create model
#         nn_model = Sequential()
#         nn_model.add(Dense(nodes_layer1, input_dim=num_input_dimensions, activation='relu'))
#         if nodes_layer2 is not None:
#             nn_model.add(Dense(nodes_layer2, activation='relu'))
#         nn_model.add(Dense(num_labels, activation='sigmoid'))

        # Retrain using the same model / hyperparameters trained before
        nn_model = self.DataStream.FeatureSpace.Data(self.model_featureset, 
                                                     variant=self.model_variant, child=self.model_child)
        nn_model_featureset = self.DataStream.FeatureSpace.Features(self.model_featureset, 
                                                     variant=self.model_variant, child=self.model_child)
                               
        # Compile model
        nn_model.compile(loss=nn_model_featureset.loss_function, optimizer='adam', metrics=['accuracy'])


        # # Fit the model
        # history = nn_model.fit(X, Y, epochs=num_epochs, batch_size=batch_size)
        print(nn_model.summary())

        # Need this to be able to call .fit on a CSR sparse matrix as the input featureset
        X_training.sort_indices()
        # from IPython.display import clear_output
        # all_losses = []
        # import gc
        # all_accuracy = []
#         num_epochs = 20

        #!free
        history = nn_model.fit(X_training, 
                               Y_training.astype(np.float32), 
                               epochs=num_epochs, batch_size=batch_size, verbose=1, shuffle=True)

        all_losses = history.history['loss']
        all_accuracy = history.history['accuracy']
        print(nn_loss_function)
        plt.plot(all_losses)
        plt.plot(all_accuracy)

        trained_nn_model = self.DataStream.FeatureSpace.addData(self.model_featureset, 
                                                                nn_model, datatype='model', 
                                                                training_cols=X_cols, 
                                                                loss_function=nn_model.loss_function, 
                                                                model_type='keras') ## need to specify 'keras' to store the loss_function with the model

    def _create_model(self, model_type='tensorflow', parameters=None):
        # Create an empty model instance with the given parameters
        print("test")
    
    def summary(self):
        super().summary()
        