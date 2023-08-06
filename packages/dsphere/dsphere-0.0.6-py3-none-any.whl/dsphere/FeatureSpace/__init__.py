import dsphere.connectors as con
import os
import dsphere.properties.functions as functions

# Set defaults for the Jupyter environment needed to make FeatureSpace behave correctly
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = 'all'
import pandas as pd
pd.set_option('display.max_columns', 300)
pd.set_option('display.max_rows', 300)

import dsphere.defaults as defaults
class dotdict(dict):
    """dot.notation access to dictionary properties"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
DEFAULTS = dotdict(defaults.DEFAULTS)       


class FeaturesetMissingError(Exception):
    pass    

class FeatureSpace:
    
    from dsphere.FeatureSpace.transform import _transform, addColumn, aggregate, dedup, subset, pivot, unpivot, clean, split, cross, merge, concat, sort, findMatches, convolve, update, upsert, createFeatureMatrix, _get_index_col
    from dsphere.FeatureSpace.model import normalize, train, predict, evaluate
    from dsphere.FeatureSpace.view import out, summary, listFeatureSets, view, query, exists
    from dsphere.FeatureSpace.load import loadFiles, load, _loadDataFromDB, _reload
    from dsphere.FeatureSpace.add import addView, addData, _addFeatureSet, addConstant
    from dsphere.FeatureSpace.access import save, delete, copy, Features, Data
    from dsphere.FeatureSpace.metadata import setFlow, setDefaultBatch, _getSaveDirectory, _getTempDirectory, getProjectDirectory, _getFeaturesetLastUpdated, getMemoryUsage, _loadFeatureSetMetadata, _updateFeatureSetMetadata, freeUpMemory, getVariantList, _clearVariantList, _getOutputVariant, _setDependency, _insertDependent, _getVariantCombinations, _getDependencyChain, _getDependents
    
    
    def __init__(self, project_label=None, load_from_file=True, reload=DEFAULTS._DEFAULT_RELOAD,               
        batch=DEFAULTS._NO_BATCH, 
        engine=DEFAULTS._DEFAULT_ENGINE, 
        memory_mode=DEFAULTS._DEFAULT_MEMORY_MODE, 
        disk_mode=DEFAULTS._DEFAULT_DISK_MODE, 
        sources=None, 
        directory=DEFAULTS._DEFAULT_BASE_DIRECTORY, 
        output_mode=DEFAULTS._DEFAULT_OUTPUT_MODE, 
        flow=DEFAULTS._DEFAULT_FLOW,
        dsphere=None):
        
        self.dsphere = dsphere
        self.feature_sets = {}
        self.models = {}
        self.project_label = project_label
        self.last_updated = None
        self.feature_set_metadata = {}
        self.constants = {}
        self.dependency_chain = {}
        self.default_batch = batch
        self.default_reload = reload
        self.default_engine = engine
        self.all_flows = {}
        self._current_flow = None
        self.default_variant = DEFAULTS._DEFAULT_VARIANT
        self.default_datatype = DEFAULTS._DEFAULT_DATATYPE
        self.memory_mode = memory_mode 
        self.disk_mode = disk_mode
        self.output_mode = output_mode
        self.memory_threshold = 25000
        self.sources = sources
        self.connectors = {}
        if sources is not None:
            for source in sources:
                self.connectors[source] = con._GetConnector(sources[source])
            
        #self.connection = None  # No longer owned by this class, instead moved into the Connector class
        self.base_directory = directory

        # Set the filename where this featurespace should be stored
        if self.project_label is not None:
            project_label = self.project_label
        else:
            # TODO: Dynamically figure out which label is not taken already
            project_label = '0'
        # TODO: Change this to .json later once have converted all active FeatureSpaces to use JSON not dill 
        self.filename = 'featurespace_{}.dll'.format(project_label)
        #self.filename = 'featurespace_{}.pkl'.format(project_label)
        self.filepath = os.path.join(self._getSaveDirectory(), self.filename)
        print("FeatureSpace metadata saved to: {}\nFeatureSet data within batch folder: {}".format(self.filepath, self.default_batch))

        if load_from_file:
            self._loadFeatureSetMetadata()
            if not os.path.exists(self.filepath):
                #os.mknod(self.filepath)
                print("Creating initial FeatureSpace file: {}".format(self.filepath))
                self.save()
            #else:
         
        # Set the flow passed in here
        self.setFlow(flow)
        print("Last updated:", self.last_updated)
        
