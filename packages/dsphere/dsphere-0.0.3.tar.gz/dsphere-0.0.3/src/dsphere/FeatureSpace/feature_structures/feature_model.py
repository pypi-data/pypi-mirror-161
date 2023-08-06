import pandas as pd
import numpy
import datetime
import dill
import os
import tensorflow.keras.models as k
#from tensorflow.keras.models import load_model, Model, Sequential
#import keras
#from keras.models import load_model, Model, Sequential

from dsphere.FeatureSpace.feature_structures.feature_data import FeatureData

class FeatureModel(FeatureData):
    __feature_type__ = 'FeatureModel'
            
    def __init__(self, save_directory=None, label=None, project=None, batch=None, variant=None, space=None):
        print("project: ", project)
        FeatureData.__init__(self, save_directory=save_directory, label=label, project=project, batch=batch, datatype='model', space=space)
        print(self.project_label)
        #self.model = None  # Obviated since the model is stored as "data" in the parent FeatureData object
        self.model_type = None
        self.model_file = None
        self.training_function = None
        self.loss_function = None
        self.prediction_function = None
        self.features = None # featureset containing the features input matrix
        self.feature_cols = '*' # default '*' = all cols in the features child
        self.features_child = None
        self.features_var = None
        self.label_cols = []
        self.labels_child = None
        self.index_cols = '*' # default '*' = all cols in the index_child
        self.index_child = None
    
    def _getDefinition(self, print_out=False):
        definition = super()._getDefinition(print_out=print_out)
        #definition['model'] = self.model
        definition['model_type'] = self.model_type
        definition['model_file'] = self.model_file
        definition['training_function'] = self.training_function
        definition['loss_function'] = self.loss_function
        definition['prediction_function'] = self.prediction_function
        definition['training_cols'] = list(self.feature_cols or [])
        definition['label_cols'] = list(self.label_cols or [])

        return definition
    
    def _setDefinition(self, status_dict):
        super()._setDefinition(status_dict=status_dict)
        #self.model = status_dict['model']
        self.model_type = status_dict.get('model_type', None)
        self.model_file = status_dict.get('model_file', None)
        self.feature_cols = status_dict.get('columns', status_dict.get('training_cols', [])) # support migration of keyword
        self.label_cols = status_dict.get('labels', status_dict.get('label_cols', [])) # support migration of keyword
        self.training_function = status_dict.get('training_function', None)
        self.loss_function = status_dict.get('loss_function', None)
        self.prediction_function = status_dict.get('prediction_function', None)
    
    def _getDatatype(self):
        return "ML Model ({})".format(self.model_type)

#     def setTrainingColumns(self, new_training_cols):
#         self.feature_cols = list(new_training_cols)
        
#     def setLabelColumns(self, new_label_cols):
#         self.label_cols = list(new_label_cols)
        
#     def setLossFunction(self, new_loss_function):
#         self.loss_function = new_loss_function
        
#     def setTrainingFunction(self, new_training_function):
#         self.training_function = new_training_function
        
#     def setPredictionFunction(self, new_prediction_function):
#         self.prediction_function = new_prediction_function
        
    # TODO: Enable saving multiple or all variants per feature set at once, in the same directory, using '*' or a list 
    # To free-up space, one can set overwrite=True and have this file replace the previous one
    # Note: child is a parameter here for compliance with FeatureSet.save(), but it is not used
    def save(self, variant=None, overwrite=False, child=None, save_to_disk=True, filetype='dill', col_types=None):
        """
        TESting
        """
        previous_filename = self.last_save_filenames[variant] if variant in self.last_save_filenames else None
        super().save(variant=variant, file_prefix='model', filetype=filetype)
        
        #filepath = self.getSaveDirectory(filename, variant=variant)
        if save_to_disk:
            filepath = self.last_save_filepaths[variant]
            if filepath is not None:
                # Currently only using 'dill' filetype
                # TODO: Enable saving a model using alternative filetypes passed-in here
                model_filename = 'model.h5' if self.model_type=='keras' else 'model.dll'
                model_path = os.path.join(filepath, model_filename)
                model_metadata_path = os.path.join(filepath, 'model_metadata.dll')
                model = self.getData(variant)
                if model is not None:
                    metadata = {'model_type':self.model_type,
                                'model_file':model_path,
                                'training_cols':list(self.feature_cols),
                                'label_cols':list(self.label_cols),
                                'training_function':self.training_function,
                                'loss_function':self.loss_function,
                                'prediction_function':self.prediction_function
                               }

                    print("Saving model (variant={}) of type '{}' inside folder: {}".format(variant, type(model), filepath))
                    with open(model_metadata_path, 'wb') as fout:
                        dill.dump(metadata, fout)
                    
                    # Save the model object itself
                    if self.model_type=='keras':
                        #keras.models.save_model(model, model_path)
                        k.save_model(model, model_path)
                    else:
                        with open(model_path, 'wb') as fout:
                            dill.dump(model, fout)
                    self.model_file = model_path

                # If overwrite=True, then delete the previous version of this featureset's file after saving the new one
                if overwrite and previous_filename is not None:
                    self._deleteFile(previous_filename)
              
        # Need to call this so the FeatureSpace updates its metadata file with the latest children created here
        #self.space.updateLastUpdated() # Moved inside updateFeatureSetList()
        self.space._updateFeatureSetMetadata()

    def delete(self):
        del((self.model, self.feature_cols, self.training_function, self.prediction_function))
        super().delete()
        
    #def loadFromFile(self, filename, variant=None, filetype=None):
    def _loadDataFromFile(self, filename, variant=None, filetype=None):
        filepath = self.getSaveDirectory(filename, variant=variant)
        if filepath is not None:        
            metadata_filepath = os.path.join(filepath, 'model_metadata.dll')
            print("Loading model metadata from file: {}".format(metadata_filepath))
            model_type = None
            model_filepath = None
            loss_function = None
            if os.path.exists(metadata_filepath):
                # Load the metadata here
                metadata = dill.load(open(metadata_filepath, 'rb'))
                model_type = metadata['model_type']
                model_filepath = metadata['model_file']
                self.feature_cols = list(metadata.get('columns', 
                                                      metadata.get('training_cols', 
                                                                              metadata.get('training_columns', []))))
                print("Model metadata contains values for:", metadata.keys())
                print("...found {} feature_cols".format(len(self.feature_cols)))
                #self.setTrainingColumns(training_cols)
                self.label_cols = list(metadata.get('labels', metadata.get('label_cols', []))) # support migration of keyword
                self.model_type = model_type
                self.loss_function = metadata.get('loss_function', None)
                #self.setLossFunction(loss_function)
                self.training_function = metadata.get('training_function', None)
                self.prediction_function = metadata.get('prediction_function', None)
                
            else:
                print("...no metadata found, will try 'model.dll' by default")
                # Try loading the model straight from 'model.dll' (for backwards compatibility as of 6/16/19)
                model_filepath = os.path.join(filepath, 'model.dll')
                
            if model_filepath is not None:
                print("...trying to load model straight from file: {}".format(model_filepath))
                if os.path.exists(model_filepath):
                    if model_type=='keras':
                        if self.loss_function is not None and not isinstance(self.loss_function, str):
                            loss_function_name = self.loss_function.__name__
                            print("...loading keras model using custom_objects = '{}':{}".format(loss_function_name, 
                                                                                                 self.loss_function))
                            #model = keras.models.load_model(model_filepath, custom_objects={loss_function_name: loss_function})
                            model = k.load_model(model_filepath, custom_objects={loss_function_name: self.loss_function})
                        else:
                            print("...loading keras model")
                            #model = keras.models.load_model(model_filepath)
                            model = k.load_model(model_filepath)
                        
                    else:
                        print("...loading model of unknown type")
                        model = dill.load(open(model_filepath, 'rb'))
            
                    self._loadDataIntoMemory(model, variant=variant)
            return True
                        
        else:
            print("ERROR: Cannot find file at {} to read into feature model {}".format(filepath, self.label))
            return False
            
    # External call to allow adding of new data into a FeatureSet
    # Mostly a wrapper around the internal call, but this is "editing" so should update the last_updated timestamp
    def addData(self, data, variant=None, child=None, **kwargs):
        self.out("Calling FeatureModel.addData(variant={}, child={}, kwargs={})".format(variant, child, kwargs))
        self._loadDataIntoMemory(data, variant=None, child=None, **kwargs)
        self._updateLastUpdated()
        
    #def addData(self, data, variant=None, child=None, **kwargs):
    def _loadDataIntoMemory(self, data, variant=None, child=None, **kwargs):
        print("In FeatureModel _loadDataIntoMemory(variant={}, child={})".format(variant, child))        
        super()._loadDataIntoMemory(data, variant=variant, child=child)
        
        # Set the model type
        if 'model_type' in kwargs:
            self.model_type = kwargs['model_type']
            print("Storing loss function for this model")
            
        # Set the training data cols
        if 'training_cols' in kwargs:
            self.feature_cols = list(kwargs['training_cols'])
            #self.setTrainingColumns(feature_cols)
            print("Setting training data cols to given list of {} cols".format(len(self.feature_cols)))
            
        # Set the training label cols
        if 'label_cols' in kwargs:
            #label_cols = kwargs['label_cols']
            self.label_cols = list(kwargs['label_cols'])
            #self.setLabelColumns(label_cols)
            print("Setting training label cols to given list of {} cols".format(len(self.label_cols)))
            
        # Set the loss function
        if 'loss_function' in kwargs:
            #self.setLossFunction(kwargs['loss_function'])
            self.loss_function = kwargs['loss_function']
            print("Storing loss function for this model")
            
        # Set the training function
        if 'training_function' in kwargs:
            #self.setTrainingFunction(kwargs['training_function'])
            self.training_function = kwargs['training_function']
            print("Storing training function for this model")

        # Set the prediction function
        if 'prediction_function' in kwargs:
            #self.setPredictionFunction(kwargs['prediction_function'])
            self.prediction_function = kwargs['prediction_function']
            print("Storing prediction function for this model")