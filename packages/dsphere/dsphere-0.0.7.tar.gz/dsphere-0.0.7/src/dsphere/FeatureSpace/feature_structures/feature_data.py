import pandas as pd
import numpy
import datetime
import dateutil.parser as date_parser
import gc
import os
import sys
import shutil
import re
import json
from pympler.asizeof import asizeof
from filelock import FileLock

# Here are methods that must be implemented by the child of this class:
#  save()
#  _getDefinition()
#  delete()

FeatureSpace_directory = 'Dataflows'
FeatureSpace_datatype = 'dataframe'

class FeatureData:
    _last_save_timestamp = None
    label = None
    
    # Make sure this matches what's in the FeatureSpace class
    _DEFAULT_OUTPUT_MODE = 'notebook'
    
    def __init__(self, save_directory=None, datatype=None, label=None, project=None, batch=None, variant=None, space=None):
        if label is not None:
            self.label = label
            
        self.data = {}
        self.save_directory = save_directory or FeatureSpace_directory
        self.last_save_filenames = {}
        self.last_save_filepaths = {}
        self.last_save_filetypes = {}
        self.last_output_locations = {}
        self.last_save_datastructs = {}
        self.last_variant_list = []
        self.last_updated = None
        self.last_updated_flows = {} # Keep track of which flows last modified this FeatureData for each variant
        #self.variant = variant
        self.datatype = datatype or FeatureSpace_datatype 
        # 'dataframe', 'model', 'list'

        # New on 11/18/20: Ability to store "notes" of any kind related to this Featureset -- links, stats, whatever
        self.notes = {}
        
        #self.metadata = {}
        self.project_label = project
        self.batch = batch
        ##self.status = True
        self.space = space
        self.out("instantiating FeatureData with project={}".format(self.project_label))
        #self._updateLastUpdated()
        
     
    def out(self, *args, **kwargs):
        type = kwargs.get('type', 'debug')
        
        # Grab the output mode from the FeatureSpace...or use the default if there is no FeatureSpace somehow
        output_mode = self.space.output_mode if self.space is not None else self._DEFAULT_OUTPUT_MODE
        if type=='debug':
            # Only print debug output if in 'debug' mode 
            if output_mode=='debug':
                print(*args)
        elif args:
            print(*args)
        return
    
    def _getDefinition(self, print_out=False):
        # What about: variant
        return {'label': self.label,
                'datatype': self.datatype,
                'batch': self.batch,
                ##'status': self.status,
                'filenames': self.last_save_filenames,
                'filepaths': self.last_save_filepaths,
                'filetypes': self.last_save_filetypes,
                'outputs': self.last_output_locations,
                'datastructs': self.last_save_datastructs,
                'variants': self.last_variant_list,
                'last_updated': self.last_updated,
                'flows': self.last_updated_flows,
                'directory': self.save_directory
               }
    
    def _setDefinition(self, status_dict):
        self.label = status_dict.get('label', self.label)
        self.datatype = status_dict.get('datatype', self.datatype)
        self.batch = status_dict.get('batch', self.batch)
        ##self.status = status_dict.get('status', self.status)
        self.last_save_filenames = status_dict.get('filenames', self.last_save_filenames)
        self.last_save_filepaths = status_dict.get('filepaths', self.last_save_filepaths)
        self.last_save_filetypes = status_dict.get('filetypes', self.last_save_filetypes)
        self.last_output_locations = status_dict.get('outputs', self.last_output_locations)
        self.last_save_datastructs = status_dict.get('datastructs', self.last_save_datastructs)
        self.last_updated_flows = status_dict.get('flows', self.last_updated_flows)
        self.last_variant_list = status_dict.get('variants', self.last_variant_list)
        if 'last_updated' in status_dict:
            if isinstance(status_dict['last_updated'], str):
                self.last_updated = date_parser.parse(status_dict['last_updated']) 
            else:
                # The metadata object provided here might already contain a datetime
                self.last_updated = status_dict['last_updated']
        #self.last_updated = status_dict.get('last_updated', self.last_updated)
        self.out("Initializing last_update={} for '{}'".format(self.last_updated, self.label), type='debug')
        self.save_directory = status_dict.get('directory', self.save_directory)
    
    def _getDatatype(self):
        return self.datatype
    
    # TODO: Unify this with the same function in FeatureSet, put it in another library somewhere
    # (i.e. don't duplicate this code)
    def getSaveDirectory(self, filename, variant=None, create_dirs=True):
        """
        Hello world
        """
        save_directory = self.save_directory
        self.out("in getSaveDirectory... save_directory={}, project_label={}".format(save_directory, self.project_label))
        batch_label = 'batch_'+self.batch if self.batch is not None else 'batch'
        project_label = self.project_label if self.project_label is not None else 'project'
        
        # Create a list of the sub directories
        path_list = ['data', project_label, batch_label, filename]
        if variant is not None:
            path_list.append(variant)

        # Successively append each nested directory onto the full path
        full_path = save_directory or FeatureSpace_directory
        for path_part in path_list:
            #print("Save directory: {} / {}".format(full_path, path_part))
            full_path = os.path.join(full_path, path_part)
            # If this set of directories do not exist yet...
            if not os.path.exists(full_path):
                # If we should create this sub-folder, go ahead
                if create_dirs:
                    os.mkdir(full_path)
                # Otherwise return null
                else:
                    return None

        return full_path

    def _updateLastUpdated(self):
        self.last_updated = datetime.datetime.now()
        self.out("New last_updated timestamp for {}: {}".format(self.label, self.last_updated))
        

    def _getMetadata(self, variant=None):
        return {'label': self.label,
                'variant': variant,
                'flow': self.space._current_flow,
                'datatype': self.datatype,
                'project': self.project_label,
                'batch': self.batch,
                'children': self.children(variant=variant),
                'last_updated': self.last_updated,
                'filename': self.last_save_filenames[variant],
                'filetype': self.last_save_filetypes[variant],
                'notes': self.notes
               }
    
    # Note: We store a metadata file within each variant's folder
    def _saveMetadata(self, variant=None, filetype=None): 
        # Call the child-class' _getMetadata() method
        featureset_metadata = self._getMetadata(variant)
        
        # Store this in memory too, since it might not already be there before we reload this
        #self.metadata[variant] = featureset_metadata

        # Write this metadata serialized to file
        filepath = self.last_save_filepaths[variant]
        if filepath is not None:
            metadata_filename = 'featureset_metadata.json'
            metadata_path = os.path.join(filepath, metadata_filename)
            self.out("Saving FeatureSet metadata (variant={}) into file: {}".format(variant, metadata_path))
            lock_name = metadata_path+".lock"
            with FileLock(lock_name, timeout=5) as lock:
                self.out("Lock acquired on FeatureSet metadata file '{}' while writing to it...".format(metadata_path))
                with open(metadata_path, 'w') as fout:
                    json.dump(featureset_metadata, fout, sort_keys=False, indent=4, default=str)

    # Load the featureset's metadata file and store its info in this FeatureData object
    def _loadMetadata(self, variant=None):
        filepath = self.last_save_filepaths[variant]
        if filepath is not None:
            metadata_filename = 'featureset_metadata.json'
            metadata_path = os.path.join(filepath, metadata_filename)
            self.out("Reloading FeatureSet metadata (variant={}) from file: {}".format(variant, metadata_path))
            this_metadata = FeatureData._parseMetadata(metadata_path)
            
            # Load parts of the metadata into the object
            metadata_notes = this_metadata.get('notes', {})
            self.notes[variant] = metadata_notes.get(variant, {})
        
            # Load the last_updated timestamp from the featureset metadata file
            if 'last_updated' in this_metadata:
                if isinstance(this_metadata['last_updated'], str):
                    self.last_updated = date_parser.parse(this_metadata['last_updated']) 
                else:
                    # The metadata object provided here might already contain a datetime
                    self.last_updated = this_metadata['last_updated']
                
            # 10/2/21: Take this out of here, put into feature_set.py instead (it shouldn't have been here)
            ##self.dataset_shapes = this_metadata.get('dataset_shapes', None)
            
            # Return the parsed metadata to the child function
            return this_metadata
        return None
                
                
    @staticmethod
    def _parseMetadata(metadata_path):
        lock_name = metadata_path+".lock"
        with FileLock(lock_name, timeout=5) as lock:
            with open(metadata_path) as json_file:
                #featureset_metadata = json.load(json_file)
                featureset_metadata = json.load(json_file, 
                                              object_hook=lambda d: {k if k!='null' else None: v for k, v in d.items()})

                return featureset_metadata
        return None
    
    # Return any notes stored in the metadata
    # If key is passed, this will return just that one note based on its key (if present).
    # If no key is passed, the default '*' means this will return all notes as a dict.
    # Notes are stored with each variant, not with the Featureset overall
    def getNotes(self, key='*', variant=None):
        if not hasattr(self, 'notes'):            
            self.out("WARNING: No notes have been stored for the Featureset {}.".format(self.label), type='warning')
            return None
        elif variant not in self.notes:
            self.out("WARNING: No variant '{}' found for the notes in Featureset {}.".format(variant, self.label), type='warning')
            return None            
        else:
            notes = self.notes[variant]
            if key=='*':
                return notes
            elif key in notes:
                return notes[key]
            else:
                self.out("WARNING: No notes stored with the key '{}' for the Featureset {}. Returning null.".format(key, self.label), type='warning')
                return None
        
    # Store the given notes tied to the given key (if provided)
    # Can take: addNotes('hello world'), addNotes(key='blah', notes='hello world')
    # Also can store anything as "notes"
    # Notes are stored with each variant, not with the Featureset overall
    def addNotes(self, notes=None, key=None, variant=None):
        if key=='*':
            self.out("WARNING: Cannot use key='*' since it's a stored keyword to refer to all notes.", type='warning')
            return None
        if not hasattr(self, 'notes'):
            self.notes = {}
        if variant not in self.notes:
            self.notes[variant] = {}
        self.notes[variant][key] = notes
        print("Stored note for Featureset {}, variant={} with key='{}' and resaved metadata.".format(self.label, variant, key))
        self._saveMetadata(variant=variant)
        return
                
    # TODO: Support sending a list of variants but a single child
    # If there's only 1 data set that matches the variant/child parameters given, just returns that dataset
    # If there's 1 variant and >1 children, return {None: child_dataset1, child1: child_dataset2}
    # If there's >1 variant and 1+ child for each variant, return {None: dataset1, variant1: {None: child_dataset2_child1, child1: child_dataset2_child2}}
    # TODO: Fix this ambiguity!!  The caller won't know the difference between 1 var/2 children and 2 vars/1 child each.
    # BUG!!!  But fix carefully...
    def getData(self, variant=None, child='*'):
        #print("\nIn getData for '{}', variant:".format(self.label), variant, "child:", child, "self.data:", type(self.data))
        if variant == '*' or variant == ['*']:
            #print("have variant='*'")
            # Recurse to get each variant's data
            if len(self.data)==1: # and None in self.data:
                #print("recursing 1")
                only_variant = list(self.data.keys())[0]
                if only_variant is None:
                    # Just return the child(ren)'s data
                    return self.getData(variant=only_variant, child=child)
                else:
                    # Recurse to return the one variant that's here in a dict
                    return {only_variant:self.getData(variant=only_variant, child=child)}
            else:
                # Recurse to return all the variants
                return self.getData(variant=list(self.data.keys()), child=child)
        elif isinstance(variant, list):
            if len(variant)==1:
                # Recurse to return just this one variant
                return self.getData(variant=variant[0], child=child)
            else:
                # If a list is provided, return all the variants for which we have data loaded
                actual_variants_list = self.data.keys()
                all_variants = {target_variant:self.getData(variant=target_variant, child=child) for target_variant in variant if target_variant in actual_variants_list}
                if len(all_variants)==0:
                    self.out("ERROR: Could not find any of the variants requested {} in '{}' (with actual variants: {})".format(variant, self.label, actual_variants_list), type='error')
                    return None
                return all_variants
                #return {target_variant:self.data[target_variant] for target_variant in variant if target_variant in self.data}
        elif variant in self.data:
            # Then requesting just one variant
            this_data_variant = self.data[variant]
            this_data_variant_children = list(this_data_variant.keys())
            #print("...for variant='{}', children are {}:".format(variant, this_data_variant_children))
            num_children = len(this_data_variant_children)
            #print("...num children:", num_children)
            
            if child=='*':
                if num_children==1 and this_data_variant_children[0] is None:
                    # Just return the child, not in a dict
                    return this_data_variant[None]
                else:
                    # Return a dict with all children
                    #print("...getting all children")
                    return {target_child:this_data_variant[target_child] for target_child in this_data_variant_children}
            elif num_children > 1:
                if child in this_data_variant_children:
                    # Return just the requested child
                    return this_data_variant[child]
                else:
                    # No children match the request, return error
                    self.out("ERROR: Child '{}' not found for variant '{}' in '{}'".format(child, variant, self.label), 
                          type='error')
                    return None
            elif num_children == 1:
                #print("...num_children==1")
                if child in this_data_variant_children:
                    #print("child {} found, returning data variant".format(child))
                    return this_data_variant[child]
                else:
                    # No children match the request, return error
                    self.out("ERROR: Child '{}' not found for variant '{}' in '{}'".format(child, variant, self.label),
                         type='error')
                    return None
            else:
                # There are no children to return, this is empty
                self.out("ERROR: No datasets to return for variant '{}' in '{}', return None".format(variant, self.label),
                     type='error')
                
#             # If a particular variant (or None) is provided, return just that variant's children in a dict
#             if child in self.data[variant]:
#                 return {child: self.data[variant][child]}
#             elif child == '*':
#                 print("Getting child='*' for variant={}...".format(variant))
#                 if len(self.data[variant])==1 and None in self.data[variant]:
#                     print("...only the None child here")
#                     return {None: self.data[variant][None]}
#                 else:
#                     print("...getting all children")
#                     return {target_child:self.data[variant][target_child] for target_child in self.data[variant]}
#                 #return {variant: self.data[variant]}
        return None
        #return self.data[variant] if variant in self.data else None
       
    # Need a precise variant/child
    #def addData(self, data, variant=None, child=None):
    def _loadDataIntoMemory(self, data, variant=None, child=None):
        self.out("...adding data to FeatureData instance with type:{}, variant:{}, child:{}".format(type(data), variant, child))
        if variant=='*' or child=='*':
            self.out("ERROR: Cannot support _loadDataIntoMemory for variant='{}' or child='*', exiting.".format(variant, child),
                    type='error')
            raise
            #return None
        if variant in self.data and child in self.data[variant]:
            self.out("...deleting current reference to the FeatureData in self.data[{}][{}]".format(variant, child))
            del(self.data[variant][child])
        gc.collect()
        if variant not in self.data:
            self.data[variant] = {}
        if isinstance(data, dict):
            # Then add each of the child data sets
            self.out("in feature_data._loadDataIntoMemory, data is a dict")
            for child in data:
                child_data = data[child]
                self.data[variant][child] = child_data
        else:
            self.data[variant][child] = data
        del(data)
        
        
    # TODO: Push this method into a super-class or library to use with both feature_model and feature_set, rather than copying
    # Return list of variants for this FeatureSet
    # ...type='memory' --> return variants currently in memory for this FeatureSet 
    # ...type='recent' --> return variants most recently loaded into memory for this FeatureSet (but maybe not in memory now)
    def variants(self, type='memory'):
        if type=='memory':
             return list(self.data.keys())
        else:
            return self.last_variant_list
        
    # Store a variant in this FeatureSet's metadata
    def _saveVariant(self, variant):
        if self.last_variant_list is None:
            self.last_variant_list = []
        if variant not in self.last_variant_list:
            self.last_variant_list.append(variant)
        
    # If you pass a variant --> returns a list of the children for that variant
    # If you don't pass a variant --> returns a dict like {var1: [child1, child2], var2: [child1]}
    # Supports variant='*', one variant, or a list of variants
    def children(self, variant='*'):
        if variant == '*':
            # Create dict of all children for all variants
            return {var:[child for child in self.data[var].keys()] for var in self.data.keys()}
        elif isinstance(variant, list):
            # Create a dict of the children for each variant in the given list
            child_dict = {}
            for var in variant:
                if var in self.data:
                    child_dict[var] = self.data[var].keys()
                else:
                    self.out("ERROR! Cannot find variant='{}' in FeatureData set '{}'".format(var, self.label), type='error')
                    return None
            return child_dict
        elif variant in self.data:
            # Just return list of the children for the given (single) variant
            return [child for child in self.data[variant].keys()]
        else:
            self.out("ERROR! Cannot find variant='{}' in FeatureData set '{}'".format(variant, self.label), type='error')
            return None
    
    def _deleteFilepath(self, filepath_to_delete):
         if filepath_to_delete is not None:
            # Delete this file
            self.out("Deleting files stored at {}".format(filepath_to_delete))
            shutil.rmtree(filepath_to_delete, ignore_errors=False, onerror=None)
            self.out("...done")
        
    def _deleteFile(self, filename_to_delete, variant=None):
        # Get the path to this filename, but do not create missing directories if not already there
        filepath_to_delete = self.getSaveDirectory(filename_to_delete, variant=variant, create_dirs=False)
        self._deleteFilepath(filepath_to_delete)            
        # TODO: Also delete this from the metadata so there's no "ghost" created

    # TODO: Enable saving multiple or all variants per feature set at once, in the same directory, using '*' or a list 
    def save(self, variant=None, file_prefix=None, filetype=None):
        # Figure out the name of the data file based on the current timestamp
        currdatetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        #previous_filename = self.last_save_filenames[variant] if variant in self.last_save_filenames else None
        self._last_save_timestamp = currdatetime
        filename = '{}_{}_{}'.format(file_prefix, self.label, currdatetime) if file_prefix is not None else '{}_{}'.format(self.label, currdatetime)
        
        # Make sure this directory does not already exist
        already_exists = True
        filename_append = ''
        attempt_num = 0
        # Keep iterating until find a file path not already used...but don't try more than 10x to prevent infinite loops
        while already_exists and attempt_num<10:
            filename_to_try = filename + filename_append
            
            # With create_dirs = False, this will return None if this dir does not exist
            filepath = self.getSaveDirectory(filename_to_try, variant=variant, create_dirs=False)
            if filepath is None:
                # This path doesn't exist, so go ahead and create it
                already_exists = False
            else:
                # This path does exist already, so try appending a different number to it until it does not exist
                attempt_num += 1
                filename_append = '_'+str(attempt_num)
                self.out("...filepath already exists:", filepath, "...trying to append '{}'".format(filename_append), 
                         type='error')
        
        filepath = self.getSaveDirectory(filename_to_try, variant=variant, create_dirs=True)
        self.last_save_filenames[variant] = filename_to_try
        self.last_save_filepaths[variant] = filepath
        self.last_save_filetypes[variant] = filetype
        self.last_save_label = self.label
        
        # Added on 10/25/19: Keep track of which flow modified this FeatureData
        current_flow = self.space._current_flow
        self.last_updated_flows[variant] = current_flow
        
        # Keep track of the list of variants stored in memory for this feature set
        self._saveVariant(variant)
            
        # New on 11/13/19: Create a metadata file for each FeatureSet instance
        # TODO: Move this call out to the sub-class that's calling .save(), like FeatureView
        self._saveMetadata(variant=variant, filetype=filetype)

        
    # Delete all data stored here (but not the metadata)
    # Only delete the data stored in the given variant or child if provided
    def _deleteData(self, variant='*', child='*'):
        # Delete all the data objects stored here
        variant_list = list(self.data.keys()).copy() if variant=='*' else list([variant]) if variant in self.data.keys() else list()
        self.out("deleteData for variant='{}', child='{}' --> variants:".format(variant, child), variant_list)
        
        for variant_to_delete in variant_list:
            children = list(self.data[variant_to_delete].keys()).copy()
            self.out("...deleting variant='{}', children:".format(variant_to_delete), children)
            #child_list = list(children).copy() if child=='*' else list(child) if child in children else list()
            for child_to_delete in children:
                if child=='*' or (isinstance(child, str) and child==child_to_delete) or child_to_delete in child:
                    del(self.data[variant_to_delete][child_to_delete])
            del(self.data[variant_to_delete])
        
    
    def delete(self, variant='*', child='*'):
        # Delete all datasets stored here
        self._deleteData(variant=variant, child=child)
        
        # Delete each of the properties stored in memory
        ##del((self.label, self.datatype, self.batch, self.status, self.last_save_filenames, self.last_save_filepaths, self.last_variant_list, self.last_updated, self.save_directory))
        del((self.label, self.datatype, self.batch, 
             self.last_save_filenames, 
             self.last_save_filepaths, 
             self.last_save_filetypes,
             self.last_save_datastructs,
             self.last_updated_flows,
             self.last_variant_list, 
             self.last_updated, 
             self.save_directory))
        gc.collect()
        
        
    def getMemoryUsage(self):
        total_size = 0
        for variant in self.data:
            for child in self.data[variant]:
                total_size += asizeof(self.data[variant][child])
            #total_size += sys.getsizeof(self.data[variant])
        return total_size

    # https://stackoverflow.com/questions/1007481/how-do-i-replace-whitespaces-with-underscore-and-vice-versa
    def _urlify(self, s):
        if not isinstance(s,str):
            s = ''+str(s)

        # Remove all non-word characters (everything except numbers and letters)
        s = re.sub(r"[^\w\s]", ' ', s)

        # Replace all runs of whitespace with a single dash
        s = re.sub(r"\s+", '_', s)

        return s.lower()