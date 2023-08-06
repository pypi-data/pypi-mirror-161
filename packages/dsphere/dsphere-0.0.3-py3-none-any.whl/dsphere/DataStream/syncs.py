# This is ready for writing "syncs" which copy data or files to/from multiple connectors (e.g. AWS S3 <--> SFTP)
import dsphere.connectors as con
import fnmatch
import os
from typing import Optional
import tempfile
import pandas as pd
import datetime
import re
import glob
import shutil
from boto.s3.key import Key
import jinja2
import six
import numbers
import sys

# Note: TYPE is a reserved keyword in the parameters for each source
# This static generator will create any type of connector -- need to add new types to this method
def _GetSync(DataStream=None, **kwargs):
    if 'TYPE' in kwargs:
        type_lower = kwargs['TYPE'].lower()
        kwargs.pop('TYPE')
    elif 'type' in kwargs:
        type_lower = kwargs['type'].lower()
        kwargs.pop('type')
    else:
        print("ERROR: Cannot create Sync since 'type' is not defined")
        return None
    
    if type_lower=='file' or type_lower=='files':
        #print("Created File Sync object...")
        return File_Sync(DataStream=DataStream, type=type_lower, **kwargs)
    elif type_lower=='load' or type_lower=='loads':
        #print("Created Load Sync object...")
        return Load_Sync(DataStream=DataStream, type=type_lower, **kwargs)
    elif type_lower == 'export' or type_lower == 'exports':
        #print("Created Export Sync object...")
        return Export_Sync(DataStream=DataStream, type=type_lower, **kwargs)    
    elif type_lower == 'archive' or type_lower == 'archives':
        #print("Created Archive Sync object...")
        return Archive_Sync(DataStream=DataStream, type=type_lower, **kwargs)
    elif type_lower == 'database' or type_lower == 'db':
        #print("Created Database Sync object...")
        return Database_Sync(DataStream=DataStream, type=type_lower, **kwargs)
    
    
    return None
    

##############################
### Parent Sync class ###
class Sync:
    # A Sync object contains Connectors
    connectors = {}
    sync_params = None
    DataStream = None
    type = None  # type can be 'files', 'database', 'featurespace'
    jinja_env = jinja2.Environment(cache_size=0)
    
    def __init__(self, DataStream=None, type=None, required=None, template_fields=None, template_dict=None, template_py_file=None, **kwargs):
        if template_fields is None:
            template_fields = []
        self.type = type
        self.DataStream = DataStream
        self.connectors = DataStream.connectors

        self.sync_params = kwargs
        self.template_fields = template_fields
        self.template_dict = template_dict
        self.template_py_file = template_py_file
        
        # If provided a list of required parameters, then confirm that each one is defined
        #print("Required:", required)
        if required is not None:
            for param in required:
                if param not in self.sync_params:
                    print("ERROR: Required parameter {} has not been defined for this connector of type {}".format(param, 
                                                                                                                   self.type))
                    raise
                        
    def run(self):
        self.apply_template_to_fields()
        return
    
    def get_context(self):
        from DataStream import macros
        project = None
        batch = None
        if self.DataStream.FeatureSpace is not None:
            project = self.DataStream.FeatureSpace.project_label
            batch = self.DataStream.FeatureSpace.default_batch

        today = datetime.date.today().strftime('%Y-%m-%d')
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # TODO: add handling for when template_py_file is specified -- need to make import dynamic
        
        return {
            'today': today,
            'yesterday': yesterday,
            'tomorrow': tomorrow,
            'project': project,
            'batch': batch,
            'macros': macros
        }
    
    def apply_template_to_field(self, value, context):
        """
        Applies jinja templating for string fields directly using provided context 
        & goes through lists/dicts recursively to render string values within them.
        Leaves numeric data & any unexpected types as-is.
        """
        env = self.jinja_env
        if isinstance(value, six.string_types):
            # render strings directly with jinja
            rendered = env.from_string(value).render(**context)
        elif isinstance(value, numbers.Number):
            # leave number values as-is
            rendered = value
        elif isinstance(value, (list, tuple)):
            # render each item in a list or tuple
            rendered = [self.apply_template_to_field(v, context) for v in value]
        elif isinstance(value, dict):
            # render the value for each key in a dict
            rendered = {k: self.apply_template_to_field(v, context) for k, v in value.items()}
        else:
            param_type = type(value)
            print("Unable to apply templating for type '{}', will leave value as-is".format(param_type))
            rendered = value
        return rendered
    
    def apply_template_to_fields(self):
        # dynamically get values to use for rendering
        render_context = self.get_context()
        if self.template_dict:
            # note: this can overwrite default values from get_context
            render_context.update(self.template_dict)

        for field in self.template_fields:
            val = self.sync_params.get(field)
            if val:
                rendered_val = self.apply_template_to_field(val, render_context)
                self.sync_params[field] = rendered_val
    
    
############################################################
### Sync files in 'from' location into the 'to' location ###
class File_Sync(Sync):
    required_params = ['from', 'to'] # This Sync will fail if either of these params are missing
    DEFAULT_REGION = 'us-east-1'

    def __init__(self, DataStream=None, type=None, **kwargs):
        Sync.__init__(self, DataStream=DataStream, type=type, required=self.required_params, **kwargs)

    def _sync_sftp_files_to_s3(self, sftp_conn: str, #SFTP_Connector, # Now pass in the name of the connector
                                  sftp_dir: str, 
                                  sftp_file_string: str, 
                                  s3_conn: str, #S3_Connector, # Now pass in the name of the connector
                                  s3_dir: str, 
                                  #local_dir: str = '.', 
                                  #temp_file: str = 'TEMP',
                                  delete_temp_file: bool = True, 
                                  overwrite_s3_files: bool = False,
                                  include_subdirs: bool = False) -> None:
            print(f'Sync files from SFTP to S3 called with args: sftp_conn={sftp_conn}, '
                  f'sftp_dir={sftp_dir}, sftp_file_string={sftp_file_string}, '
                  f's3_conn={s3_conn}, s3_dir={s3_dir}, ' #local_dir={local_dir}, '
                  #f'temp_file={self.temp_file}, '
                  f'delete_temp_file={delete_temp_file}, '
                  f'overwrite_s3_files={overwrite_s3_files}, include_subdirs={include_subdirs}\n')

            local_temp_file = self.DataStream.temp_file #os.path.join(local_dir, temp_file)

            # Get S3 and SFTP connectors
            if sftp_conn in self.connectors:
                sftp_connector = self.connectors[sftp_conn]
            else:
                print("Do not have connector information for the given SFTP connector '{}'".format(sftp_conn))
                return None
            if s3_conn in self.connectors:
                s3_connector = self.connectors[s3_conn]
            else:
                print("Do not have connector information for the given S3 connector '{}'".format(s3_conn))
                return None

            # get list of existing s3 files
            s3_files = s3_connector.read(s3_dir, type='list')
            print("Found {} files in the target directory on S3: {}".format(len(s3_files), s3_dir))
            # get list of SFTP files
            sftp_file_list = sftp_connector.read(sftp_dir, type='list')
            print("...searching from {} files on SFTP in {} matching {}".format(len(sftp_file_list), sftp_dir, sftp_file_string))
            for filename in sftp_file_list:
                if fnmatch.fnmatch(filename, sftp_file_string):
                    print(filename)
                    print("...matched")
                    if filename not in s3_files or overwrite_s3_files:
                        if sftp_connector._is_remote_directory(os.path.join(sftp_dir, filename)):
                            # recursively iterate through this directory
                            if include_subdirs:
                                print(f"...{filename} is a directory, will recurse through files")
                                self._sync_sftp_files_to_s3(sftp_conn=sftp_conn, 
                                                      sftp_dir=os.path.join(sftp_dir, filename),
                                                      sftp_file_string='*',
                                                      s3_conn=s3_conn,
                                                      s3_dir=os.path.join(s3_dir, filename) + '/',
                                                      #local_dir=local_dir,
                                                      #temp_file=self.temp_file,
                                                      delete_temp_file=False,
                                                      overwrite_s3_files=overwrite_s3_files,
                                                      include_subdirs=include_subdirs)
                            else:
                                print(f'Skipping {filename} since it is a directory')
                        else:
                            self._copy_file_from_sftp_to_s3(
                                sftp_conn=sftp_conn,
                                sftp_dir=sftp_dir,
                                sftp_filename=filename,
                                s3_conn=s3_conn,
                                s3_dir=s3_dir,
                                s3_filename=filename,
                                #temp_local_dir=local_dir,
                                #temp_local_filename=temp_file,
                                overwrite_s3_file=overwrite_s3_files,
                                overwrite_local_file=True,
                                delete_local_file=False)
                    else:
                        print("...already have a copy on S3")
            # clean up temp file if needed
            if delete_temp_file:
                if os.path.exists(local_temp_file):
                    print(f'Deleting temp local file {local_temp_file} now that S3 sync is complete')
                    os.remove(local_temp_file)

    # TODO: Unify these two functions into a more generalized ds.copy() function that can copy any set of files 
    # from one source to another (so it could take both SFTP->S3 and S3->SFTP
    # Also then we can make the default temporary directory the location inside the _DataStream folder
    def _copy_file_from_sftp_to_s3(self, sftp_conn: str, #SFTP_Connector, # Now pass in the name of the connector
                                  sftp_dir: str, 
                                  sftp_filename: str, 
                                  s3_conn: str, #S3_Connector, # Now pass in the name of the connector
                                  s3_dir: str, 
                                  s3_filename: Optional[str] = None, 
                                  #temp_local_dir: str = '/tmp',
                                  #temp_local_filename: Optional[str] = None, 
                                  overwrite_s3_file: bool = False,
                                  overwrite_local_file: bool = False, 
                                  delete_local_file: bool = False) -> None:
        
        # Get S3 and SFTP connectors
        if sftp_conn in self.connectors:
            sftp_connector = self.connectors[sftp_conn]
        else:
            print("Do not have connector information for the given SFTP connector '{}'".format(sftp_conn))
            return None
        if s3_conn in self.connectors:
            s3_connector = self.connectors[s3_conn]
        else:
            print("Do not have connector information for the given S3 connector '{}'".format(s3_conn))
            return None
        
        # TODO: Confirm with Lara if this captures similar logic as before
        local_temp_file = self.DataStream.temp_file
        if local_temp_file is None:
            base, ext = os.path.splitext(sftp_filename)
            local_temp_filepath = tempfile.NamedTemporaryFile(dir=self.base_folder, suffix=ext).name
            #temp_local_filename = tempfile.NamedTemporaryFile(dir=temp_local_dir, suffix=ext).name
        else:
            local_temp_filepath = local_temp_file #os.path.join(temp_local_dir, temp_local_filename)
        temp_local_dir, temp_local_filename = os.path.split(local_temp_file)
        sftp_filepath = os.path.join(sftp_dir, sftp_filename)
        print(f'Downloading SFTP file {sftp_filepath} temporarily to local file: {local_temp_filepath}')
        sftp_connector.read(sftp_dir, type='download', sftp_file_string=sftp_filename, local_dir=temp_local_dir,
                       local_filename=temp_local_filename, overwrite=overwrite_local_file)
        if s3_filename is None:
            s3_filename = sftp_filename
        s3_filepath = os.path.join(s3_dir, s3_filename)
        print(f'Pushing to S3 at {s3_filepath}')
        try:
            s3_connector.write(None, s3_filepath, local_filename=local_temp_filepath, overwrite=overwrite_s3_file)
        except:
            raise
        finally:
            if delete_local_file:
                if os.path.exists(local_temp_filepath):
                    print(f'Deleting local temp file {local_temp_filepath}')
                    os.remove(local_temp_filepath)
                    
    def run(self):
        super().run()
        from_connector_label = self.sync_params['from']['connector']
        from_path = self.sync_params['from']['path']
        from_filestring = self.sync_params['from']['files']
        to_connector_label = self.sync_params['to']['connector']
        to_path = self.sync_params['to']['path']
        include_subdirs=self.sync_params['from'].get('include_subdirs', False)
        overwrite_s3_files = self.sync_params['to'].get('overwrite', False)
        
        print("\nSyncing files:", self.sync_params)
        self._sync_sftp_files_to_s3(
            sftp_conn=from_connector_label,
            sftp_dir=from_path, 
            sftp_file_string=from_filestring,
            s3_conn=to_connector_label,
            s3_dir=to_path,
            include_subdirs=include_subdirs,
            delete_temp_file=True,
            overwrite_s3_files=overwrite_s3_files
        )
        
############################################################
### Load files into the FeatureSpace ###
class Load_Sync(Sync):
    required_params = ['featureset', 'files'] # This Sync will fail if either of these params are missing
    
    def __init__(self, DataStream=None, type=None, **kwargs):
        Sync.__init__(self, DataStream=DataStream, type=type, required=self.required_params, **kwargs)
        
    def run(self, **kwargs):
        super().run()
        print("\nLoading files into the FeatureSpace with params:", self.sync_params)
        
        # Use any run-specific parameters first, then the sync's pre-defined parameters otherwise
        run_params = {**self.sync_params, **kwargs}

        if self.DataStream.FeatureSpace is not None:
            print("...loading files into FeatureSpace with parameters:", run_params)
            self.DataStream.FeatureSpace.loadFiles(**run_params)


############################################################
### Export data from the FeatureSpace to a file ###
class Export_Sync(Sync):
    required_params = ['featureset', 'variant', 'to']  # This Sync will fail if any of these params are missing
    # note: 'to' will be a dict of params containing connector, path, filename, file_type, and output_kwargs to pass
    #  to the outputting function if needed (e.g. for pandas: index=False, delimiter='|', etc.)
    optional_params = ['check_for_archived_file', 'archive_file']
    template_fields = ['to', 'archive_file']

    def __init__(self, DataStream=None, type=None, template_dict=None, template_py_file=None, **kwargs):
        Sync.__init__(self, DataStream=DataStream, type=type, required=self.required_params,
                      template_fields=self.template_fields, template_dict=template_dict,
                      template_py_file=template_py_file, **kwargs)

    def run(self, **kwargs):
        super().run()
        print("\nExporting data from FeatureSpace to remote file with params:", self.sync_params)

        # make 'to' a list of dicts if it's not already
        if isinstance(self.sync_params['to'], dict):
            self.sync_params['to'] = [self.sync_params['to']]

        check_for_archived = self.sync_params.get('check_for_archived_file', False)
        # archive_file will be a dict containing: connector, path, filename
        archive_file = self.sync_params.get('archive_file')
        if check_for_archived:
            assert archive_file is not None, \
                "Must specify 'archive_file' details in order to use check_for_archived_file option"
            assert 'connector' in archive_file, "Must specify connector for archive_file"
            assert 'path' in archive_file, "Must specify path for archive_file"
            assert 'filename' in archive_file, "Must specify filename for archive_file"

        # Use any run-specific parameters first, then the sync's pre-defined parameters otherwise
        run_params = {**self.sync_params, **kwargs}

        if self.DataStream.FeatureSpace is not None:
            print("...exporting data from FeatureSpace to remote file with parameters:", run_params)

            output_data = self.DataStream.FeatureSpace.Data(self.sync_params['featureset'],
                                                            variant=self.sync_params['variant'])

            if not isinstance(output_data, pd.DataFrame):
                raise NotImplementedError('Only support output of pandas dataframe')

            print("checking for archived:", check_for_archived)
            if check_for_archived:
                print('Checking for existing archived file')
                archive_connector_label = archive_file['connector']
                archive_path = archive_file['path']
                archive_filename = archive_file['filename']
                if archive_connector_label in self.connectors:
                    archive_conn = self.connectors[archive_connector_label]
                    # TODO: update read functionality for s3
                    assert archive_conn.type in ['sftp'], \
                        f'Only support checking for archived files on SFTP or S3, not {archive_conn.type}'
                else:
                    print("Do not have connector information for the given archive_file connector label '{}'".format(
                        archive_connector_label))
                    return None
                if archive_conn.read(archive_path, type='exists', sftp_file_string=archive_filename):
                    print('Archived file exists, will not output')
                    return None

            for output in self.sync_params['to']:
                to_connector_label = output['connector']
                to_path = output['path']
                to_filename = output['filename']
                to_file_type = output['file_type']
                to_overwrite = output.get('overwrite', False)
                to_output_kwargs = output.get('output_kwargs', {})
                if to_connector_label in self.connectors:
                    connector = self.connectors[to_connector_label]
                    assert connector.type in ['sftp', 's3'], f"Only support output to SFTP or S3, not {connector.type}"
                else:
                    print("Do not have connector information for the given to connector label '{}'".format(
                        to_connector_label))
                    return None
                output_filename = os.path.join(to_path, to_filename)

                if to_file_type.lower() == 'csv':
                    output_data_for_file = output_data.to_csv(**to_output_kwargs)
                elif to_file_type.lower() == 'excel':
                    output_data_for_file = output_data.to_excel(**to_output_kwargs)
                else:
                    raise NotImplementedError('Only support output file types of csv & excel')

                connector.write(output_data_for_file, output_filename, overwrite=to_overwrite,
                                suppress_overwrite_error=True)
                
############################################################
### Export data from the FeatureSpace to a file ###
class Archive_Sync(Sync):
    required_params = ['to']  # This Sync will fail if any of these params are missing
    # note: 'to' will be a dict of params containing connector and path where the featureset files should be backed up
    template_fields = ['to', 'archive_file']

    def __init__(self, DataStream=None, type=None, **kwargs):
        Sync.__init__(self, DataStream=DataStream, type=type, required=self.required_params,
                      **kwargs)

    # Either use featureset param or from param containing path and/or files
    def run(self, **kwargs):
        super().run()

        # make 'to' a list of dicts if it's not already
        if isinstance(self.sync_params['to'], dict):
            self.sync_params['to'] = [self.sync_params['to']]
            
        # Support for either featureset or a set of files in the 'from' parameter
        featureset = self.sync_params.get('featureset', None)
        from_params = self.sync_params.get('from', None)
        
        # Allow multiple archive locations
        for to_params in self.sync_params['to']:
            
            s3_connector = to_params.get('connector', None)
            archive_folder = to_params.get('path', None)

            assert s3_connector is not None and archive_folder is not None, \
                'Must provide the connector and path in the "to" parameters for this archive sync'

            # Call the native archive() command for the DataStream
            if featureset is not None:
                # Either archive a featureset
                self.DataStream.archive(featureset, s3_connector, archive_folder, **kwargs)
            else:
                # Or archive a set of files (default is all files in the current path)
                from_path = from_params.get('path', '.')
                from_files = from_params.get('files', '*')
                print("Archiving using path={} and files={}".format(from_path, from_files))
                if from_files is not None:
                    self.DataStream.archive(None, s3_connector, archive_folder, path=from_path, files=from_files)

############################################################
### Push data from the FeatureSpace to a database table ###
class Database_Sync(Sync):
    required_params = []  # This Sync will fail if any of these params are missing
    # note: 'to' will be a dict of params containing connector, path, filename, file_type, and output_kwargs to pass
    #  to the outputting function if needed (e.g. for pandas: index=False, delimiter='|', etc.)
    # If 'query' is passed in --> this sync runs a given query
    # If 'featureset', 'variant' are passed in --> this sync copies the given featureset to the given database table
    optional_params = ['featureset', 'variant', 'to', 'from', 'query', 
                       'data_types', 'num_rows', 'start_row', 'max_str_len', 'chunk_size']
    template_fields = ['to', 'archive_file', 'query']

    def __init__(self, DataStream=None, type=None, template_dict=None, template_py_file=None, **kwargs):
        Sync.__init__(self, DataStream=DataStream, type=type, required=self.required_params,
                      template_fields=self.template_fields, template_dict=template_dict,
                      template_py_file=template_py_file, **kwargs)
    
    def insertmany_df_into_db(self, connector, output_df, db_table, 
                              data_types=None,
                              date_format='%m/%d/%Y', 
                              max_str_len=650,
                              max_num_rows_per_query=10000):
        import datetime
        import numpy as np

        #cols_list = "'"+"','".join(list(output_df.columns))+"'"
        cols_list = ",".join([col if ' ' not in col else f"[{col}]" for col in list(output_df.columns)])
        print("Going to insert {} rows".format(output_df.shape[0]))
        print("...starting:", datetime.datetime.now())
        values_superlist = []
        values_string = ','.join(['?' for i in range(output_df.shape[1])])
        print(datetime.datetime.now())
        query = f"INSERT INTO {db_table} ({cols_list}) VALUES ({values_string})"
        print(query)
        total_num_rows = output_df.shape[0]
        row_num = 0
        while row_num < total_num_rows:
            # Get a chunk of rows
            output_df_chunk = output_df.reset_index(drop=True).loc[row_num:row_num+max_num_rows_per_query-1, :].copy()
            print(datetime.datetime.now())
            print("Inserting chunk {} starting at row {}".format(output_df_chunk.shape, row_num))
            # Convert date vars to datetime format
            for var in output_df_chunk.columns:
                var_data_type = data_types.get(var, None) if data_types is not None else None
                print(f"...{var}={var_data_type}")
                if var_data_type=='date':
                    output_df_chunk[var] = output_df_chunk[var].apply(lambda x: datetime.datetime.strptime(x, date_format) if x!='' else None)
                elif var_data_type=='float':
                    #output_df_chunk[var] = output_df_chunk[var].apply(lambda x: '{}'.format(x, '.3f'))
                    output_df_chunk[var] = pd.to_numeric(output_df_chunk[var].apply(lambda x: x if x!='' else 0.0)).astype(float).apply(lambda x: '{}'.format(x, '.3f'))
                elif var_data_type=='int':
                    output_df_chunk[var] = pd.to_numeric(output_df_chunk[var].apply(lambda x: x if x!='' else 0)).astype(int).astype(str)
                elif isinstance(var_data_type, list) and var_data_type[0]=='str':
                    # Then get the length of the string
                    this_var_str_len = var_data_type[1]
                    output_df_chunk[var] = output_df_chunk[var].apply(lambda x: str(x).replace("'", "''").replace(" & "," &amp; ")[:this_var_str_len])
                else:
                    # string
                    output_df_chunk[var] = output_df_chunk[var].apply(lambda x: str(x).replace("'", "''").replace(" & "," &amp; ")[:max_str_len])
            row_num += max_num_rows_per_query

            # Add each row as a tuple of values to a big list
            #print("Converted chunk of {} rows".format(output_df_chunk.shape[0]))
            values_superlist = []
            for index, row in output_df_chunk.iterrows():
                values_list = tuple(list(row.values))
                #values_list = get_row_list(row, float_vars=float_vars, int_vars=int_vars, date_vars=date_vars)

                values_superlist.append(values_list)

            # Try executing the INSERT query as a chunk
            params = list(tuple(row) for row in values_superlist)
            connector.write(params, query)

        print("...finished:", datetime.datetime.now())
                
    def run(self, **kwargs):
        super().run()
        print("\Running Database sync with params:", self.sync_params)

        # Use any run-specific parameters first, then the sync's pre-defined parameters otherwise
        run_params = {**self.sync_params, **kwargs}
            
        # Push the given featureset to the 'to' database table, if provided these parameters
        have_featureset_to_push = False
        if 'featureset' in self.sync_params:
            if self.DataStream.FeatureSpace is not None:
                print(datetime.datetime.now())
                print("...pushing data from FeatureSpace to database with parameters:", run_params)

                output_data = self.DataStream.FeatureSpace.Data(self.sync_params['featureset'],
                                                                variant=self.sync_params['variant'])
                have_featureset_to_push = True
                print("...done.")
                print(datetime.datetime.now())

                # Optional parameters
                data_types = self.sync_params.get('data_types', {})
                num_rows_to_insert = self.sync_params.get('num_rows', None)
                start_row = self.sync_params.get('start_row', None)
                insert_params = {}
                if 'max_str_len' in self.sync_params:
                    insert_params['max_str_len'] = self.sync_params['max_str_len']
                if 'chunk_size' in self.sync_params:
                    insert_params['max_num_rows_per_query'] = self.sync_params['chunk_size']

                if not isinstance(output_data, pd.DataFrame):
                    raise NotImplementedError('Only support output of pandas dataframe')

        # Iterate through each 'to' set of parameters
        if 'to' in self.sync_params:
            # make 'to' a list of dicts if it's not already
            if isinstance(self.sync_params['to'], dict):
                to_params = [self.sync_params['to']]
            else:
                to_params = self.sync_params['to']
            
            for output in to_params:
                to_connector_label = output['connector']
                if to_connector_label in self.connectors:
                    connector = self.connectors[to_connector_label]
                    assert connector.type in ['postgres', 'sql'], f"Only support output to Postgres, Redshift or SQL, not {connector.type}"
                else:
                    print("Do not have connector information for the given 'to' connector label '{}'".format(
                        to_connector_label))
                    return None

                if 'table' in output:
                    # Then treat this as pushing the given featureset to this database table
                    to_database = output.get('database', None)
                    to_table = output['table']
                    if to_database is not None and to_table is not None:
                        to_database_table = f"{to_database}.{to_table}"
                    elif to_table is not None:
                        to_database_table = to_table
                    else:
                        print("Must provide either 'database' or 'table' in the 'to' parameters.")
                        raise
                    to_overwrite = output.get('overwrite', False)
        #                 to_output_kwargs = output.get('output_kwargs', {})

                    # Count the # of rows in this table
                    num_rows = connector.read(to_database_table, type='rows')
                    print(f"Table {to_database_table} has {num_rows} rows")
                    print(datetime.datetime.now())

                    # Query for the data to get all the columns
                    database_table_columns = connector.read(to_database_table, type='columns')              

                    # Make sure have data to push
                    if not have_featureset_to_push:
                        print("No featureset data was acquired to push to this database table...exiting.")
                        raise

                    # Pick the columns in common between the featureset and the DB table
                    sql_table_columns_in_output = [col for col in database_table_columns if col in output_data.columns]

                    # Re-sort and subset only the columns from the featureset to match those in the database
                    # Note: If there are more columns in the DB than in the featureset they will not be pushed here
                    output_data_colsreordered = output_data[sql_table_columns_in_output]

                    print("Database cols not in featureset", set(database_table_columns) - set(output_data_colsreordered.columns))
                    print("Featureset cols not in database", set(output_data_colsreordered.columns) - set(database_table_columns))
                    cols_list = ','.join(list(output_data_colsreordered.columns))

                    if to_overwrite:
                        # Only if specified by overwrite parameter, truncate the DB table before writing to it
                        print(f"Overwrite=True, so going to truncate the table {to_database_table} before writing to it")
                        connector.truncate(to_database_table)
                    print(datetime.datetime.now())

                    # Insert the featureset data in chunks
                    if num_rows_to_insert is None:
                        if start_row is None:
                            # Get all rows
                            output_data_to_insert = output_data_colsreordered
                        else:
                            # Use start_row
                            output_data_to_insert = output_data_colsreordered[start_row:]
                    else:
                        if start_row is None:
                            # Use num_rows_to_insert
                            output_data_to_insert = output_data_colsreordered[:num_rows_to_insert]
                        else:
                            # Use num_rows_to_insert and start_row
                            output_data_to_insert = output_data_colsreordered[start_row:start_row+num_rows_to_insert]                    
                    self.insertmany_df_into_db(connector, 
                                               output_data_to_insert,
                                               to_database_table,
                                               data_types=data_types,
                                               **insert_params)

                    # Count the # of rows in this table
                    num_rows = connector.read(to_database_table, type='rows')
                    print(f"Table {to_database_table} has {num_rows} rows")
                    print(datetime.datetime.now())

                elif 'query' in output:
                    # If 'query' provided, then run this query 
                    query_to_run = output['query']
                    
                    # Call the connector's write command to execute this query (assuming it's an INSERT/UPDATE)
                    connector.write(None, query_to_run)
                    #query_result_df = connector.read(to_database_table, type='columns')  
                    
        # Iterate through each 'from' set of parameters
        if 'from' in self.sync_params:
            # make 'to' a list of dicts if it's not already
            if isinstance(self.sync_params['from'], dict):
                from_params = [self.sync_params['from']]
            else:
                from_params = self.sync_params['from']
            
            # Iterate through each 'from'
            for from_param in from_params:
                from_connector_label = from_param['connector']
                if from_connector_label in self.connectors:
                    connector = self.connectors[from_connector_label]
                    assert connector.type in ['postgres', 'sql'], f"Only support input from Postgres, Redshift or SQL, not {connector.type}"
                else:
                    print("Do not have connector information for the given 'from' connector label '{}'".format(
                        from_connector_label))
                    return None
                
                # Run any SELECT queries
                if 'query' in from_param:
                    query = from_param['query']
                    print("Running query:", query)
                    
                    # Run the query
                    query_result_df = connector.read(query, type='select')
                    
                    # If output=true, then print the results to the log
                    if 'output' in from_param and from_param['output']:
                        print("Outputting result:")
                        print(query_result_df)
                          
                    
