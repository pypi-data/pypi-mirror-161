import dsphere.defaults as defaults
import os
import json
import datetime
import shutil
import psutil
import subprocess
import re
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import dsphere.DataStream.executors as executors
import dsphere.connectors as con
import dsphere.DataStream.syncs as sync
import dsphere.DataStream.modelers as model
import dsphere.DataStream.archive as archive
from dsphere.FeatureSpace import FeatureSpace
import tempfile
import sys

class dotdict(dict):
    """dot.notation access to dictionary properties"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
DEFAULTS = dotdict(defaults.DEFAULTS)


# Returns the contents returned by the given connector's read() command
# rows should be None (full file) or an integer (to get the header for a given # of rows) or 'head' for the first-5 rows
# kwargs can contain a decryption_key (optional, not supported by all connectors)
def read(self, path, rows=None, connector=None, **kwargs):
    if connector is not None:
        if connector in self.connectors:
            read_type = 'read' if rows is None else 'head:{}'.format(rows) if isinstance(rows, int) else 'head'
            return self.connectors[connector].read(path, type=read_type, **kwargs)
    print("No results returned")
    return None

# Wrapper to execute read() with type='download' command through the given connector
def download(self, path, localpath=None, connector=None, decryption_key=None):
    if connector is not None:
        if connector in self.connectors:
            self.connectors[connector].read(path, to_file=localpath, type='download')
    print("File at {} has been downloaded locally to {}".format(path, localpath))
    return None

# Archive old files/folders for one or all featuresets in this DataStream's FeatureSpace
# by copying them to the given S3 bucket in the given archive_folder location (only if that folder is not the most-recent
# or active copy of the featureset)
# - min_days_ago (default=2): Wait until a featureset is this many days old before archiving it 
# - delete_local_copy (default=True): Whether to also delete the local copy of this featureset's files/folders
# TODO: Support other types of connectors than just S3 for archiving
# TODO: Support deleting old copies locally without also copying them to the archive S3 bucket
# TODO: Support overwriting of the archived copy if it's already there
# TODO: Clean up the code in archive.py to be directly connected to the DataStream object and use the connectors' native commands, rather than replay those lines of code in archive.py
# TODO: Skip archiving of featuresets with "[[TEMP]]" in the name, since these are necessarily temporary
# If featureset is None, we will archive the files defined in the 'files' parameter
def archive(self, featureset, s3_connector, archive_folder, min_days_ago=2, delete_local_copy=True, path=None, files=None):
    self.connectors[s3_connector].connect()
    if featureset is not None:
        if featureset == '*':
            print("Archiving all FeatureSet in this FeatureSpace to the directory {} on the S3 connector '{}'".format(archive_folder, s3_connector))
            for one_featureset in self.FeatureSpace.feature_set_metadata:
                archive.archive_featureset(one_featureset, 
                                           self.FeatureSpace, 
                                           self.connectors[s3_connector].bucket, 
                                           archive_folder, 
                                           min_days_ago=min_days_ago,
                                           delete_local_copy=delete_local_copy)  
        else:
            print("Archiving the FeatureSet '{}' in this FeatureSpace to the directory {} on the S3 connector '{}'".format(featureset, archive_folder, s3_connector))
            archive.archive_featureset(featureset, 
                                       self.FeatureSpace, 
                                       self.connectors[s3_connector].bucket, 
                                       archive_folder, 
                                       min_days_ago=min_days_ago,
                                       delete_local_copy=delete_local_copy)   
    # If featureset is None, look to the files parameter
    elif files is not None:
        # Get a list of files alredy in the target S3 directory
        print("Archiving files: {} in {}".format(files, path))
        s3_location = archive_folder
        prefix_len = len(s3_location)
        s3_bucket = self.connectors[s3_connector].bucket
        s3_files = [fkey.key[prefix_len:] for fkey in s3_bucket.list(prefix=s3_location)]

        archive.archive_files_to_s3(path, s3_location, '', s3_files, s3_bucket, files=files)


# Restore an archived copy of an *active* featureset from an external S3 bucket back into this local FeatureSpace directory
# (only works for the most-recent or active variants of the given featureset, and only if they are also archived on the S3 bucket...which should rarely be the case because ordinarily archiving does not copy the most recent version)
# TODO: Support restoring of past (non-active) copies of the featureset
# TODO: Support non-S3 bucket archives
# TODO: Control whether/not to overwrite the local copy
# TODO: Allow control over where locally to restore the archived copy (by choosing a FeatureSpace or folder)
def restore(self, featureset, s3_connector, base_s3_dir):
    self.connectors[s3_connector].connect()
    print("Restoring the FeatureSet '{}' into this FeatureSpace from the directory {} on the S3 connector '{}'".format(featureset, base_s3_dir, s3_connector))
    archive.restore_featureset(featureset, 
                               self.FeatureSpace, 
                               self.connectors[s3_connector].bucket, 
                               self.connectors[s3_connector].client, 
                               base_s3_dir)


########################
### helper functions
#     # TODO: Unify these two functions into a more generalized ds.copy() function that can copy any set of files 
#     # from one source to another (so it could take both SFTP->S3 and S3->SFTP
#     # Also then we can make the default temporary directory the location inside the _DataStream folder
#     def copy_file_from_sftp_to_s3(self, sftp_conn: str, #SFTP_Connector, # Now pass in the name of the connector
#                                   sftp_dir: str, 
#                                   sftp_filename: str, 
#                                   s3_conn: str, #S3_Connector, # Now pass in the name of the connector
#                                   s3_dir: str, 
#                                   s3_filename: Optional[str] = None, 
#                                   #temp_local_dir: str = '/tmp',
#                                   #temp_local_filename: Optional[str] = None, 
#                                   overwrite_s3_file: bool = False,
#                                   overwrite_local_file: bool = False, 
#                                   delete_local_file: bool = False) -> None:

#         # Get S3 and SFTP connectors
#         if sftp_conn in self.connectors:
#             sftp_connector = self.connectors[sftp_conn]
#         else:
#             print("Do not have connector information for the given SFTP connector '{}'".format(sftp_conn))
#             return None
#         if s3_conn in self.connectors:
#             s3_connector = self.connectors[s3_conn]
#         else:
#             print("Do not have connector information for the given S3 connector '{}'".format(s3_conn))
#             return None

#         # TODO: Confirm with Lara if this captures similar logic as before
#         if self.temp_file is None:
#             base, ext = os.path.splitext(sftp_filename)
#             local_temp_filepath = tempfile.NamedTemporaryFile(dir=self.base_folder, suffix=ext).name
#             #temp_local_filename = tempfile.NamedTemporaryFile(dir=temp_local_dir, suffix=ext).name
#         else:
#             local_temp_filepath = self.temp_file #os.path.join(temp_local_dir, temp_local_filename)
#         temp_local_dir, temp_local_filename = os.path.split(self.temp_file)
#         sftp_filepath = os.path.join(sftp_dir, sftp_filename)
#         print(f'Downloading SFTP file {sftp_filepath} temporarily to local file: {local_temp_filepath}')
#         sftp_connector.read(sftp_dir, type='download', sftp_file_string=sftp_filename, local_dir=temp_local_dir,
#                        local_filename=temp_local_filename, overwrite=overwrite_local_file)
#         if s3_filename is None:
#             s3_filename = sftp_filename
#         s3_filepath = os.path.join(s3_dir, s3_filename)
#         print(f'Pushing to S3 at {s3_filepath}')
#         try:
#             s3_connector.write(None, s3_filepath, local_filename=local_temp_filepath, overwrite=overwrite_s3_file)
#         except:
#             raise
#         finally:
#             if delete_local_file:
#                 if os.path.exists(local_temp_filepath):
#                     print(f'Deleting local temp file {local_temp_filepath}')
#                     os.remove(local_temp_filepath)


#     def sync_sftp_files_to_s3(self, sftp_conn: str, #SFTP_Connector, # Now pass in the name of the connector
#                               sftp_dir: str, 
#                               sftp_file_string: str, 
#                               s3_conn: str, #S3_Connector, # Now pass in the name of the connector
#                               s3_dir: str, 
#                               #local_dir: str = '.', 
#                               #temp_file: str = 'TEMP',
#                               delete_temp_file: bool = True, 
#                               overwrite_s3_files: bool = False,
#                               include_subdirs: bool = False) -> None:
#         print(f'Sync files from SFTP to S3 called with args: sftp_conn={sftp_conn}, '
#               f'sftp_dir={sftp_dir}, sftp_file_string={sftp_file_string}, '
#               f's3_conn={s3_conn}, s3_dir={s3_dir}, ' #local_dir={local_dir}, '
#               #f'temp_file={self.temp_file}, '
#               f'delete_temp_file={delete_temp_file}, '
#               f'overwrite_s3_files={overwrite_s3_files}, include_subdirs={include_subdirs}\n')

#         local_temp_file = self.temp_file #os.path.join(local_dir, temp_file)

#         # Get S3 and SFTP connectors
#         if sftp_conn in self.connectors:
#             sftp_connector = self.connectors[sftp_conn]
#         else:
#             print("Do not have connector information for the given SFTP connector '{}'".format(sftp_conn))
#             return None
#         if s3_conn in self.connectors:
#             s3_connector = self.connectors[s3_conn]
#         else:
#             print("Do not have connector information for the given S3 connector '{}'".format(s3_conn))
#             return None

#         # get list of existing s3 files
#         s3_files = s3_connector.read(s3_dir, type='list')
#         print("Found {} files in the target directory on S3: {}".format(len(s3_files), s3_dir))
#         # get list of SFTP files
#         sftp_file_list = sftp_connector.read(sftp_dir, type='list')
#         print("...searching from {} files on SFTP in {} matching {}".format(len(sftp_file_list), sftp_dir, sftp_file_string))
#         for filename in sftp_file_list:
#             if fnmatch.fnmatch(filename, sftp_file_string):
#                 print(filename)
#                 print("...matched")
#                 if filename not in s3_files or overwrite_s3_files:
#                     if sftp_connector._is_remote_directory(os.path.join(sftp_dir, filename)):
#                         # recursively iterate through this directory
#                         if include_subdirs:
#                             print(f"...{filename} is a directory, will recurse through files")
#                             self.sync_sftp_files_to_s3(sftp_conn=sftp_conn, 
#                                                   sftp_dir=os.path.join(sftp_dir, filename),
#                                                   sftp_file_string='*',
#                                                   s3_conn=s3_conn,
#                                                   s3_dir=os.path.join(s3_dir, filename) + '/',
#                                                   #local_dir=local_dir,
#                                                   #temp_file=self.temp_file,
#                                                   delete_temp_file=False,
#                                                   overwrite_s3_files=overwrite_s3_files,
#                                                   include_subdirs=include_subdirs)
#                         else:
#                             print(f'Skipping {filename} since it is a directory')
#                     else:
#                         self.copy_file_from_sftp_to_s3(
#                             sftp_conn=sftp_conn,
#                             sftp_dir=sftp_dir,
#                             sftp_filename=filename,
#                             s3_conn=s3_conn,
#                             s3_dir=s3_dir,
#                             s3_filename=filename,
#                             #temp_local_dir=local_dir,
#                             #temp_local_filename=temp_file,
#                             overwrite_s3_file=overwrite_s3_files,
#                             overwrite_local_file=True,
#                             delete_local_file=False)
#                 else:
#                     print("...already have a copy on S3")
#         # clean up temp file if needed
#         if delete_temp_file:
#             if os.path.exists(self.temp_file): #local_temp_file):
#                 print(f'Deleting temp local file {self.temp_file} now that S3 sync is complete')
#                 os.remove(self.temp_file)