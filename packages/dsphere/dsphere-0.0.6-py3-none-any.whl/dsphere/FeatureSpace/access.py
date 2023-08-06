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
import copy as cop
from filelock import FileLock
import io
import pgpy

#############################################################################################
def save(self):
    self.out("...in _save() for the FeatureSpace, with last_updated=", self.last_updated)
    # Create dict to store the latest definition of this featurespace
    dependency_chain = self._getDependencyChain(print_out=False)
    featurespace_definition = {'constants': self.constants,
                               'feature_sets': self.feature_set_metadata,
                               'flows': self.all_flows,
                               'chain': dependency_chain,
                               'last_update': self.last_updated,
                              }

    # Save the representation of this featurespace to a dill file
    #ofile = os.path.join(self.save_directory, self.filename)
    #print("Saving FeatureSpace to {}".format(self.filepath))
    #if not os.path.exists(self.filepath):
    #    os.mknod(self.filepath)

    # TODO: Catch errors thrown here when the file doesn't pickle successfully using try ... except ...

    # New on 5/24/20: Lock the metadata file while writing to it, to prevent scripts from writing to it simultaneously
    lock_name = self.filepath+".lock"
    with FileLock(lock_name, timeout=5) as lock:
        self.out("Lock acquired on FeatureSpace metadata file while writing to it...")
        with open(self.filepath, 'w') as fout:
            self.out("Saving FeatureSpace metadata as JSON")
            # Change on 5/2/19: Use JSON, not dill, since only text now and dill/pickle is too precarious
            json.dump(featurespace_definition, fout, sort_keys=False, indent=4, default=str)

    self.out("...done: {}".format(datetime.datetime.now()))


#############################################################################################
# Note: Currently this can only delete the entire FeatureSet *from memory*, not individual variants within it
# The underlying file copies remain in the metadata and file backups.
# batch=None --> delete the default batch for this labeled feature set
def delete(self, label, batch=None):
    batch = batch if batch is not None else self.default_batch
    self.out("Deleting FeatureSet '{}' with batch='{}'".format(label, batch))
    if label in self.feature_sets and self.feature_sets[label] is not None:
        if batch in self.feature_sets[label] and self.feature_sets[label][batch] is not None:
            self.feature_sets[label][batch].delete()
            del(self.feature_sets[label][batch])
            if len(self.feature_sets[label])==0:
                del(self.feature_sets[label])

            gc.collect()
        else:
            self.out("WARNING: Cannot find batch {} to delete for FeatureSet {}".format(batch, label),
                    type='warning')
    else:
        self.out("WARNING: Cannot find FeatureSet {} to delete".format(label),
                type='warning')


#############################################################################################
# TODO: Fix all calls to fs.copy() to use 'batch' instead of 'copy_batch', then push it through as **kwargs
# Note: Only works on the child=None
# Note: If you call copy() on one variant 'A' before another _transform() on another variant 'B' for the same FeatureSet,
#  then the resulting FeatureSet will contain both 'A' and 'B' variants
#  However if you call the _transform() before copy(), then you'll only end up with variant 'A'.
# TODO: Figure out why/how copy() is clearing out the variants, and stop it
# Can pass data_types to force them to a different col type -- does not support '*' yet though, and only works on parent
def copy(self, new_label, old_label, **kwargs):
    reload = kwargs.get('reload', self.default_reload)
    batch = kwargs.get('output_batch', self.default_batch)
    new_variant = kwargs.get('output_variant', None)
    kwargs.pop('output_variant', None)
    view_output = kwargs.get('view_output', True)
    copy_data_types = kwargs.get('data_types', None)
    kwargs.pop('data_types', None)
    children_to_copy = kwargs.get('child', '*')

    # Reload the FeatureSpace metadata first to make sure we reload the latest files
    self.out("Reloading the FeatureSpace...")
    self._loadFeatureSetMetadata()

    #output_variant = kwargs.get('output_variant', variant)
    #kwargs.pop('output_variant', None)

    old_variant = kwargs.get('variant', '*')
    old_batch = kwargs.get('batch', batch)
    kwargs.pop('variant', None)
    kwargs.pop('batch', None)

    # Get the previous data set
    old_kwargs = cop.deepcopy(kwargs)
    old_kwargs['batch'] = old_batch
    old_featureset = self.Features(old_label, **old_kwargs)

    if old_featureset is not None:
        #old_data = old_featureset.getData(old_variant)
        #print("old data:", old_data.keys())
        old_type = old_featureset.datatype
        old_col_types = old_featureset.types
        old_schemas = old_featureset.schemas
        old_shapes = old_featureset.dataset_shapes

        # Get the list of variants in the input set to copy
        if old_variant == '*':
            old_variant_list = cop.deepcopy(old_featureset.variants())
        elif old_variant is None:
            old_variant_list = [None]
        elif isinstance(old_variant, str):
            old_variant_list = [old_variant]
        else:
            old_variant_list = old_variant

        # Get the list of new variants to create
        if new_variant == '*' or new_variant is None:
            new_variant_list = old_variant_list
        elif isinstance(new_variant, str):
            if len(old_variant_list)>1:
                self.out("ERROR: Cannot copy {} old variants into 1 new variant. Exiting.".format(len(old_variant_list)),
                         type='error')
                return None
            new_variant_list = [new_variant]
        elif isinstance(new_variant, list):
            if len(old_variant_list) > len(new_variant):
                self.out("ERROR: Cannot copy {} old variants into {} new variants. Exiting.".format(len(old_variant_list), 
                                                                                                 len(new_variant)),
                        type='error')
                return None
            elif len(old_variant_list) < len(new_variant):
                if len(old_variant_list)>1:
                    self.out("ERROR: Cannot copy {} old variants into {} new variants. Exiting.".format(len(old_variant_list), len(new_variant)),
                            type='error')
                    return None

                elif len(old_variant_list)==1:
                    # Otherwise we can multiply one old variant into >1 new variants
                    one_old_variant = old_variant_list[0]

                    # Create copies of the old variant for each new one
                    old_variant_list = [one_old_variant for one_new_var in new_variant]
                    new_variant_list = new_variant
                else:
                    # Must have no variants
                    self.out("ERROR: Zero variants found to copy. Exiting", type='error')
                    return None
            else:
                new_variant_list = new_variant

        # After the above, we should have an equal number of variants in old_variant_list and new_variant_list

        # Keep a list of the output variants
#             if new_variant == '*' or old_variant == '*':
#                 old_variant_list = old_featureset.variants().copy()
#             elif new_variant is None:
#                 # Here we should output the same variant as the input variants
#                 old_variant_list = [old_variant] if isinstance(old_variant, str) else old_variant #[None]
#             elif isinstance(new_variant, str):
#                 old_variant_list = [variant]
#             else:
#                 old_variant_list = new_variant
        self.out("Will copy variant {} into variants {}".format(old_variant_list, new_variant_list))

        # Add the old data to a new feature set for each output variant
        for (new_variant,old_variant) in zip(new_variant_list, old_variant_list): 
            # do getData here
            kwargs['variant'] = new_variant
            old_data = old_featureset.getData(old_variant, child=children_to_copy)
            if not isinstance(old_data, dict):
                old_data = {old_featureset.children(variant=old_variant)[0]: old_data}

            old_data_children = list(old_data.keys())
            last_child = old_data_children[-1]
            for old_data_child in old_data:
                # Iterate through each child
                self.out("Copying data from old variant '{}' into new variant '{}' for child='{}'".format(old_variant, new_variant, old_data_child))
                kwargs['child'] = old_data_child
                kwargs['save_to_disk'] = False #(old_data_child==last_child) # Added 9/22/20: Only save the last child
                kwargs['view_output'] = False
                old_data_child_data = old_data[old_data_child]
                if copy_data_types is not None and old_data_child is None:
                    # Only can change the data types for the parent
                    kwargs['forced_types'] = copy_data_types
                    current_cols_to_exclude = [col for col in old_data_child_data.columns if col not in copy_data_types]
                    old_data_child_data, unified_types = FeatureSet._unifyDataTypes(old_data_child_data,  
                                                                          debug=(self.output_mode=='debug' or (self.dsphere is not None and self.dsphere.output_mode=='debug')),

                                                                          cols_to_exclude=current_cols_to_exclude,
                                                                          forced_types=copy_data_types)
                new_featureset = self.addData(new_label, old_data_child_data, datatype=old_type, **kwargs)

            # Copy the shapes of the old variant to the new variant
            if old_variant in old_shapes:
                new_featureset._setDatasetShape(cop.deepcopy(old_shapes[old_variant]),
                                                variant=new_variant,
                                                child='*')

        new_featureset.label = new_label
        self.out("New featureset has label: ", new_featureset.label, new_featureset.last_save_filenames)
        # Note: We should not reload the new feature set from file in this case

        # Make sure to change the new file's label / filename definition
        self.out(old_featureset._getDefinition())
        copy_definition = cop.deepcopy(old_featureset._getDefinition())
        copy_definition['label'] = new_label
        copy_definition['filenames'] = new_featureset.last_save_filenames
        copy_definition['filepaths'] = new_featureset.last_save_filepaths
        copy_definition['filetypes'] = new_featureset.last_save_filetypes
        filetype = old_featureset.last_save_filetypes[old_variant]
        copy_definition['variants'] = new_featureset.last_variant_list
        copy_definition['dataset_shapes'] = new_featureset.dataset_shapes
        new_featureset._setDefinition(copy_definition)

        # Keep the old column types if not redefined here
        for old_col in old_col_types:
            if copy_data_types is None or (old_col not in copy_data_types and '*' not in copy_data_types):
                new_featureset.types[old_col] = old_col_types[old_col]

        # Copy the col types, schema, and shapes
        #new_featureset.types = copy.deepcopy(old_col_types)
        #new_featureset.schemas = copy.deepcopy(old_schemas)

        #new_featureset.dataset_shapes = new_shapes

        # Update the last updated timestamp
        new_featureset._updateLastUpdated()

        # Save *all* the children to file, even though only one changed here
        save_kwargs = {} if old_type=='model' or old_type=='view' else {'schema_changed': True} 
        self.out("Saving variants in {}...".format(new_variant_list))
        for new_variant in new_variant_list:
            new_featureset.save(overwrite=True, variant=new_variant, child='*', 
                                save_to_disk=True, filetype=filetype, # col_types=types,
                                **save_kwargs)

        del(old_data_child_data)
        del(old_data)

#             new_featureset.label = new_label
#             self.out("New featureset has label: ", new_featureset.label, new_featureset.last_save_filenames)
#             # Note: We should not reload the new feature set from file in this case

#             # Make sure to change the new file's label / filename definition
#             self.out(old_featureset.getDefinition())
#             copy_definition = old_featureset.getDefinition().copy()
#             copy_definition['label'] = new_label
#             copy_definition['filenames'] = new_featureset.last_save_filenames
#             copy_definition['filepaths'] = new_featureset.last_save_filepaths
#             copy_definition['filetypes'] = new_featureset.last_save_filetypes
#             copy_definition['variants'] = new_featureset.last_variant_list
#             new_featureset.setDefinition(copy_definition)

#             # Copy the col types, schema, and shapes
#             new_featureset.types = old_col_types.copy()
#             new_featureset.schemas = old_schemas.copy()
#             new_featureset.dataset_shapes = old_shapes.copy()

#             # Save *all* the children to file, even though only one changed here
#             save_kwargs = {} if datatype=='model' or datatype=='view' else {'schema_changed': True}        
#             new_featureset.save(overwrite=overwrite, variant=variant, child='*', 
#                                 save_to_disk=True, filetype=filetype, # col_types=types,
#                                 **save_kwargs)

        self.out("Now, new featureset has label: ", new_featureset.label, ", filenames:", new_featureset.last_save_filenames, "filetypes:", new_featureset.last_save_filetypes, ", recent variants:", new_featureset.last_variant_list)
        self._updateFeatureSetMetadata(new_featureset.label)
        del(old_featureset)

        # Print the outputted featureset
        if new_featureset is not None and view_output:
            new_featureset.view('shape')

        return new_featureset
    else:
        self.out("WARNING: Could not create new copy of {} because it does not exist".format(old_label), type='warning')
        del(old_featureset)
        return None


#############################################################################################
# reload=True --> force reload
# reload=None --> only reload if the FeatureSet is None or if variants are not in memory
# reload=False --> don't reload, period
# batch=None --> don't know, use the self.default_batch
# variant --> '*' (by default) which reloads any variants not already in memory, or a specific variant to reload like None
def Features(self, featureset, **kwargs):
    label = featureset
    reload = kwargs.get('reload', self.default_reload)
    batch = kwargs.get('batch', self.default_batch)
    variant = kwargs.get('variant', '*') # Change on 4/3/19: Use '*' so as not to assume there's a None variant
    filename = kwargs.get('filename', None)
    filetype = kwargs.get('filetype', None)
    datatype = kwargs.get('datatype', self.default_datatype) # This is only used with filename

    # Allow featureset to be a dict containing (possible) featureset, variant, batch, filename, and/or version parameters
    # which (if provided) will override the kwargs passed in here
    if isinstance(featureset, dict):
        if 'featureset' in featureset:
            label = featureset['featureset']
        if 'variant' in featureset:
            variant = featureset['variant']
        if 'batch' in featureset:
            batch = featureset['batch']
        if 'filename' in featureset:
            filename = featureset['filename']
        if 'version' in featureset:
            version = featureset['version']
    self.out("In Features({}) with reload={}, batch={}, variant={}, filename={}, filetype={}, datatype={}".format(label, reload, batch, variant, filename, filetype, datatype))

    # Initialize to the state of reload
    # also force reload from disk if filename parameter is provided here
    to_reload = False
    if reload or filename is not None:
        to_reload = True
        variants_to_reload = variant
        self.out("reload=True so reloading variants={}".format(variants_to_reload))

    # Need to reload if this feature set is not in memory
    elif label not in self.feature_sets \
        or self.feature_sets[label] is None \
        or batch not in self.feature_sets[label] \
        or self.feature_sets[label][batch] is None:

        to_reload = True
        variants_to_reload = variant
        self.out("setting to_reload=True  for variants {} because the label '{}' or batch '{}' is not yet in memory".format(variants_to_reload, label, batch))        

    else:
        # FeatureSet is in memory, so check if any given variants are not in memory or not the most updated version
        feature_set = self.feature_sets[label][batch]

        # Store which variants are in memory already
        variants_in_memory = feature_set.variants(type='memory')
        #print("variants in memory:", variants_in_memory)

        # Figure out which variants need to be reloaded
        if variant == '*':
            # Make sure all possible variants are in memory
            #all_variants = feature_set.variants()
            all_variants = self.getVariantList(label, batch=batch, type='recent')
        elif isinstance(variant, str) or variant is None:
            all_variants = [variant]
        else:
            all_variants = variant

        variants_to_reload = []
        # Reload if flagged to do so, or 
        if reload or reload is None: 
            # New 1/3/21: Also reload if this featureset has been updated after the version in memory
            feature_set_last_updated_on_disk = self._getFeaturesetLastUpdated(label, batch, type='metadata')
            feature_set_last_updated_in_memory = self._getFeaturesetLastUpdated(label, batch, type='memory')
            self.out("...feature_set_last_updated_on_disk={}".format(feature_set_last_updated_on_disk))
            self.out("...feature_set_last_updated_in_memory={}".format(feature_set_last_updated_in_memory))
            if feature_set_last_updated_on_disk is not None and \
                feature_set_last_updated_in_memory < feature_set_last_updated_on_disk:
                self.out("...the feature set in memory is an older version ({}) than the version on disk ({}), so reloading the featureset {} for variants {}".format(feature_set_last_updated_in_memory, feature_set_last_updated_on_disk, label, all_variants))
                to_reload = True
                variants_to_reload = all_variants
            # Figure out which variants are not in memory (as long as reload!=False)
            else:
                for this_variant in all_variants:
                    self.out("...checking if variant='{}' is in memory".format(this_variant))
                    if this_variant not in variants_in_memory:
                        to_reload = True
                        self.out("...nope...going to reload it.")
                        variants_to_reload.append(this_variant)

    if to_reload:
        self.out("Reloading {} for variants {} vs. {}, batch={}".format(label, variants_to_reload, variant, batch))

        # Check if this featureset exists, throw an error if not and exit
        if not self.exists(label, variant=variants_to_reload, batch=batch):
            raise FeaturesetMissingError("The Featureset '{}' does not exist with variant='{}' in batch='{}'".format(label, 
                                                                                                                    variant,
                                                                                                                    batch))

        import psutil
        self.out('...in Features()...Memory: {}'.format(psutil.virtual_memory()))
        reload_success = self._reload(label, batch=batch, variant=variants_to_reload, filename=filename, datatype=datatype, filetype=filetype)
        self.out("...reload success=", 'success' if reload_success is not None else 'failed')
        self.out('...in Features() after reload...Memory: {}'.format(psutil.virtual_memory()))

        # Check if the reload worked, return the feature set if it did
        if reload_success and label in self.feature_sets and batch in self.feature_sets[label]:
            return self.feature_sets[label][batch]
        else:
            return None
    else:    
        # If didn't need to reload, then we should have this feature set in memory
        return self.feature_sets[label][batch]


#############################################################################################
def Data(self, label, **kwargs):
    variant = kwargs.get('variant', '*') #self.default_variant) Change on 4/3/19
    child = kwargs.get('child', None)

    import psutil
    self.out('...in Data()...Memory: {}'.format(psutil.virtual_memory()))
    # Get the feature set (which will reload if necessary)
    self.out("Retrieving feature set '{}' with kwargs: {}".format(label, kwargs))
    f = self.Features(label, **kwargs)
    if f is None:
        self.out("...returned null feature set", type='error')
        return None

    # Only pass variant/child into the getData() call if provided here, otherwise leave out so that
    # getData() decides the defaults
    if 'variant' in kwargs:
        if 'child' in kwargs:
            return f.getData(variant=kwargs['variant'], child=kwargs['child'])
        else:
            return f.getData(variant=kwargs['variant'])
    elif 'child' in kwargs:
        return f.getData(child=kwargs['child'])
    else:
        return f.getData()

