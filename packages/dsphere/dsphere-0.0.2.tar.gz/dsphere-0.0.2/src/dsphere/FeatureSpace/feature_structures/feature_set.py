import pandas as pd
import dill
import numpy as np
import decimal as dec
import matplotlib.pyplot as plt
from scipy.sparse import coo_matrix
import os
from os import listdir
from os.path import isfile, join
import re
import json
import datetime as dt
#from datetime import datetime as dt
import gc
import dask
import dask.dataframe as dd
import dask.array as da
import pyarrow as pa
import pyarrow.parquet as pq
from IPython.display import display
import copy
        
# Wrapper around a Dataframe
# Also contains the set of operations/transformations needed to get from input data to processed outputs


from dsphere.FeatureSpace.feature_structures.feature_data import FeatureData
from dsphere.FeatureSpace.feature_structures.feature_matrix import FeatureMatrix

from dsphere.properties.functions import *

class FeatureSet(FeatureData):
    
    _COL_TYPE_FLAGS_FORCED = 'f'
    _COL_TYPE_FLAGS_INFERRED = 'i'
    _MAX_ROWS_IN_VIEW = 300
    _MAX_COLS_IN_VIEW = 100
    __feature_type__ = 'FeatureSet'
    
    def __init__(self, save_directory=None, label=None, project=None, batch=None, space=None):
        FeatureData.__init__(self, save_directory=save_directory, label=label, project=project, batch=batch, datatype='dataframe', space=space)

        self.this_depends_on = []
        self.transformer_function = []
        self.depends_on_this = []
        self.feature_cols = set()
        self.index_cols = set()
        self.label_cols = set()
        self.types = {}
        self.schemas = {}
        self.dataset_shapes = {}
        self.source_files = {}
    
    def _getDefinition(self, print_out=False):
        definition = super()._getDefinition(print_out=print_out)
        # 10/2/21: Stop pushing these to the FS metadata file, only include in the featureset's metadata file
        ##definition['index_cols'] = list(self.index_cols)
        ##definition['feature_cols'] = list(self.feature_cols)
        ##definition['label_cols'] = list(self.label_cols)
        #definition['types'] = self.types if hasattr(self, 'types') else {}
        definition['schemas'] = self.schemas if hasattr(self, 'schemas') else {}
        definition['dependents'] = self.depends_on_this
        definition['depends_on'] = self.this_depends_on
        definition['transformer_fn'] = self.transformer_function
        definition['dataset_shapes'] = self.dataset_shapes
        return definition
        
    def _setDefinition(self, status_dict):
        super()._setDefinition(status_dict=status_dict)
        # 10/2/21: Keep temporarily for backwards compatibility to load these when they're only in FS metadata file
        self._addColumnTypes(index_cols=status_dict.get('index_cols', None),
                            feature_cols=status_dict.get('feature_cols', None),
                            label_cols=status_dict.get('label_cols', None))
        #self.types = status_dict.get('types', {})
        self.schemas = status_dict.get('schemas', {})
        self.depends_on_this = status_dict['dependents']
        self.this_depends_on = status_dict['depends_on']
        self.transformer_function = status_dict['transformer_fn']                                  
        self.dataset_shapes = status_dict.get('dataset_shapes', None)                                  

    def _getMetadata(self, variant=None):
        metadata = super()._getMetadata(variant=variant)
        metadata['index_cols'] = list(self.index_cols)
        metadata['feature_cols'] = list(self.feature_cols)
        metadata['label_cols'] = list(self.label_cols)
        metadata['types'] = self.types if hasattr(self, 'types') else {}
        #metadata['schemas'] = self.schemas if hasattr(self, 'schemas') else {}
        metadata['dependents'] = self.depends_on_this
        metadata['depends_on'] = self.this_depends_on
        metadata['transformer_fn'] = self.transformer_function
        metadata['dataset_shapes'] = self.dataset_shapes
        metadata['source_files'] = self.source_files
        return metadata
    
    def _loadMetadata(self, variant=None):
        metadata = super()._loadMetadata(variant=variant)
        
        # Load parts of the metadata for FeatureSets into the object
        self.types = metadata.get('types', {})
        self.source_files = metadata.get('source_files', {})
        
        # 10/2/21: Start loading these from the featureset's metadata file if present there
        if 'dataset_shapes' in metadata and variant in metadata['dataset_shapes']:
            self._setDatasetShape(copy.deepcopy(metadata['dataset_shapes'][variant]),
                                  variant=variant,
                                  child='*')
            
        self._addColumnTypes(index_cols=metadata.get('index_cols', None),
                            feature_cols=metadata.get('feature_cols', None),
                            label_cols=metadata.get('label_cols', None)
                            )
        
    # Returns a schema if associated with this variant/child
    def _getSchema(self, variant=None, child=None):
        if variant in self.schemas:
            if child in self.schemas[variant]:
                saved_schema_path = self.schemas[variant][child]
                self.out("...got saved_schema_path=", saved_schema_path)
 
                # Load the schema from this file
                if saved_schema_path is not None and saved_schema_path!='':
                    if os.path.exists(saved_schema_path):
                        self.out("Reading schema in from file:", saved_schema_path)
                        with open(saved_schema_path, 'rb') as fin:
                            new_schema = dill.load(fin)
                            self.out("...read this schema from file:", new_schema)
                            return new_schema
        return None
        
    # Stores the given schema for this variant/child
    def _saveSchema(self, new_schema, variant=None, child=None):
        if new_schema is None:
            return
        
        # Write this schema serialized to file
        schema_serialized = new_schema.serialize()
        filepath = self.last_save_filepaths[variant]
        if filepath is not None:
            schema_filename = 'schema{}.dll'.format('' if child is None else '_'+child)
            schema_path = os.path.join(filepath, schema_filename)
            self.out("Saving schema (variant={}, child={}) into file: {}".format(variant, child, schema_path))
            with open(schema_path, 'wb') as fout:
                dill.dump(new_schema, fout)
                #fout.write(schema_serialized)

        # Keep track of the file containing the schema
        if variant not in self.schemas:
            self.schemas[variant] = {}
        self.schemas[variant][child] = schema_path
        
    # New on 12/19/20: Keep track of source files
    def _addSourceFile(self, source_filename, variant=None):
        # For now just a simple wrapper to add this to the list of source files
        if variant not in self.source_files:
            self.source_files[variant] = []
        self.source_files[variant].append(source_filename)
        print("SOURCE FILES:")
        print(self.source_files)
        
        # In the future we could embellish this source file with other info such as its source location (SFTP?) or shape
        
        # Then need to resave the featureset's metadata
        self._saveMetadata(variant=variant)
        
    def _resetSourceFiles(self, variant=None):
        if not hasattr(self, 'source_files'):
            self.source_files = {}
        self.source_files[variant] = [] 
                
    # Returns a part of the the data that meet the given where condition(s)
    # Can pass = (exact match) or ~= (partial match) inside 'where'
    # also can pass in a list of conditions (to AND together) or ' AND ' or ' & ' or ' and ': where='var1=val1 & var2=val2'
    # Note: Not supporting OR conditions yet here, too complex.
    # TODO: Allow escaping of reserved tokens like /= /AND /& /~ inside the query conditions
    def query(self, where='', variant='*', child='*'):
        if isinstance(where, str):
            where_array = [where]
        else:
            where_array = where
            
        # Check for AND, and, or & instead of a list of conditions
        where_new_array = []
        for where_cond in where_array:
            where_cond_split = [where_cond]
            if ' AND ' in where_cond:
                where_cond_split = where_cond.split(' AND ')
            elif ' and ' in where_cond:
                where_cond_split = where_cond.split(' and ')
            elif ' & ' in where_cond:
                where_cond_split = where_cond.split(' & ')
            for where_cond_sub in where_cond_split:
                where_new_array.append(where_cond_sub.strip())
        print("Using AND conditions:", where_new_array)
            
        # Get the list of variants to iterate through
        if variant=='*':
            all_variants = self.variants()
        elif isinstance(variant, str):
            all_variants = [variant]
        else:
            all_variants = variant   
            
        all_results = {}
        num_results = 0
        last_var = None
        # Get results of applying the where condition on each variant
        for this_var in all_variants:
            this_df = self.getData(variant=this_var, child=child)
            this_df_where = this_df
            # Iterate through all 1+ where conditions
            for where_condition in where_new_array:
                # Parse out the where condition to apply
                where_split = where_condition.split('=')
                where_var = where_split[0]
                where_val = where_split[1] if len(where_split)>1 else None
                
                # Try to convert the where_val into a numeric value
                #try:
                #    where_val = pd.to_numeric(where_val)
                #    print("...treating value {} as a number".format(where_val))
                #except:
                #    print("...treating value '{}' as a string".format(where_val))
                    
                # Apply each iteratively
                print("...limiting '{}' to rows where {}={}".format(self.label, where_var, where_val))
                this_df_where = this_df_where[this_df_where[where_var]==where_val]
                print("...result has {} rows".format(this_df_where.shape[0]))
                
            all_results[this_var] = this_df_where
            num_results += 1
            last_var = this_var
         
        # Returns {'var1':<dataframe1>, 'var2':<dataframe2>} if there are >1 variant results to return
        if len(all_results)>1:
            return all_results
        else:
            # Otherwise just return the one result
            return all_results[last_var]
    
    # Can pass a string or list of strings to query
    def view(self, *args, **kwargs):
        query = kwargs.get('query', args or '')
        variant = kwargs.get('variant', '*')
        child = kwargs.get('child', '*')
        result = kwargs.get('results', None)
        
        # Get the list of variants to iterate through
        if variant=='*':
            all_variants = self.variants()
        elif isinstance(variant, str):
            all_variants = [variant]
        elif variant is None:
            all_variants = [None]
        else:
            all_variants = variant
            
        query_list = []
        if isinstance(query, str):
            query_list = [query]
        elif query is not None:
            query_list = query
        elif args is not None:
            query_list = args
        if len(query_list)>1:
            print("QUERY:", query_list)
            
        all_results = {}
        
        # Iterate through the 1+ queries to run on this FeatureSet
        for this_query in query_list:
            this_query_array = this_query.split(':')
            query_type = this_query_array[0]
            query_val = this_query_array[1] if len(this_query_array)>1 else None
            all_results[this_query] = []
            
            # If query is 'shape' or 'size', just get the shape of the overall Featureset
            if query_type in ['shape', 'size']:
                shape = self.shape(memory_mode='normal')
                this_desc = "Shape for Featureset:"
                
                # Store each result
                all_results[this_query].append({'variant':'*',
                                                'child':'*',
                                                'description':this_desc,
                                               'result':shape,
                                               'error':None
                                              })
                
            else:
                # Otherwise iterate through each variant                                
                for this_var in all_variants:
                    #print("\n===================")
                    #print("VIEWING '{}' for data set '{}', variant '{}'".format(query, self.label, this_var))            
                    data_all_children = self.getData(variant=this_var, child=child)
                    # Create a dict to iterate through for each child below
                    # Note: This is to handle the variably-typed output of getData()
                    if not isinstance(data_all_children, dict):
                        data_all_children = {child: data_all_children}

                    for this_child in data_all_children:
                        #print("CHILD: '{}'".format(this_child))
                        data = data_all_children[this_child]

                        # Check if the child is a FeatureMatrix, since some queries aren't supported for them
                        is_matrix = hasattr(data, '__feature_type__') and data.__feature_type__=='FeatureMatrix'

                        this_result = None
                        this_desc = None
                        this_error = None
                        with pd.option_context('display.max_rows', self._MAX_ROWS_IN_VIEW):
                            # Have a single dataset
                            if query_type in ['', 'head', 'top', 'first', 'shape', 'size']: 
                                num_rows = None if query_val is None else int(query_val)
                                #print(self.head(num_rows))
                                # Note: Assuming we should calculate the full shape when this is called
                                shape = self.shape(variant=this_var, child=this_child, memory_mode='normal')
                                #this_desc = "Shape: {}, Type: {}".format(, type(data))
                                #print("Type:", type(self.getData(variant=variant, child=this_child)))
                                #print("Type:", type(data))
                                if query_type in ['', 'head', 'top', 'first']:
                                    this_desc = "Head for dataset of type: {}, shape: {}".format(type(data), shape)
                                    this_result = self.head(num_rows, variant=this_var, child=this_child)
                                    #display(self.head(num_rows, variant=this_var, child=this_child))
                                else:
                                    this_desc = "Shape for dataset of type: {}".format(type(data))
                                    this_result = shape


                            elif query_type=='nulls' or query_type=='null' and not is_matrix:
                                if query_val is None:
                                    this_desc = "Nulls for each column:"
                                    null_counts = data.isna().sum().compute() if isinstance(data, dd.DataFrame) else data.isna().sum() if isinstance(data, pd.DataFrame) else None
                                    if null_counts is not None:
                                        #shape = self.shape(variant=this_var, child=this_child, memory_mode='normal')
                                        num_rows = data.shape[0]
                                        null_counts_df = pd.DataFrame(null_counts)
                                        null_counts_df.columns = ['nulls']
                                        null_counts_df['non-nulls'] = null_counts_df['nulls'].apply(lambda x: num_rows-x)
                                        this_result = null_counts_df
                                    else:
                                        this_result = 'CANNOT COMPUTE NULLS FOR A FEATURE MATRIX'
    #                                 this_result = data.isna().sum().compute() if isinstance(data, dd.DataFrame) else data.isna().sum() if isinstance(data, pd.DataFrame) else 'CANNOT COMPUTE NULLS FOR A FEATURE MATRIX'
                                else:
                                    this_desc = "Nulls for '{}':".format(query_val)
                                    this_result = data[query_val].isna().sum().compute() if isinstance(data, dd.DataFrame) else data[query_val].isna().sum() if isinstance(data, pd.DataFrame) else 'CANNOT COMPUTE NULLS FOR A FEATURE MATRIX'

                            elif query_type=='blank' or query_type=='blanks' and not is_matrix:
                                if query_val is None:
                                    this_desc = "Blanks:"
                                    this_result = (data=='').sum().compute() if isinstance(data, dd.DataFrame) else (data=='').sum() if isinstance(data, pd.DataFrame) else 'CANNOT COMPUTE BLANKS FOR A FEATURE MATRIX'
                                else:
                                    this_desc = "Blanks for '{}':".format(query_val)
                                    this_result = (data[query_val]=='').sum().compute() if isinstance(data, dd.DataFrame) else (data[query_val]=='').sum() if isinstance(data, pd.DataFrame) else 'CANNOT COMPUTE BLANKS FOR A FEATURE MATRIX'

                            elif query_type in ['min', 'mins'] and not is_matrix:
                                if query_val is None:
                                    if data.dtype.name == 'category':
                                        this_result = data.cat.as_ordered().min()
                                    else:
                                        this_result = data.min().compute() if isinstance(data, dd.DataFrame) else data.min()
                                    this_desc = "Min values of all {} columns:".format(this_result.shape[0])
                                else:
                                    if isinstance(data, dd.DataFrame):
                                        this_result = data[query_val].min().compute()
                                        this_desc = "Min values of '{}' column:".format(query_val)
                                    elif isinstance(data, pd.DataFrame):
                                        if data[query_val].dtype.name == 'category':
                                            this_result = data[query_val].cat.as_ordered().min()
                                        else:
                                            this_result = data[query_val].min()
                                        this_desc = "Min values of '{}' column:".format(query_val)
                                #display(mins)

                            elif query_type in ['max', 'maxs'] and not is_matrix:
                                if query_val is None:
                                    if isinstance(data, dd.DataFrame):
                                        this_result = data.max().compute()
                                    elif isinstance(data, pd.Series) and data.dtype.name == 'category':
                                        this_result = data.cat.as_ordered().max()
                                    else:
                                        this_result = data.max()
                                    this_desc = "Max values of all {} columns:".format(this_result.shape[0])
                                else:
                                    if data[query_val].dtype.name == 'category':
                                        this_result = data[query_val].cat.as_ordered().max()
                                    else:
                                        this_result = data[query_val].max().compute() if isinstance(data, dd.DataFrame) else data[query_val].max()
                                    this_desc = "Max values of '{}' column:".format(query_val)                   
                                #display(maxs)

                            elif query_type in ['cols', 'columns', 'types', 'dtypes', 
                                                'lengths', 'len', 'length', 'hist', 'histogram']:
                                columns_list = self.columns(variant=this_var, child=child) #list(data.columns)
                                if query_type in ['cols', 'columns']:
                                    if len(columns_list) > self._MAX_ROWS_IN_VIEW:
                                        this_desc = "Columns ({} total, showing first {}):\n".format(len(columns_list),
                                                                                                     self._MAX_ROWS_IN_VIEW)
                                        this_result = columns_list[:self._MAX_ROWS_IN_VIEW]
                                    else:
                                        this_desc = "Columns ({}):\n".format(len(columns_list)) 
                                        this_result = columns_list

                                if query_type in ['types', 'dtypes'] and not is_matrix:
                                    if query_val is not None:
                                        if isinstance(data, dd.DataFrame):
                                            type_counts = data[query_val].map(type).value_counts().compute()
                                            this_result = type_counts
                                        elif isinstance(data, pd.DataFrame):
                                            type_counts = data[query_val].map(type).value_counts()
                                            this_result = type_counts
                                        else:
                                            this_error = "WARNING! view() does not support 'types' on anything but a dask or pandas dataframe."
                                        this_desc = "Data types for column '{}':".format(query_val)
                                    else:
                                        if isinstance(data, dd.DataFrame) or isinstance(data, pd.DataFrame):
                                            this_result = pd.DataFrame(data.dtypes)
                                        elif 'FeatureMatrix' in str(type(data)):
                                            this_result = data.getMatrix()
                                        else: 
                                            this_result = type(data)
                                        this_desc = "Data types for {} columns, data type is {}:".format(len(columns_list), type(data))
                                    #display(types_df)
                                if query_type in ['lengths', 'length', 'len'] and not is_matrix:
                                    if query_val is not None:
                                        if isinstance(data, dd.DataFrame) or isinstance(data, pd.DataFrame):
                                            #non_null_vals = data[data[query_val]==data[query_val]][query_val]
                                            query_vals = data[query_val]
                                            str_query_vals = query_vals[query_vals.apply(lambda x: isinstance(x, str))]
                                            if isinstance(data, dd.DataFrame):
                                                type_counts = str_query_vals.map(len).value_counts().compute()
                                            else:
                                                type_counts = str_query_vals.map(len).value_counts()
                                            this_result = type_counts
                                        else:
                                            this_error = "WARNING! view() does not support 'lengths' or 'len' on anything but a dask or pandas dataframe."
                                        this_desc = "Lengths for column '{}':".format(query_val)
                                    else:
                                        this_error = "WARNING! Must pass a column with 'lengths' or 'len'"

                                if query_type in ['hist', 'histogram']:
                                    if query_val is not None:
                                        if isinstance(data, dd.DataFrame) or isinstance(data, pd.DataFrame):
                                            #non_null_vals = data[data[query_val]==data[query_val]][query_val]
                                            query_vals = data[query_val]
                                            hist_counts = plt.hist(query_vals)
                                            plt.show();
                                            this_result = hist_counts
                                        else:
                                            this_error = "WARNING! view() does not support 'hist' or 'histogram' on anything but a dask or pandas dataframe."
                                        this_desc = "Histogram of values in column '{}':".format(query_val)
                                    else:
                                        this_error = "WARNING! Must pass a column with 'hist' or 'histogram'"

                            elif query_type in ['dups', 'num_dups', 'counts', 'count', 'uniques'] and not is_matrix:
                                if query_val is None:
                                    if query_type == 'uniques':
                                        # Output the # unique values for all columns
                                        if isinstance(data, dd.DataFrame):
                                            this_result = data.nunique().compute()
                                            this_desc = "# Unique Values of all {} Columns:\n".format(this_result.shape[0])
                                        elif isinstance(data, pd.DataFrame):
                                            this_result = data.nunique()
                                            this_desc = "# Unique Values of all {} Columns:\n".format(this_result.shape[0])
                                        else:
                                            this_result = 'CANNOT COMPUTE UNIQUES FOR A FEATURE MATRIX'
                                            this_desc = ""
                                        #display(nuniques)
                                    else:
                                        this_error = "ERROR! CANNOT CALCULATE WITHOUT A SINGLE COLUMN NAME"
                                    #return None
                                elif not is_matrix:
                                    # query_val is not None so calculate counts/uniques for one column
                                    value_counts = None
                                    if isinstance(data, dd.DataFrame) and data.compute().shape[0]>0:
                                        value_counts = data[query_val].value_counts().compute()
                                        this_result = value_counts
                                    elif isinstance(data, pd.DataFrame) and data.shape[0]>0:
                                        value_counts = data[query_val].value_counts()
                                        this_result = value_counts
                                    else:
                                        this_error = "WARNING! view() does not support 'dups' or 'counts' on anything but a dask or pandas dataframe."
                                        #return None
                                    if value_counts is not None:
                                        value_dups = value_counts[value_counts>1]
                                        if query_type == 'dups':
                                            this_desc = "Values of '{}' with Duplicates Rows:\n".format(query_val)
                                            this_result = value_dups
                                        elif query_type == 'num_dups':
                                            this_desc = "Total # Values of '{}' with Duplicate Rows:".format(query_val)
                                            this_result = value_dups.shape[0]
                                        elif query_type == 'count' or query_type == 'counts':
                                            this_desc = "# Rows of each Value of '{}' (out of {} unique values):".format(query_val, value_counts.shape[0])
                                            this_result = value_counts.to_frame()

                                        elif query_type == 'uniques':
                                            # Per the logic chain above, this will definitely have a query_val
                                            this_desc = "# Unique Values of '{}':".format(query_val)
                                            this_result = value_counts.shape[0]

                        # Store each result
                        all_results[this_query].append({'variant':this_var,
                                                   'child':this_child,
                                                   'description':this_desc,
                                                   'result':this_result,
                                                   'error':this_error
                                                  })
                    
        # Now output all the results using the given result flag
        if result is None:
            for one_query in all_results:
                one_result_list = all_results[one_query]
                print("\n===================")
                print("VIEWING '{}' for data set '{}' last updated {} in flow {}".format(one_query, 
                                                                                        self.label,
                                                                                        self.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
                                                                                        self.last_updated_flows))
                prev_variant = None
                for one_result in one_result_list:
                    one_variant = one_result['variant']
                    one_child = one_result['child']
                    if one_variant!=prev_variant:
                        print("\n------------------")
                    if one_result['description'] is not None:
                        print("\nVARIANT = '{}', CHILD = '{}':".format(one_variant, one_child))
                        print(one_result['description'])
                    if one_result['result'] is not None:
                        display(one_result['result'])
                    if one_result['error'] is not None:
                        print(one_result['error'])
                    prev_variant = one_variant

                
        elif result=='dataframe' or result=='df' or result=='data':
            if len(all_results)==1:
                # Just one query
                if len(all_results[query])==1:
                    # Just one result so just return it
                    return all_results[query][0]['result']
                else:
                    # Multiple results for one query
                    return all_results[query]
            else:
                # Multiple queries
                return all_results
            
        else:
            print("ERROR: Cannot support result='{}'. Returning all results as-is.".format(result))
            return all_results
            
        
    @staticmethod
    def getDatasetShape(df, memory_mode='low'):
        # Thanks to: https://stackoverflow.com/questions/41902069/slow-len-function-on-dask-distributed-dataframe
        from multiprocessing.pool import ThreadPool
        
        def threadedGetShape(df, get_num_cols=True):
            pool=ThreadPool(10)
            #with dask.config.set(scheduler='threads'):  # no cluster, just local threads
            with dask.config.set(pool=pool):
                rows = len(df)
                pool.close()
                pool.join()
                if get_num_cols:
                    cols = len(df.columns)
                    return (rows, cols)
                else:
                    return (rows,)
            
        #print("in getDatasetShape({})".format(type(df)))
        if df is None:
            return None
        if isinstance(df, dd.DataFrame):
            if memory_mode=='low':
                # Don't run compute() if memory_mode is 'low' 
                child_shape = ('UNKNOWN', df.shape[1])
            else:
                #print("...converting dask to pandas for getDatasetShape")
                df_pandas = df.compute(scheduler='threads', num_workers=20)
                #print("...calling threadedGetShape")
                child_shape = threadedGetShape(df_pandas, True)
                #print("......done")
        elif isinstance(df, dd.Series):
            if memory_mode=='low':
                child_shape = ('UNKNOWN', df.shape[1])
            else:
                child_shape = threadedGetShape(df, False)
        elif hasattr(df, '__feature_type__') and df.__feature_type__=='FeatureMatrix':
            #print(df)
            child_shape = df.getShape()
        else:
            # Then assume this has a shape attribute (pandas dataframe/series, numpy matrix, etc.)
            return df.shape

        return child_shape
    
    def _getDatasetShape(self, variant='*', child='*'):
        if variant=='*':
            return self.dataset_shapes
        elif variant in self.dataset_shapes:
            if child=='*':
                return self.dataset_shapes[variant]
            elif child in self.dataset_shapes[variant]:
                curr_shape = self.dataset_shapes[variant][child]
                if curr_shape is None:
                    return (0,0)
                else:
                    return curr_shape
                
        # Return null if there isn't a shape for the given variant or child
        return None
    
    # Send in tuple to be the new shape for one variant/child
    # If child='*' then set shape for the entire variant
    # If variant='*' then set shape for entire featureset
    # Note: We need to be able to convert between shapes that are tuples, dicts, and dicts of dicts
    def _setDatasetShape(self, new_shape, variant=None, child=None):
        self.out(f"...in _setDatasetShape with new_shape={new_shape}, variant={variant}, child={child}")
        if variant=='*':
            # Set shape for the whole featureset
            self.dataset_shapes = new_shape
        else:
            # For backwards-compatibility if shapes were stored without being in a dict, convert to a dict structure
            if isinstance(self.dataset_shapes, list) or isinstance(self.dataset_shapes, tuple):
                self.dataset_shapes = {None: {None: self.dataset_shapes}}
            elif isinstance(self.dataset_shapes, dict) and len(self.dataset_shapes)==0:
                self.dataset_shapes = {variant: {child: new_shape}}

            if child=='*':
                # Set shape for a whole variant and keep the other variants
                self.dataset_shapes[variant] = new_shape
            else:
                if variant not in self.dataset_shapes:
                    self.dataset_shapes[variant] = {}
                # Set the shape for the variant+child and don't delete other variant/child shapes already stored        
                self.dataset_shapes[variant][child] = new_shape 
    
    # Send in (500, 0) to grow the # of rows by 500 but 0 new cols
    def _incrementDatasetShape(self, shape_increment, variant=None, child=None):
        curr_dataset_shape = self._getDatasetShape(variant=variant, child=child)
        if curr_dataset_shape is not None:
            new_dataset_shape = (curr_dataset_shape[0]+shape_increment[0],
                                 curr_dataset_shape[1]+shape_increment[1])
            
            self._setDatasetShape(new_dataset_shape, variant=variant, child=child)
        
    def _getDatatype(self):
        return "Featureset (dataframe)"
        
    # NO LONGER RELEVANT Return shape tuple if a single variant provided
    # NO LONGER RELEVANT Return dict of variant:tuple pairs if '*' or a list of variants is provided
    # Note change on 4/3/19 to make default variant='*' instead of None
    # Change on 4/19/19 to make this alwasy return a dict structure {variant1: {child1: shapetuple}}
    def shape(self, variant='*', child='*', memory_mode=None):
        #print("Getting shape for feature_set '{}', variant '{}', child '{}'".format(self.label, variant, child))
        
        # Check the memory mode
        #MEMORY_MODE = self.space.memory_mode if memory_mode is None else memory_mode
        #print("Using MEMORY_MODE='{}'".format(MEMORY_MODE))
        
        if self.dataset_shapes is None:
            self.dataset_shapes = {}
            
#         # Don't reload, use the stored shapes (unless missing a shape)
#         print("Using the stored shapes...")

        # Construct a shapes dict based on the given variant/child
        if variant=='*':
            variant_list = self.variants()
        elif isinstance(variant, list):
            variant_list = variant
        elif variant is None:
            variant_list = [None]
        elif isinstance(variant, str):
            variant_list = [variant]
        else:
            self.out("WARNING! Invalid variant format passed to shape()", type='warning')
            variant_list = []

        # Iterate through the variants
        all_shapes = {}
        for this_variant in variant_list:
            shapes_this_variant = self._getDatasetShape(variant=this_variant)
            #if this_variant not in self.dataset_shapes:
            # Check if this variant actually exists
            #if this_variant in self.variants():
                # Just start the dict, and the below code will calculate each child's shape
            #    self.dataset_shapes[this_variant] = {}
            #else:
            if shapes_this_variant is None:
                # Degrade gracefully by returning None and printing error if a given variant is not found
                self.out("ERROR! Could not find variant='{}' in '{}'. Exiting shape()".format(this_variant, self.label),
                        type='error')
                return None

            all_shapes[this_variant] = {}

            # Now determine which children to iterate through
            if child=='*':
                child_list = self.children(variant=this_variant)
            elif isinstance(child, list):
                child_list = child
            elif child is None:
                child_list = [None]
            elif isinstance(child, str):
                child_list = [child]
            else:
                self.out("WARNING! Invalid child format passed to shape()", type='warning')
                child_list = []

            # Iterate through the children to find their shapes
            for this_child in child_list:
                if this_child not in shapes_this_variant: #self.dataset_shapes[this_variant]:
                    # If this child does not have a known shape, need to calculate it
                    this_child_data = self.getData(variant=this_variant, child=this_child)
                    if this_child_data is not None:
                        # Store this shape for use later
                        new_dataset_shape = FeatureSet.getDatasetShape(this_child_data, memory_mode=memory_mode)
                        self._setDatasetShape(new_dataset_shape, variant=this_variant, child=this_child)
                        #self.dataset_shapes[this_variant][this_child] = FeatureSet.getDatasetShape(this_child_data, 
                        #                                                                           memory_mode=memory_mode)    
                    else:
                        # Degrade gracefully by returning None and printing error if a given child is not found
                        self.out("ERROR! Could not find child='{}' for variant='{}' in '{}'. Exiting shape()"\
                              .format(this_child, this_variant, self.label), type='error')
                        return None

                # Return the shape for this child/variant
                all_shapes[this_variant][this_child] = self._getDatasetShape(variant=this_variant, child=this_child)
                #all_shapes[this_variant][this_child] = self.dataset_shapes[this_variant][this_child]

        # Return the one or more shapes queried
        if len(variant_list)>1 or (len(variant_list)==1 and variant_list[0] is not None):
            return all_shapes
        elif len(child_list)>1:
            return all_shapes[variant_list[0]]
        else:
            return all_shapes[variant_list[0]][child_list[0]]
        #return all_shapes               
        
    # Return true if this featureset is empty
    def isEmpty(self, variant='*', child='*'):
        curr_shape = self.shape(variant=variant, child=child)
        
        if curr_shape is None or curr_shape=={} or curr_shape==[]:
            return True
        elif isinstance(curr_shape, dict):
            # The shape dict could have keys=variants or keys=children
            for curr_shape_key, curr_shape_value in curr_shape.items():
                if isinstance(curr_shape_value, dict):
                    # Then curr_shape_key is a variant, so iterate through the children
                    if variant=='*' or curr_shape_key==variant or curr_shape_key in variant:
                        for curr_child, curr_child_shape in curr_shape_value.items():
                            # Return false if the shape for any child is non-empty
                            if len(curr_child_shape)>0 and curr_child_shape[0]>0:
                                return False
                elif len(curr_shape_value)>0 and curr_shape_value[0]>0:
                    # Just check the shape of each child if it's non-empty
                    return False
        else:
            # Assume just have the shape of the overall featureset or the given variant/child
            if len(curr_shape)>0 and curr_shape[0]>0:
                return False
        
        # If none of the above apply, then it's empty
        return True
                    
        
    # Return head dataframe if a single variant provided
    # Return dict of variant:head pairs if '*' or a list of variants is provided
    def head(self, n=5, variant='*', child='*'):
        if n is None:
            n = 5
        
        def getDatasetHead(df, child, n):
            if isinstance(df, pd.DataFrame) or isinstance(df, dd.DataFrame):
                return df.head(n=n)
            elif hasattr(df, '__feature_type__') and df.__feature_type__=='FeatureMatrix':
                #print("Getting head for FeatureMatrix")
                return df.head(n)
            return None
   
        data_dict = self.getData(variant=variant, child=child)
        if data_dict is None:
            self.out("WARNING: Dataframe is null, cannot return head", type='warning')
            return None
        if isinstance(data_dict, dict):
            heads = {}
            #print("Got dict")
            # Then there are multiple variants and/or multiple children
            for var in data_dict:
                this_dict = data_dict[var]
                #print("...key:", var)
                if isinstance(this_dict, dict):
                    #print('...got another dict')
                    # Then there are multiple variants and multiple children
                    this_var_heads = {}
                    for child in this_dict:
                        #print("...child:",child)
                        # Iterate through each child
                        child_data = this_dict[child]
                        child_head = getDatasetHead(child_data, child, n)
                        this_var_heads[child] = child_head
                    heads[var] = this_var_heads
                else:
                    # Then there's only one variant and one/multiple children, so get its head
                    #print(this_dict)
                    child_head = getDatasetHead(this_dict, var, n)
                    heads[var] = child_head

            # Return the dict of shapes
            return heads[None] if len(heads)==1 and None in heads else heads

        else:
            #print("Got single dataset")
            # Then there's only one variant/child
            return getDatasetHead(data_dict, child, n)
    
    # Returns dataframe or numpy/scipy matrix of columns provided within this FeatureSet (if single variant given)
    # Returns dict of variant:data pairs if '*' or a list of variants is provided
    # If child='*' then this will find the columns in whatever child they are in
    # If child is specified, this will look only in that child for the columns
    # If columns are found in both the parent dataframe and child matrices, the result will be a dataframe
    def getColumns(self, columns, variant='*', child='*'):
        columns = [columns] if isinstance(columns, str) else columns
        
        # First infer where the given columns can be found in each variant
        all_columns = self.columns(variant=variant, child=child)
        if isinstance(all_columns, list):
            # Just check one child/variant
            columns_found_set = set([col for col in all_columns if col in columns])
            columns_not_found_set = set(columns) - columns_found_set
            
            # Make sure all the columns can be found
            if len(columns_not_found_set)>0:
                self.out("ERROR: Some columns requested in getColumns() were not found in variant={}, child={}: {}".format(columns_not_found_set, variant, child), type='error')
                raise
                
            else:
                # Get the columns of data from the given child
                data = self.getData(variant=variant, child=child)
                if isinstance(data, pd.DataFrame):
                    return data[columns]
                elif isinstance(data, dd.DataFrame):
                    return data[columns].compute()
                elif hasattr(data, '__feature_type__') and data.__feature_type__=='FeatureMatrix':
                    return data.getColumns(columns)
            
        elif isinstance(all_columns, dict):
            # Check within all variants/children returned
            # and handle the ambiguity of what's returned here (dict vs dict of dicts)
            print("Cannot handle multiple variants/children yet")
            return None
        
        
    # Return list of columns if a single variant provided
    # Return dict of variant:columns pairs if '*' or a list of variants is provided
    # If child='*' and there are multiple children, the columns of all of them are combined together
    def columns(self, variant='*', child='*'):
        def getDatasetColumns(df):
            if isinstance(df, pd.DataFrame) or isinstance(df, dd.DataFrame):
                return list(df.columns)
            elif hasattr(df, '__feature_type__') and df.__feature_type__=='FeatureMatrix':
                return df.columns()
            elif isinstance(df, dict):
                return df['columns']
            else:
                return None
            
        data_dict = self.getData(variant=variant, child=child)
        if data_dict is None:
            self.out("WARNING: Dataframe is null, cannot return columns", type='debug')
            return None

        if isinstance(data_dict, dict):
            columns = {}
            # Then there are multiple variants and/or multiple children
            for var in data_dict:
                this_dict = data_dict[var]
                if isinstance(this_dict, dict):
                    self.out('...got another dict')
                    # Then there are multiple variants and multiple children
                    this_var_cols = {}
                    for child in this_dict:
                        self.out("...child:",child)
                        # Iterate through each child
                        child_data = this_dict[child]
                        child_cols = getDatasetColumns(child_data)
                        this_var_cols[child] = child_cols
                    columns[var] = this_var_cols
                else:
                    # Then there's only one variant or one child, so get its shape
                    child_cols = getDatasetColumns(this_dict)
                    columns[var] = child_cols

            # Return the dict of shapes
            return columns[None] if len(columns)==1 and None in columns else columns
        else:
            self.out("Got single dataset")
            # Then there's only one variant/child
            return getDatasetColumns(data_dict)
              
    # Can only rename columns for an individual data set (one variant, one child)
    # Either pass cols as a dict with each oldCol:newCol pair,
    # or pass in old_cols and new_cols as equal-length lists of the columns
    def renameColumns(self, old_cols=None, new_cols=None, cols=None, variant=None, child=None):
        df = self.getData(variant=variant, child=child) #[child]
        if df is None:
            self.out("ERROR! Could not find a data set with variant={} and child={}. Cannot execute renameColumns.".format(variant, child), type='error')
            return None
        elif isinstance(df, dict):
            self.out("ERROR! Cannot currently execute renameColumns on multiple data sets at once, given variant={} and child={}.".format(variant, child), type='error')
            return None
        rename_dict = None
        if old_cols is not None and new_cols is not None:
            if isinstance(old_cols, str):
                old_cols = [old_cols]
            if isinstance(new_cols, str):
                new_cols = [new_cols]
            if len(old_cols) != len(new_cols):
                self.out("ERROR! Must pass same number of column names into old_cols and new_cols in renameColumns()", 
                         type='error')
                return None
            
            # If okay, then put the old/new cols together into a dict used to rename the cols inside the dataframe
            col_mappings = zip(old_cols, new_cols)
            rename_dict = dict(col_mappings)
        elif cols is not None and isinstance(cols, dict):
            rename_dict = cols
            #col_mappings = cols.items()
            #old_cols, new_cols = cols.items()
            old_cols = list(cols.keys())
            new_cols = [v for k, v in cols.items()] 

        if rename_dict is not None:
            new_df = df.rename(columns=rename_dict)
            self.out("Renamed columns as ", rename_dict)
            # Store the new data set back into the FeatureSet (which updates the last_updated timestamp)
            self._loadDataIntoMemory(new_df, variant=variant, child=child)
            
            # Make sure each new column has the same column type as the old column
            for old_col, new_col in zip(old_cols, new_cols):
                old_col_set = set(old_col)
                new_col_set = set(new_col)
                if old_col in self.index_cols:
                    self.index_cols |= new_col_set
                    #self.index_cols -= old_col_set
                if old_col in self.label_cols:
                    self.label_cols |= new_col_set
                    #self.label_cols -= old_col_set
                if old_col in self.feature_cols:
                    self.feature_cols |= new_col_set
                    #self.feature_cols -= old_col_set
                
                if not hasattr(self, 'types') or self.types is None:
                    self.types = {}
                if old_col in self.types:
                    self.types[new_col] = self.types[old_col]
                    self.out("Copying types[{}] to types[{}] = {}".format(old_col, new_col, self.types[new_col]))
                    self._removeColumnTypes([old_col])
                else:
                    self.out("WARNING: Cannot find types[{}]".format(old_col), type='warning')

            # Proactively delete copies of datasets from memory
            del(new_df)
            gc.collect()

            # Update the last_updated timestamp
            self._updateLastUpdated()
            
            # Save this updated FeatureSet
            self.save(overwrite=True, variant=variant, schema_changed=True)  

            
    # Currently only works on one variant/child at a time
    # cols: Single column (string) or list of columns to drop
    def dropColumns(self, cols=None, variant=None, child=None):
        if child is not None:
            self.out("ERROR: Cannot execute dropColumns() yet on the child matrices, only on the parent dataframe with child=None.", type='error')
            raise        
        df = self.getData(variant=variant, child=child) #[child]
        if df is None:
            self.out("ERROR! Could not find a data set with variant={} and child={}. Cannot execute renameColumns.".format(variant, child), type='error')
            return None
        elif isinstance(df, dict):
            self.out("ERROR! Cannot currently execute renameColumns on multiple data sets at once, given variant={} and child={}.".format(variant, child), type='error')
            return None
        
        if cols is not None:
            if isinstance(cols, str):
                cols_to_drop = [cols]
            else:
                cols_to_drop = cols

            # Drop the columns (works for pandas or dask)
            new_df = df.drop(labels=cols_to_drop, axis=1)
            self.out("Dropped columns: {} from variant={}, child={}".format(cols_to_drop, variant, child))
            
            # Store the new data set back into the FeatureSet
            self._loadDataIntoMemory(new_df, variant=variant, child=child)
        
            # Also remove this column(s) from the column type sets
            self._removeColumnTypes(cols_to_drop)
            
            #for col_to_drop in cols_to_drop:
            #    if col_to_drop in self.index_cols:
            #        self.index_cols -= set(col_to_drop)
            #    if col_to_drop in self.label_cols:
            #        self.label_cols -= set(col_to_drop)
            #    if col_to_drop in self.feature_cols:
            #        self.feature_cols -= set(col_to_drop)

            # Proactively delete copies of datasets from memory
            del(new_df)
            gc.collect()
            
            # Update the last_updated timestamp
            self._updateLastUpdated()

            # Save this updated FeatureSet
            self.save(overwrite=True, variant=variant, schema_changed=True)
            
            
    # TODO: Need to make column types specific to each variant, not tied to the feature set level
    # This will replace the col types when given (not None)
    # Note: On 8/22/19, adding col_types as the first positional parameter
    # We will phase-out the index/feature/label cols functionality and use this function to change the dtype instead
    # Also note that this changes the underlying dataframe of the FeatureSet without creating a new one (i.e. not a transform)
    def _setColumnTypes(self, variant=None, child='*',
                       index_cols=None, feature_cols=None, label_cols=None, 
                       forced_types=None, inferred_types=None):
        # Only proceed if no types value was passed in
        if index_cols is not None:
            self.index_cols = set()
        if feature_cols is not None:
            self.feature_cols = set()
        if label_cols is not None:
            self.label_cols = set()
        self._addColumnTypes(variant=variant, index_cols=index_cols, feature_cols=feature_cols, label_cols=label_cols, child=child, forced_types=forced_types, inferred_types=inferred_types)
        
        # Update the last_updated timestamp since this is an "edit" to the FeatureSet
        self._updateLastUpdated()
        self._printColumnTypes()

    # When removing a column or changing its name, remove the associated types by calling this
    # (otherwise they'll linger even though the column is gone)
    # NOTE: If there are >1 columns with the same name, this will remove both of them so be careful.
    # cols can be a set or list or str
    def _removeColumnTypes(self, cols):
        cols_to_remove = set(cols)
        self.out("types:", self.types)
        self.out("cols:", cols_to_remove)
        for col in cols_to_remove:
            self.out("Removing type for col:", col)
            if col in self.types:
                del(self.types[col])
                #self.types = self.types.pop(col, None)
        self.index_cols -= cols_to_remove
        self.feature_cols -= cols_to_remove
        self.label_cols -= cols_to_remove
        
    # TODO: Need to make column types specific to each variant, not tied to the feature set level
    # Currently can only do this for one variant at a time, so do not support variant='*' or a list of variants
    # Note: On 10/2/19 making this internal only, so that external users can only call _setColumnTypes() which will 
    # be treated as an "edit" to the FeatureSet.
    def _addColumnTypes(self, variant=None, child='*', index_cols=None, feature_cols=None, label_cols=None, 
                        forced_types=None, inferred_types=None):
        # New on 10/15/19: Append (and overwrite) any column data types passed here in 'types'
        if not hasattr(self, 'types'):
            self.types = {}
        if inferred_types is not None:
            if isinstance(inferred_types, dict):
                # Save each column type into the FeatureSet (and overwrite anything already saved)
                for new_type_col in inferred_types:
                    # Store a tuple of the column type and whether it was inferred or forced
                    # Note: inferred_types comes in formatted as {'var1':'str'}
                    self.types[new_type_col] = (inferred_types[new_type_col], FeatureSet._COL_TYPE_FLAGS_INFERRED)
            else:
                self.out("ERROR: inferred_types must be specified as a dict structure, e.g. {'col1':'str', 'col2':'date'}", 
                         type='error')
        if forced_types is not None:
            if isinstance(forced_types, dict):
                # Save each column type into the FeatureSet (and overwrite anything already saved)
                for new_type_col in forced_types:
                    # Store a tuple of the column type and whether it was inferred or forced
                    # Note: forced_types comes in formatted as {'var1':'str'}
                    self.types[new_type_col] = (forced_types[new_type_col], FeatureSet._COL_TYPE_FLAGS_FORCED)
            else:
                self.out("ERROR: forced_types must be specified as a dict structure, e.g. {'col1':'str', 'col2':'date'}", 
                         type='error')
        
        # Make sure there's a set() attribute ready
        if not hasattr(self, 'label_cols'):
            self.label_cols = set()
        if not hasattr(self, 'feature_cols'):
            self.feature_cols = set()
        if not hasattr(self, 'index_cols'):
            self.index_cols = set()
            
        current_cols = self.columns(variant=variant, child=child)
        current_col_set = set()
        if current_cols is not None:
            if isinstance(variant, list) or variant=='*':
                self.out("ERROR! Cannot execute addColumnTypes on multiple variants, given variant={}, child={}: {}".format(variant, child, current_cols), type='error')
                return None
            if isinstance(current_cols, dict):
                #print("...self.columns(variant={}, child={}) returned:".format(variant, child), current_cols)
                # Then we have a list of children to put together
                # TODO: Keep track somehow of the child where each column came from
                # For now we just push all the columns together into one big superset
                for this_child in current_cols:
                    child_col_set = set(current_cols[this_child])
                    current_col_set |= child_col_set
            else:
                current_col_set = set(current_cols)

            # Make sure if columns were removed, they're removed from the index/feature/label cols too
            self.label_cols &= current_col_set
            self.feature_cols &= current_col_set
            self.index_cols &= current_col_set

        # Allow '*' to pass-in for label/feature/index cols
        # Note there is an order-of-operations implied here: (1) index_cols, (2) feature_cols, (3) label_cols
        # Also if label_cols='*' and feature_cols=['blah'], then label_cols gets everything except 'blah'
        if index_cols=='*':
            index_cols = current_col_set
        if feature_cols=='*':
            feature_cols = current_col_set - set(index_cols if index_cols is not None else [])
        if label_cols=='*':
            label_cols = current_col_set - set(feature_cols if feature_cols is not None else []) - set(index_cols if index_cols is not None else [])           
        
        if label_cols is not None and len(label_cols)>0:
            # Add new label cols if provided and in the current dataset
            add_label_cols_set = set([label_cols] if isinstance(label_cols,str) else label_cols)
            label_cols_to_add = add_label_cols_set & current_col_set
            self.label_cols |= label_cols_to_add 

            # If one of the new columns was a feature/index col, remove it from there
            self.index_cols -= label_cols_to_add
            self.feature_cols -= label_cols_to_add 

        if feature_cols is not None and len(feature_cols)>0:
            # Add new feature_cols if given and in the current dataset
            add_feature_cols_set = set([feature_cols] if isinstance(feature_cols,str) else feature_cols)
            feature_cols_to_add = add_feature_cols_set & current_col_set
            self.feature_cols |= feature_cols_to_add

            # If one of the new columns was a label/index col, remove it from there
            self.index_cols -= feature_cols_to_add
            self.label_cols -= feature_cols_to_add 

        if index_cols is not None and len(index_cols)>0:
            # Add new index_cols if given and in the current dataset
            add_index_col_set = set([index_cols] if isinstance(index_cols,str) else index_cols)
            index_cols_to_add = add_index_col_set & current_col_set
            self.index_cols |= index_cols_to_add

            # If one of the new columns was a label/feature col, remove it from there
            self.feature_cols -= index_cols_to_add
            self.label_cols -= index_cols_to_add 

            # NOTE: Removing this for now...I think it's not helpful and causes problems later
            # Make these columns the index of the dataframe (if non-empty)
            #self.df.set_index(self.index_cols)

    def _printColumnTypes(self, show_cols=False):
        self.out("FeatureSet {} has {} index cols ({}), {} feature cols, {} label cols".format(self.label, len(self.index_cols), self.index_cols, len(self.feature_cols), len(self.label_cols)))
        if self.types is not None and len(self.types)>0:
            self.out("...column data types: {}".format(self.types))
        else:
            self.out("...no column data types set yet.")
        if show_cols:
            self.out("...feature cols: {}".format(self.feature_cols))
            self.out("...label cols: {}".format(self.label_cols))
     
    # External call to allow adding of new data into a FeatureSet
    # Mostly a wrapper around the internal call, but this is "editing" so should update the last_updated timestamp
    def addData(self, data, variant=None, child=None, **kwargs):
        self.out("Calling FeatureSet.addData(variant={}, child={}, kwargs={})".format(variant, child, kwargs))
        self._loadDataIntoMemory(data, variant=None, child=None, **kwargs)
        self._updateLastUpdated()
        
     # Added on 4/19/19 to pre-calculate shapes
    #def addData(self, data, variant=None, child=None, **kwargs):
    def _loadDataIntoMemory(self, data, variant=None, child=None, **kwargs):
        self.out("In FeatureSet._loadDataIntoMemory(variant={}, child={})".format(variant, child))        
        super()._loadDataIntoMemory(data, variant=variant, child=child)
         
        # Check the memory mode
        self.out("Using MEMORY_MODE='{}'".format(self.space.memory_mode))
        
        # Calculate the shape of the given data set
        new_shape = FeatureSet.getDatasetShape(data, memory_mode=self.space.memory_mode)
        self.out("...New shape found:", new_shape, type(data), data is None)
        
        # Store that one new dataset's shape
        self.out(f"...storing shape for variant={variant}, child={child}")
        self._setDatasetShape(new_shape, variant=variant, child=child)
        #if variant not in self.dataset_shapes:
        #    self.dataset_shapes[variant] = {}
        #self.dataset_shapes[variant][child] = new_shape   

        #self.dataset_shapes = self.shape(reload=True)
        self.out("Stored shapes for '{}' with new shape: {} for variant={}, child={}".format(self.label, 
                                                                                          new_shape, variant, child))

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++    
    # This function takes in a dataframe df and modifies all columns to "unify" their datatypes in preparation
    # for saving as parquet files.  In Dask/Pandas, there is a generic "object" type of column.  But when the values in
    # such a column are varied (some null, some strings), this causes problems when writing/reading to/from parquet.
    # So here we look for those columns, infer the correct "dominant" data type, and convert the values accordingly.
    # This is meant to address this dask bug: https://github.com/dask/dask/issues/4194.
    # cols = '*' if should unify all columns in this df, otherwise specifies the columns to unify
    # cols_to_exclude = optional list of columns (or string for one column) *not* to unify (such as index columns)
    # force_types = optional dict of columns:type values, where the type: ['str', 'int', 'float', 'blank', 'date', 'null']
    # TODO: Support 'bool' as fundamental datatype
    @staticmethod
    def _unifyDataTypes(df, fillna=False, debug=False, cols='*', cols_to_exclude=None, forced_types=None):
        # from dateutil import parser
        if cols=='*':
            # Unify all columns in this dataframe not in cols_to_exclude
            cols_to_unify = list(df.columns)
        elif cols is None:
            cols_to_unify = []
        elif isinstance(cols, list):
            cols_to_unify = cols
        elif isinstance(cols, str):
            cols_to_unify = [cols]
        else:
            cols_to_unify = list(cols)
        if isinstance(cols_to_exclude, str) and cols_to_exclude in cols_to_unify:
            cols_to_unify.remove(cols_to_exclude)
        elif isinstance(cols_to_exclude, list):
            cols_to_unify = [col for col in cols_to_unify if col not in cols_to_exclude]
        
        from pandas.api.types import is_string_dtype, is_numeric_dtype
        #numeric_dtypes = [np.int64, np.int32, np.int16, np.int, np.float32, np.float64, np.float16, np.float]
        int_dtypes = [np.int64, np.int32, np.int16, np.int]
        default_int_dtype = np.int32
        float_dtypes = [np.float32, np.float64, np.float16, np.float]
        default_float_dtype = np.float32
        datetime_dtypes = [np.datetime64, 'datetime64[ns]', 'datetime64[us]', '<M8[ns]']
        default_categorical_dtype = 'category'
        
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Function that simplifies the mapping of types for each var to ['num', 'str', 'date', 'none', other]
        # TODO: Cover all types in the "other" bucket
        # 11/17/20: Added optional flag forced_type to help obviate unnecessary parsing of strings --> float/int/date if
        # later those will be converted back to strings anyway
        # Note: This will remove any "standardization" of values like conversion of 6/5/80 to '1980-06-05 00:00:00' but 
        # that might be wise anyway (not to alter the underlying data) and algorithmically has big savings
        def getDataType(x, forced_type=None):
            if x is None or x!=x:
                # Note: Check for nulls *first* since NaN will return true for isinstance(x, float) too
                return 'none'
            elif isinstance(x, int):
                return 'int'
            elif isinstance(x, float) or isinstance(x, dec.Decimal):
                return 'float'
            elif isinstance(x, bool):
                return 'bool'
            elif isinstance(x, str):
                if x=='':
                    return 'blank'
                
                # Shortcut the parsing of the string if we know this will be forced to remain a string anyway
                if forced_type=='str':
                    return 'str'
                
                # Try to convert this string to an int
                # https://stackoverflow.com/questions/1265665/how-can-i-check-if-a-string-represents-an-int-without-using-try-except
                if x[0] in ('-', '+'):
                    x_without_sign = x[1:]
                    if x_without_sign[1:].replace(',','').isdigit():
                        return 'int'
                
                if x.isdigit():
                    return 'int'
                
                # Otherwise try to convert to a float
                # https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
                if '.' in x:
                    x_parts = x.partition('.')
                    if (x_parts[0]=='' or x_parts[0].replace(',','').isdigit()) and x_parts[1]=='.' and (x_parts[2]=='' or x_parts[2].isdigit()):
                        return 'float'
                #try:
                #    i = int(x)
                #    return 'int'
                #except ValueError:
                #    try:
                #        i = float(x)
                #        return 'float'
                #    except ValueError:
                
                # Otherwise try to convert to a date
                # https://stackoverflow.com/questions/14411633/python-fastest-way-to-check-if-a-string-contains-specific-characters-in-any-of
                # Need to balance speed of search (i.e. don't try parser.parse() too often) vs. recall (find all the dates)
                if x.count('-') in [1,2] or x.count('/')==2 or x.count(':')==2:
                    d = tryDateConversion(x)
                    if d is not None:
                        return 'date'
                    #try:
                    #    d = parser.parse(x)
                    #    return 'date'
                    #except:
                    #    return 'str'
                    
                # Check for boolean-like strings
                if x in ['True', 'true', 'False', 'false', 'T', 'F', 'Yes', 'yes', 'No', 'no']:
                    return 'bool'
                         
                return 'str'
            elif isinstance(x, np.datetime64):
                return 'timestamp'
            elif isinstance(x, dt.datetime) or isinstance(x, dt.date):
                return 'date'
            else:
                return type(x)

        # Try to convert the given date_value to a datetime object using dateutil.parser
        # Return None if it doesn't work (or cannot be stored later as a parquet datetime)
        # so the calling function can decide how to handle errors
        def tryDateConversion(date_value):
            from dateutil import parser
            # See https://issues.apache.org/jira/browse/ARROW-7856 for ranges that pyarrow can support
            min_date = pd.Timestamp.min
            max_date = pd.Timestamp.max
            
            try:
                # Try to convert the given date_value to a datetime
                d = parser.parse(date_value)
                
                # If the date is out of bounds [min_date, max_date] then we cannot store in parquet
                if d<min_date or d>max_date:
                    # So return null
                    return None
                return d
            except:
                # If any error throws, return null
                return None
            
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Given a Dask Series, find the "dominant" column type based on a hierarchy encoded here
        # Pass in a list of column types and how many of each occurs
        def getDominantColType(col_types):
            dominant_col_type = None
            for col_type, col_type_count in zip(col_types.index, col_types):
                
                # Pick the "dominant" col type based on a hierarchy
                if col_type=='blank': 
                    if dominant_col_type is None:
                        dominant_col_type = 'blank'
                elif col_type=='none':
                    if dominant_col_type is None:
                        dominant_col_type = 'none'
                elif col_type=='str':
                    # Any presence of strings means the dominant col type is 'str'
                    dominant_col_type = 'str'
                elif col_type=='int':
                    if dominant_col_type == 'date':
                        # If there are both nums and dates, convert both to str
                        dominant_col_type = 'str'
                    elif dominant_col_type == 'float':
                        dominant_col_type = 'float'
                    elif dominant_col_type is None or dominant_col_type != 'str':
                        # Convert to num if there were no strings
                        dominant_col_type = 'int'
                elif col_type=='float':
                    if dominant_col_type == 'date':
                        # If there are both nums and dates, convert both to str
                        dominant_col_type = 'str'
                    elif dominant_col_type == 'int':
                        # Float should overrule ints
                        dominant_col_type = 'float'
                    elif dominant_col_type is None or dominant_col_type != 'str':
                        # Convert to num if there were no strings
                        dominant_col_type = 'float'
                elif col_type=='date' or col_type=='timestamp':
                    if dominant_col_type == 'int' or dominant_col_type == 'float':
                        # If there are both ints/floats and dates, convert both to str
                        dominant_col_type = 'str'
                    elif dominant_col_type is None or dominant_col_type != 'str':
                        # Convert to date if there were no strings
                        dominant_col_type = 'date'
                elif col_type=='bool':
                    if dominant_col_type is None:
                        dominant_col_type = 'bool'

            return dominant_col_type.lower()

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # This is not air-tight, in that it doesn't cover every possible combination of x_datatype + dominant_col_type
        # So it's possible that the outputted datatypes are not always 100% the same.
        # TODO: Support x_datatype=='bool' with fillna--> False
        # TODO: Support 'cat' for integer values where there are nulls
        def unify_values(x, dominant_col_type, fillna):
            x_datatype = getDataType(x, dominant_col_type)
            if x_datatype == 'none': # or x_datatype == 'blank':
                if dominant_col_type == 'none':
                    return np.nan
                elif dominant_col_type in ['num', 'float']:
                    return 0.0 if fillna else np.nan
                elif dominant_col_type == 'int':
                    return 0 if fillna else np.nan
                elif dominant_col_type == 'date':
                    # Converting to plain None type, since pyarrow fails if x is numpy datetime64
                    return None # if fillna else x
                    #return np.datetime64('nat') if fillna else x
                elif dominant_col_type == 'str' or dominant_col_type == 'blank':
                    #print("Converting {}={} to {}...".format(x, x_datatype, '' if fillna else None))
                    return '' if fillna else None
                elif dominant_col_type == 'bool':
                    return False if fillna else np.nan
                elif dominant_col_type == 'cat':
                    return ''
            elif x_datatype == 'blank':
                # This only applies to strings
                if dominant_col_type == 'str' or dominant_col_type == 'blank':
                    return ''
                elif dominant_col_type == 'none':
                    return np.nan
                elif dominant_col_type in ['num', 'float']:
                    return 0.0
                elif dominant_col_type == 'int':
                    return 0
                elif dominant_col_type == 'date':
                    # Converting to plain None type, since pyarrow fails if x is numpy datetime64
                    return None # if fillna else x
                    #return np.datetime64('nat') if fillna else x
                elif dominant_col_type == 'bool':
                    return False                
            elif x_datatype == 'str':
                if dominant_col_type == 'int':
                    # Try to convert this string to an int
                    try:
                        i = int(x.replace(',',''))
                        return i
                    except ValueError:
                        return x
                elif dominant_col_type == 'float':
                    # Try to convert this string to an float
                    try:
                        i = float(x.replace(',',''))
                        return i
                    except ValueError:
                        return x
                elif dominant_col_type == 'date':
                    # Try to convert this string to a date
                    return tryDateConversion(x)
                    
                    # If converting didn't work, return the date string
                    #return d # if d is not None else x
                    #try:
                    #    d = parser.parse(x)
                    #    #return np.datetime64(d)
                    #    return d
                    #except:
                    #    return x
                elif dominant_col_type == 'bool':
                    # Try to conver this to a bool
                    if x.lower() in ['true', 'yes', 't', '1']:
                        return True
                    elif x.lower() in ['false', 'no', 'f', '0']:
                        return False
                else:
                    return x
            elif x_datatype == 'int':
                if dominant_col_type == 'str':
                    return str(x)
                elif dominant_col_type == 'float':
                    return float(x)
                elif dominant_col_type == 'date':
                    # Try to convert this number to a date
                    return tryDateConversion(x)
                    #return d if d is not None else x
                    #try:
                    #    d = parser.parse(x)
                    #    #return np.datetime64(d)
                    #    return d
                    #except:
                    #    return x
                elif dominant_col_type == 'bool':
                    return True if x==1 else False
                else:
                    # Note this accounts for the string->int conversion
                    # ...dependent on the try / except statements in the function above (not great)
                    return int(x)
            elif x_datatype == 'float':
                if dominant_col_type == 'str':
                    # 8/23/20: To handle floats with .0 as the decimal, we should convert to int first
                    if isinstance(x, str):
                        return x
                    if x==int(x): #x.is_integer():
                        return str(int(x))
                    return str(x)
                elif dominant_col_type == 'int':
                    # Round to convert to integer
                    return round(x) #np.round(x)
                elif dominant_col_type == 'date':
                    # Try to convert this number to a date
                    return tryDateConversion(x)
                    #return d if d is not None else x
                    #try:
                    #    d = parser.parse(x)
                    #    #return np.datetime64(d)
                    #    return d
                    ##except (ValueError, TypeError) as e:
                    #except:
                    #    return x
                elif isinstance(x, str):
                    # This accounts for string->float conversion
                    # ...dependent on the try / except statements in the function above (not great)
                    return float(x.replace(',',''))
                else:
                    return float(x)
            elif x_datatype == 'timestamp':
                if dominant_col_type == 'str':
                    return str(dt.datetime.utcfromtimestamp(x))
                elif dominant_col_type == 'date':
                    if np.issubdtype(x.dtype, np.datetime64):
                        # Need to convert numpy datetimes to datetime
                        ts = (x - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
                        return dt.datetime.utcfromtimestamp(ts)
                    else:
                        # Otherwise convert datetime timestamp to just date format
                        return dt.datetime.utcfromtimestamp(x)
                    #print("Converting timestamp:", x, type(x))
                    #if x!=x:
                    #    print("Converting null timestamp")
                    
                    
                return x
            elif x_datatype == 'date':
                if dominant_col_type == 'str':
                    return str(x)
                elif isinstance(x, str):
                    # This accounts for string->date conversion
                    # ...dependent on the try / except statements in the function above (not great)
                    #return np.datetime64(parser.parse(x))
                    #return parser.parse(x)
                    return tryDateConversion(x)
                    #return d if d is not None else x
                else:
                    return x
                # We shouldn't try to coerce a date into a number...bound to be problematic
                #return x #.replace(nanosecond=0)
            elif x_datatype == 'bool':
                if dominant_col_type == 'str' or dominant_col_type == 'blank':
                    return str(x)
                else:
                    x_lower = x.lower()
                    x_bool = x if isinstance(x, bool) else True if x_lower in ['true', 'yes', 't'] else False
                    return x_bool if dominant_col_type=='bool' else int(x_bool) if dominant_col_type=='int' else np.nan
            else:
                return x

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++    
        def get_unify_fn(dominant_col_type, fillna=False):
            return lambda x, dom_col=dominant_col_type, fillna=fillna: unify_values(x, dom_col, fillna)
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # Go through each column in the joining dataframe
        #feature_set_to_merge_dtypes = feature_set_to_merge_df.dtypes
        df_dtypes = df.dtypes
        df_dtypes_to_unify = df_dtypes[cols_to_unify]

        dominant_col_types = {} # this might be unnecessarily a dict...failed attempt to fix a bug
        unify_fns = {} # this might be unnecessarily a dict...failed attempt to fix a bug
        # Calculate # nulls for all columns, to use below
        if debug:
            print("Calculating # nulls for all columns...")
        num_nulls_all_cols = df.isna().sum().compute() if isinstance(df, dd.DataFrame) else df.isna().sum()
        if debug:
            print('...done')
            print(num_nulls_all_cols)

        # Iterate through 
        for col, coltype in df_dtypes_to_unify.iteritems():
            # Don't unify or store the '*' itself, it's just a placeholder to affect other column types
            if col != '*':
                if debug:
                    print("--> Checking whether to unify column '{}' with type '{}', fillna={}".format(col, coltype, fillna))
                # Don't fill in nulls for the index column -- we need those
                #if col != index_col:
                # Otherwise preserve int/float types
                #if coltype in numeric_dtypes:

                # Check if we should force the type of this column
                forced_type = None
                if forced_types is not None:
                    if col in forced_types:
                        forced_type = forced_types[col]
                    elif '*' in forced_types:
                        # New 10/4/20: Allow '*' as backup type to force for all columns
                        # also allow sending '*':None to undo a previous '*' typing
                        if forced_types['*'] is not None:
                            forced_type = forced_types['*']

                # If indeed forcing the type, just change each value to that type
                if forced_type is not None:
                    if debug:
                        #col_types = df[col].map(getDataType).value_counts().compute() if isinstance(df, dd.DataFrame) \
                        #        else df[col].map(getDataType).value_counts()

                        #print("...have these col_types: \n{}".format(col_types))
                        print("...forcing type of col {} ({}) to {}".format(col, coltype, forced_type))

                    unify_fns[col] = get_unify_fn(forced_type, fillna=fillna)
                    default_dtype = None
                    if forced_type=='float':
                        df[col] = df[col].map(unify_fns[col]).astype(default_float_dtype, errors='ignore')
                    elif forced_type=='cat':
                        df[col] = df[col].astype(str).astype(default_categorical_dtype, errors='ignore')
                    elif forced_type=='int':
                        # Infer the right int dtype to use based on how large the values in this column can be
                        try:
                            inferred_int_dtype = getDtype(np.max(np.abs(pd.to_numeric(df[col], 
                                                                                      errors='coerce').astype('Int64'))))
                            if inferred_int_dtype is not None:
                                # Then there is a numpy type to use
                                df[col] = df[col].map(unify_fns[col]).astype(inferred_int_dtype, errors='ignore')
                            else:
                                # Store in pandas data types which can handle any length
                                df[col] = df[col].map(unify_fns[col])
                            if debug:
                                print("Forcing df[{}] to int type:".format(col), inferred_int_dtype)
                                print(df.dtypes)
                        except Exception as e:
                            print(f"ERROR: Cannot force column '{col}' to data type 'int', contains these types:",
                                  df[col].map(type).value_counts())
                            print(df[col].value_counts())
                            print(str(e))
                            # Help find the exact row that cannot be converted to int
                            found_error = False
                            for i, item in enumerate(df[col]):
                                try:
                                    int(item)
                                except ValueError:
                                    print('...ERROR at index {}: {!r}'.format(i, item))
                                    found_error = True
                            if not found_error:
                                print("...cannot find row with problems")
                            raise
                    else:
                        if debug:
                            print("Current types:\n", df[col].map(getDataType).value_counts())
                        # Otherwise just let the values take their raw form once mapped to the dominant col type
                        df[col] = df[col].map(unify_fns[col])
                    if debug and forced_type is not None:
                        print("Forcing df[{}] to {} type:".format(col, forced_type))
                    #df[col] = df[col].map(unify_fns[col])
                    dominant_col_types[col] = forced_type
                    if debug:
                        print("...done")
                    
                # Otherwise infer the column type(s) and then convert values accordingly to unify to a single type per column
                else:
                    # Count the nulls
                    num_nulls = num_nulls_all_cols[col]
                    if debug:
                        if isinstance(num_nulls, int):
                            print("...WARNING: {} has >1 column so there will be problems trying to unify".format(col))
                        print("...found {} nulls".format(num_nulls))

                    # Otherwise if the column (itself) is of int type
                    if coltype in int_dtypes:
                        dominant_col_types[col] = 'int'
                        # Using the custom numpy null value that can preserve the int64 type of the column
                        fillna_val = 0 if fillna else np.nan
                        #print("NUM NULLS:", num_nulls)
                        if num_nulls > 0:
                            if debug:
                                print("...filling nulls in numeric int column {} ({}) with value={}".format(col, coltype, fillna_val))
                            df[col] = df[col].fillna(fillna_val).astype(default_int_dtype, errors='ignore')
                            if not fillna:
                                # Also convert this column to float type, since keeping ints with np.nans causes problems
                                df[col] = df[col].astype(default_float_dtype, errors='ignore')
                                dominant_col_types[col] = 'float'

                    # float type
                    elif coltype in float_dtypes:
                        #print("...coltype is float, converting to {}".format(default_float_dtype))
                        dominant_col_types[col] = 'float'
                        # Using the custom numpy null value that can preserve the int64 type of the column
                        fillna_val = 0.0 if fillna else np.nan

                        # New 9/21/20: By default reduce the precision of float columnt to reduce memory requirements
                        if num_nulls > 0:
                            if debug:
                                print("...filling nulls in numeric float column {} ({}) with value={}".format(col, coltype, fillna_val))
                            df[col] = df[col].fillna(fillna_val).astype(default_float_dtype, errors='ignore')
                        #else:
                        # If this is already a float type, leave it as such
                        #    df[col] = df[col].astype(default_float_dtype)

                    # datetime type
                    elif coltype in datetime_dtypes:
                        dominant_col_types[col] = 'date'
                        # TODO: Should we ever fill datetimes with non-null values?  Which value??
                        fillna_val = np.datetime64('nat')

                        if num_nulls > 0:
                            if debug:
                                print("...filling nulls in datetime column {} ({}) with value={}".format(col, coltype, fillna_val))
                            df[col] = df[col].fillna(fillna_val)

                    # If it's an object-type column, it may be mixed-typed so we need to look at each row
                    #elif fillna:
                    else:
                        # Using str() to make this immutable, so it's not a pointer passed around to *all* function calls
                        #dominant_col_types[col] = getDominantColType(merge_df[col])
                        if debug:
                            print("...calculating all column types")

                        # 9/6/19: Overwriting this since it overlooks nulls *before* it gets all the data types 
                        #value_counts = df[col].value_counts().compute().reset_index() if isinstance(df, dd.DataFrame) \
                        #               else df[col].value_counts().reset_index()
                        #value_counts['type'] = value_counts['index'].map(getDataType)
                        #col_types = value_counts.groupby('type')[col].sum()
                        col_types = df[col].map(getDataType).value_counts().compute() if isinstance(df, dd.DataFrame) \
                                    else df[col].map(getDataType).value_counts()

                        if debug:
                            print("...have these col_types: \n{}".format(col_types))

                        if len(col_types)>1:
                            # If there are multiple column types here, find the dominant col type from the list
                            dominant_col_types[col] = getDominantColType(col_types)
                            if debug:
                                print("...found this to be the dominant col type: {}".format(dominant_col_types[col]))

                            unify_flag = True
                            # Check for case where all values are already 'str' or 'blank', so no need to unify again
                            col_type_strings = list(col_types.index)
                            if dominant_col_types[col] == 'str' and len(col_types)==2 \
                                and col_type_strings[0] in ['str','blank'] and col_type_strings[1] in ['str','blank']:
                                if debug:
                                    print("...not unifying since all values are already strings or blank ''")
                            elif dominant_col_types[col] == 'str' and fillna and len(col_types)==2 \
                                and col_type_strings[0] in ['str','none'] and col_type_strings[1] in ['str','none']:
                                if debug:
                                    print("...filling nulls with ''")
                                df[col] = df[col].fillna('')
                            # Note: Not working so commenting out...pyarrow can't save this type of Int64 column
                            #elif dominant_col_types[col] == 'int' and len(col_types)==2 \
                            #    and col_type_strings[0] in ['int','none'] and col_type_strings[1] in ['int','none']:
                            #    if debug:
                            #        print("...converting column to Int64 to preserve NaN values")
                            #    df[col] = pd.Series(df[col], dtype="Int64")
                            #if unify_flag:
                            else:
                                # TODO: Handle fillna=False here

                                # If there's a more complicated combination of column types here, convert values to a
                                # consistent format in each column (filling nulls if need be)
                                unify_fns[col] = get_unify_fn(dominant_col_types[col], fillna=fillna)                                    
                                if debug:
                                    print("...unifying mixed col {} ({}) and converting all values to {} with fillna={}".format(col, 
                                                                                                           coltype, 
                                                                                                           dominant_col_types[col],
                                                                                                           fillna))

                                # Alter the type of each value in this column using the given function
                                if dominant_col_types[col]=='float':
                                    # Keep precision down to the default level
                                    df[col] = df[col].map(unify_fns[col]).astype(default_float_dtype, errors='ignore')
                                elif dominant_col_types[col]=='int':
                                    df[col] = df[col].map(unify_fns[col]).astype(default_int_dtype, errors='ignore')
                                else:
                                    df[col] = df[col].map(unify_fns[col])

                                new_col_types = df[col].map(type).value_counts().compute() if isinstance(df, dd.DataFrame) else df[col].map(type).value_counts()
                                if debug:
                                    print("......new unified col has these datatypes:", new_col_types)
                        elif len(col_types)==1:
                            # Store the one col_type as the dominant col_type
                            dominant_col_types[col] = col_types.index[0]
                            unify_fns[col] = get_unify_fn(dominant_col_types[col], fillna=fillna)
                            if debug:
                                print("...converting all values in col {} ({}) to {}".format(col, coltype, dominant_col_types[col]))
                            if dominant_col_types[col]=='float':
                                # Keep precision down to the default level
                                df[col] = df[col].map(unify_fns[col]).astype(default_float_dtype, errors='ignore')
                            elif dominant_col_types[col]=='int':
                                # Keep precision down to the default level
                                df[col] = df[col].map(unify_fns[col]).astype(default_int_dtype, errors='ignore')
                            else:
                                df[col] = df[col].map(unify_fns[col])
                        else:
                            dominant_col_types[col] = 'none'

                        #elif len(col_types)==1 and col_types.index[0]=='none':
                            # If the entire column is nulls and fillna=True, need to fill this column with blanks
                            # Note: Leaving this case out, so that all-null columns just remain such (like date cols)
                            # Rather than trying to guess what the right fillna values should be (0? ''? np.nan?)

                    #else:
                    #    print("...not filling nulls in {} ({})".format(col, coltype))
        if debug:
            print(df.dtypes)
            print(os.popen('free').read())
            
        return df, dominant_col_types
    
    
    # TODO: Enable saving multiple or all variants per feature set at once, in the same directory, using '*' or a list 
    # To free-up space, one can set overwrite=True and have this file replace the previous one
    # By default the filetype is parquet/pyarrow (to save space). But you can pass 'csv' or 'fastparquet' in too.
    # Note: On 6/21/19, deprecating 'path' and 'filename' here, shifting that functionality to new function output()
    # Note: On 10/15/19, deprecating 'col_types' since it's unused here
    def save(self, variant=None, child='*', overwrite=False, save_to_disk=True, 
             #path=None, filename=None,
             filetype='parquet', schema_changed=True):
        self.out("\nCalling FeatureSet '{}' save(variant={}, child={}, overwrite={}, save_to_disk={}, filetype={}, schema_changed={})".format(self.label, variant, child, overwrite, save_to_disk, filetype, schema_changed))
                
        #++++++++++++++++++++++++++++++++++++++++++++++++++++
        def saveDatasetToFile(df, filepath, variant=None, child=None):
            self.out("\n...Inside saveDatasetToFile(df={}, filepath={}, child={})".format(type(df), filepath, child))
            
            #self.df.to_csv(partition_path, index=False, na_rep='NaN')
            #self.df.to_hdf(partition_path)
            #df_to_save.to_hdf(partition_path, '/data')            

            #if isinstance(df, dd.DataFrame):
            #    print("...running to_parquet on dataframe")
            #    #new_df = dd.to_parquet(df, partition_path, engine='pyarrow', write_index=False)
            #    #print("...got new_df: ", type(new_df))
            if isinstance(df, dd.Series):
                # Since dask.Series.to_parquet fails currently, 
                # need to convert to dask.DataFrame first
                # See my issue here: https://github.com/dask/dask/issues/3982
                
                # Change on 5/6/19: Convert everything to pandas dataframe before saving
                df = df.to_frame().compute()
                # dd.to_parquet(df_dataframe, partition_path, engine='pyarrow', write_index=False)
            elif not isinstance(df, dd.DataFrame) and not isinstance(df, pd.DataFrame) and not isinstance(df, pd.Series):
                if hasattr(df, '__feature_type__') and df.__feature_type__=='FeatureMatrix':
                    # Use the custom class's save method
                    self.out("...saving FeatureMatrix to file as a numpy sparse matrix: ", filepath)
                    df.saveToFile(filepath)
                else:
                    self.out("WARNING! Data was not a DataFrame or Series, so cannot write it to file", type='warning')
                return df

            if filetype=='csv' or filetype=='CSV':
                csv_path = os.path.join(filepath, 'output.csv')
                self.out("...starting to write to csv:", csv_path)
                # TODO: Improve consistency of saving dataframe to file via CSV, especially for nulls and mixed-type cols
                if isinstance(df, dd.DataFrame):
                    df.compute().to_csv(csv_path, index=False, na_rep='')
                else:
                    df.to_csv(csv_path, index=False, na_rep='')
                    
            elif filetype is None or filetype=='parquet' or filetype=='pyarrow' or filetype=='fastparquet':
                engine = 'fastparquet' if filetype=='fastparquet' else 'pyarrow'
                partition_path = os.path.join(filepath, 'parts.pq')
                
                # Need to reduce precision of datetime[ns] columns to microseconds before saving to parquet with Dask
                # Since reloading later will cause problems 
                # (when the parquet file saved with schema [ms] is converted back to [ns] by dask then 
                # saved again to [ms], an error is thrown) 
                schema = None
                if engine == 'pyarrow':
                    # Check if the schema for this variant/child is already stored
                    if not schema_changed:
                        schema = self._getSchema(variant=variant, child=child)
                        self.out("Going to use this schema:", schema)
                        
                
                # Write the dataframe to a set of partitioned parquet files
                if isinstance(df, dd.DataFrame) or isinstance(df, dd.Series):
                    self.out("...writing Dask dataframe to parquet (engine={}, schema={}):".format(engine, schema), 
                          partition_path)
                    # Need to set the original Dask dataframe to point to the new one on disk
                    # 5/6/19: Passing in pyarrow_schema per https://github.com/dask/dask/issues/4194 
                    if engine=='pyarrow':
                        self.out("...since using pyarrow, must convert from Dask to pandas dataframe first")
                        new_df = df.compute()
                        self.out("...done")
                        if schema is not None:
                            self.out("...have a schema, won't resave it.")
                            new_table = pa.Table.from_pandas(new_df, schema=schema, preserve_index=False)
                            #pa.parquet.write_to_dataset(new_table, partition_path, preserve_index=False)
                            #pd.DataFrame.to_parquet(new_df, partition_path, engine='pyarrow', index=False, schema=schema)
                        else:
                            new_table = pa.Table.from_pandas(new_df, preserve_index=False)
                            self._saveSchema(new_table.schema, variant=variant, child=child)
                            self.out("...got new schema, will save it to disk:", new_table.schema)
                        
                        pa.parquet.write_to_dataset(new_table, partition_path, 
                                                    partition_filename_cb=lambda x:'part.{}.parquet'.format('0' if x is None else x),
                                                    coerce_timestamps='ms', allow_truncated_timestamps=True)
                        # Remove preserve_index since it was deprecated starting with pyarrow 0.14.0
                        #pa.parquet.write_to_dataset(new_table, partition_path, preserve_index=False)
                            #pd.DataFrame.to_parquet(new_df, partition_path, engine='pyarrow', index=False)
                    else:
                        dd.to_parquet(df, partition_path, engine='fastparquet', write_index=False)
                        
                        new_df = dd.read_parquet(partition_path, engine=engine)
                    
                    # Returning the df in this case to signal to add it back into the FeatureSet below
                    return new_df
                elif isinstance(df, pd.DataFrame):
                    self.out("...starting to write pandas dataframe to parquet (engine={}, schema={}):".format(engine, schema), 
                          partition_path)
                    # Save this pandas dataframe to parquet
                    # 5/6/19: Passing in pyarrow_schema per https://github.com/dask/dask/issues/4194 
                    if engine=='pyarrow':
                        if schema is not None:
                            self.out("...have a schema, won't resave it.")
                            new_table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)
                            #pd.DataFrame.to_parquet(df, partition_path, engine='pyarrow', index=None, schema=schema)
                        else:
                            new_table = pa.Table.from_pandas(df, preserve_index=False)
                            self._saveSchema(new_table.schema, variant=variant, child=child)
                            self.out("...got new schema, will save to disk:", new_table.schema)
                            #pd.DataFrame.to_parquet(df, partition_path, engine='pyarrow', index=None)
                        
                        pa.parquet.write_to_dataset(new_table, partition_path, 
                                                    partition_filename_cb=lambda x:'part.{}.parquet'.format('0' if x is None else x),
                                                    coerce_timestamps='ms', allow_truncated_timestamps=True)

                        # Remove preserve_index since it was deprecated starting with pyarrow 0.14.0
                        #pa.parquet.write_to_dataset(new_table, partition_path, preserve_index=False)
                    else:
                        pd.DataFrame.to_parquet(df, partition_path, engine='fastparquet', index=False)
                    
                    # Returning None to signal don't need to update the FeatureSet
                    return None
                elif isinstance(df, pd.Series):
                    self.out("...writing pandas series to parquet (engine={}, schema={}):".format(engine, schema), partition_path)
                    if engine=='pyarrow':
                        df_dataframe = pd.DataFrame(df)
                        new_table = pa.Table.from_pandas(df_dataframe, preserve_index=False)
                        pa.parquet.write_to_dataset(new_table, partition_path, 
                                                    partition_filename_cb=lambda x:'part.{}.parquet'.format('0' if x is None else x),
                                                    coerce_timestamps='ms', allow_truncated_timestamps=True)
                        #pa.parquet.write_to_dataset(new_table, partition_path, preserve_index=False)
                        #pd.Series.to_parquet(df, partition_path, engine='pyarrow', index=False)
#                         new_array = pa.Array.from_pandas(df)
#                         new_table = pa.Table.from_arrays(new_array)
#                         pa.parquet.write_to_dataset(new_table, partition_path, preserve_index=False)
                    else:
                        pd.Series.to_parquet(df, partition_path, engine='fastparquet', index=False)

                else:
                    return None
                #print("...returning: ", new_df.head())
                #return new_df
                
            else:
                self.out("WARNING! Filetype '{}' is not supported for saving this dataframe to file.".format(filetype), 
                         type='warning')
            self.out("...done")
            
            # Return None if the dataframe didn't change
            return None
        #++++++++++++++++++++++++++++++++++++++++++++++++++++

        if not save_to_disk:
            # Still need to save the variant into the FeatureSpace metadata, even if not writing to disk
            self._saveVariant(variant)
        else:
            # Fixing bug on 12/25/19 (Yes, Xmas): previous vs. new comparison needs to include variants
            # Only write to disk if instructed
            previous_filepath = self.last_save_filepaths.get(variant, None)
            super().save(variant=variant, file_prefix='data', filetype=filetype)
            new_filepath = self.last_save_filepaths.get(variant, None)

            filepath = self.last_save_filepaths[variant]
            self.out("starting filepath:", filepath)

            # TODO: Allow dask / pandas "modes" and only use partition_path if in dask mode, rather than assume dask
            if filepath is not None:   
                self.out("...filepath:", filepath)
                self.out("...calling getData({},{})".format(variant, child))
                data_dict = self.getData(variant=variant, child=child)
                self.out("...returned data_dict with keys:", type(data_dict))
                if data_dict is None:
                    self.out("ERROR! Could not find data sets to save for variant={}, child={}".format(variant, child), 
                             type='error')
                    return None

                self.out("...children:{}, this child='{}'".format(self.children(), child))
                self.out("...saving partitions for df (variant={}, child={}) inside folder: {}".format(variant, child, filepath))

                # Note! There's a bug in getData() that allows this dict to be ambiguous
                # Could be 1 var/>1 child or >1 vars/1 child each
                if isinstance(data_dict, dict):
                    # At this point we don't know whether the keys are variants or children...
                    for var_or_child in data_dict:
                        this_dict = data_dict[var_or_child]
                        #print("...key:", var_or_child)
                        if isinstance(this_dict, dict):
                            self.out('...got another dict')
                            # Then there are multiple variants and multiple children
                            var = var_or_child
                            this_var_cols = {}
                            for this_child in this_dict:
                                self.out("...child:", this_child)
                                # Iterate through each child and save it to disk
                                child_data = this_dict[this_child]
                                child_data_saved = saveDatasetToFile(child_data, filepath, variant=var, child=this_child)

                                # If the dataframe changed, save the child data to disk and store a reference to it again in memory
                                if child_data_saved is not None:
                                    self._loadDataIntoMemory(child_data_saved, variant=var, child=this_child)
                                    self._updateLastUpdated()

                                self.out("...done saving {}".format(type(child_data_saved)))
                        else:
                            # Save each variant/child (but we don't know which)
                            self.out("Going to save dataset for child='{}', type={} ==> path={}".format(var_or_child, type(this_dict), filepath))
                            #data_saved = saveDatasetToFile(this_dict, filepath)

                            # Save the new version too if it changed
                            #if data_saved is not None:
                            # Infer the variant/child
                            if variant == '*':
                                # Then we know each var_or_child is a variant
                                curr_variant = var_or_child
                                curr_child = child
                            elif child == '*':
                                # Then we know each var_or_child is a child
                                curr_variant = variant
                                curr_child = var_or_child
                            else:
                                # Not sure how this case could be reached!  But let's handle it by assuming each is a child.
                                curr_variant = variant
                                curr_child = var_or_child

                            data_saved = saveDatasetToFile(this_dict, filepath, variant=curr_variant, child=curr_child)
                            if data_saved is not None:
                                self._loadDataIntoMemory(data_saved, variant=curr_variant, child=curr_child)
                                self.out("...done saving {}".format(type(data_saved)))
                                self._updateLastUpdated()
                            else:
                                self.out("...saved data returned None")
                    self.out("...children: ", self.children())

                else:
                    # Then only one variant/child must have been returned by getData

                    # Infer which child is the only one for this variant
                    this_child = self.children()[variant][0]
                    self.out("...children before _loadDataIntoMemory: ", self.children(), this_child if this_child is not None else "None")

                    data_saved = saveDatasetToFile(data_dict, filepath, variant=variant, child=this_child)
                    if data_saved is not None:
                        self._loadDataIntoMemory(data_saved, variant=variant, child=this_child)
                        self.out("...only have one variant={} and child={}, saving {}".format(variant, this_child, type(data_saved)))
                        self._updateLastUpdated()
                    self.out("...children after _loadDataIntoMemory: ", self.children())

                # If overwrite=True, then delete the previous version of this featureset's file after saving the new one
                # Fixing this bug on 12/25/19
                # Note: Check to make sure the filename/path changed. It's possible for it to take <1 ms and *not* change.
                #if overwrite and previous_filename is not None and previous_filename != new_filename:
                    #self.out("...new filename: '{}'".format(new_filename))
                    #self.out("...previous filename: '{}'".format(previous_filename))
                    #self.deleteFile(previous_filename)
                if overwrite and previous_filepath is not None and previous_filepath != new_filepath:
                    self.out("...new filepath: '{}'".format(new_filepath))
                    self.out("...previous filepath: '{}'".format(previous_filepath))
                    self._deleteFilepath(previous_filepath)

        
        # Need to call this so the FeatureSpace updates its metadata file with the latest children created here
        # self.space.updateLastUpdated() # Moved inside updateFeatureSetList()
        self.space._updateFeatureSetMetadata(self.label)
    
    # TODO: Simplify this so it's not just a copy of save() with a few lines changed
    # TODO: Enable saving multiple or all variants per feature set at once, in the same directory, using '*' or a list 
    # By default the filetype is parquet/pyarrow (to save space). But you can pass 'csv' or 'fastparquet' in too.
    # Note: On 10/15/19, deprecating col_types since it's unused here
    # hide_index (added 10/16/20): True if all index columns ("IX::") created by FS should be hidden from the output
    # Added float_precision as an integer of the # of decimals to include, otherwise None will go by default
    def output(self, variant=None, child='*', overwrite=False, 
               save_to_disk=True, path=None, filename=None,
               filetype='parquet', schema_changed=True, 
               hide_index=False, encoding='utf-8', 
               float_precision=None):
        self.out("\nCalling FeatureSet '{}' output(variant={}, child={}, overwrite={}, save_to_disk={}, filetype={}, path={}, filename={}, schema_changed={})".format(self.label, variant, child, overwrite, save_to_disk, filetype, path, filename, schema_changed),
                type='progress')
        
#         previous_filename = self.last_save_filenames[variant] if variant in self.last_save_filenames else None
#         super().save(variant=variant, file_prefix='data', filetype=filetype)
#         new_filename = self.last_save_filenames[variant] if variant in self.last_save_filenames else None
        
        #++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Note: filename does not apply to saving a FeatureMatrix yet
        # Currently hide_index only applies to outputting dataframes to CSV
        def outputDatasetToFile(df, filepath, filename=None, variant=None, child=None, hide_index=False):
            self.out("\n...Inside saveDatasetToFile(df={}, filepath={}, child={})".format(type(df), filepath, child))
            
            if isinstance(df, dd.Series):
                # Since dask.Series.to_parquet fails currently, 
                # need to convert to dask.DataFrame first
                # See my issue here: https://github.com/dask/dask/issues/3982
                
                # Change on 5/6/19: Convert everything to pandas dataframe before saving
                df = df.to_frame().compute()
                # dd.to_parquet(df_dataframe, partition_path, engine='pyarrow', write_index=False)
            elif not isinstance(df, dd.DataFrame) and not isinstance(df, pd.DataFrame) and not isinstance(df, pd.Series):
                if hasattr(df, '__feature_type__') and df.__feature_type__=='FeatureMatrix':
                    # Use the custom class's save method
                    self.out("...saving FeatureMatrix to file as a numpy sparse matrix: ", filepath)
                    df.saveToFile(filepath)
                else:
                    self.out("WARNING! Data was not a DataFrame or Series, so cannot write it to file", type='warning')
                return df

            if filetype=='csv' or filetype=='CSV':
                csv_path = os.path.join(filepath, 'output.csv' if filename is None else filename)
                self.out("...starting to write to csv:", csv_path)
                
                # Hide the index cols (IX::) if hide_index=True
                if hide_index:
                    import FeatureSpace
                    index_col_prefix = FeatureSpace._get_index_col('')
                    non_index_cols = [col for col in df.columns if col[:len(index_col_prefix)]!=index_col_prefix and col not in self.index_cols]
                    df_to_save = df[non_index_cols]
                else:
                    df_to_save = df
                if isinstance(df_to_save, dd.DataFrame):
                    df_to_save.compute().to_csv(csv_path, index=False, na_rep='')
                else:
                    print("Saving dataframe {} to CSV with encoding '{}'".format(df_to_save.shape, 
                                                                                 encoding))
                    if isinstance(float_precision, int) and float_precision is not None:
                        df_to_save.to_csv(csv_path, index=False, na_rep='', encoding=encoding, 
                                          float_format='%.{}f'.format(float_precision))
                    else:
                        df_to_save.to_csv(csv_path, index=False, na_rep='', encoding=encoding, 
                                          float_format='%g')
                    
            elif filetype is None or filetype=='parquet' or filetype=='pyarrow' or filetype=='fastparquet':
                engine = 'fastparquet' if filetype=='fastparquet' else 'pyarrow'
                partition_path = os.path.join(filepath, 'parts.pq' if filename is None else filename)
                
                # Need to reduce precision of datetime[ns] columns to microseconds before saving to parquet with Dask
                # Since reloading later will cause problems 
                # (when the parquet file saved with schema [ms] is converted back to [ns] by dask then 
                # saved again to [ms], an error is thrown) 
                schema = None
                if engine == 'pyarrow':
                    # Check if the schema for this variant/child is already stored
                    if not schema_changed:
                        schema = self._getSchema(variant=variant, child=child)
                        self.out("Going to use this schema:", schema)
                        
                
                # Write the dataframe to a set of partitioned parquet files
                if isinstance(df, dd.DataFrame) or isinstance(df, dd.Series):
                    self.out("...writing Dask dataframe to parquet (engine={}, schema={}):".format(engine, schema), 
                          partition_path)
                    # Need to set the original Dask dataframe to point to the new one on disk
                    # 5/6/19: Passing in pyarrow_schema per https://github.com/dask/dask/issues/4194 
                    if engine=='pyarrow':
                        self.out("...since using pyarrow, must convert from Dask to pandas dataframe first")
                        new_df = df.compute()
                        self.out("...done")
                        if schema is not None:
                            new_table = pa.Table.from_pandas(new_df, schema=schema, preserve_index=False)
                            #pa.parquet.write_to_dataset(new_table, partition_path, preserve_index=False)
                            #pd.DataFrame.to_parquet(new_df, partition_path, engine='pyarrow', index=False, schema=schema)
                        else:
                            new_table = pa.Table.from_pandas(new_df, preserve_index=False)
                            self._saveSchema(new_table.schema, variant=variant, child=child)
                            self.out("...got new schema:", new_table.schema)
                        
                        pa.parquet.write_to_dataset(new_table, partition_path,
                                                    partition_filename_cb=lambda x:'part.{}.parquet'.format('0' if x is None else x))
                        #pa.parquet.write_to_dataset(new_table, partition_path, preserve_index=False)
                            #pd.DataFrame.to_parquet(new_df, partition_path, engine='pyarrow', index=False)
                    else:
                        dd.to_parquet(df, partition_path, engine='fastparquet', write_index=False)
                        
                        new_df = dd.read_parquet(partition_path, engine=engine)
                    
                    # Returning the df in this case to signal to add it back into the FeatureSet below
                    return new_df
                elif isinstance(df, pd.DataFrame):
                    self.out("...starting to write pandas dataframe to parquet (engine={}, schema={}):".format(engine, schema), 
                          partition_path)
                    # Save this pandas dataframe to parquet
                    # 5/6/19: Passing in pyarrow_schema per https://github.com/dask/dask/issues/4194 
                    if engine=='pyarrow':
                        if schema is not None:
                            new_table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)
                            #pd.DataFrame.to_parquet(df, partition_path, engine='pyarrow', index=None, schema=schema)
                        else:
                            new_table = pa.Table.from_pandas(df)
                            #new_table = pa.Table.from_pandas(df, preserve_index=False)
                            self._saveSchema(new_table.schema, variant=variant, child=child)
                            self.out("...got new schema:", new_table.schema)
                            #pd.DataFrame.to_parquet(df, partition_path, engine='pyarrow', index=None)
                        pa.parquet.write_to_dataset(new_table, partition_path,
                                                    partition_filename_cb=lambda x:'part.{}.parquet'.format('0' if x is None else x))
                        #pa.parquet.write_to_dataset(new_table, partition_path, preserve_index=False)
                    else:
                        pd.DataFrame.to_parquet(df, partition_path, engine='fastparquet', index=False)
                    
                    # Returning None to signal don't need to update the FeatureSet
                    return None
                elif isinstance(df, pd.Series):
                    self.out("...writing pandas series to parquet (engine={}, schema={}):".format(engine, schema), 
                             partition_path)
                    if engine=='pyarrow':
                        df_dataframe = pd.DataFrame(df)
                        new_table = pa.Table.from_pandas(df_dataframe, preserve_index=False)
                        pa.parquet.write_to_dataset(new_table, partition_path,
                                                    partition_filename_cb=lambda x:'part.{}.parquet'.format('0' if x is None else x))                        
                        #pa.parquet.write_to_dataset(new_table, partition_path, preserve_index=False)
                    else:
                        pd.Series.to_parquet(df, partition_path, engine='fastparquet', index=False)

                else:
                    return None
                #print("...returning: ", new_df.head())
                #return new_df
                
            else:
                self.out("WARNING! Filetype '{}' is not supported for saving this dataframe to file.".format(filetype), 
                         type='warning')
            self.out("...done")
            
            # Return None if the dataframe didn't change
            return None
        #++++++++++++++++++++++++++++++++++++++++++++++++++++

        if path is None:
            filepath = self.last_save_filepaths[variant]
        else:
            filepath = path
        self.out("starting filepath:", filepath)

        # TODO: Allow dask / pandas "modes" and only use partition_path if in dask mode, rather than assume dask
        if filepath is not None and save_to_disk:   
            self.out("...filepath:", filepath)
            self.out("...calling getData({},{})".format(variant, child))
            data_dict = self.getData(variant=variant, child=child)
            self.out("...returned data_dict with keys:", type(data_dict))
            if data_dict is None:
                self.out("ERROR! Could not find data sets to save for variant={}, child={}".format(variant, child), 
                         type='error')
                return None

            self.out("...children:{}, this child='{}'".format(self.children(), child))
            self.out("...saving partitions for df (variant={}, child={}) inside folder: {}".format(variant, child, filepath))
            # Note! There's a bug in getData() that allows this dict to be ambiguous
            # Could be 1 var/>1 child or >1 vars/1 child each
            if isinstance(data_dict, dict):
                # At this point we don't know whether the keys are variants or children...
                for var_or_child in data_dict:
                    this_dict = data_dict[var_or_child]
                    #print("...key:", var_or_child)
                    if isinstance(this_dict, dict):
                        self.out('...got another dict')
                        # Then there are multiple variants and multiple children
                        var = var_or_child
                        this_var_cols = {}
                        for this_child in this_dict:
                            self.out("...child:", this_child)
                            # Iterate through each child and save it to disk
                            child_data = this_dict[this_child]
                            child_data_saved = outputDatasetToFile(child_data, filepath, filename=filename, 
                                                                   variant=var, child=this_child, hide_index=hide_index)                                                        
                    else:
                        # Save each variant/child (but we don't know which)
                        self.out("Going to save dataset for child='{}', type={} ==> path={}".format(var_or_child, 
                                                                                                 type(this_dict), 
                                                                                                 filepath))
                        #data_saved = saveDatasetToFile(this_dict, filepath)
                        
                        # Save the new version too if it changed
                        #if data_saved is not None:
                        # Infer the variant/child
                        if variant == '*':
                            # Then we know each var_or_child is a variant
                            curr_variant = var_or_child
                            curr_child = child
                            # self._loadDataIntoMemory(data_saved, variant=var_or_child, child=child)
                        elif child == '*':
                            # Then we know each var_or_child is a child
                            curr_variant = variant
                            curr_child = var_or_child
                            #self._loadDataIntoMemory(data_saved, variant=variant, child=var_or_child)
                        else:
                            # Not sure how this case could be reached!  But let's handle it by assuming each is a child.
                            curr_variant = variant
                            curr_child = var_or_child
                            #self._loadDataIntoMemory(data_saved, variant=variant, child=var_or_child)

                        data_saved = outputDatasetToFile(this_dict, filepath, filename=filename, 
                                                         variant=curr_variant, child=curr_child, hide_index=hide_index)
                self.out("...children: ", self.children())

            else:
                # Then only one variant/child must have been returned by getData
                
                # Infer which child is the only one for this variant
                this_child = self.children()[variant][0]
                self.out("...children before _loadDataIntoMemory: ", self.children(), this_child if this_child is not None else "None")

                data_saved = outputDatasetToFile(data_dict, filepath, filename=filename, 
                                                 variant=variant, child=this_child, hide_index=hide_index)
                
            # Store the output location
            self.last_output_locations[variant] = {'path':path, 'filename':filename, 'filetype':filetype}
   
    # Appends the new rows of data to this FeatureSet in the file itself
    # Note: This assumes there is already a FeatureSet directory to write to -- it doesn't create one from scratch
    # new_schema=False: Use the previously saved schema if there is one
    # new_schema=True: Start over with a new schema to define the rows in this appended dataframe
    # TODO: Add checks that new_rows_df and this FeatureSet have the same columns/dtypes
    # TODO: Get rid of this manual coding for pyarrow
    # force_schema=True: if columns are missing in the new_rows_df but in the schema, create them to comply with the schema
    def append(self, new_rows_df, path=None, filename=None, variant=None, new_schema=False, filetype='parquet',
               force_schema=True):

        # TODO: Support appending to other than the parent
        child = None
        
        # Get the current location of the files storing this FeatureSet
        if path is None:
            filepath = self.last_save_filepaths[variant]
        else:
            filepath = path
        
        if filetype is None or filetype=='parquet' or filetype=='pyarrow' or filetype=='fastparquet':
            engine = 'fastparquet' if filetype=='fastparquet' else 'pyarrow'
            partition_path = os.path.join(filepath, 'parts.pq' if filename is None else filename)
            self.out("...appending to existing parquet files ({}):".format(engine), partition_path)
            if not os.path.exists(partition_path):
                self.out("...creating directory for parquet files:", partition_path)
                os.mkdir(partition_path)
            
            if engine=='fastparquet':
                dd.to_parquet(new_rows_df, partition_path, engine=engine, write_index=False, append=True)
            
            else:
                # Appending for pyarrow not yet implemented by dask, so implementing ourselves here 
                # From: https://stackoverflow.com/questions/47113813/using-pyarrow-how-do-you-append-to-parquet-file
                parquet_file_nums = sorted([int(re.findall(r'part.([0-9]+).parquet', f)[0]) for f in listdir(partition_path) 
                                    if isfile(join(partition_path, f)) and re.match("part.[0-9]+.parquet", f)])
                if len(parquet_file_nums)>0:
                    max_chunk_num = max(parquet_file_nums)
                    chunk_num = max_chunk_num + 1
                    self.out("...found last chunk saved #{}, will write to chunk #{}".format(max_chunk_num, chunk_num))
                else:
                    chunk_num = 0
                
                chunksize=self.space._DEFAULT_CHUNK_SIZE  #10000 # this is the number of lines

                # Convert the dataframe to pandas (if dask)
                new_rows_df = new_rows_df.compute() if isinstance(new_rows_df, dd.DataFrame) else new_rows_df

                # Reduce precision of datetime values to microseconds, to handle pyarrow bug (same as in save())
                df_dtypes = new_rows_df.dtypes
                self.out("Fixing pyarrow bug, found df types:", df_dtypes)
                datetime_cols = df_dtypes[df_dtypes=='datetime64[ns]']
                self.out("...have datetime_cols:", datetime_cols)
                for datetime_col in datetime_cols.index:
                    self.out("...fixing datetime_col:", datetime_col)
                    #new_rows_df[datetime_col] = new_rows_df[datetime_col].apply(lambda x: x.replace(nanosecond=0))
                self.out("...now have dtypes:", new_rows_df.dtypes)
                        
                # Get the schema of the base pyarrow table
                # NOTE: We assume the base pyarrow table is 'part.0.parquet', which is a byproduct of Dask really
#                 if 0 in parquet_file_nums:
#                     base_parquet_path = os.path.join(partition_path, 'part.0.parquet')
#                     base_table = pq.read_table(base_parquet_path)
#                     base_schema = base_table.schema
#                     print("Found schema:", base_schema)
#                 else:
#                     base_schema = None
                    
                if new_schema is True:
                    # Make sure to create a new schema file based on the data in the first chunk of this dataframe
                    base_schema = None
                else:
                    # Check if the schema for this variant/child is already stored
                    base_schema = self._getSchema(variant=variant, child=child)
                    self.out("Going to use this schema:", base_schema)
                
                pqwriter = None
                num_rows_to_append = new_rows_df.shape[0]
                num_cols_to_append = new_rows_df.shape[1]
                start_row = 0
                while start_row < num_rows_to_append:
                    # Create a pyarrow table, making sure it has the same schema as the base table
                    if base_schema is not None:
                        self.out("Creating pyarrow table on rows {} to {}".format(start_row, start_row+chunksize))
                        new_rows_df_thischunk = new_rows_df[start_row:start_row+chunksize]
                        
                        # Only if the setting is to force the given schema to work with the given dataframe
                        if force_schema:
                            new_rows_cols = new_rows_df_thischunk.columns
                            schema_cols = base_schema.names
                            schema_cols_not_in_new_rows = list(set(schema_cols)-set(new_rows_cols))
                            if len(schema_cols_not_in_new_rows)>0:
                                self.out("...schema has columns missing in the dataframe to append: {}".format(schema_cols_not_in_new_rows))
                                for schema_col_missing in schema_cols_not_in_new_rows:
                                    new_rows_df_thischunk[schema_col_missing] = None
                                    
                        table = pa.Table.from_pandas(new_rows_df_thischunk, 
                                                     preserve_index=False, schema=base_schema)
                    else:
                        # There wasn't a base schema for the first table, so save this table's schema
                        self.out("Creating pyarrow table on rows {} to {} with no schema".format(start_row, 
                                                                                                 start_row+chunksize))
                        table = pa.Table.from_pandas(new_rows_df[start_row:start_row+chunksize], 
                                                     preserve_index=False)
                        self._saveSchema(table.schema, variant=variant, child=child)
                        
                        # New on 3/18/20: Use this schema for the next chunks of the table
                        base_schema = table.schema
                        #print("...got schema:", table.schema)
                        
                        
                    self.out("Have table for rows {}:{}".format(start_row, start_row+chunksize))
                    
                    # create a parquet write object giving it an output file
                    parquet_path = os.path.join(partition_path, 'part.{}.parquet'.format(chunk_num))
                    self.out("...writing a chunk to parquet file: ", parquet_path)
                    pqwriter = pq.ParquetWriter(parquet_path, table.schema)
                    pqwriter.write_table(table)
                    pqwriter.close()
                    
                    self.out("...appended")
                    start_row += chunksize
                    chunk_num += 1
                    
                # Add to the # rows stored in dataset_shapes (and # cols if it's the first one so currently 0)
                curr_dataset_shape = self._getDatasetShape(variant=variant, child=child)
                cols_increment = num_cols_to_append if curr_dataset_shape is None or curr_dataset_shape[1]==0 else 0
                self._incrementDatasetShape((num_rows_to_append, cols_increment), variant=variant, child=child)
            
            
        elif filetype=='csv' or filetype=='CSV':
            csv_path = os.path.join(filepath, 'parts.csv')
            self.out("...appending to existing csv file:", csv_path)
            with open(csv_path, 'a') as f:
                new_rows_df.to_csv(f, index=False, header=False, na_rep='')
                
        else:
            self.out("WARNING! Filetype '{}' is not supported for appending this dataframe to file.".format(filetype),
                    type='warning')
            
        self.out("...done")
        self._updateLastUpdated()
             
    # Deletes from memory only, not from disk
    def delete(self):
        if hasattr(self, 'feature_cols') and hasattr(self, 'label_cols') and hasattr(self, 'index_cols'):
            del([self.feature_cols, self.index_cols, self.label_cols])
        # TODO: transformer function needs to be tied to the variant
        if hasattr(self, 'this_depends_on') and hasattr(self, 'transformer_function') and hasattr(self, 'depends_on_this'):
            del([self.this_depends_on, self.transformer_function, self.depends_on_this])
        if hasattr(self, 'dataset_shapes'):
            del([self.dataset_shapes])
        super().delete()
    
    # This is an external call that lets you load data into a FeatureSet from an external file
    # Note: This is considered "editing" to the FeatureSet if you provide an external file path (even if you direct this to a prior version of the FeatureSet on disk in the FeatureSpace archive)
    # Optionally you can leave the folder/path/filename out and this will reload the data from the existing backup file, but this will be considered "non-editing"
    #def load(self, variant=None):
    def load(self, folder=None, path=None, filename=None, variant=None, filetype='parquet'):
        if folder is None and path is None and filename is None:
            self.out("Using last_save_filenames to find the file path, since none provided.", type='debug')
            last_filename = self.last_save_filenames[variant]
            last_filetype = self.last_save_filetypes[variant]
            if last_filename is not None:
                self._loadDataFromFile(last_filename, variant=variant, filetype=last_filetype)
            else:
                self.out("Cannot load from file...don't know last saved filename", type='error')
        else:
            # If folder/path/filename provided, use them
            self._loadDataFromFile(folder, path=path, filename=filename, variant=variant, filetype=filetype)
            
            # Also consider this "editing" if an external file is being loaded
            self._updateLastUpdated()
            
    
    # Default is parquet / pyarrow, but can also specify 'fastparquet' or 'csv'
    def _loadDataFromFile(self, folder, path=None, filename=None, variant=None, filetype='parquet'):
        import psutil
        if path is None:
            filepath = self.getSaveDirectory(folder, variant=variant)
        else:
            filepath = path
        
        if filepath is not None:
        #if os.path.exists(filepath):
            if filetype is None or filetype=='parquet' or filetype=='pyarrow' or filetype=='fastparquet':
                engine = 'fastparquet' if filetype=='fastparquet' else 'pyarrow'
                # TODO: Push this filepath into a method that takes in filetype, not hard-coded everywhere
                # To remain backwards-compatible...
                filenames_to_try = ['parts.pq', 'part*.pq']
                filename_worked = False
                filename_load_errors = ''
                for filename_to_try in filenames_to_try:
                    if not filename_worked:
                        partition_filepath = os.path.join(filepath, filename_to_try if filename is None else filename)
                        self.out("Loading dataframe for variant '{}' from files in: {}".format(variant, partition_filepath), 
                                 type='debug')
                        #df = dd.read_parquet(partition_filepath, engine=engine, index=False)
                        # Change on 5/30/19: Read dataframes in as pandas, not dask (since they are saved as pandas)
                        self.out('...in _loadDataFromFile() before calling read_parquet...Memory: {}'.format(psutil.virtual_memory()))
                        try:
                            df = pd.read_parquet(partition_filepath, engine=engine)
                            filename_worked = True
                        except Exception as e:
                            filename_worked = False
                            filename_load_errors += "\n" + str(e)
                                                                                                                 
                # If all filenames didn't work, throw an error
                if not filename_worked:
                    self.out("ERROR: Failed to load parquet files at {} in directories: {}. Error={}".format(filepath, 
                                                                                                             filenames_to_try,
                                                                                                         filename_load_errors), 
                             type='error')
                    # Return False to indicate an error
                    return False
                self.out('...in _loadDataFromFile() after calling read_parquet...Memory: {}'.format(psutil.virtual_memory()))
            elif filetype=='csv' or filetype=='CSV':
                csv_filepath = os.path.join(filepath, 'output.csv' if filename is None else filename)
                self.out("Loading dataframe from CSV file: {}".format(csv_filepath), type='progress')
                #df = dd.read_csv(csv_filepath)                
                # Change on 5/30/19: Read dataframes in as pandas, not dask (since they are saved as pandas)
                self.out('...in _loadDataFromFile() before calling pd.read_csv...Memory: {}'.format(psutil.virtual_memory()))
                df = pd.read_csv(csv_filepath)
                self.out('...in _loadDataFromFile() after calling pd.read_csv...Memory: {}'.format(psutil.virtual_memory()))
            self._loadDataIntoMemory(df, variant=variant)
            del(df)
            self.out('...in _loadDataFromFile() after calling _loadDataIntoMemory...Memory: {}'.format(psutil.virtual_memory()))
        else:
            self.out("ERROR: Cannot find file at {} to read into feature set {}".format(filepath, self.label), type='error') 
            
            
        # Check for any children by looking for matrix_*.npz in the filepath
        metadata_files = [f for f in listdir(filepath) if isfile(join(filepath, f)) and re.match(r'metadata_[^"]+.dll', f)]
        self.out("FOUND CHILD METADATA FILES:", metadata_files)
        for metadata_file in metadata_files:
            child_label = re.findall(r'metadata_(.+).dll', metadata_file)[0]
            child_metadata = dill.load(open(join(filepath, metadata_file), 'rb'))
            self.out(child_label, "...", child_metadata.keys())
            child_matrix_file = child_metadata['matrix_file']
            
            # Note: Assuming all chilren are FeatureMatrix objects for now
            #child_matrix_obj = FeatureMatrix(child_label, matrix, 
            child_matrix_obj = FeatureMatrix(label=child_label, 
                                             project=self.project_label, 
                                             batch=self.batch, 
                                             space=self.space,
                                             variant=variant,
                                             parent_label=self.label,
                                             #matrix=onehot_coo_matrix, 
                                             columns=child_metadata['columns'], 
                                             mappings=child_metadata['mappings'])
            #new_featureset = FeatureSet(save_directory=FeatureSpace_directory, label=feature_set_label, project=self.project_label, batch=batch, space=self)
            child_matrix_obj._loadDataFromFile(child_matrix_file, variant=variant)
            self._loadDataIntoMemory(child_matrix_obj, variant=variant, child=child_label)
            
        # If find a child, create a FeatureMatrix object and call its _loadDataFromFile
        # Store that child in this FeatureSet using _loadDataIntoMemory
        
        # Return True to indicate this worked
        return True
        
    def _addDependency(self, this_depends_on=None, depends_on_this=None, transformer_function=None):
        if this_depends_on is not None:
            if this_depends_on not in self.this_depends_on:
                self.this_depends_on.append(this_depends_on)
                self.transformer_function.append(transformer_function)
                self._updateLastUpdated()
        if depends_on_this is not None:
            if depends_on_this not in self.depends_on_this:
                self.depends_on_this.append(depends_on_this)
                self._updateLastUpdated()
                
    # category_list can be one of these types:
    # - List or Set of category values --> use these values (and onehot_prefix if provided) to create the one-hot var names automatically
    # - String --> indicates to use the FeatureSet with this label, must be accompanied by a *category_list_var* indicating which column to use in that FeatureSet (this also uses the values in that column to create the one-hot var names)
    #   Note: For this option, we currently only support variant=None
    # - Dict --> {val_1:'A', val_2:'B', ...} indicating to label the one-hot var [onehot_prefix|'is']_A for category value val_1, and so on.  Use this to customize one-hot var names yourself without relying on the values themselves.
    # - None --> indicates to use all values in *values_var* as categories to create one-hot vars
    # Note: We will de-duplicate values provided for the category list here. If provided a Dict with duplicate keys, this means we will pick the *last* one of the key-value pairs to decide which category var name to use.  And if provided duplicate values
    # for different keys, then the category var names will be appended with 1,2,3,etc. so as not to have conflicting mappings.
    # However if we are given ['Category One', 'Category. One'], these values are not duplicates yet both map to 'category_one' as the onehot var name, so we will automatically make the second one 'category_one_2'.
    # matrix_label: If None --> the outputted child matrix will be given the label of values_var.  Otherwise this will be the outputted child matrix's label.
    # 10/10/20: Introducing values_var as a list of vars, where the 1HV will be created for each token found in any of those columns
    # 10/11/20: Added ignore, which can be a string or a list of values to ignore when creating 1HVs, such as '' or None
    def createCategoricalOneHot(self, values_var, 
                                category_list=None, category_list_var=None, 
                                onehot_prefix=None, 
                                matrix_label=None, 
                                ignore=None, # str or list or None
                                max_length=None, # must be int or None
                                variant='*',
                                save_to_disk=True): # allow for this not to update the whole featureset on disk, just in RAM
        import psutil
        self.out("\nStarting createCategoricalOneHot(values_var={}...)".format(values_var), type='progress')
        self.out('...Memory: {}'.format(psutil.virtual_memory()))

        # Reload the FeatureSpace metadata first to make sure we reload the latest files
        self.out("Reloading the FeatureSpace...")
        self.space._loadFeatureSetMetadata()
        
        # New feature 1/1/2021: This should free up memory too
        self.space.freeUpMemory([self.label])
        
        # Create a new column for each value in the given category_list
        df_variants = self.getData(variant, child=None)
        self.out('...after getData...Memory: {}'.format(psutil.virtual_memory()))
        
        # If this is a single dataframe, then turn it into a dict so we can iterate through anyway
        # TODO: Change this if we change the contract on getData() returning just a dataframe if the only variant is None
        if not isinstance(df_variants, dict):
            if variant=='*':
                # The variant in this case should be None. But let's check for sure.
                df_variants = {self.variants()[0]: df_variants}
            else:
                df_variants = {variant: df_variants}
        
        # Create a copy of the list of variants since this dict is mutable
        variant_list_copy = list(df_variants.keys()).copy()
        self.out("...got data with list of variants: ", variant_list_copy)
           
        ignore_list = [ignore] if isinstance(ignore, str) and ignore is not None else ignore
        
        # Iterate through each variant and run this transform on it
        for this_variant in variant_list_copy:
            self.out('...Memory: {}'.format(psutil.virtual_memory()))
            this_df = df_variants[this_variant] #Already requested just the None child
            self.out("this_df: {}".format(this_df.shape))
            self.out('...Memory: {}'.format(psutil.virtual_memory()))
            #this_df_shape = self.shape(variant=this_variant, child=None)
            #print("Starting with variant={}...shape={}".format(this_variant, this_df_shape))
            self.out("Starting with variant={}".format(this_variant))
            self.out(type(this_df))
            
            new_cols = []
            ##onehot_vars_dict = {}  # Deprecating as of 10/11/20
            
            # Check how the names of the new one-hot vars should be created
            category_values = None
            create_category_vars_from_values = True
            if isinstance(category_list, list) or isinstance(category_list, tuple):
                # Use the given list of values
                create_category_vars_from_values = True
                
                # De-duplicate any repeated values in the given list
                category_values = list(set(category_list))
            elif isinstance(category_list, set):
                create_category_vars_from_values = True
                category_values = list(category_list)
            elif isinstance(category_list, str):
                # Use the FeatureSpace
                if category_list_var is not None:
                    # Lookup the category values in the FeatureSpace using category_list_var
                    category_list_variant = None # Current assumption, see note above
                    self.out("Using category values from fs.Features('{}')['{}'] for variant={}: ".format(category_list, category_list_var, category_list_variant), category_values)
                    category_data = self.space.Data(category_list, variant=category_list_variant)[category_list_var]
                    if isinstance(category_data, dd.DataFrame) or isinstance(category_data, da.Array) or isinstance(category_data, dd.Series):
                        self.out("Converting from Dask {} to Numpy/Pandas".format(type(category_data)))
                        category_data = category_data.compute()
                    category_values = category_data.drop_duplicates().values.tolist()
                    create_category_vars_from_values = True
                else:
                    self.out("ERROR: If 'category_list' is a string indicating which FeatureSet to use, then you must provide a 'category_list_var' to tell which column in that FeatureSet to use to get the list of category values.", type='error')
                    return None
            elif isinstance(category_list, dict):
                # Use the keys in the given dict structure
                category_values = list(set(category_list.keys()))
                create_category_vars_from_values = False
            elif category_list is None:
                category_data = self.getData(variant=this_variant, child=None)[values_var]
                if isinstance(category_data, dd.DataFrame) or isinstance(category_data, da.Array) or isinstance(category_data, dd.Series):
                    self.out("Converting from Dask {} to Numpy/Pandas".format(type(category_data)))
                    category_data = category_data.compute()
                # Create a list of unique values in all column(s) of values_var
                category_values = pd.unique(category_data.values.ravel('K')).tolist()
                #category_values = category_data.drop_duplicates().values.tolist()
                self.out("Using category values in column '{}': ".format(values_var), category_values)
                create_category_vars_from_values = True
            else:
                self.out("ERROR: Parameter 'category_list' must be a list, tuple, set, string, dict, or None.", type='error')
                return None
        
            # Remove any values given in 'ignore' from the category values to use to create 1HVs
            if ignore_list is not None:
                self.out("Removing category values from ignore list: {}".format(ignore_list))
                category_values = [val for val in category_values if val not in ignore_list]
                
            # Remove any values with length > max_length (if given), to take out long text
            if max_length is not None and isinstance(max_length, int):
                self.out("Removing category values with length>{}".format(max_length))
                category_values = [val for val in category_values if not isinstance(val, str) or len(val)<=max_length]
            
            # Iterate through each value in the list of categories
            self.out("Looking for each of {} unique values in these {} category vars: {}".format(len(category_values),
                                                                                                 len(values_var) if isinstance(values_var, list) else 1, values_var))
            for val in category_values:
                # Create the column for the new one-hot variable
                prefix = onehot_prefix if onehot_prefix is not None else 'is'
                new_val_label = '{0}_{1}'.format(prefix, super()._urlify(val) if create_category_vars_from_values else category_list[val])
                
                # Cap the length of the column labels, in case the category value is long text 
                max_column_length = 100
                if len(new_val_label) > max_column_length:
                    new_val_label = new_val_label[:max_column_length]

                # Look for duplicative column labels --> append _1, _2 etc. to keep them all unique
                if new_val_label in new_cols:
                    try_to_append = 1
                    while new_val_label+'_{}'.format(try_to_append) in new_cols:
                        try_to_append += 1
                    new_val_label = new_val_label+'_{}'.format(try_to_append)
                
                # Make sure this column name is not already there from a previous category
                append_num = 0
                base_new_val_label = new_val_label
                while new_val_label in new_cols:
                    append_num += 1
                    new_val_label = base_new_val_label + '_{}'.format(append_num)

                # Store this new column label
                new_cols.append(new_val_label)

                #if onehot_type in ['freq', 'frequency', 'count', 'counts']:
                #    # If the onehot type is frequency, count up the # of times any variable in this row has each value
                #    onehot_vars_dict[new_val_label] = lambda x, y=val:(x==y).sum()
                #else:
                #    # Otherwise it's a 1/0 vector of whether or not that row has a value
                #    onehot_vars_dict[new_val_label] = lambda x, y=val:int((x==y).max())
                #    #onehot_vars_dict[new_val_label] = lambda x, y=val:(x[values_var]==y).astype(int)
                if isinstance(values_var, list):
                    self.out("Creating one-hot {} when any values_var='{}'".format(new_val_label, val[:200] if isinstance(val,str) else val))
                else:
                    self.out("Creating one-hot {} when {}='{}'".format(new_val_label, values_var, val[:200] if isinstance(val,str) else val))
            self.out("Finished collecting values for creation of one-hots.")       
            self.out('...Memory: {}'.format(psutil.virtual_memory()))

            vals = category_values #['aaa','bbb','ccc']
            column_mapper = {x:i for i,x in enumerate(vals)}

            self.out("...column_mapper:", len(column_mapper))
            column_data = this_df[values_var].compute() if isinstance(this_df, dd.DataFrame) else this_df[values_var]
            self.out("...column_data:", column_data.shape)
            self.out("...this_df:", this_df.shape)
            
            if isinstance(values_var, list):
                self.out("Going to apply column_mapper with {} values".format(len(column_mapper)))
                row_cols = None
                for value_var in values_var:
                    self.out("...values_var={}".format(value_var))
                    one_column_data = this_df[value_var].compute() if isinstance(this_df, dd.DataFrame) else this_df[value_var]
                    self.out("...one_column_data={}".format(one_column_data.shape))
                    one_row_cols = np.array([(i, column_mapper[x]) for i,x in enumerate(one_column_data) if x in column_mapper],
                                             dtype=np.uint32)
                    self.out("...one_row_cols={}".format(one_row_cols.shape))

                    #all_row_cols.append(one_row_cols)
                    if one_row_cols is not None and one_row_cols.shape[0]>0:
                        if row_cols is None:
                            row_cols = one_row_cols
                        else:
                            # Only stack more 1s if there are mapped values in this column
                            row_cols = np.vstack([row_cols, one_row_cols])
                        self.out("...after flagging {} values of column {}, now have row_cols: {}".format(one_row_cols.shape,
                                                                                                         value_var,
                                                                                                         row_cols.shape))
                    else:
                        self.out("...no values found in column {}".format(value_var), type='error')
                        
                    #self.out('...Memory after values_var={}: {}'.format(values_var, psutil.virtual_memory()))
                #del(one_row_cols)
                #row_cols = np.vstack(all_row_cols) #[inner for outer in all_row_cols for inner in outer]
                if row_cols is None:
                    self.out("ERROR: No values of {} found after excluding the ignore list ({}) to use to create one-hots.".format(values_var, ignore_list), type='error')
                    raise
                self.out("...now have row_cols: {}".format(row_cols.shape))
                self.out('...Memory after values_vars={}: {}'.format(values_var, psutil.virtual_memory()))

            else:
                self.out("single values_var:", values_var)
                self.out(column_data)
                row_cols = np.array([(i, column_mapper[x]) for i,x in enumerate(column_data) if x in column_mapper])
                self.out(len(row_cols))
                
            # Create ones matrix for all non-zero values found above
            # TODO: Enable counting (>1) of occurrences instead of only 1/0 if a list is passed into values_var
            data = np.ones(len(row_cols), dtype=np.int8)

            self.out("data", data.shape)
            self.out("row_cols", len(row_cols), row_cols.shape)
            self.out("column_data:", column_data.shape)
            self.out("shape: ({},{})".format(column_data.shape[0], len(column_mapper)))
            self.out("new_cols:", len(new_cols))
            self.out("column_mapper:", len(column_mapper))
            self.out('...Memory before coo_matrix: {}'.format(psutil.virtual_memory()))
            
            # Also check if all the values in the dataframe don't match any of the given categorical values
            if len(row_cols)==0:
                self.out("ERROR: None of the values in var '{}' match the given categorical values: {}".format(values_var,
                                                                                                               category_values),
                         type='error')
                raise
                
            # Check for no values to convert to 1HV, throw an error so this is shown to the user
            elif data.shape[0]==0:
                self.out("ERROR: There are no values in var '{}' to convert into a one hot vector.".format(values_var),
                         type='error')
                raise
                

                
            # Note on 1/1/2021: Changing to storage as csr (not coo) matrix since it's more compressed for many-rows / Big Data
            # (and we end up converting to csr often in transforms anyway)
            #onehot_csr_matrix = coo_matrix((data, zip(*row_cols)), # <-- this zip(*row_cols) crashes the kernel!
            onehot_csr_matrix = coo_matrix((data, (row_cols[:,0], row_cols[:,1])), 
                                           shape=(column_data.shape[0], len(column_mapper)), 
                                           dtype=np.int8).tocsr()
            self.out('...Memory after coo_matrix: {}'.format(psutil.virtual_memory()))
            del(row_cols)

            self.out("New sparse matrix:", type(onehot_csr_matrix), onehot_csr_matrix.shape)
            self.out('...Memory: {}'.format(psutil.virtual_memory()))
            
            #onehot_df = this_df[[values_var]].merge(onehot_dummy_vector).drop(values_var, axis=1).compute()
            #onehot_numpy_matrix = onehot_df.values
            #print("Created new one-hot df:", onehot_df.shape, " and numpy matrix:", onehot_numpy_matrix.shape)
            
            # TODO handle >1 values_var
            # Change on 7/29/19: Need to take out any / in the var name before saving the child matrices
            if matrix_label is not None:
                child_matrix_label = matrix_label
            elif isinstance(values_var, str):
                child_matrix_label = values_var.replace('/', '_')
            else:
                # Assume a list
                if len(values_var)<=3:
                    # Then concatenate the values vars
                    child_matrix_label = '_'.join(values_var).replace('/', '_')
                else:
                    child_matrix_label = values_var[0].replace('/','_')+'('+str(len(values_var))+')'
                     
            # Store the one-hot matrix data with the columns and mappings of string:column #
            #onehot_matrix_object = FeatureMatrix(values_var, onehot_coo_matrix, columns=new_cols, mappings=column_mapper)
            onehot_matrix_object = FeatureMatrix(label=child_matrix_label,
                                                 parent_label=self.label,
                                                 matrix=onehot_csr_matrix, 
                                                 columns=new_cols, 
                                                 mappings=column_mapper)
            self._loadDataIntoMemory(onehot_matrix_object, variant=this_variant, child=child_matrix_label)
            
            # Update the last updated timestamp
            self._updateLastUpdated()
            
            # Use assign() to insert all the new one-hot vars at once
            #print("Using one-hot vars dict:", onehot_vars_dict)
            ##this_df = this_df.assign(**onehot_vars_dict)

            self.out("Created {} new one-hot columns using column(s) {}".format(len(new_cols), values_var), type='progress')
            #print(this_df.iloc[:,22:120].sum().compute().values)

            # Add these new one-hot columns as feature columns
            ##self._loadDataIntoMemory(this_df, variant=this_variant)
            #print("...result is df with shape:", self.shape(this_variant))
            ##del(this_df)
            ##gc.collect()
            
            # Deprecating as of 10/10/20
            # Turn the categorical col into an index_col, and the one-hots into feature_cols
            #self._addColumnTypes(variant=this_variant, feature_cols=new_cols, index_cols=values_var)
            #self.save(overwrite=True, variant=this_variant, child='*')
            self.save(overwrite=True, variant=this_variant, child='*', schema_changed=True,
                      save_to_disk=save_to_disk)
        #self.view()
            # Need to call this so the FeatureSpace updates its metadata file with the latest children created here
            #self.space.updateLastUpdated()
            #self.space.updateFeatureSetList()

    # index_var is how to group poolings together
    # col is what to aggregate
    # pooling_var is the name of the new pooling var
    # pool_type is 'max', 'min', 'mean', 'median', 'count'
    def createEncodingFeature(self, index_var, col, encoding_var, encoding_type='max', variant=None):
        # Reload the FeatureSpace metadata first to make sure we reload the latest files
        self.out("Reloading the FeatureSpace...")
        self.space._loadFeatureSetMetadata()

        # New feature 1/1/2021: This should free up memory too
        self.space.freeUpMemory([self.label])
        
        df = self.getData(variant=variant, child=None)
        agg_df = df.groupby(index_var, as_index=False).agg({col:(encoding_type)})
        agg_df.columns = [index_var, encoding_var]
        import psutil
        # In case this encoding var is already there, drop it and create new one
        if encoding_var in df:
            old_df = df.drop(encoding_var, axis=1, inplace=False)
        else:
            old_df = df
        
        # Merge in the new encoding var
        #new_agg_df = pd.merge(old_df[[index_var]], agg_df, how='left', on=[index_var])
        new_agg_df = dd.merge(old_df[[index_var]], agg_df, how='left', on=[index_var])
        new_agg_col = new_agg_df[encoding_var]
        #new_df = pd.concat([old_df, new_agg_col], axis=1)
        new_df = dd.concat([old_df, new_agg_col], axis=1)
        #new_df = pd.merge(old_df, agg_df, how='left', on=[index_var])
        del((old_df, agg_df, new_agg_df, new_agg_col))
        #self.update(new_df)
        self._loadDataIntoMemory(new_df, variant=variant)
        
        # Make sure this new encoding var is considered a feature
        self._addColumnTypes(index_cols=index_var, feature_cols=encoding_var)
        del(new_df)
        gc.collect()
        #print(psutil.virtual_memory()) 
        self.out("Created new {} encoding var: {}".format(encoding_type, encoding_var), type='progress')

        # Update the last updated timestamp
        self._updateLastUpdated()

        # Save this updated FeatureSet
        #self.save(overwrite=True, variant=variant)
        self.save(overwrite=True, variant=variant, child='*', schema_changed=True)

         
        self.view()
        # Need to call this so the FeatureSpace updates its metadata file with the latest children created here
        #self.space.updateLastUpdated()
        #self.space.updateFeatureSetList()
       
    # For numeric buckets between some min and max values, buckets should be tuples:
    # {bucket_var1: (min or None, max or None), 
    #  bucket_var2: (min or None, max or None)}
    # exclusive=True means min/max are < or >, exclusive=False means min/max are <= or >= (only relevant for numeric)
    # For category buckets to create buckets around a list of values, buckets should be lists:
    # {bucket_var1: [bucket_val1, bucket_val2],
    #  bucket_var2: [bucket_val3],
    #  bucket_var3: '*' --> this indicates to give bucket_var3 all other values not in the other lists.  only works for one bucket.
    # } 
    # TODO: Enable this for children other than child=None
    def createBucketFeature(self, col, buckets, exclusive=False, variant='*', engine='dask'):
        # Reload the FeatureSpace metadata first to make sure we reload the latest files
        self.out("Reloading the FeatureSpace...")
        self.space._loadFeatureSetMetadata()
        
        # New feature 1/1/2021: This should free up memory too
        self.space.freeUpMemory([self.label])
        
        # TODO: Don't repeat this code for variants.  Instead create some equivalent of transform() for a FeatureSet.
        this_child = None
        df_variants = self.getData(variant, child=this_child)
        
        # If this is a single dataframe, then turn it into a dict so we can iterate through anyway
        # TODO: Change this if we change the contract on getData() returning just a dataframe if the only variant is None
        if not isinstance(df_variants, dict):
            if variant=='*':
                # The variant in this case should be None. But let's check for sure.
                df_variants = {self.variants()[0]: df_variants}
            else:
                df_variants = {variant: df_variants}
        
        # Create a copy of the list of variants since this dict is mutable
        variant_list_copy = list(df_variants.keys()).copy()
        self.out("...got data with list of variants: ", variant_list_copy)
            
        # Iterate through each variant and run this transform on it
        for this_variant in variant_list_copy:
            df = df_variants[this_variant] #[this_child]
            #df_shape = self.shape(variant=this_variant, child=this_child)
            #print("Starting with variant={}...shape={}".format(this_variant, df_shape))
            self.out("Starting with variant={}".format(this_variant))
            #shape_this_variant = df_shape[this_variant]
            #if isinstance(shape_this_variant, dict):
            #    num_rows = shape_this_variant[this_child][0]
            #else:
                # Handling the possibility that this holds a tuple
            #num_rows = shape_this_variant[0]
            #num_rows = df_shape[0]

            if engine=='pandas' and isinstance(df, dd.DataFrame):
                self.out("...converting dask to pandas for variant='{}'".format(this_variant))
                df = df.compute()
                self.out("...done")
            
            self.out(df.columns)
            new_cols = []
            all_bucket_values = set()
            for bucket_var in buckets:
                bucket_def = buckets[bucket_var]
                bucket_condition = None
                if isinstance(bucket_def, tuple):
                    # Then treat this as a numeric bucket with a min / max
                    bucket_min = bucket_def[0]
                    bucket_max = bucket_def[1]
                    self.out("For bucket '{}', adding numeric values between {} and {} ({})".format(bucket_var, bucket_min, bucket_max, 'exclusive' if exclusive else 'inclusive'), type='progress')
                    
                    # Create a new var
                    if exclusive:
                        # 4/19/19: Fixing bug in closure of variable referenced in lambda function here
                        bucket_condition = lambda x, bucket_min=bucket_min, bucket_max=bucket_max: 1 if ((bucket_min is None or x>bucket_min) and (bucket_max is None or x<bucket_max)) else 0           
                    else:
                        bucket_condition = lambda x, bucket_min=bucket_min, bucket_max=bucket_max: 1 if ((bucket_min is None or x>=bucket_min) and (bucket_max is None or x<=bucket_max)) else 0
                elif isinstance(bucket_def, list):
                    # Then bucket together the values provided in this list
                    bucket_list = bucket_def
                    self.out("For bucket '{}', adding values {}".format(bucket_var, bucket_list))
                    bucket_condition = lambda x, bucket_list_copy=bucket_list: 1 if x in bucket_list_copy else 0
                    all_bucket_values |= set(bucket_list)
                elif isinstance(bucket_def, str) and bucket_def=='*':
                    # Then add all values not already listed before to this bucket
                    self.out("For bucket '{}', '*' provided so adding all values not in {}".format(bucket_var, all_bucket_values))
                    bucket_condition = lambda x, all_bucket_values_copy=all_bucket_values: 1 if x not in all_bucket_values_copy else 0
                
                if bucket_condition is not None:
                    self.out("...applying condition")
                    df[bucket_var] = df[col].apply(bucket_condition)
                    new_cols.append(bucket_var)

            self._loadDataIntoMemory(df, variant=this_variant)
            self._addColumnTypes(feature_cols=new_cols, variant=this_variant)

            # Update the last updated timestamp
            self._updateLastUpdated()            
            
            self.out("Calling save from createBucketFeature...")
            #self.save(overwrite=True, variant=this_variant)
            self.save(overwrite=True, variant=this_variant, child='*', schema_changed=True)
            

            
        self.view()
            
            # Need to call this so the FeatureSpace updates its metadata file with the latest children created here
            #self.space.updateLastUpdated()
            #self.space.updateFeatureSetList()

  
        