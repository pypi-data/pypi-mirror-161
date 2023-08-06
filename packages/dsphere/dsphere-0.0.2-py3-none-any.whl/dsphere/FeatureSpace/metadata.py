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

import dsphere.defaults as defaults
class dotdict(dict):
    """dot.notation access to dictionary properties"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
DEFAULTS = dotdict(defaults.DEFAULTS)

#############################################################################################
# TODO: Support parallel flow operations, whether in different scripts/notebooks or in different batches.
# Note: Calling this does not re-save the FeatureSpace's metadata.  Another transform must be called for that to happen.
# Calling it here is causing bugs elsewhere (having to do with timestamps).
def setFlow(self, flow=None):
    """Sets the current flow as what's currently executing changes to the FeatureSpace.

    * Parameters:
       - flow: The label of the current flow (a short string).  Only one flow can be current at a time.

    * Returns:
       *Nothing returned*
    """
    self._current_flow = flow

    # Also store all the flows in the FeatureSpace-level metadata
    flow_batches = self.all_flows.get(flow, {})
    curr_batch = self.default_batch
    flow_locations = flow_batches.get(curr_batch, [])
    curr_location = sys.argv[0]
    if curr_location not in flow_locations:
        flow_locations.append(curr_location)
    flow_batches[curr_batch] = flow_locations
    self.all_flows[flow] = flow_batches

    #self.save()  # Can't call this here (for now), it causes bugs


#############################################################################################
def setDefaultBatch(self, batch=DEFAULTS._NO_BATCH):
    """Sets the default batch for future operations on this FeatureSpace.

    * Parameters:
        - batch: The batch that should be treated as the default.

    * Returns:
        *Nothing returned*
    """
    self.default_batch = batch


#############################################################################################
def _getSaveDirectory(self):
    """Returns the base path where this FeatureSpace's metadata file is saved.

    If that directory does not yet exist, it's created here.

    * Parameters:
        *No parameters*

    * Returns: (string) Path of the directory where this FeatureSpace's metadata file is saved.
    """
    project_dir = self.getProjectDirectory()

    save_dir = os.path.join(project_dir, 'metadata')
    if not os.path.exists(save_dir):
        print("...creating metadata directory:", save_dir)
        os.mkdir(save_dir)
    return save_dir

#############################################################################################
def _getTempDirectory(self):
    """Returns the base path where this FeatureSpace's temp files will be saved.

    If that directory does not yet exist, it's created here.

    * Parameters:
        *No parameters*

    * Returns: (string) Path of the directory where this FeatureSpace's temp files will be saved.
    """
    project_dir = self.getProjectDirectory()

    save_dir = os.path.join(project_dir, 'temp')
    if not os.path.exists(save_dir):
        print("...creating temp file directory:", save_dir)
        os.mkdir(save_dir)
    return save_dir        


#############################################################################################
def getProjectDirectory(self):
    """Returns the base path where this FeatureSpace is saved.

    If that directory does not yet exist, it's created here.

    * Parameters:
        *No parameters*

    * Returns: (string) Path of the directory where this FeatureSpace's data and metadata are saved.
    """
    # Make sure the FeatureSpace base directory exists
    if not os.path.exists(self.base_directory):
        print("...creating FeatureSpace directory:", self.base_directory)
        os.mkdir(self.base_directory)

    # Make sure the data directory exists
    data_dir = os.path.join(self.base_directory, 'data')
    if not os.path.exists(data_dir):
        print("...creating data directory:", data_dir)
        os.mkdir(data_dir)

    # Make sure the project directory exists too
    project_dir = os.path.join(data_dir, self.project_label or 'project')
    if not os.path.exists(project_dir):
        print("...creating project directory:", project_dir)
        os.mkdir(project_dir)

    return project_dir
    #return os.path.join(FeatureSpace_directory, 'data', self.project_label or 'project')
#############################################################################################
# Wrapper to get the last updated timestamp in datetime format for a featureset
# Note this timestamp is either the last updated for all featuresets on disk ('metadata') or what's in memory ('memory')
def _getFeaturesetLastUpdated(self, label, batch, type='metadata'): # Can be 'metadata' or 'memory'
    # Note not doing error checking one existence of this label/batch to force calling functions to fail
    if type=='metadata':
        if label in self.feature_set_metadata:
            if batch in self.feature_set_metadata[label]:
                metadata_last_updated = self.feature_set_metadata[label][batch]['last_updated']
                if isinstance(metadata_last_updated, str):
                    # The last_updated timestamp is a string if it was recently loaded from the FS metadata file
                    return date_parser.parse(metadata_last_updated)
                else:
                    # Otherwise we can assume it's already in datetime format if this featureset was loaded into memory
                    return metadata_last_updated
        return None

    else:
        # Assume the alternative is 'memory' where we seek the last_updated timestamp of the Featureset in memory
        if label in self.feature_sets:
            if batch in self.feature_sets[label]:
                return self.feature_sets[label][batch].last_updated
        # Return None if this feature set is not currently in memory
        return None

#############################################################################################
def freeUpMemory(self, keep=[]):
    # New on 9/21/20: Default is to free up everything, don't waste time calculating sizes 
    free_up_all_featuresets = True

    def get_memory_usage(data):
        if hasattr(data, '__feature_type__') and data.__feature_type__=='FeatureMatrix':
            return asizeof(data.getMatrix())
        elif isinstance(data, dd.DataFrame) or isinstance(data, dd.Series):
            return data.compute().memory_usage(index=True).sum()
            #return asizeof(data.compute()) # Too slow!
        else:
            return data.memory_usage(index=True).sum()
            #return asizeof(data) # Too slow!

    #if self.memory_mode == 'low':
    #    self.out("LOW MEMORY MODE: Trying to free up space in memory:")
    feature_sets_in_memory = list(self.feature_sets.keys())
    for label in feature_sets_in_memory:
        if label not in keep:
            if self.feature_sets[label] is not None:
                batches_in_memory = list(self.feature_sets[label].keys())
                for batch in batches_in_memory:
                    feature_set = self.feature_sets[label][batch]
                    if feature_set.datatype != 'model':
                        self.out("...checking {} in batch {}".format(label, batch))
                        featureset_mem_usage = 0
                        if not free_up_all_featuresets:
                            feature_set_data = feature_set.getData(variant='*', child='*')
                            if isinstance(feature_set_data, dict):
                                # Iterate through all variants/children to sum up the size of all datasets 
                                for fs_key in feature_set_data:
                                    fs_val = feature_set_data[fs_key]
                                    if isinstance(fs_val, dict):
                                        for fs_key2 in fs_val:
                                            fs_val2 = fs_val[fs_key2]
                                            self.out("getting memory usage for ", type(fs_val2))
                                            featureset_mem_usage += get_memory_usage(fs_val2)
                                    else:
                                        self.out("getting memory usage for ", type(fs_val))
                                        featureset_mem_usage += get_memory_usage(fs_val)

                            else:
                                self.out("getting memory usage for ", type(feature_set_data))
                                featureset_mem_usage = get_memory_usage(feature_set_data) #feature_set.getMemoryUsage()
                        #print("...checking whether to delete '{}' with memory usage {}".format(label, featureset_mem_usage))
                        if free_up_all_featuresets or featureset_mem_usage > self.memory_threshold:
                            # Delete this featureset from (local) memory if using more than the threshold
                            self.out("...deleting Feature Set {}, Batch {} from local memory (was using {} bytes)".format(label, batch, featureset_mem_usage))
                            self.delete(label, batch)
                            del(feature_set)

#############################################################################################
def getMemoryUsage(self):
    self.out("FeatureSpace {} memory usage:".format(self.project_label))
    for label in self.feature_sets:
        for batch in self.feature_sets[label]:
            self.out("FeatureSet {}, Batch {} uses {}".format(label, batch, self.feature_sets[label][batch].getMemoryUsage()))


#############################################################################################
# Check the featurespace file
def _loadFeatureSetMetadata(self):
    #ofile = os.path.join(self.save_directory, self.filename)
    #print(ofile)
    if os.path.exists(self.filepath):
        self.out("Importing feature space details from {}".format(self.filepath))

        # Parse the data out of the json file
        #json_text = open(ofile).read()
        #featurespace_data = json.loads(json_text)

        # New on 5/24/20: Lock the metadata file while reading from it, to prevent the metadata from being edited 
        # in the middle of json loading it (causing the json to be mal-formed)
        lock_name = self.filepath+".lock"
        with FileLock(lock_name, timeout=5) as lock:
            self.out("Lock acquired on FeatureSpace metadata file while reading from it...")

            # Now open the metadata as usual to read from it
            with open(self.filepath, 'rb') as metadata_file:
                try:
                    self.out("Trying to load the FeatureSpace using json...current timestamp: {}".format(datetime.datetime.now()))
                    featurespace_data = json.load(metadata_file, 
                                                  object_hook=lambda d: {k if k!='null' else None: v for k, v in d.items()})
                    self.out("...success")
                    self.out("...got last_update value in metadata file:", featurespace_data['last_update'])
                except:
                    self.out("...trying to load the FeatureSpace metadata using dill instead...")
                    featurespace_data = dill.load(metadata_file)
                    self.out("...success")

                    #featurespace_data = pickle.load(open(self.filepath, 'rb'))
                    # TODO: What if reloading one featureset but have newer file?

                if featurespace_data is not None and isinstance(featurespace_data, dict):
                    # Store these in the featurespace object
                    self.out("...saving featurespace metadata into memory")
                    self.out("...currently last_updated for the FS is:", self.last_updated)
                    self.feature_set_metadata = featurespace_data['feature_sets']
                    self.dependency_chain = featurespace_data['chain']
                    self.constants = featurespace_data.get('constants', {})
                    self.all_flows = featurespace_data.get('flows', {})
                    self.last_updated = date_parser.parse(featurespace_data['last_update']) if featurespace_data['last_update'] is not None else None
                    self.out("...after parsing the featurespace data, last_updated for the FS is:", self.last_updated)
                    self.out("...new last_updated for the FS metadata: {}".format(self.last_updated))
                else:
                    self.out("...featurespace metadata loaded as {}".format(type(featurespace_data)))
    else:
        self.out("ERROR: Cannot find featurespace file: {}".format(self.filename), type='error')



#############################################################################################
# Update the FeatureSpace's metadata to match the latest status details for each feature set in memory
# Note that if we delete a feature set from memory, its details will stay here
# Also if the FeatureSpace metadata changed (because the last_updated timestamp for any FeatureSet is after
# the last_updated timestamp for the metadata) then also re-save the metadata to file because it has changed
# New on 1/3/21: Allow control over which feature sets are updated in the metadata, since sometimes the featuresets in
# memory are older than what's in metadata so the metadata was being overwritten accidentally ('*'=all, or list or string)
def _updateFeatureSetMetadata(self, feature_sets='*'):
    latest_feature_set_update = None
    metadata_has_been_updated = False
    self.out("Updating Featureset metadata for '{}'...".format(feature_sets))

    # Keep track of when this copy of the metadata was last updated
    # -- we will want to write to the FeatureSpace metadata if any feature set was changed after that
    current_metadata_last_updated = self.last_updated

    # Important subtle change 5/24/20: Before we update the FS and featureset metadata to match what's in memory,
    # we need to check for any updates to the whole FS metadata that might have occurred elsewhere.
    # This way we only check-in changes to this featureset (and the overall metadata) that happen after the 
    # FS was updated.  If this update happens before then -- in a race condition -- then this update to the FS metadata
    # will not overwrite the metadata from the previous update.  The last check-in always wins.

    # This way we check for any updates to the FS metadata that occurred during a transform, in addition to before
    # the transform.  This will be called by addData().
    # Reload the FeatureSpace metadata first to make sure we reload the latest files
    self.out("...reloading the FeatureSpace...")
    # TODO: Put a lock on the FS metadata file that persists across _loadFeatureSetMetadata all the way through the end of self.save() below, to prevent the possibility that the FS is changed between them here
    self._loadFeatureSetMetadata()

    # Allow control over which feature sets are updated in the metadata
    if feature_sets=='*':
        feature_sets_to_update = list(self.feature_sets.keys())
    elif isinstance(feature_sets, str):
        feature_sets_to_update = [feature_sets]
    else:
        feature_sets_to_update = feature_sets

    # Iterate through the list of feature sets to update in the metadata
    for feature_set_label in feature_sets_to_update:
        if feature_set_label in self.feature_sets:
            for batch in self.feature_sets[feature_set_label]:
                feature_set = self.feature_sets[feature_set_label][batch]
                if feature_set is not None:
                    # Make sure the metadata stored in-memory is in sync with the metadata for each FeatureSet
                    if feature_set_label not in self.feature_set_metadata:                        
                        self.feature_set_metadata[feature_set_label] = {}
                        self.out("self.feature_set_metadata[{}] = empty".format(feature_set_label))

                    self.feature_set_metadata[feature_set_label][batch] = feature_set._getDefinition()

                    # Keep track of the latest update to any FeatureSet
                    self.out('......last_updated={} for "{}"'.format(feature_set.last_updated, feature_set_label), type='debug')
                    if feature_set.last_updated is None:
                        # This FeatureSet is new so need to update its metadata
                        #metadata_has_been_updated = True
                        latest_feature_set_update = datetime.datetime.now()
                    elif latest_feature_set_update is None or feature_set.last_updated > latest_feature_set_update:
                        # Use the first FeatureSet's last_updated timestamp
                        latest_feature_set_update = feature_set.last_updated

                        # Should update the metadata file if this FeatureSet was updated after it 
                        #if self.last_updated is None or latest_feature_set_update > self.last_updated:
                        #    metadata_has_been_updated = True
                    #else:

                        # If we have a last_updated timestamp for the FeatureSet, keep track of the latest one
                    #elif feature_set.last_updated > latest_feature_set_update:
                    #    latest_feature_set_update = feature_set.last_updated
                        #    if self.last_updated is None or latest_feature_set_update > self.last_updated:
                        #        # If this one is later, then remember to update the metadata accordingly
                        #        metadata_has_been_updated = True

    self.out('...latest FeatureSet last_updated timestamp: {}'.format(latest_feature_set_update), type='debug')
    self.out('...latest update to the FeatureSpace metadata in memory: {}'.format(current_metadata_last_updated), type='debug')
    self.out('...latest update to the FeatureSpace metadata on disk: {}'.format(self.last_updated), type='debug')

    # Only write the metadata back to disk if there's been a change since when it was last read-in
    # i.e. if we're just reading in FeatureSets from disk, then don't need to update the metadata
    #if metadata_has_been_updated:
    if current_metadata_last_updated is None or \
            (latest_feature_set_update is not None and latest_feature_set_update > current_metadata_last_updated):
        self.out('...updating FeatureSpace metadata on disk because there has been a change to a FeatureSet after when the FeatureSpace metadata in memory was last written to disk', type='debug')

        # Update the FeatureSpace's last_updated datetime to match the latest FeatureSet last_update time
        self.last_updated = latest_feature_set_update

        # Then re-save the metadata out to file
        self.save()

        # Now update the last updated timestamp for the FeatureSpace 
        #self.updateLastUpdated()
    else:
        self.out('...not updating the FeatureSpace metadata on disk', type='debug')

#############################################################################################
# If type='all': Get the full list of possible variants for the given feature set (from the FeatureSpace's metadata)
# If type='recent' (default): Get the variants that were most recently loaded into memory for the given feature set 
# Note: These variants are not all necessarily loaded into memory yet in the corresponding FeatureSet
# Change on 10/27/21: Need to prevent variants from being '*' and ignore any '*' saved in the past
def getVariantList(self, label, batch=None, type='recent'):
    if batch is None:
        batch = self.default_batch
    if label in self.feature_set_metadata:
        if batch in self.feature_set_metadata[label]:
            all_variants = []
            if type=='all':
                all_variants = list([var for var in self.feature_set_metadata[label][batch]['filenames'].keys() if var!='*'])
            # Always check the variants in memory too, since some can be only in memory not on disk
            feature_set_definition = self.feature_set_metadata[label][batch]
            if 'variants' in feature_set_definition:
                #print("have variants for self.feature_set_metadata[{}][{}]".format(label, batch))
                variant_list = feature_set_definition['variants']
                self.out("...variant_list={}".format(variant_list))
                if variant_list is None:
                    # Throw None as soft error if there are no variants here
                    return None

                # Iterate through each variant in memory
                for var in variant_list:
                    if var!='*' and var not in all_variants:
                        all_variants.append(var)
                #return list([var for var in variant_list if var!='*']) if variant_list is not None else None
            return all_variants
    return []


#############################################################################################
# This clears out all of the 'recent' variants for a given feature set,
# to help eliminate clutter of too many combinations of variants piling up
def _clearVariantList(self, label, batch=None):
    if batch is None:
        batch = self.default_batch
    if label in self.feature_set_metadata:
        if batch in self.feature_set_metadata[label]:
            feature_set_definition = self.feature_set_metadata[label][batch]
            if feature_set_definition is not None:
                # Reset this list of recent variants
                feature_set_definition['variants'] = []
                self.out("Reset the list of recent variants for feature set '{}', batch '{}'".format(label, batch))
                return None

    self.out("Could not find a list of recent variants for feature set '{}', batch '{}'".format(label, batch),
            type='warning')
    return None


#############################################################################################
# Figure out what variant to use for the output feature set based on the variants of the inputs
# output_variant=None --> use the input_variant_combination to infer the output variant
# output_variant=[None] --> use output_variant=None as the output
def _getOutputVariant(self, input_variant_combination, output_variant, num_variant_combos):
    input_variant_combo_label_deduped = list(filter(None, set([x for x in input_variant_combination])))
    if len(input_variant_combo_label_deduped)>0:
        input_variant_combo_label = '+'.join(input_variant_combo_label_deduped)
    else:
        input_variant_combo_label = None

    # if output_variant is a list...
        # if more in output_variant than combinations...throw error

        # if one output_variant 
        # otherwise line up each output_variant with the combination in order

    # if output_variant is None...
        # use each inferred output_variant from the input_combination

    # if output_variant is a string...
        # treat as a list of one output_variant

    # otherwise throw an error

    # Figure out what the output variant should be based on the input combo label + any output_variant parameter
    this_output_variant = input_variant_combo_label
    # If output_variant provided, use it for the output if only 1 combination of input variants was used
    if output_variant is not None:
        # If output_variant provided and >1 combos of input variants, then concatenate output_variant with each combo
        this_output_variant = output_variant if num_variant_combos == 1 else output_variant+'_'+(input_variant_combo_label if input_variant_combo_label is not None else 'NONE')
#             this_output_variant = output_variant if num_variant_combos == 1 else (output_variant if output_variant is not None else 'NONE') + '_' + (input_variant_combo_label if input_variant_combo_label is not None else 'NONE')

    return this_output_variant

#############################################################################################
# TODO: Track batch and variant in the dependency chain
def _setDependency(self, dependent, dependency_on, transformation, **kwargs):
    reload = False # Do not need to reload data sets here
    batch = kwargs.get('batch', self.default_batch)
    variant = kwargs.get('variant', self.default_variant)

    # Insert this dependency into the dependency_chain (recursively)
    if not self._insertDependent(self.dependency_chain, 
                         dependent, dependency_on, transformation):
        self.dependency_chain[dependency_on] = {'-->':{dependent: {'-->':{},
                                                                   't':transformation
                                                                   }
                                                       }
                                               }

    # If have the feature sets in memory, then add the dependency into them
    if self.exists(dependent, batch=batch, variant=variant):
        dependent_feature_set = self.Features(dependent, batch=batch, reload=reload, variant=variant)
        if dependent_feature_set is not None:
            dependent_feature_set._addDependency(this_depends_on=dependency_on, transformer_function=transformation)
    if self.exists(dependency_on, batch=batch, variant=variant):
        dependency_on_feature_set = self.Features(dependency_on, batch=batch, reload=reload, variant=variant)
        if dependency_on_feature_set is not None:
            dependency_on_feature_set._addDependency(depends_on_this=dependent)
    # self.save()



#############################################################################################
def _insertDependent(self, chain, dependent, dependency_on, transformation):
    for node in chain:
        if node == dependency_on:
            # Insert the dependent here if this is the dependency_on
            if chain[node] is None:
                chain[node] = {'-->':{}, 't':None}
            chain[node]['-->'][dependent] = {'-->':{},
                                             't':transformation
                                             }
            #print("...added new dependency chain[{}][-->][{}]".format(node, dependent))
            return True
        elif chain[node] is not None and len(chain[node]['-->'])>0:
            # Keep going if there are deeper dependents                
            if self._insertDependent(chain[node]['-->'], 
                                    dependent, 
                                    dependency_on, 
                                    transformation):
                return True

    # If could not find a place for this, then return False
    return False

    #############################################################################################
# If variant='*' and have multiple input featuresets, create a structure storing each combination of variants to use: i.e.
# [['var1'], ['var2']] for a single input feature set with 2 variants
# [['var1','var1'], ['var2','var2']] for 2 feature sets with 2 variants (but not ['var1','var2']
# [['var1','var3'], ['var2','var3']] for 2 feature sets where the first has 2 variants and the second has 1 variant that doesn't overlap
# If a specific variant is specified, create the list of combinations of variants in common to all inputs:
# [['var1','var1'],['var2','var2']] for 2 feature sets if both have ['var1','var2'], 
# and even if 'var3' is in the target variant list, it will not appear in the combinations if it is missing from an input
# Note: Expecting target_variant_list to be a list, not a string
# - input_labels should be a list of featureset labels (or a string for just one)
# - target_variant_list should be a list of variants 
# If input_labels is a dict with {featureset1:var1, featureset2:[var1,var2]} then only look at the given variants for each
# featureset as specified in the dict.  Overrides anything passed into target_variant_list.  Equivalent to 
# target_variant_list=[[var1],[var1,var2]] and input_labels=[featureset1, featureset2].
# Note that if you want to pass in the same featureset twice (e.g. concat with itself), you need to use 
# the target_variant_list, not the dict, since {featureset1:[var1], featureset1:[var2]}=={featureset1:[var2]}.
# This lets you control exactly which combinations of variants to use rather than let the transform infer it.
# Note that this target_variant_list=[['training+past'], ['training+past', 'training+future']] will still result in
# this function choosing only [['training+past'],['training+past']]. So that's not a good way to force transforms on 
# both combinations [['training+past'],['training+past']] and [['training+past'],['training+future']]
# Also new on 2/6/21: Combining _getOutputVariants() into this function, so they are figured out together.
# - as a result, the output_variant provided to the transform must have the same length as the calculated
# number of input variant combinations, or an error will be thrown (to prevent unexpected output_variants)
def _getVariantCombinations(self, input_labels, target_variant_list, target_output_variant_list, batch):
    self.out("Finding all variant combinations using input_labels={}, target variants={}...".format(input_labels, target_variant_list))
    all_input_variant_combos = []
    variants_so_far = []
    num_inputs_so_far = 0
    all_possible_combos = None
    if input_labels is None:
        self.out("ERROR: _getVariantCombinations() called with input_labels=None", type='error')
        raise

    input_labels = [input_labels] if isinstance(input_labels, str) else input_labels 

    for input_featureset in input_labels:
        self.out("...label: ", input_featureset)
        input_variants = None

        # If the input_label itself is a dict like {'featureset':'featureset_1', 'variant':['var1','var2']}
#             if isinstance(input_featureset, dict):
#                 # Get the label of the input featureset
#                 if 'featureset' not in input_featureset and 'label' not in input_featureset:
#                     self.out("ERROR: Must provide a 'featureset' or 'label' parameter in the input {}".format(input_featureset),
#                              type='error')
#                     raise
#                 input_label = input_featureset['featureset'] if 'featureset' in input_featureset else input_featureset['label']

#                 # Also get the variant(s) if provided here
#                 if 'variant' in input_featureset or 'variants' in input_featureset:
#                     input_variants = input_featureset['variant'] if 'variant' in input_featureset \
#                                      else input_featureset['variants']
#                     if isinstance(input_variants, str):
#                         input_variants = [input_variants]

        # If a dict is provided for all the input_labels like {'featureset_1':['var1'], 'featureset_2':['var1', 'var2']}
        if isinstance(input_featureset, str):
            input_label = input_featureset

            # Check if this featureset exists, throw an error if not and exit
            if not self.exists(input_label, batch=batch):
                raise FeaturesetMissingError("The Featureset '{}' does not exist in batch='{}'".format(input_label, 
                                                                                                       batch))
#                 if isinstance(input_labels, dict):
#                     # Use the variants for each input if provided in the dict structure
#                     input_variants = input_labels[input_featureset]
#                     if isinstance(input_variants, str):
#                         input_variants = [input_variants]

            # Otherwise if a list of variants is provided in target_variant_list
            if isinstance(target_variant_list, list) and len(target_variant_list)>0:
                # Check if there is a nested list like target_variant_list=[[var1], [var2]]
                if isinstance(target_variant_list[0], list):
                    # Then use each variant list corresponding to the index of the input_label
                    if num_inputs_so_far >= len(target_variant_list):
                        self.out("ERROR: If passing a list of lists into target_variant_list, then the number of sub-lists ({}) must correspond to the number of input_labels provided ({}) in _getVariantCombinations()".format(len(target_variant_list), len(input_labels)), type='error')
                        raise
                    input_variants = target_variant_list[num_inputs_so_far]
                    if not isinstance(input_variants, list):
                        self.out("ERROR: If passing a list of lists into target_variant_list, then *all* elements of target_variant_list must be sub-lists. Here the variant list {} corresponding to input_label '{}' is of type {}.".format(input_variants, input_label, type(input_variants)), type='error')
                        raise
                else:
                    # Treat the list of variants in target_variant_list as the set of variants to check for all input_labels
                    input_variants = target_variant_list

        else:
            # Throw an error
            self.out("ERROR: One of the input featuresets was not a string -- {}".format(input_featureset),
                     type='error')
            raise

        # If '*' or None provided for one of the inputs in a dict input_labels, or input_labels is a list, 
        # then get all its recent variants
        if input_variants is None or input_variants == '*' or input_variants == ['*']:
            # Otherwise look up the list of recently loaded variants for each input
            input_variants = self.getVariantList(input_label, batch=batch, type='recent')
        else:
            # If given a list of variants to use, only consider the ones that are in the given input_label featureset
            recent_variants = self.getVariantList(input_label, batch=batch, type='recent')
            self.out("...comparing input_variants {} vs. variants {} currently in the featureset '{}'".format(input_variants,
                                                                                                              recent_variants,
                                                                                                              input_label))
            input_variants = [var for var in input_variants if var in recent_variants]
            self.out("...only {} of the input_variants are in the featureset".format(input_variants)) 
        self.out("...checking variants {} for input '{}'".format(input_variants, input_label))

        # Check if there are no input_variants to use for this input_label
        if isinstance(input_variants, list) and len(input_variants)==0:
            self.out("ERROR: No variants from the given target_variant_list ({}) are in the featureset '{}', cannot proceed to _getVariantCombinations()".format(target_variant_list, input_label), type='error')
            raise

        # If variant='*' or specific variants provided for each input, then combine all those variants together
        #if target_variant_list == ['*'] or isinstance(input_labels, dict) or isinstance(target_variant_list, list):
        if input_variants is None or isinstance(input_variants, list):
            # Keep all possible combinations of all variants for each input set
            if all_possible_combos is None:
                if input_variants is None or input_variants == [None]:
                    all_possible_combos = [[None]]
                else:
                    all_possible_combos = [[x] for x in input_variants]
            else:
                self.out("Getting product of ({}, {})".format(all_possible_combos, input_variants))
                product = [(x if isinstance(x,list) else [x])+[y] for x in all_possible_combos for y in input_variants]
                #product = itertools.product(all_possible_combos, input_variants)
                all_possible_combos = list(product)
            all_input_variant_combos = all_possible_combos

        # If given a specific set of variants, make sure each variant is in every input feature set's variant list
        else:
            if num_inputs_so_far > 0:
                new_combo_list = []
                for prev_variant_combo in all_input_variant_combos:
                    this_combo_variant = prev_variant_combo[0]
                    # If this is one of the target variants and in the next input feature set's list, add a new combo
                    if this_combo_variant in target_variant_list and this_combo_variant in input_variants:
                        prev_variant_combo.append(this_combo_variant)
                        new_combo_list.append(prev_variant_combo)
                all_input_variant_combos = new_combo_list

            elif input_variants is not None:
                # If it's the first input feature set, add all this feature set's variants if in the target list
                for input_variant in input_variants:
                    if input_variant in target_variant_list:
                        all_input_variant_combos.append([input_variant])

        num_inputs_so_far += 1

    # If variant='*' then find the subset of the combos with the most "points"
    # (as a heuristic to pick the right combinations)
    best_combos = all_input_variant_combos
    if target_variant_list == ['*'] or isinstance(target_variant_list, list):
        self.out("Final list of possible combos: {}".format(all_possible_combos))

        # Calculate the "score" of each possible combo, only pick the ones with the highest score
        num_possible_combos = len(all_possible_combos)
        all_combo_scores = np.zeros(num_possible_combos)
        for (i,possible_combo) in enumerate(all_possible_combos):
            variant_string_so_far = ''
            self.out("checking combo {} = {} (type:{})".format(i, possible_combo, type(possible_combo)))
            points_so_far = 0
            for one_variant in possible_combo:
                #TODO: Store the previous variants as a list not a string, to avoid mistaken substrings
                # such as 'batch_b1' in 'batch_b10' = True
                one_variant_string = 'NONE' if one_variant is None else one_variant
                # Change on 4/7/19: Give more points to (None,None) or ('blah','blah') than to (None,'blah')
                if one_variant in target_variant_list:
                    points_so_far += 2
                if variant_string_so_far!='' and one_variant_string in variant_string_so_far:
                    points_so_far += 2
                elif one_variant is None or variant_string_so_far=='':
                    points_so_far += 1

                variant_string_so_far += ',' if variant_string_so_far != '' else ''   
                variant_string_so_far += one_variant_string

                self.out("...variant_string = ", variant_string_so_far, "points = ", points_so_far)
            all_combo_scores[i] = points_so_far

        combo_indexes_with_max_points = np.argwhere(all_combo_scores == np.amax(all_combo_scores)).flatten() 
        best_combos = [all_possible_combos[i] for i in combo_indexes_with_max_points]
        self.out("...Have {} combos with the most points (out of {} possible combos):".format(len(best_combos), len(all_combo_scores), best_combos))
        #return best_combos

    #else:
    #    return all_input_variant_combos

    # New 2/6/21: Determine the list of output variants here to correspond to the list of input variant combinations
    output_variant_list = None
    if target_output_variant_list=='*' or target_output_variant_list==['*']:
        # Infer the output variants from the combinations of input variants
        output_variant_list = []
        for input_variant_combination in best_combos: 
            input_variant_combo_label_deduped = list(filter(None, set([x for x in input_variant_combination])))
            if len(input_variant_combo_label_deduped)>0:
                input_variant_combo_label = '+'.join(input_variant_combo_label_deduped)
            else:
                input_variant_combo_label = None

            # Figure out what the output variant should be based on the input combo label + any output_variant parameter
            output_variant_list.append(input_variant_combo_label)

    elif isinstance(target_output_variant_list, list):
        # Make sure there aren't more or fewer output_variant values than input variant combinations
        if len(target_output_variant_list) != len(best_combos):
            self.out("ERROR: The number of output_variants specified in {} cannot be different from the number of combinations of input_variants ({}) that will be used in this transform.".format(target_output_variant_list, len(best_combos), best_combos), type='error')
            raise

        # Otherwise use the output_variants as given, regardless of the input variant combinations
        output_variant_list = target_output_variant_list

    elif isinstance(target_output_variant_list, str) or target_output_variant_list is None:
        # Make sure there's only a single input variant combination being used
        if len(best_combos)!=1:
            self.out("ERROR: output_variant was specified to be '{}' yet there are {} combinations of input variants to be used: {}".format(target_output_variant_list, len(best_combos), best_combos), type='error')
            raise

        # Otherwise use this one output_variant 
        output_variant_list = [target_output_variant_list]

    else:
        # Don't know how to use this type of output_variant
        self.out("ERROR: Cannot pass output_variant={} of type={}".format(target_output_variant_list,
                                                                             type(target_output_variant_list)), type='error')
        raise

    return best_combos, output_variant_list

#############################################################################################
def _getDependencyChain(self, print_out=True):
    """Testing this docstring"""
    if print_out:
        print("Dependency chain: {}".format(self.dependency_chain))
    return self.dependency_chain


#############################################################################################
def _getDependents(self, label, print_out=True, **kwargs):
    if print_out:
        ##print("--> {} ({})".format(label, self.getStatus(label, **kwargs)))
        print("--> {}".format(label))
    dependents = []
    #print("Getting dependents for {}".format(label))
    feature_set = self.Features(label, **kwargs)
    if feature_set is not None:
        dependees = feature_set.depends_on_this
        for dependee in dependees:
            dependents.append(self._getDependents(dependee, print_out=print_out, **kwargs))
    else:
        print("...do not have a FeatureSet {}, Batch {} loaded".format(label, kwargs))
    return {label: dependents}
