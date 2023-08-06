import numpy as np
import pandas as pd
import dask.dataframe as dd
import dill
from scipy.sparse import coo_matrix, save_npz, load_npz
import os
import matplotlib.pyplot as plt

from dsphere.FeatureSpace.feature_structures.feature_data import FeatureData
from dsphere.FeatureSpace.feature_structures.feature_set import FeatureSet


class FeatureView(FeatureData):
    __feature_type__ = 'FeatureView'

    def __init__(self, save_directory=None, label=None, project=None, batch=None, space=None,
                        data_featureset=None, data_child=None, data_variant=None, datatype='view',
                        parameters=None):
        FeatureData.__init__(self, save_directory=save_directory, label=label, project=project, batch=batch, 
                             datatype=datatype, space=space)
        self.data_featureset = data_featureset
        self.data_featureset_child = data_child
        self.data_featureset_variant = data_variant
        
        # Keep a list of parameters with their default values (if missing) that can be used to dynamically generate a view
        self.parameters = {} if parameters is None else parameters

    def _getDefinition(self, print_out=False):
        definition = super()._getDefinition(print_out=print_out)
        definition['data_featureset'] = self.data_featureset
        definition['data_featureset_child'] = self.data_featureset_child
        definition['data_featureset_variant'] = self.data_featureset_variant
        return definition
        
    def _setDefinition(self, status_dict):
        super()._setDefinition(status_dict=status_dict)
        self.data_featureset = status_dict['data_featureset']
        self.data_featureset_child = status_dict['data_featureset_child']
        self.data_featureset_variant = status_dict['data_featureset_variant']

    def _getDatatype(self):
        return "FeatureView"
    
    def save(self, variant=None, file_prefix='view', filetype='png'):
        super().save(variant=variant, file_prefix=file_prefix, filetype=filetype)

    def _getMetadata(self, variant=None):
        metadata = super()._getMetadata(variant=variant)
        metadata['data_featureset'] = self.data_featureset
        metadata['data_featureset_child'] = self.data_featureset_child
        metadata['data_featureset_variant'] = self.data_featureset_variant
        return metadata
    
    def _setParameters(self, parameters):
        self.parameters = parameters