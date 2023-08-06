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
#def updateLastUpdated(self):
#    self.last_updated = datetime.datetime.now()
    # Add the given FeatureView object to this FeatureSpace and save to disk
def addView(self, label, view, type='chart', **kwargs):

    # Reload the FeatureSpace first to make sure we reload the latest files
    self.out("Reloading the FeatureSpace...")
    self._loadFeatureSetMetadata()

    self.out("\nCalling addView({}, view_type={}, kwargs={})".format(label, type, kwargs))
    batch = kwargs.get('batch', self.default_batch)
    print("...batch:", batch)
    variant = kwargs.get('variant', self.default_variant)
    child = kwargs.get('child', None)
    if view is not None:
        # Need to attach the given View this FS
        view.batch = batch
        view.label = label
        view.save_directory = self.base_directory
        view.project_label = self.project_label
        view.space = self
        view.child = child
        view.variant = variant

        if type=='chart':
            # Save the new FeatureSet/FeatureModel into the FeatureSpace    
            self._addFeatureSet(label, view, batch=batch)

            # Add the given dataset(s) to the right FeatureSet/FeatureModel as the given child
            add_data_kwargs = copy.deepcopy(kwargs)
            add_data_kwargs.pop('child', None)
            add_data_kwargs.pop('variant', None)

            self.out("Calling _loadDataIntoMemory for FeatureData '{}' with variant={}, child={}, kwargs={}".format(label, variant, child, add_data_kwargs))
            view._loadDataIntoMemory(view.plot, variant=variant, child=child, **add_data_kwargs)   
            self.out("...done with _loadDataIntoMemory")

            # Update the last_updated timestamp for the featureset (by assuming this is an "editing" step)
            view._updateLastUpdated()

            view.save(variant=variant, file_prefix='view', filetype='png')
            self.out("...in fs.addView just executed view.save() and new filepath is:", view.last_save_filepaths)


#############################################################################################
# Set reset=True if you want to clear out all data/children before adding data (if this is a FeatureSet in memory)
# This is a "write" operation that changes the FeatureSet on disk and updates the last_updated timestamps
# TODO: Enable addData for a FeatureMatrix type too, including creating that FeatureMatrix object here
# TODO: Change forced_types to be data_types instead to be consistent with _transform()
def addData(self, label, data=None, datatype='dataframe', index_cols=None, feature_cols=None, label_cols=None, reset_data=False, save_to_disk=True, filetype=None, view_output=True, **kwargs):
    self.out("\nCalling addData({}, data={}, datatype={}, index_cols={}, feature_cols={}, label_cols={}, reset_data={}, save_to_disk={}, filetype={}, kwargs={})".format(label, type(data), datatype, index_cols, feature_cols, label_cols, reset_data, save_to_disk, filetype, kwargs))

    batch = kwargs.get('batch', self.default_batch)
    variant = kwargs.get('variant', self.default_variant)
    child = kwargs.get('child', None)
    forced_types = kwargs.get('forced_types', None) # Store forced column data types
    inferred_types = kwargs.get('inferred_types', None) # Store forced column data types
    self.out("...received forced types: {}".format(forced_types))
    overwrite = kwargs.get('overwrite', False)

    # Note on 10/27/21: Going to enforce against variant='*' here, it shouldn't happen since it's meaningless
    if variant=='*':
        self.out("ERROR: Cannot pass variant='*' into addData. Exiting.", type='error')
        raise

    reload = False # hard-code as False because do not need to reload a data set from file here, since we're adding it
    self.out("...using batch={}, variant={}, child={}, overwrite={}, reload={}".format(batch, variant, child, overwrite, reload))
    num_rows = None
    num_cols = None
    if isinstance(data, pd.DataFrame):
        self.out("Data is a pandas dataframe...")

        # Check all the columns for certain datatypes we know will fail to save to parquet format
        #print("data column data types: ", data.dtypes)
        (num_rows, num_cols) = data.shape

        # Check to make sure there are not duplicate columns
        # For now throw an error if so, because to support this requires changes throughout FS
        data_cols = list(data.columns)
        for col in data_cols:
            if data_cols.count(col)>1:
                self.out("ERROR: There are duplicates of column '{}' being added to {}.  FeatureSpace cannot support this.".format(col, label),
                         type='error')
                raise

        # Convert this into a dask dataframe before storing
        # Important change on 5/6/19: Don't convert everything to Dask anymore
        ###data = dd.from_pandas(data, sort=False, chunksize=self._DEFAULT_CHUNK_SIZE) #npartitions=5, 
    elif isinstance(data, np.ndarray):
        #print("Data is a numpy array, so converting it to dask dataframe")
        self.out("Data is a numpy array...")
        (num_rows, num_cols) = data.shape
        # Important change on 5/6/19: Don't convert everything to Dask anymore
        ###data = dd.from_array(data, chunksize=self._DEFAULT_CHUNK_SIZE)



    # If we do not already have this FeatureSet in memory, create a new one
    # Or if overwrite=True then we need to create a fresh FeatureSet/FeatureModel
    if label not in self.feature_sets or self.feature_sets[label] is None or batch not in self.feature_sets[label]:
        if datatype=='dataframe':
            self.out("Creating new FeatureSet '{}' with batch '{}', variant '{}'".format(label, batch, variant), 
                     type='debug')
            new_featureset = FeatureSet(save_directory=self.base_directory, label=label, project=self.project_label, 
                                        batch=batch, space=self)
        elif datatype=='model':
            self.out("Creating new FeatureModel '{}' for batch '{}', variant '{}'".format(label, batch, variant), 
                    type='debug')
            new_featureset = FeatureModel(save_directory=self.base_directory, label=label, project=self.project_label, 
                                          batch=batch, space=self)
        elif datatype=='view':
            self.out("Creating new FeatureView '{}' for batch '{}', variant '{}'".format(label, batch, variant),
                     type='debug')
            # Create a new FeatureView with the given 'data' string as the label of the data FeatureSet
            data_featureset_child = kwargs.get('data_child', None)
            data_featureset_variant = kwargs.get('data_variant', None)                
            new_featureset = FeatureView(save_directory=self.base_directory, label=label, project=self.project_label, 
                                         batch=batch, space=self, 
                                         data_featureset=label, 
                                         data_child=data_featureset_child, 
                                         data_variant=data_featureset_variant)

            # Overwrite the 'data' var with the corresponding dataframe
            #data = self.Data(data, child=data_featureset_child, variant=data_featureset_variant)

        else:
            self.out("ERROR: Unknown feature datatype '{}', cannot proceed with addData()".format(datatype),
                    type='error')
            return None

        # Save the new FeatureSet/FeatureModel into the FeatureSpace 
        self.out("...calling addFeatureSet on label='{}' with new_featureset={} and batch={}".format(label, new_featureset, batch))
        self._addFeatureSet(label, new_featureset, batch=batch)

        output_message = "Created new"

        #new_featureset.addData(data, variant=variant)
#             if datatype=='dataframe':
#                 logging.info("Created new FeatureSet '{}', batch='{}', variant={} with shape={}".format(label, batch, "'"+variant+"'" if variant is not None else 'None', new_featureset.shape(variant)))
#             elif datatype=='model':
#                 logging.info("Created new FeatureModel '{}', batch='{}', variant={}".format(label, batch, "'"+variant+"'" if variant is not None else 'None'))
    else:
        # Do not reload the FeatureSet because we're going to add a new dataset here
        new_featureset = self.Features(label, reload=False, batch=batch, variant=variant)
        new_featureset_datatype = new_featureset.datatype

        # If reset_data=True and this is a dataframe --> clear out the data for all children before adding new data
        if reset_data:
            self.out("Resetting all child datasets in FeatureSet '{}'".format(label))
            new_featureset._deleteData(variant=variant, child='*')

        # Check to make sure the types match...for now don't stop, just issue warning
        if new_featureset_datatype != datatype and child is None:
            # Only throw this warning if this is attempting to modify the parent
            # TODO: Allow changing to a new datatype
            self.out("WARNING! The datatype of the input data to addData('{}'...) is {}, but the current FeatureData is datatype {}".format(label, datatype, new_featureset_datatype),
                    type='warning')

        output_message = "Adding data to existing"

    # Add the given dataset(s) to the right FeatureSet/FeatureModel as the given child
    add_data_kwargs = copy.deepcopy(kwargs)
    add_data_kwargs.pop('child', None)
    add_data_kwargs.pop('variant', None)

    self.out("Calling _loadDataIntoMemory for FeatureData '{}' with variant={}, child={}, kwargs={}".format(label, variant, child, add_data_kwargs))
    new_featureset._loadDataIntoMemory(data, variant=variant, child=child, **add_data_kwargs)   
    self.out("...done with _loadDataIntoMemory")

    # Update the last_updated timestamp for the featureset (by assuming this is an "editing" step)
    new_featureset._updateLastUpdated()

    # If provided, add new feature/index/label cols to the new FeatureSet
    #new_featureset.setColumnTypes(index_cols=index_cols, feature_cols=feature_cols, label_cols=label_cols, child=child)
    # Need to pass child='*' to make sure all children's columns are considered
    # New on 10/15/19: Append generic column types
    self.out("...setting forced types: {}".format(forced_types), type='debug')
    self.out("...setting inferred_types: {}".format(inferred_types), type='debug')
    if datatype=='dataframe':
        if index_cols or feature_cols or label_cols or forced_types or inferred_types:
            if forced_types is not None and '*' in forced_types:
                types_to_force = inferred_types
            else:
                types_to_force = forced_types
            new_featureset._addColumnTypes(variant=variant, child='*', 
                                           index_cols=index_cols, feature_cols=feature_cols, label_cols=label_cols,
                                           forced_types=types_to_force, # New 11/16/20
                                           inferred_types=inferred_types)
            if index_cols or feature_cols or label_cols:
                self.out("...then new feature set column types: index_cols={}, feature_cols={}, label_cols={}".format(len(new_featureset.index_cols), len(new_featureset.feature_cols), len(new_featureset.label_cols)))


    # Save a copy of the entire feature set to file if flagged
    #if save_to_disk:
    # Save the entire FeatureSet including all children

    # Save *all* the children to file, even though only one changed here
    save_kwargs = {} if datatype=='model' or datatype=='view' else {'schema_changed': True}
    new_featureset.save(overwrite=overwrite or self.disk_mode=='low', # Overwrite the previous copy on disk
                        variant=variant, child='*', 
                        save_to_disk=save_to_disk, filetype=filetype, # col_types=types,
                        **save_kwargs)
    self.out("...in fs.addData just executed new_featureset.save() and new filepath is:", new_featureset.last_save_filepaths)
    #self.out("...types just saved:", new_featureset.types)
    # Also save the updated copy of this featurespace to file
    #self.save()

    if datatype=='dataframe':
        self.out("...types just saved:", new_featureset.types)
        new_shape = new_featureset.shape(variant=variant, child='*')
        new_shape_one_variant_child = new_featureset._getDatasetShape(variant=variant, child=child)
        self.out("...got new shape for variant={}: {}".format(variant, new_shape))
        logging.info("{} FeatureSet '{}' with batch='{}', variant={}, child={} (shape:{})...new shape of FeatureSet is {}".format(output_message, label, batch, "'"+variant+"'" if variant is not None else 'None', child, new_shape_one_variant_child, new_shape))
        if view_output:
            self.view(label)
    elif datatype=='model':
        logging.info("{} FeatureModel '{}' with batch='{}', variant={}, child={}".format(output_message, label, batch, "'"+variant+"'" if variant is not None else 'None', child))   
    elif datatype=='view':
        logging.info("{} FeatureView '{}' with batch='{}', variant={}, child={}".format(output_message, label, batch, "'"+variant+"'" if variant is not None else 'None', child))   


    #self.updateLastUpdated() # Moved inside updateFeatureSetList()
    #self._updateFeatureSetMetadata(label) # Commented out on 2/1/2021 -- this is duplicative of call within FeatureSet.save()

    return new_featureset


#############################################################################################
# 10/20/2021: Nothing is calling this, so commenting it out (will delete later)
#     def _saveFeatureSet(self, label, filename, **kwargs):
#         # TODO: Look into why filename is ignored below but included in the parameter list
#         self.out("In _saveFeatureSet({})".format(label))
#         batch = kwargs.get('batch', self.default_batch)
#         variant = kwargs.get('variant', self.default_variant)
#         filetype = kwargs.get('filetype', None) # Don't set the filetype here, let the underlying FeatureSet do that
#         if label in self.feature_sets and self.feature_sets[label] is not None:
#             if batch in self.feature_sets[label] and self.feature_sets[label][batch] is not None:
#                 self.feature_sets[label][batch].save(variant=variant, filetype=filetype, schema_changed=False)
    #self.feature_sets[label].df.to_csv(os.path.join(self._getSaveDirectory(), filename), index=False)



#############################################################################################
# Stores the given feature_set object in memory
def _addFeatureSet(self, label, feature_set, batch=None):
    batch = batch if batch is not None else self.default_batch
    if label not in self.feature_sets:
        self.feature_sets[label] = {}
    self.feature_sets[label][batch] = feature_set
    # 10/20/2021 William turns 10! Taking this out since storing the featureset in memory shouldn't also overwrite
    # the FS metadata, since we're now supporting "temporary" loading of featuresets when filename is passed in
    ##self._updateFeatureSetMetadata(label) # Altered on 1/3/21 to only affect one featureset's metadata at a time


#############################################################################################
# Create constants to be accessible throughout the FeatureSpace pipeline
# Can take: addConstant('hello world') or addConstant('blah', key='blue')
# Note: Only can store strings.  Other types will get converted to strings when saving these constants.
def addConstant(self, key=None, constant=None):
    if key=='*':
        self.out("WARNING: Cannot use key='*' since it's a stored keyword to refer to all constants.", type='warning')
        return None
    if not hasattr(self, 'constants'):
        self.constants = {}
    self.constants[key] = constant
    print("Stored constant {} with key='{}' and resaved metadata.".format(constant, key))
    self.save()
    return
