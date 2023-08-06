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
# Prints out the given output if in 'debug' output_mode, otherwise hides it
# TODO: Have alternative place to log this debug output
# TODO: Handle when running this from cronjob vs. notebooks
def out(self, *args, **kwargs):
    type = kwargs.get('type', 'debug')
    if type=='debug':
        # Only print debug output if in 'debug' mode 
        if self.output_mode=='debug' or (self.dsphere is not None and self.dsphere.output_mode=='debug'):
            print(*args)
    elif args:
        print(*args)
    return

#############################################################################################
def summary(self, featureset=None, batch=None):
    """Prints a summary of all the FeatureSets stored in this FeatureSpace.

    Also shown is whether each FeatureSet is currently in memory (indicated by \**) and when it was last updated/edited.

    * Parameters:
        - featureset: (optional) If provided, then search for only the Feature Sets with featureset in the label.
        - batch: (optional) If provided, then only that batch will be summarized.  Otherwise the current default batch will be shown.

    * Returns: 
        *Nothing returned*
    """
    print("FeatureSpace: {}".format(self.project_label))
    if batch is None:
        batch = self.default_batch
    print("Batch: {}".format(batch))
    print("Current Flow: {}".format(self._current_flow))
    print("Last updated: {}".format(self.last_updated))
    print("...has {} feature sets overall, {} are currently in memory (***)".format(len(self.feature_set_metadata), len(self.feature_sets)))
    for feature_set in self.feature_set_metadata:
        if featureset=='*' or featureset is None or featureset in feature_set:
            #num_batches = len(self.feature_set_metadata[feature_set])
            if batch == '*':
                batches = []
                for this_batch in self.feature_set_metadata[feature_set].keys():
                    variants = self.feature_set_metadata[feature_set][this_batch]['variants']
                    if len(variants)>1:
                        batches.append('{}:{}'.format(this_batch, list(variants)))                    
                    elif len(variants)==1 and variants[0] is not None:
                        batches.append('{}:{}'.format(this_batch, list(variants)))                    
                    else:
                        batches.append('{}'.format(this_batch))                               
                feature_set_variants = self.feature_set_metadata[feature_set]
                # TODO: Support flows for batch='*'
                print("-> {}{}: {} ({})".format("***" if feature_set in self.feature_sets else "", feature_set, 
                                                batches, self.last_updated))
            else:
                if batch in self.feature_set_metadata[feature_set]:
                    variants = self.feature_set_metadata[feature_set][batch]['variants']
                    last_updated = self.feature_set_metadata[feature_set][batch]['last_updated']
                    flows = self.feature_set_metadata[feature_set][batch].get('flows', None)
                    if isinstance(flows, dict):
                        flows = list(set([flows[var] for var in flows]))
                    if len(variants)>1 or (len(variants)==1 and variants[0] is not None):
                        print("-> {}{}: {} ({}) {}".format("***" if feature_set in self.feature_sets else "", 
                                                        feature_set, variants, last_updated, flows))
                    else:
                        print("-> {}{} ({}) {}".format("***" if feature_set in self.feature_sets else "", 
                                                    feature_set, last_updated, flows))      


#############################################################################################
# Returns a list of the featuresets in this FeatureSpace
def listFeatureSets(self):
    return list(self.feature_sets.keys())



#############################################################################################
# Wrapper around FeatureSet.view()
def view(self, label, *args, **kwargs):
#def view(self, label, query='', **kwargs):
    featureset = self.Features(label, **kwargs)
    if featureset is None:
        self.out("ERROR: Cannot find FeatureSet '{}' with args:{}".format(label, kwargs),
                type='error')
        return None
    return featureset.view(*args, **kwargs)

#############################################################################################
# Wrapper around FeatureSet.query()
def query(self, label, where='', **kwargs):
    featureset = self.Features(label, **kwargs)
    if featureset is None:
        self.out("ERROR: Cannot query FeatureSet '{}' with args:{}".format(label, kwargs),
                type='error')
        return None
    return featureset.query(where, **kwargs)

#############################################################################################
# Return true if a given Featureset exists
# If variant is passed in, only return true if the featureset exists for that variant 
# If list or tuple of variants passed in, return true if all of them exist
# Otherwise return False
# Default batch is the current one
def exists(self, label, variant='*', batch=None):
    featureset_var_list = self.getVariantList(label, batch=batch, type='all')
    if len(featureset_var_list)==0:
        return False
    if variant=='*':
        return len(featureset_var_list)>0
    else:
        if isinstance(variant, str) or variant is None:
            return variant in featureset_var_list
        elif isinstance(variant, list) or isinstance(variant, tuple):
            for var in variant:
                # Return True if all of these variants exist, otherwise False
                if var not in featureset_var_list:
                    return False
            return True
    return False

