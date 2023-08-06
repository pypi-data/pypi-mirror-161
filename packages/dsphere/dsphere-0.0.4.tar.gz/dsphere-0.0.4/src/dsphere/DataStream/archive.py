import glob
import re
from datetime import datetime as dt
import os
from boto.s3.key import Key
import shutil
import fnmatch

def archive_files_to_s3(path, s3_location, s3_destination, s3_files, s3_bucket, files='*'):                
    # Iterate through all files in this local featureset folder
    print("Archiving files in:", path)
    for local_path, local_subdirs, local_files in os.walk(path):
        local_directory_name = local_path.replace(path,"")+"/"
        if local_directory_name[0]=='/':
            local_directory_name = local_directory_name[1:]
        print("...local directory:", local_directory_name)
        s3_target_path = s3_location+s3_destination+local_directory_name
        print("...target path:", s3_target_path)
        for file in local_files:
            # If provided files parameter, check for match to the file to archive here
            if fnmatch.fnmatch(file, files):
                # Check if the file is already in the equivalent location on S3
                curr_file = os.path.join(local_path, file)
                new_file = s3_target_path+file
                file_to_compare = s3_destination+local_directory_name+file
                print("...checking if file {} is already on S3".format(file_to_compare))
                if file_to_compare not in s3_files:
                    # If not, copy the file from local to S3
                    print("...not already there")
                    print("...upload_file({}, {})".format(curr_file, new_file))
                    k = Key(s3_bucket)
                    k.key = new_file
                    k.set_contents_from_filename(curr_file) #, cb=percent_cb, num_cb=10)
                    print("...done")
                else:
                    print("...already there!")

# function as of 20200120
def archive_featureset(featureset, fs, s3_bucket, base_s3_dir, min_days_ago=2, delete_local_copy=False):
    project = fs.project_label
    batch = fs.default_batch
    featureset_metadata = fs.feature_set_metadata[featureset]
    if batch in featureset_metadata:
        # Find the directory where each featureset is stored
        featureset_metadata_this_batch = featureset_metadata[batch]
        featureset_dir = featureset_metadata_this_batch['directory']
        dir_with_batch = os.path.join(featureset_dir, 'data', project, 'batch_{}'.format(batch))
        print(featureset)
        
        # Look up all archived versions there
        file_string = "data_{}_20*".format(featureset)
        all_featureset_paths = sorted(glob.glob("{}/{}".format(dir_with_batch, file_string)))
        
        # Get the list of active featureset paths
        filepaths = featureset_metadata_this_batch['filepaths']
        active_paths = [filepaths[var] for var in filepaths]
        print(active_paths)
        
        # Create an archive metadata collection file
        
        # Create the correct filename for S3
        s3_location = os.path.join(base_s3_dir, project, "batch_{}".format(batch))
        print("Checking S3 location:", s3_location)
        
        # Get a list of files alredy in the target S3 directory
        prefix_len = len(s3_location)
        s3_files = [fkey.key[prefix_len:] for fkey in s3_bucket.list(prefix=s3_location)]
        #print("Files already in S3: ", s3_files)
        
        # Get the datatype (dataframe / model)
        datatype = featureset_metadata_this_batch['datatype']
        
        # Check which ones are not one of the current active FeatureSets
        days_ago_active = None
        for path in all_featureset_paths:
            print("\nChecking path:", path)
            is_active = False
            for active_path in active_paths:
                if path in active_path:
                    is_active = True
                    print("...already active")
            
            # Find the datetime from the filename
            datetimestring = re.match('[A-Za-z0-9\/\._ ]*_(20[0-9]{6})', path)[1]
            if datetimestring is not None and datetimestring!='':
                try:
                    days_ago = (dt.now() - dt.strptime(datetimestring, '%Y%m%d')).days
                    #days_ago = (dt.now() - dt.strptime(datetimestring, '%Y%m%d%H%M%S')).days
                except:
                    days_ago = 0
            else:
                days_ago = 0
            print(path, "***" if is_active else "", days_ago, "days ago")
            
            # Keep track of the date of the earliest active featureset
            if is_active:
                days_ago_active = days_ago
            
            # Also get the whole folder name
            folder = path[len(dir_with_batch):] + "/"
            print("...folder={}".format(folder))
            
            if datatype!='dataframe':
                # Don't archive models (or non-dataframe types)
                print("...not archiving featureset of type:", datatype)
            elif is_active:
                # Don't archive the "active" featuresets
                print("...not archiving, this is the active featureset")
            elif days_ago < min_days_ago:
                # Don't archive anything within the last N day (configurable parameter)
                print("...not archiving since this is too recent ({} days ago)".format(days_ago))
            elif days_ago_active is not None and days_ago <= days_ago_active:
                # Don't archive anything timestamped after the active featuresets (in case of parallel processing)
                print("...not archiving anything after the active feature sets that were created {} days ago".format(days_ago_active))
            else:
                print("...archiving")
                
                # Check if this featureset is already archived
                s3_destination = os.path.join(s3_location, folder)

                try:
                    archive_files_to_s3(path, s3_location, s3_destination, s3_files, s3_bucket)
                                
                    # Delete the local featureset directory (if told to do so)
                    if delete_local_copy:
                        print("...DELETING", path)
                        shutil.rmtree(path, ignore_errors=False, onerror=None)
                        print("...done")
                        
                except Exception as err:
                    print("ERROR:", err)
                    raise
                
    print("FINISHED ARCHIVING", featureset)
    

def restore_featureset(featureset, fs, s3_bucket, s3_client, base_s3_dir):
    from pathlib import Path
    project = fs.project_label
    batch = fs.default_batch
    featureset_metadata = fs.feature_set_metadata[featureset]
    if batch in featureset_metadata:
        # Find the directory where each featureset is stored
        featureset_metadata_this_batch = featureset_metadata[batch]
        featureset_dir = featureset_metadata_this_batch['directory']
        dir_with_batch = os.path.join(featureset_dir, 'data', project, 'batch_{}'.format(batch))
        print("Base local directory:", dir_with_batch)

        # Get the list of active featureset paths
        filepaths = featureset_metadata_this_batch['filepaths']
        active_paths = [filepaths[var] for var in filepaths]
        print(active_paths)

        # Create the correct filename for S3
        s3_location = os.path.join(base_s3_dir, project, "batch_{}".format(batch))+"/"
        print("Checking S3 location:", s3_location)

        # Get a list of files alredy in the target S3 directory
        prefix_len = len(s3_location)
        s3_files = [fkey.key[prefix_len:] for fkey in s3_bucket.list(prefix=s3_location)]
        print("Sample S3 files:", s3_files)

        # Iterate through each active FeatureSet directory
        for active_path in active_paths:
            # Also get the whole folder name
            dir_len = len(dir_with_batch)+1
            folder = active_path[dir_len:] + "/"
            print("...local folder={}".format(folder))

            # Check if this featureset is already archived
            s3_source = os.path.join(s3_location, folder)
            s3_source_len = len(s3_source)
            print("...s3 source", s3_source)

            # Find matching files on the S3 archive
            matching_s3_files = [s3_file for s3_file in s3_files if s3_file[:len(folder)]==folder]
            print("...matching files", matching_s3_files)

            # Copy each matching file to the local corresponding FS directory (if not already there)
            for matching_s3_file in matching_s3_files:
                local_path = os.path.join(dir_with_batch, matching_s3_file)
                print("...checking if this local file exists:", local_path)

                s3_full_path = os.path.join(s3_location, matching_s3_file)

                if os.path.exists(local_path):
                    print("...already have file!")
                else:
                    print("...don't have local file, copying from S3.")

                    # Create the parent directories if needed
                    local_path_dir = os.path.dirname(local_path)
                    print("...creating parent directories:", local_path_dir)
                    Path(local_path_dir).mkdir(parents=True, exist_ok=True)

                    # Copy the file from S3 to local
                    if s3_client is not None:
                        print("...downloading file from S3 client in path '{}' to local file '{}'".format(s3_full_path, local_path))
                        s3_client.download_file(s3_bucket, s3_full_path, local_path)
                        print("...done")
                    else:
                        print("Need to create S3 client")
