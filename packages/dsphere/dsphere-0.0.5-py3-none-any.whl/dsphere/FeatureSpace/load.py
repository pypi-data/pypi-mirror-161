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



# Can now pass in any date-like string into start_date or end_date like '20200113' or '1/3/20'
# files = regex string or list of filenames or lambda function to choose which filenames in filepath to use
def loadFiles(self, featureset, path, files, source=None, 
                   append=True, start_date=None, end_date=None,
                   data_types=None, encoding='cp1252', delimiter=',', fillna=True,
                   only_latest=False,
                   exclude=None,
                   variant=None,
                   column_names=None,
                   column_widths=None,
                   date_format=None, # Pass a specific date format for parsing dates in the filenames, or None to use generic dateutil date parser
                   store_file_dates=False, # Send True only if you want to keep the file date as a column
                   **kwargs):

    import re
    import os
    from dateutil.parser import parse
    from datetime import datetime
    from os.path import isfile, join

    # Allowing reload=True to override append=True and force append=False
    if 'reload' in kwargs:
        if kwargs['reload']:
            append = False

    files_already_loaded = []
    if append and not only_latest and self.exists(featureset):
        output_featureset = self.Features(featureset)
        if output_featureset is not None:
            if hasattr(output_featureset, 'source_files'):
                files_already_loaded = output_featureset.source_files.get(variant, [])
        print("Files already loaded:", files_already_loaded)

    # Also exclude any files passed in
    if exclude is not None:
        files_already_loaded += ([exclude] if isinstance(exclude, str) else exclude)
        print("Added files on exclude list:", exclude)

    #filenames = files
    exclude = files_already_loaded
    filepath = path

    # Otherwise subset from all the files in the given filepath
    if source is not None:
        # Get the list of files from an external source if provided one
        if source not in self.connectors:
            print("ERROR: Cannot find a connector for source '{}' to use to get files during load()".format(source))
            return None

        list_of_files = self.connectors[source].read(filepath, type='list')
        print("Loading some or all of the {} files in '{}' in the external source '{}'".format(len(list_of_files), 
                                                                                               filepath, source))
    else:
        # Otherwise get the list locally
        from os import listdir
        list_of_files = [f for f in listdir(filepath) if isfile(join(filepath, f))]
        print("Loading some or all of the {} files in '{}'".format(len(list_of_files), filepath))

    # Subset the list of files to import
    file_dates = None
    if isinstance(files, str):
        filenames_list = [files]
    elif isinstance(files, list):
        # Use the given list of files
        #data_files = [join(filepath, f) for f in list_of_files if f in files]

        # Order the files alphabetically using just the filename
        #data_file_list = sorted(data_files)
        filenames_list = files
    else:
        # Assume 'files' is a lambda function to use as the filter/sort the files (if not a str or list)
        #data_file_list = [join(filepath, f) for f in files(list_of_files)]
        filenames_list = files(list_of_files)

    # Iterate through all the files/file regex strings to parse
    file_tuples = []
    for filenames in filenames_list:
            #     def choose_files_to_load(all_files, filenames, start_date=None, end_date=None, exclude=None, filepath=None, 
#                              #sort_by=None, 
#                              only_latest=False):

        print("...matching on file string:", filenames)

        # Convert start_date and end_date into datetime
        try:
            start_date_val = parse(start_date)
        except:
            self.out("...cannot parse start_date={} into a date, so treating start_date as null".format(start_date))
            start_date_val = None
        try:
            end_date_val = parse(end_date)
        except:
            self.out("...cannot parse end_date={} into a date, so treating end_date as null".format(start_date))
            end_date_val = None

        # Choose files after the given start_date, using the date part within the given regex string
        # If only_latest=True then it will return only the last file
        all_files = list_of_files
        for file in all_files:
            self.out("...comparing file '{}' to regex '{}'".format(file, filenames))
            is_match = re.match(r'{}'.format(filenames), file)
            self.out("...is_match=", is_match)
            if is_match is not None:
                # If there was a match
                self.out("file:", file)
                self.out("filepath:", filepath)
                self.out("is_match:", is_match)
                full_filepath = os.path.join(filepath, file)
                self.out("filepath:", full_filepath)
                # Exclude files on the given list (if provided)
                if exclude is None or full_filepath not in exclude:
                    if len(is_match.groups())==0:
                        # If there were no () in the file string, then we just match the entire string and sort on that
                        file_tuples.append((file, file))
                    else:
                        # If there is a date wrapped in () in the file string, use the date to sort the files
                        date_part = is_match.group(1)
                        self.out("...date={}".format(date_part))

                        # Parse the date part
                        have_date = False
                        try:
                            if date_format is None:
                                # Use dateutil's generic date parser
                                date_to_compare = parse(date_part)
                            else:
                                # Use the given date format to parse the filename
                                date_to_compare = datetime.strptime(date_part, date_format)
                            have_date = True
                        except:
                            # If we cannot parse the date, treat it as the minimum (so it's placed first)
                            date_to_compare = datetime.min
                            have_date = False

                        # If there is a start_date, then make sure each file is after that
                        date_is_after = True
                        if start_date_val is not None and date_to_compare is not None:    
                            date_is_after = (date_to_compare >= start_date_val)
                            self.out("...after start date:", date_is_after)

                        # If there is an end_date, make sure the files are before that
                        date_is_before = True
                        if end_date_val is not None and date_to_compare is not None:
                            date_is_before = (date_to_compare <= end_date_val)
                            self.out("...before end date:", date_is_before)

                        # If this date is after the start date (or none was given)
                        if date_is_after and date_is_before:
                            file_tuples.append((file, date_to_compare if have_date else None))
                else:
                    self.out("...skipping this file, already loaded.")

        self.out("...found {} files that match:".format(len(file_tuples)), file_tuples)

    # Sort all the files matched by the full version of their date YYYYMMDD
    #sorted_files = sorted(file_tuples, key=lambda x: x[1])
    # Clever algorithm to handle None and treat them as first in the list: 
    # https://stackoverflow.com/questions/18411560/sort-list-while-pushing-none-values-to-the-end
    sorted_files = sorted(file_tuples, key=lambda x: (x[1] is not None, x[1])) 
    self.out("...sorted:", sorted_files)


    # Once sorted, then choose just the filenames
    # If only_latest is True then just pick the last one in this list
    if only_latest:
        matching_files = [sorted_files[-1][0]]
        print("Choosing only the latest file: {}".format(matching_files))
        file_dates = [sorted_files[-1][1]]
    else:
        matching_files = [file_tuple[0] for file_tuple in sorted_files]
        file_dates = [file_tuple[1] for file_tuple in sorted_files]

    # Sort alphabetically within this list
    #return matching_files 

    # Use the given 'files' string as a regex filter
    #data_files = [join(filepath, f) for f in list_of_files if re.match(r'{}'.format(files), f)]

    # Order the files alphabetically using just the filename
    #data_file_list = sorted(data_files)
    data_file_list = matching_files

    if only_latest:
        print("Found the latest matching file to load: {}".format(files)) 
    elif append:
        print("Found {} files that match and are not already loaded: {}".format(len(data_file_list), files))            
    else:
        print("Found {} files that match: {}".format(len(data_file_list), files))


    self.load(featureset,
                filepath=path,
                source=source,
                append=append,
                files=data_file_list,
                encoding=encoding,
                delimiter=delimiter,
                fillna=fillna,
                data_types=data_types,
                #quotechar=quotechar,
                variant=variant,
                column_names=column_names,
                column_widths=column_widths,
                file_dates=file_dates if store_file_dates else None,
             **kwargs) 

# Options:
# 1) Send in filepath --> Local file
# 2) Send in filepath + files --> Set of local files (where 'files' can be: 
#   (a) a regex defining which files to include from the 'filepath' folder (sorted alphabetically), 
#   (b) a list of filenames to choose from the 'filepath' folder, or 
#   (c) a lambda function defining the filter to apply to all the filenames inside the 'filepath' folder to output the ordered set of files to load
# 3) Send in database+table --> From DB connection
# 4) Send in query --> Pull results of that SELECT query
# 5) Send in SFTP site (and optionally filenames) --> Aggregate together all files there that should be used to order the file loads 
# 6) [added 3/13/20] append=True --> This will append rows found in the given filepath/files onto the data in the existing FeatureSet with the label provided, rather than creating a new FeatureSet if append=False.
# Note: Most of load() can be done with engine='pandas' or engine='dask', except 'dask' with a list of files, which we still need to implement.
# Note: Currently only the data_types provided will be "forced" on all the files.  If a type inferred in file 1 is different from the type inferred in file 2, this function will intentionally throw an error to reveal to the user so they can be aware and send in forced typing through data_types, rather than all data types being coincidentally determined by the first file 
# Pass in sheet='abc' if loading an Excel file and want to determine the sheet to load within it; otherwise will load all sheets by default and concat them together.  (sheet=0 will load the first sheet too, if you don't know the name)
# column_widths=list of col widths or list of tuples (each with first,last position of each fixed-width field) if the file is has fixed-width (not delimited) columns, to be parsed using pandas.read_fwf(), otherwise None to use pd.read_csv()
# column_names=list of column names to use instead of parsing the column names from the first row, otherwise None to use the first row by default in pd.read_csv() or pd.read_fwf()
# .gz or .zip files okay for read_csv, not for read_fwf or read_excel
# upsert_vars: Provide list or string (one var) to dictate when to overwrite rows in previously-loaded dataframe with rows in the newly-loaded one when they overlap on these upsert_on vars
# Note: If upsert_vars is not None, append append will be treated as True even if you pass append=False
# and as a consequence, upsert may change the order of rows (i.e. a person in row 1000 moves to row 2000 after upsert)
def load(self, label, append=False,
         upsert_vars=None, 
         filepath=None, files=None, delimiter=',', encoding=None,
         database=None, table=None, where=None, limit=None, 
         query=None, chunked=False, 
         ftp_path=None, # /blah/blah/file1.csv or /blah/blah/file*.csv 
         order='filename', # 'filename'=order the files (if >1) by filename, 'date'=order by the date on each file
         index_cols=None, feature_cols=None, label_cols=None, 
         source=None, # None=local, or can pull from an external source loaded in the FeatureSpace
         local_file=None, # Only if you want to keep a copy of the external file locally, provide the name here
         column_names=None, # Pass in if you want to determine the column names (not read from the first line of the file)
         # Note on 1/2/21: column_names only works for pandas.read_csv, not for Excel or dask yet
         column_widths=None, # Pass in a list of fixed column widths or a list of tuples (each with first/last position of the fixed columns) if the columns are fixed-width, not delimited
         file_dates=None, # Pass in a list of file dates corresponding to each file in 'files', if they should be stored
         decryption_key=None,
         lineterminator=None,
         **kwargs):
    from os import listdir
    from os.path import isfile, join
    import re
    from pandas.errors import EmptyDataError # Changed in pandas 1.1.5
    #from pandas.io.common import EmptyDataError
    fillna = kwargs.get('fillna', False)
    _DEFAULT_TEMP_FILE = os.path.join(self._getTempDirectory(),
                                      '__TEMP_IMPORT_FILE_{}__'.format(label))

    # Reload the FeatureSpace metadata first to make sure we reload the latest files
    self.out("Reloading the FeatureSpace...")
    self._loadFeatureSetMetadata()

    # Collect col types if defined by the function call
    # Note: For now we overwrite any types already saved for this FeatureSet, treating load() as a new dataset
    data_types = kwargs.get('data_types', None)
    print("Have data_types={}".format(data_types))

    if isinstance(upsert_vars, str):
        upsert_vars = [upsert_vars]

    def set_equals(list1, list2):
        if len(list1) != len(list2):
            print("Different lengths")
            return False
        set1 = set(list1) if list1 is not None else set()
        set2 = set(list2) if list2 is not None else set()
        set1_not_set2 = set1 - set2
        set2_not_set1 = set2 - set1
        if len(set1_not_set2)>0:
            print("In List 1 but not List 2:", set1_not_set2)
            return False
        if len(set2_not_set1)>0:
            print("In List 2 but not List 1:", set2_not_set1)
            return False
        return True

    # If a filepath is given, look for the list of files to read-in
    if filepath is not None:
        engine = kwargs.get('engine', 'pandas')
        header = kwargs.get('header', 0)
        if files is None:
            # If 'files' not provided, use the 'filepath' as the single file to load
            data_file_list = [filepath]

        elif isinstance(files, list):
            # If files is a string, assume it's a regex to select which filenames to include

            # If provided a list, just use that and prepend the filepath for each filename in the list
            data_file_list = [join(filepath, f) for f in files]
            print("LOADING THE {} FILES PROVIDED".format(len(data_file_list)))

        elif isinstance(files, str):
            data_file_list = [join(filepath, files)]
            print("LOADING THE 1 FILE PROVIDED:", data_file_list)
        else:
            print("ERROR: Must provide a string filename or list of filenames in 'files' parameter")
            raise

        ### Read-in the list of files
        columns_list = None
        local_file_created_flag = False
        num_files_so_far = 0
        num_files_to_load = len(data_file_list)
        for data_file in data_file_list:
            print("\nLoading into FeatureSet '{}' using engine '{}' from file at path: {} with kwargs: {}".format(label, engine, data_file, kwargs))

            # Figure out whether there's already a dataframe here
            #curr_df = self.Data(label, **kwargs)
            #curr_df_has_data = curr_df is not None and curr_df.shape[0]>0

            # Store the file extension to use below
            data_filepath_split = data_file.split('.')
            file_extension = data_filepath_split[-1] if len(data_filepath_split)>0 else ''
            print("...file extension:", file_extension)

            # Check whether to get each file locally or externally
            #data_full_path = join(filepath, data_file)
            if source is not None:
                if source not in self.connectors:
                    print("ERROR: Cannot find a connector for source '{}' to use to get files during load()".format(source))
                    return None

                # Set up connection to that external source
                self.connectors[source].connect()

                # Download the file to a temporary local file
                if local_file is not None:
                    local_file_copy = local_file
                else:
                    # Store in a temp file with the same extension as the given data_file
                    local_file_copy = _DEFAULT_TEMP_FILE + ('.'+file_extension if file_extension!='' else '')
                print("...storing file locally as", local_file_copy)

                # Use the connector to download the file locally
                self.connectors[source].read(data_file, type='download', to_file=local_file_copy)
                print("...done")
                local_filepath = local_file_copy

                # Set a flag that a local file was created, so we delete it below
                local_file_created_flag = True
            else:
                # Just use the filepath 
                local_filepath = data_file

            # Check for .gz or .zip files, unzip them in the TEMP file if possible
            compression = 'infer'
            if len(data_file)>3:
                if file_extension in ['gz', 'GZ']:
                    compression = 'gzip'
                elif file_extension in ['zip', 'ZIP']:
                    compression = 'zip'
                print("Compression:", compression)

            # Default quotechar is ", otherwise takes optional value passed in
            quotechar = kwargs.get('quotechar', '"')
            import csv
            if quotechar is None:
                # Complying with https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
                # Must not enable quoting if quotechar is None
                quoting = csv.QUOTE_NONE
            else:
                quoting = kwargs.get('quoting', csv.QUOTE_MINIMAL)
                if 'quoting' in kwargs:
                    kwargs.pop('quoting')
            print("Quotechar:", quotechar, ", quoting:", quoting)

            #quotechar = '"'
            #if 'quotechar' in kwargs:
            #    kwargs_quotechar = kwargs.get('quotechar')
            #    if kwargs_quotechar is not None:
            #        quotechar = kwargs_quotechar
            if 'quotechar' in kwargs:
                kwargs.pop('quotechar')

            # Default escapechar is None, but you can pass in an optional value to escape
            # Complying with this, where default is escapechar=None
            # https://docs.python.org/3/library/csv.html
            escapechar = kwargs.get('escapechar', None)

            if os.path.exists(local_filepath):                 
                print("...reading from", local_filepath)

                # If there's a decryption key, use it here
                decrypted_file = None
                if decryption_key is not None:
                    decryption_key_filepath = None
                    if isinstance(decryption_key, str):
                        # By default the passphrase is blank
                        decryption_key_filepath = decryption_key
                        decryption_key_passphrase = ''
                    elif isinstance(decryption_key, dict):
                        # Look for 'path' and 'passphrase'
                        decryption_key_filepath = decryption_key.get('path', None)
                        decryption_key_passphrase = decryption_key.get('passphrase', '')

                    if decryption_key_filepath is not None:
                        # Check that the key file exists
                        if not os.path.exists(decryption_key_filepath) or not os.path.isfile(decryption_key_filepath):
                            self.out("ERROR: Cannot find a decryption key at the given path: {}".format(decryption_key_filepath), type='error')
                            raise

                        # Use the given (local) decryption key to decrypt the local TEMP file
                        key,_ = pgpy.PGPKey.from_file(decryption_key_filepath)
                        emsg = pgpy.PGPMessage.from_file(local_filepath)
                        with key.unlock(passphrase=decryption_key_passphrase):
                            decrypted_bytesarray = (key.decrypt(emsg).message)

                            # Convert the decrypted bytes array to a file-like buffer stored only in RAM
                            decrypted_file = io.BytesIO(decrypted_bytesarray)
                            print("...decrypted file using key at '{}', now have file of type {}".format(decryption_key_filepath, type(decrypted_file)))
                            # Note this decrypted file-like buffer will be used instead of the filepath below


                if engine=='pandas':
                    # Note change on 11/11/19: dtype=str forces the initial read-in to use all strings,
                    # which avoids problem of int values casted as floats by pandas read_csv (when there are nulls)
                    # Then the call to unifyDataTypes below will try to infer the true data types of each col 
                    try:
                        # Infer if the file type is Excel from the file extension (.xlsx, .xls, .XLSX, .XLS)
                        #data_filepath_split = data_file.split('.')
                        #file_extension = data_filepath_split[-1] if len(data_filepath_split)>0 else ''
                        #print("...file extension:", file_extension)
                        if file_extension in ['xls', 'XLS', 'xlsx', 'XLSX']:
                            # Grab the sheet specified, or the first tab if none specified
                            excel_sheet = kwargs.get('sheet', None)

                            if excel_sheet is None:
                                # Get the full list of sheets in the excel file
                                print("...opening ExcelFile:", local_filepath)
                                excel_file = pd.ExcelFile(local_filepath, engine='openpyxl')
                                excel_sheets = excel_file.sheet_names
                                print("...loading all sheets in the Excel file:", excel_sheets)
                            else:
                                # Allow for 'sheet' to be a list of sheets to grab at once
                                excel_sheets = excel_sheet if isinstance(excel_sheet, list) else [excel_sheet]

                            print("Loading Excel file {}, sheet={}".format(local_filepath, excel_sheets))
                            df = None
                            for one_excel_sheet in excel_sheets:
                                try:
                                    print("...one_excel_sheet = {} ({})".format(one_excel_sheet, one_excel_sheet is None))
                                    all_sheets_df = pd.read_excel(decrypted_file or local_filepath, # Use the decrypted file if available
                                                       sheet_name=one_excel_sheet,
                                                       keep_default_na=False if fillna else True,
                                                       parse_dates=True,
                                                                 engine='openpyxl')

                                    # This might return a single dataframe or a dict of each sheet->dataframe
                                    if isinstance(all_sheets_df, dict):
                                        print("Read in multi-tab Excel sheet with keys:", all_sheets_df.keys())
                                        sheet_df = None
                                        for sheet_name, one_sheet_df in all_sheets_df.items():
                                            one_sheet_df['source_excel_sheet'] = sheet_name
                                            if sheet_df is None:
                                                print("...first sheet", one_sheet_df.shape)
                                                sheet_df = one_sheet_df
                                            else:
                                                print("...later sheet", one_sheet_df.shape)
                                                sheet_df = pd.concat([sheet_df, one_sheet_df], 
                                                                     axis=0, sort=False).reset_index(drop=True)
                                                print("...new sheet_df", sheet_df.shape)
                                    else:
                                        sheet_df = all_sheets_df
                                        print("Read in single-tab Excel sheet with tab:", one_excel_sheet)
                                        sheet_df['source_excel_sheet'] = one_excel_sheet
                                except Exception:
                                    self.out("WARNING: Could not find sheet '{}' in the Excel file '{}'".format(one_excel_sheet, 
                                                                                                                local_filepath),
                                             type='warning')
                                    sheet_df = None

                                # Concat all the sheets together vertically if >1
                                if df is None:
                                    df = sheet_df
                                    print("Starting sheet_df type={}, shape={}".format(type(sheet_df), sheet_df.shape))
                                else:
                                    df = pd.concat([df, sheet_df], axis=0, sort=False).reset_index(drop=True)
                                    print("Appending sheet_df type={}, shape={} into df type={}, shape={}".format(type(sheet_df), sheet_df.shape, type(df), df.shape))

                        # Allow fixed-width files to be loaded
                        elif column_widths is not None:
                            # Check if column_widths is a list of tuples (defining start/end chars) or list of ints (defining widths)
                            has_positions_or_widths = 'positions' if isinstance(column_widths[0], list) or isinstance(column_widths[0], tuple) else 'widths'
                            print("Loading fixed-width file with encoding={}, fillna={}, {}={}, names={}".format(encoding, fillna, has_positions_or_widths, column_widths, column_names))
                            df = pd.read_fwf(decrypted_file or local_filepath, # Use the decrypted file if available
                                             encoding=encoding, 
                                             #error_bad_lines=False, #deprecated since pandas 1.3.0
                                             on_bad_lines='skip',
                                             #warn_bad_lines=True, #deprecated since pandas 1.3.0
                                             skip_blank_lines=True,
                                             keep_default_na=False if fillna else True,
                                             parse_dates=True,
                                             compression=compression, # To handle .gz or .zip files
                                             infer_datetime_format=True,
                                             header=None if column_names is not None else 'infer', 
                                                 # default is to read the col headers in line 1
                                             names=column_names,
                                             colspecs=column_widths if has_positions_or_widths=='positions' else 'infer',
                                             widths=column_widths if has_positions_or_widths=='widths' else None
                                            )
                            print("...loaded dataframe:", df.shape)                                

                        else:
                            print("Loading CSV with quotechar={}, quoting={}, delimiter={}, encoding={}, fillna={}, escapechar={}, names={}".format(quotechar, quoting, delimiter, encoding, fillna, escapechar, column_names))
                            df = pd.read_csv(decrypted_file or local_filepath, # Use the decrypted file if available
                                         encoding=encoding, 
                                         delimiter=delimiter,
                                         #error_bad_lines=False, #deprecated since pandas 1.3.0
                                         on_bad_lines='skip',
                                         #warn_bad_lines=True, #deprecated since pandas 1.3.0
                                         skip_blank_lines=True,
                                         keep_default_na=False if fillna else True,
                                         lineterminator=lineterminator,
                                         parse_dates=True,
                                         infer_datetime_format=True,
                                         compression=compression, # To handle .gz or .zip files
                                         header=0 if column_names is not None else 'infer', 
                                             # default is to read the col headers in line 1
                                         names=column_names,
                                         dtype=str, # Start out loading as strings, convert to other data types elsewhere
                                         quotechar=quotechar,
                                         escapechar=escapechar,
                                         quoting=quoting,
                                         engine='python' if lineterminator is None else 'c') # allow passing in other fields
                            print("...loaded dataframe:", df.shape)
                    except EmptyDataError:
                        print("Empty file found: {}...skipping this file".format(local_filepath))
                        df = None
                else:
                    #df = pd.read_csv(filepath, delimiter=delimiter)
                    df = dd.read_csv(decrypted_file or local_filepath, # Use the decrypted file if available 
                                     delimiter=delimiter,
                                     encoding=encoding, # todo: confirm encoding=None works fine
                                     assume_missing=False, 
                                     dtype=str)    

                # Only proceed if a file was actually loaded in
                if df is not None:
                    # Append a column that stores the name of the original file loaded in here
                    df['source_filename'] = data_file

                    # if file_dates are provided, pull the corresponding file date and store it as a column too
                    if file_dates is not None and isinstance(file_dates, list) and len(file_dates)>=num_files_so_far:
                        if file_dates[num_files_so_far] is not None:
                            print("STORING FILE DATE:", file_dates[num_files_so_far], type(file_dates[num_files_so_far]))
                            df['source_file_date'] = file_dates[num_files_so_far]
                        else:
                            # Store the None as the date
                            print("STORING NULL FILE DATE...")
                            # Commenting this out to prevent pyarrow errors, but the code below will concat source_file_date
                            #df['source_file_date'] = df.apply(lambda x: None, axis=1)

                        # Store this as a 'date' data type
                        data_types['source_file_date'] = 'date'                                

                    variant = kwargs.get('variant', self.default_variant)

                    # Append the data to the end (bottom) 
                    if (append or (num_files_so_far>0 and num_files_to_load>1)) and self.exists(label):
                        new_featureset = self.Features(label)
                        # Check the current dataframe for columns
                        curr_df = self.Data(label, **kwargs)
                        print("...after getting curr_df for '{}' with kwargs={}, have shape:".format(label, kwargs),
                              "None" if curr_df is None else curr_df.shape)
                        curr_df_has_data = curr_df is not None and curr_df.shape[0]>0
                    else:
                        curr_df_has_data = False

                    # Removing: Confirm the columns lists stay exactly the same
                    #if columns_list is None:
                    if not curr_df_has_data:
                        # If we're not appending and this is the first dataframe, or if appending to nothing there yet, 
                        # use the new dataframe's columns
                        columns_list = df.columns
                    else:
                        # If appending to an existing dataframe, then get the columns already there
                        columns_list = curr_df.columns

                    # Case (1) If there's no data saved yet or this is the first file of several or append=False...
                    if (not curr_df_has_data and append) or \
                        (num_files_so_far==0 and num_files_to_load>1 and not append):
                        # Create a new FeatureSet with no data in it
                        self.out("...creating blank dataframe for this featureset")
                        new_featureset = self.addData(label, None, datatype='dataframe', 
                                                      filetype='parquet',
                                                      **kwargs)

                        # Unify the new dataframe with types given
                        self.out("...unifying this dataframe with shape:", df.shape)
                        df_unified, unified_types = FeatureSet._unifyDataTypes(df, fillna=True, 
                                                                          debug=(self.output_mode=='debug' or (self.dsphere is not None and self.dsphere.output_mode=='debug')),
                                                                              forced_types=data_types)

                        # Also append this first one again to create part.0.parquet properly
                        print("...appending the dataframe to the blank child with a new schema")
                        # Using new_schema=True to force .append() to create a new schema file
                        new_featureset.append(df_unified, filetype='parquet', new_schema=True)

                        # Keep track of column data types (and whether forced or inferred)
                        # Note: This will only keep track of the first chunk's inferred types
                        # TODO: Keep track of whether inferred types change for different chunks
                        # New on 11/16/20: Force all the inferred types as forced if '*' 
                        if data_types is not None and '*' in data_types:
                            types_to_force = unified_types
                        else:
                            types_to_force = data_types
                        new_featureset._addColumnTypes(forced_types=types_to_force,
                                                       inferred_types=unified_types)

                        self.out("...created new FeatureSet '{}' with {} rows".format(label, df_unified.shape[0])) 
                        self.out("...types:", new_featureset.types)

                        # Reset the list of source files
                        new_featureset._resetSourceFiles(variant=variant) 

                    # Case (2) If there is prior data and have upsert_vars...
                    elif upsert_vars is not None and curr_df_has_data:
                        print("Upserting...")
                        # If the new file has different columns, must use concat and addData to combine old/new files
                        if not set_equals(columns_list, df.columns):
                            self.out("During upsert found different columns!\nOld:", columns_list, "\nNew:", df.columns)

                        # Concat the old df and new df together
                        self.out("...old df has shape:", curr_df.shape)
                        self.out('...types:', curr_df.dtypes)

                        self.out("...new df has shape:", df.shape)
                        self.out('...types:', df.dtypes)

                        # Keep only the rows in the old dataframe that don't overlap with the new one on the upsert_vars
                        try:
                            upsert_vars_in_new_df = df[upsert_vars].drop_duplicates()
                        except:
                            self.out("ERROR: Cannot find upsert_vars [{}] in the next file loaded: {}".format(upsert_vars,
                                                                                                              data_file),
                                     type='error')
                            raise


                        # Get left outer join to keep only rows in the old dataframe not in the new one
                        curr_df_merge = curr_df.merge(upsert_vars_in_new_df, 
                                                        on=upsert_vars,
                                                        how='left',
                                                        indicator=True)
                        curr_df_not_in_new_df = curr_df_merge[curr_df_merge['_merge'] == 'left_only'][curr_df.columns]
                        print("...keeping {} rows from previous dataframe:".format(curr_df_not_in_new_df.shape))

                        # Concat the two dataframes together (keeping all columns, even if different)
                        df_concat = curr_df_not_in_new_df.append(df)

                        # Unify the new concatted dataframe with the given types
                        df_unified, unified_types = FeatureSet._unifyDataTypes(df_concat, fillna=True, 
                                                                          debug=(self.output_mode=='debug' or (self.dsphere is not None and self.dsphere.output_mode=='debug')),
                                                                              forced_types=data_types)


                        self.out("...new upserted df has shape:", df_unified.shape)
                        self.out('...types:', df_unified.dtypes)
                        columns_list = df_unified.columns

                        # Then add this new unified dataframe in place of any previous one
                        self.out("...overwriting data in featureset, not appending")
                        new_featureset = self.addData(label, df_unified, datatype='dataframe', 
                                                      forced_types=data_types, inferred_types=unified_types,
                                                      overwrite=True, # Added on 12/14/20 to avoid creating many copies
                                                      **kwargs)

                    # Case (3) If there is prior data but the columns in the new dataframe are different...
                    elif curr_df_has_data and not set_equals(columns_list, df.columns):
                        # If the new file has different columns, must use concat and addData to combine old/new files
                        self.out("Found different columns!\nOld:", columns_list, "\nNew:", df.columns)

                        # Unify the new dataframe with the given types
#                             df_unified, unified_types = FeatureSet.unifyDataTypes(df, fillna=True, 
#                                                                                   debug=(self.output_mode=='debug'),
#                                                                                   forced_types=data_types)

                        # Concat the old df and new df together
                        self.out("...old df has shape:", curr_df.shape)
                        self.out('...types:', curr_df.dtypes)

                        self.out("...new df has shape:", df.shape)
                        self.out('...types:', df.dtypes)

                        # Concat the two dataframes together
                        df_concat = pd.concat([curr_df, df], axis=0, sort=True).reset_index(drop=True)

                        # Unify the new concatted dataframe with the given types
                        df_unified, unified_types = FeatureSet._unifyDataTypes(df_concat, fillna=True, 
                                                                              debug=(self.output_mode=='debug' or (self.dsphere is not None and self.dsphere.output_mode=='debug')),
                                                                              forced_types=data_types)


                        self.out("...new concatted df has shape:", df_unified.shape)
                        self.out('...types:', df_unified.dtypes)
                        columns_list = df_unified.columns

                        # Then add this new unified dataframe in place of any previous one
                        self.out("...overwriting data in featureset, not appending")
                        new_featureset = self.addData(label, df_unified, datatype='dataframe', 
                                                      forced_types=data_types, inferred_types=unified_types,
                                                      overwrite=True, # Added on 12/14/20 to avoid creating many copies
                                                      **kwargs)

                    # Case (4) If there's only one file to load and we're not appending it...
                    elif num_files_to_load == 1 and not append:
                        # Unify the new dataframe with the old data types
                        self.out("...unifying this dataframe")
                        df_unified, unified_types = FeatureSet._unifyDataTypes(df, fillna=True, 
                                                                          debug=(self.output_mode=='debug' or (self.dsphere is not None and self.dsphere.output_mode=='debug')),
                                                                              forced_types=data_types)

                        # Then use addData to overwrite the previous dataframe here with the new types
                        self.out("...overwriting data in featureset, not appending")
                        new_featureset = self.addData(label, df_unified, datatype='dataframe', 
                                                      forced_types=data_types, inferred_types=unified_types,
                                                      **kwargs)

                        # Reset the list of source files
                        new_featureset._resetSourceFiles(variant=variant)

                    # Case (5) Otherwise if appending to a prior dataset and the columns are the same...
                    else:
                        # Unify the new dataframe with any given data types
                        self.out("...unifying this dataframe")
                        df_unified, unified_types = FeatureSet._unifyDataTypes(df, fillna=True, 
                                                                          debug=(self.output_mode=='debug' or (self.dsphere is not None and self.dsphere.output_mode=='debug')),
                                                                              forced_types=data_types)

                        # Append using the schema created from the first chunk
                        self.out("...appending to an existing dataframe on disk")
                        new_featureset.append(df_unified, filetype='parquet', new_schema=False)
                        self.out("...appended dataframe of {} rows".format(df_unified.shape[0]))
                        self.out("...types:", new_featureset.types)

                    # New on 12/19/20: Keep track of source files in the FeatureSet's metadata
                    new_featureset._addSourceFile(data_file, variant=variant)
                    self.out("...added {} to the list of source files for this featureset".format(data_file))

                    # Need to manually update the FeatureSpace metadata since no call to addData() here
                    self._updateFeatureSetMetadata(label)
                    reload_success = self._reload(label)

                    num_files_so_far += 1
                    print("Total num files loaded so far:", num_files_so_far)
                    self.view(label, '', 'shape')

                    # Delete the temporary import file if it was downloaded from an external source
                    if local_file_created_flag:
                        os.unlink(local_filepath)
                        local_file_created_flag = False

                    # Free up RAM
                    del(df)
                    del(df_unified)

                    self.out("Setting dependency for '{}' on the file: {}".format(label, filepath))
                    self._setDependency(label, 'File', {'type':'loadDataFromFile',
                                                       'file':filepath,
                                                       'delimiter': delimiter}, 
                                                       **kwargs)
            else:
                print("WARNING: Could not find file to load data from: {}".format(local_filepath))
                return None

        if num_files_so_far>0:
            # Need to update the FeatureSpace metadata since no call to addData() here
            self._updateFeatureSetMetadata(label)

            # Due to the manual code inside FeatureSet.append(), need to reload the FeatureSet so Dask updates the metadata
            reload_success = self._reload(label)
        ######################################################

    # Otherwise query an entire DB table (if given)
    elif database is not None and table is not None and source is not None:
        bigdata_threshold = DEFAULTS._DEFAULT_MAX_DB_LOAD_SIZE
        numrows_per_query = DEFAULTS._DEFAULT_MAX_DB_LOAD_SIZE
        whereStatement = '' if where is None else " WHERE {}".format(where)
        limitStatement = '' if limit is None else " LIMIT {}".format(limit)

        # First query the size of the database table
        sizeQuery = 'SELECT COUNT(*) as count FROM {}.{}{}'.format(database, table, whereStatement)
        logging.info("Querying: {}".format(sizeQuery))
        print("Querying: {}".format(sizeQuery))
        db_connector = self.connectors[source]

        # Use the connector to create an initial DB connection
        db_connector.connect()
        #if self.connection is None:
        #    self.connectToDB(source)
        df = pd.read_sql_query(sizeQuery, con=db_connector.connection,
                               coerce_float=False) # Added this 1/3/22 because large ints (>=1e20) are getting curtailed

        num_rows = df['count'][0]
        del(df)
        print("...found {} rows".format(num_rows))

        # Set 'chunked' flag based on whether there are more rows in the DB table than the default max to load 
        chunked = num_rows >= bigdata_threshold
        if chunked:
            print("...this is considered 'Big Data' for being larger than {} rows".format(bigdata_threshold))

        # Otherwise query all the data in the table at once
        query = 'SELECT * FROM {}.{}{}{}'.format(database, table, whereStatement, limitStatement)
        print("running this query:", query)
        self._loadDataFromDB(label, query, source=source,
                            index_cols=index_cols, feature_cols=feature_cols, label_cols=label_cols, 
                            chunked=chunked, **kwargs)

    # Otherwise execute the given query (if given)
    elif query is not None:
        self._loadDataFromDB(label, query, source=source, 
                            index_cols=index_cols, feature_cols=feature_cols, label_cols=label_cols,
                            chunked=chunked, **kwargs)

    else:
        print("NO SOURCE OF DATA TO LOAD.")



#############################################################################################
# TODO: Support variants here?
# TODO: Keep track of whether inferred column types change across chunks, notify the user, maybe go back and re-save if so
def _loadDataFromDB(self, label, query, source, index_cols=None, feature_cols=None, label_cols=None, chunked=False, **kwargs):
    # have to query
    logging.info("Querying for {} data: {}".format(label, query))
    #if self.connection is None:
    #    self.connectToDB(source)
    if source not in self.connectors:
        print("No connector found for source '{}'...creating connector".format(source))
        self.connectors[source] = con._GetConnector(parameters)
    if source in self.connectors:
        db_connector = self.connectors[source]

        # Use the connector to create an initial DB connection
        db_connector.connect()

        # Check if any column data types are defined in the function call
        data_types = kwargs.get('data_types', None)

        # If chunked=True, separate the result set of the given query into chunks of rows
        if chunked:
            # Get an iterator to run through all the chunks of rows
            chunk_size = DEFAULTS._DEFAULT_CHUNK_SIZE
            df_chunks = pd.read_sql_query(query, con=db_connector.connection, chunksize=chunk_size,
                                          coerce_float=False)

            # If this table is considered "big data", then break up the query into shards by groups of rows
            num_rows_so_far = 0
            for df in df_chunks:                
                # Create the initial output Feature Set
                if num_rows_so_far == 0:
                    # Create a new FeatureSet with no data in it
                    new_featureset = self.addData(label, None, datatype='dataframe', 
                                                  index_cols=index_cols, feature_cols=feature_cols, 
                                                  label_cols=label_cols, 
                                                  filetype='parquet',
                                                  **kwargs)

                    df_unified, unified_types = FeatureSet._unifyDataTypes(df, fillna=True, 
                                                                          debug=(self.output_mode=='debug' or (self.dsphere is not None and self.dsphere.output_mode=='debug')),
                                                                          forced_types=data_types)

                    # Commenting out on 5/28/19 to let FeatureSet.append infer the schema from pyarrow, not create it here
                    #schema = FeatureSet.createPyArrowSchema(unified_types)
                    #new_featureset.saveSchema(schema)

                    #kwargs_output['types'] = unified_types

                    # Also append this first one again to create part.0.parquet properly
                    new_featureset.append(df_unified, filetype='parquet', new_schema=False)

                    # Keep track of column data types (and whether forced or inferred)
                    # Note: This will only keep track of the first chunk's inferred types
                    # TODO: Keep track of whether inferred types change for different chunks
                    # New on 11/16/20: Special handling of '*' inside forced_types to treat all inferred_types as forced too, and remove '*' from the forced_types going forward so it's not repeated forever downstream
                    if data_types is not None and '*' in data_types:
                        types_to_force = unified_types
                    else:
                        types_to_force = data_types
                    new_featureset._addColumnTypes(forced_types=types_to_force,
                                                   inferred_types=unified_types)

                    self._setDependency(label, 'DB', 'connectToDB', **kwargs)
                    num_rows_so_far += chunk_size
                    print("...created new FeatureSet '{}' with {} rows".format(label, num_rows_so_far))

                    # Store the datatypes for the first chunk, to make sure other chunks use the same dtypes
                    #df_datatypes = dict(df.dtypes)
                    #print("...dtypes:\n", df_datatypes)                

                # After that create a temp FeatureSet, add the new chunk of rows to that, and concat them
                else:
                    df_unified, unified_types = FeatureSet._unifyDataTypes(df, fillna=True, 
                                                                          debug=(self.output_mode=='debug' or (self.dsphere is not None and self.dsphere.output_mode=='debug')),
                                                                          forced_types=data_types)
                    #schema = FeatureSet.createPyArrowSchema(unified_types)
                    #new_featureset.saveSchema(schema)

                    # TODO: This can still break if, for instance, chunk #2 has a column with all nulls while chunk #1
                    # had ints.  How would chunk #2 know how to fillna that column correctly? In unifyDataTypes
                    # it would find the dominant col type to be 'none' and we're just hoping that the default fillna value
                    # there matches the desired fillna value for that column according to the schema picked for chunk #1.

                    # Force all cols to have the datatypes of the first chunk, to prevent inconsistencies (i.e. null cols)
                    #self.addData('TEMP_{}_{}'.format(label, num_rows_so_far), df, datatype='dataframe')
                    #df_typed = df.astype(df_datatypes)
                    num_rows_so_far += chunk_size
                    # Note: Append will use the schema created from the first chunk
                    new_featureset.append(df_unified, filetype='parquet', new_schema=False)
                    print("...appended chunk of {} rows, now have {} total rows".format(chunk_size, num_rows_so_far))

                #self.updateLastUpdated() # Need to call this since we're not calling addData() here
                del(df_unified)
                del(df)

            # Need to update the FeatureSpace metadata since no call to addData() here
            self._updateFeatureSetMetadata(label)

            # Due to the manual code inside FeatureSet.append(), we need to reload the FeatureSet so Dask updates the metadata
            reload_success = self._reload(label)

        # Run the given SQL query and load results all at once
        else:
            df = pd.read_sql_query(query, con=db_connector.connection, coerce_float=False)
            #dask_df = dd.from_pandas(df, chunksize=self._DEFAULT_CHUNK_SIZE, sort=False) #npartitions=10)
            df_unified, unified_types = FeatureSet._unifyDataTypes(df, fillna=True, 
                                                                          debug=(self.output_mode=='debug' or (self.dsphere is not None and self.dsphere.output_mode=='debug')),
                                                                  forced_types=data_types)

            new_featureset = self.addData(label, df_unified, datatype='dataframe', 
                                          index_cols=index_cols, feature_cols=feature_cols, label_cols=label_cols,
                                          forced_types=data_types, inferred_types=unified_types,
                                          **kwargs)
            self._setDependency(label, 'DB', 'connectToDB', **kwargs) 

#############################################################################################
# Pass featureset_to_reload as a string if just want to reload one featureset, a list if multiple ones,
# '*' if all featuresets, otherwise None if not reloading any
# TODO: Prevent overwriting details for feature set already in memory
# TODO: Switch these parameters to **kwargs
# Note: If provided a specific filename to reload, we will interpret variant='*' as variant=None since a filename corresponds
# to a single variant's folder.
def _reload(self, featureset_to_reload=None, batch=None, variant=None, filename=None, filetype=None, datatype=None):            
    batch = batch if batch is not None else self.default_batch
    self.out("Feature set to reload: ", featureset_to_reload, ", variant: ", variant, ", batch:", batch)
    self.out("...in reload, project is '{}'".format(self.project_label))

    # Reload the FeatureSpace first to make sure we reload the latest files
    self.out("Reloading the FeatureSpace...")
    self._loadFeatureSetMetadata()

    # Load in each file from the given feature set list
    featuresets_to_reload = []
    if featureset_to_reload=='*':
        self.out("Reloading all feature sets...")
        # Load all of them
        featuresets_to_reload = self.feature_set_metadata
        #for feature_set_label in self.feature_set_metadata:
        #    self.initialize(feature_set_label)
    elif isinstance(featureset_to_reload, str):
        featuresets_to_reload = [featureset_to_reload]
    elif featureset_to_reload is not None:
        featuresets_to_reload = featureset_to_reload
    #else:
        #print("Reloading feature set {}".format(featureset_to_reload))
        #self.initialize(featureset_to_reload)
    #print("...in reload, project is 2'{}'".format(self.project_label))

    import psutil
    # Iterate through the one or many featuresets to reload
    for feature_set_label in featuresets_to_reload:
        # Load this feature set into memory
        print("...reloading {}".format(feature_set_label))
        if filename is not None:
            # Reload the file from the given filename (don't need to look to the metadata to find the filename)
            # Problem: Don't have datatype yet
            self.out("Using filename: {}, filetype: {}, datatype: {} instead of looking for metadata".format(filename, filetype, datatype))
            datatype_to_reload = datatype
        elif feature_set_label not in self.feature_set_metadata:
            # No metadata for this label at all
            #self.out("WARNING: Cannot initialize FeatureSet {} because do not have metadata for it in the FeatureSpace file".format(feature_set_label),
            #        type='warning')
            return None
        elif batch not in self.feature_set_metadata[feature_set_label]:
            # No metadata for this batch
            self.out("WARNING: Cannot reload feature set={}, batch={} because its metadata is not stored".format(feature_set_label, batch),
                    type='warning')
            return None
        else:
            # There is metadata for this feature_set_label / batch
            feature_set_data = self.feature_set_metadata[feature_set_label][batch]
            datatype_to_reload = feature_set_data['datatype']
            self.out("...will reload feature data of type:", datatype_to_reload)
            #print("Feature set data for {}: {}".format(feature_set_label, feature_set_data))

        # If the FeatureSet object does not exist yet, create it
        if feature_set_label not in self.feature_sets or self.feature_sets[feature_set_label] is None or batch not in self.feature_sets[feature_set_label] or self.feature_sets[feature_set_label][batch] is None:
            if datatype_to_reload=='model':
                self.out("Creating new feature model '{}' for batch '{}', variant '{}'".format(feature_set_label, batch, variant), type='progress')
                new_featureset = FeatureModel(save_directory=self.base_directory, label=feature_set_label, project=self.project_label, batch=batch, space=self)
            elif datatype_to_reload=='chart':
                self.out("Creating new feature chart '{}' for batch '{}', variant '{}'".format(feature_set_label, batch, variant), type='progress')
                new_featureset = FeatureChart(save_directory=self.base_directory, label=feature_set_label, project=self.project_label, batch=batch, space=self)

            else:
                self.out("Creating new FeatureSet object '{}'".format(feature_set_label),
                        type='debug')
                new_featureset = FeatureSet(save_directory=self.base_directory, label=feature_set_label, project=self.project_label, batch=batch, space=self)
                self.out("...feature set directory: {}, project: {}".format(new_featureset.save_directory, new_featureset.project_label))
                self.out("...new featureset has last_updated={}".format(new_featureset.last_updated), type='debug')

            self.out('...in _reload() creating new featureset...Memory: {}'.format(psutil.virtual_memory()))

        else:
            new_featureset = self.feature_sets[feature_set_label][batch]
            #print("new_featureset:", new_featureset.feature_cols, new_featureset.index_cols, new_featureset.label_cols)
            self.out("...feature set directory: {}, project: {}, batch: {}".format(new_featureset.save_directory, new_featureset.project_label, batch))
            self.out('...in _reload() already have featureset...Memory: {}'.format(psutil.virtual_memory()))

        # If using a specific filename, then we need a specific variant
        if filename is not None:
            # Load just the given filename
            print("...loading featureset from directory: {}, file: {}, filetype: {}".format(new_featureset.save_directory, filename, filetype))

            # If variant='*' then switch it to default as None
            if variant=='*':
                variant = None

            new_featureset._loadDataFromFile(filename, variant=variant, filetype=filetype)
            self.out("...new featureset has last_updated={}".format(new_featureset.last_updated), type='debug')

            # Need to set the metadata inside the new featureset, since it was not already known
            new_featureset.last_save_filenames[variant] = filename
            new_featureset.last_save_filetypes[variant] = filetype
            self.out("...new featureset type: {}".format(type(new_featureset)))
            filepath = new_featureset.getSaveDirectory(filename, variant=variant)
            self.out("...new featureset has filepath={}".format(filepath))
            new_featureset.last_save_filepaths[variant] = filepath
            if new_featureset.last_variant_list is None:
                new_featureset.last_variant_list = []
            if variant not in new_featureset.last_variant_list:
                new_featureset.last_variant_list.append(variant)

            # 10/20/21 William Turns 10: Removing this, the FS metadata shouldn't be overwritten by an old featureset
            # when filename is passed into _reload() here.
            # Then need to update the metadata for the FeatureSpace to match this new featureset's metadata
            ##if feature_set_label not in self.feature_set_metadata:
            ##    self.feature_set_metadata[feature_set_label] = {}
            ##self.feature_set_metadata[feature_set_label][batch] = new_featureset._getDefinition()

            # 3/28/20: Also load the metadata specific to this FeatureSet
            new_featureset._loadMetadata(variant=variant)

        else:
            # Otherwise look to the metadata for the list of variants and load one or all of them
            # Now load the featureset from file (for one variant, or all variants if '*' given)
            all_variants = self.getVariantList(feature_set_label, batch=batch, type='recent' if variant=='*' else 'all')
            self.out("reloading...all_variants=", all_variants)
            if variant == '*':
                # Get all the variants in the metadata (since this FeatureSet isn't loaded yet)
                variants_to_reload = all_variants
            elif isinstance(variant, list):
                # Only reload the variants provided in a list (if they are indeed available to reload)
                variants_to_reload = [this_var for this_var in variant if this_var in all_variants] 
            else:
                # If have a specific variant to reload
                if all_variants is not None:
                    variants_to_reload = [variant] if variant in all_variants else []
                else:
                    variants_to_reload = [None] if variant is None else []

            self.out("...in reload, project is '{}'".format(self.project_label))
            self.out("...new featureset has last_updated={}".format(new_featureset.last_updated), type='debug')
            for variant_to_reload in variants_to_reload:
                self.out("...new featureset has last_updated={}".format(new_featureset.last_updated), type='debug')
                self.out("...reloading '{}' with batch '{}' and variant '{}'".format(feature_set_label, batch, variant_to_reload))
                feature_set_info = self.feature_set_metadata[feature_set_label]
                if feature_set_info is not None:
                    feature_set_batch_info = feature_set_info[batch]
                    if feature_set_batch_info is not None:
                        feature_set_filenames = feature_set_batch_info['filenames']
                        feature_set_filetypes = feature_set_batch_info.get('filetypes', None)
                        self.out("...have feature_set_filenames:", feature_set_filenames)
                        self.out("...have feature_set_filetypes:", feature_set_filetypes)
                        if feature_set_filenames is not None and variant_to_reload in feature_set_filenames:
                            latest_filename = feature_set_filenames[variant_to_reload]
                            latest_filetype = feature_set_filetypes.get(variant_to_reload, None) if feature_set_filetypes is not None else None
                            if latest_filename is not None:
                                #print("have latest filename:", latest_filename)
                                #latest_filename = feature_set_info[batch]['filenames'][variant_to_reload]
                                self.out("...loading featureset from directory: {}, file: {}, filetype: {}".format(new_featureset.save_directory, latest_filename, latest_filetype))
                                self.out('...in _reload() before calling _loadDataFromFile...Memory: {}'.format(psutil.virtual_memory()))
                                load_file_success = new_featureset._loadDataFromFile(latest_filename, variant=variant_to_reload, filetype=latest_filetype)
                                self.out('...in _reload() after calling _loadDataFromFile...Memory: {}'.format(psutil.virtual_memory()))
                                if load_file_success:
                                    self.out("...new featureset has last_updated={}".format(new_featureset.last_updated), type='debug')
                                else:
                                    # If there was an error loading the parquet files, quit now 
                                    self.out("ERROR: FeatureSet {} failed to load because files were missing".format(feature_set_label), type='error')
                                    return False
                self.out("...new featureset {} has last_updated={}".format(variant_to_reload, new_featureset.last_updated), type='debug')

            self.out("...in reload, directory is {} and project is '{}', new definition is: {}".format(new_featureset.save_directory, self.project_label, feature_set_data.keys()))
            # Update the parameters within the FeatureSet object to match the metadata
            new_featureset._setDefinition(feature_set_data)

            # 3/28/20: Also load the metadata specific to this FeatureSet
            for var in variants_to_reload:
                new_featureset._loadMetadata(variant=var)


        # Store this FeatureSet in memory
        self._addFeatureSet(feature_set_label, new_featureset, batch=batch)
        del(new_featureset)                
        return True
    # TODO: Do something with the dependency chain...what?
