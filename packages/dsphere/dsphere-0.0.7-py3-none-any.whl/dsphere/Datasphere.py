from dsphere.FeatureSpace import *
from dsphere.DataStream import *
import importlib
from datetime import datetime as dt
import pandas as pd
import sys
from dsphere.properties import plots
from dsphere.properties import functions
import matplotlib.pyplot as plt
import dsphere.connectors as con
import dsphere.defaults as defaults
class dotdict(dict):
    """dot.notation access to dictionary properties"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    
DEFAULTS = dotdict(defaults.DEFAULTS)        

class Datasphere():
    from dsphere.ffuncs import Data, Features, _addFeatureSet, _clearVariantList, _getDependencyChain, _getDependents, _getFeaturesetLastUpdated, _getOutputVariant, _getSaveDirectory, _getTempDirectory, _getVariantCombinations, _insertDependent, _loadDataFromDB, _loadFeatureSetMetadata, _reload, _setDependency, _transform, _updateFeatureSetMetadata, addColumn, addConstant, addData, addView, aggregate, clean, concat, convolve, copy, createFeatureMatrix, cross, dedup, delete, evaluate, exists, findMatches, freeUpMemory, getMemoryUsage, getProjectDirectory, getVariantList, listFeatureSets, load, loadFiles, merge, normalize, out, pivot, predict, query, save, setDefaultBatch, setFlow, sort, split, subset, summary, train, unpivot, update, upsert, view
    from dsphere.dfuncs import reload, _load_config, _create_filename, _convert_ipynb_to_py, _send_email, deploy, _create_log_file, run, on_terminate, list, read, download, archive, restore, archive_files_to_s3, archive_featureset, restore_featureset
    
    def __init__(self, constants=None, status_log=None, config=None, project_label=None, load_from_file=True,
                 reload=DEFAULTS._DEFAULT_RELOAD,
                 batch=DEFAULTS._NO_BATCH,
                 engine=DEFAULTS._DEFAULT_ENGINE,
                 memory_mode=DEFAULTS._DEFAULT_MEMORY_MODE,
                 disk_mode=DEFAULTS._DEFAULT_DISK_MODE,
                 sources=None,
                 path=DEFAULTS._DEFAULT_BASE_DIRECTORY,
                 output_mode=DEFAULTS._DEFAULT_OUTPUT_MODE,
                 flow=DEFAULTS._DEFAULT_FLOW,
                 dsphere=None):
        
        self.memory_mode = memory_mode
        self.output_mode = output_mode
        self.disk_mode = disk_mode
        
        #Import in constants
        sys.path.append(path)
        
        constants_imported = False
        if constants is not None:
            try:
                constants = importlib.import_module(constants)
                constants_imported = True
                
            except:
                print('ERROR IMPORTING CONSTANTS')
                constants = None
                
        # Get today's date
        self.TODAY = dt.today()
        
        if constants_imported:
            self.fs = FeatureSpace(project_label or constants.PROJECT or None,
                      batch=batch or constants.BATCH or None,
                      directory=path or constants.DIRECTORY or None,
                      flow=flow or constants.FLOW or None,
                           memory_mode='',
                           output_mode='',
                           disk_mode='',
                           dsphere= self
                     )
        else:
            self.fs = FeatureSpace(project_label or None,
                      batch=batch or None,
                      directory=path or None,
                      flow=flow or None,
                           memory_mode='',
                           output_mode='',
                           disk_mode='',
                           dsphere= self
                     )
        self.ds = DataStream(directory=path,
                    status_logfile=status_log,
                    config=config)
        self.Plots = dotdict({})
        self.Functions = functions
        self.Constants = constants
        self.Models = self.fs.models
        self.datastream_config = self.ds.datastream_config
        self.dataflows = self.ds.dataflows
        self.alerts = self.ds.alerts
        self.parameters = self.ds.parameters
        self.streams = self.ds.streams
        self.schedule = self.ds.schedule
        self.executors = self.ds.executors
        self.sources = self.ds.sources
        self.connectors = self.ds.connectors
        self.connector_definitions = self.ds.connector_definitions
        self.syncs = self.ds.syncs
        self.modelers = self.ds.modelers
        self.FeatureSpace = self.ds.FeatureSpace
        self.feature_sets = self.fs.feature_sets
        self.models = self.fs.models
        self.project_label = self.fs.project_label
        self.feature_set_metadata = self.fs.feature_set_metadata
        self.constants = self.fs.constants
        self.dependency_chain = self.fs.dependency_chain
        self.all_flows = self.fs.all_flows
        self.connectors = self.fs.connectors

    #Create Plot object and store in Plots
    def Plot(self, title, label, xlabel, ylabel=None, *args, **kwargs):
        self.Plots[title] = plots.Plot(self, title, label, xlabel, ylabel, *args, **kwargs)

