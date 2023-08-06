import numpy as np
import pandas as pd
import dask.dataframe as dd
import dill
from scipy.sparse import coo_matrix, csr_matrix, save_npz, load_npz
import os

from dsphere.FeatureSpace.feature_structures.feature_data import FeatureData

class FeatureMatrix(FeatureData):
    
    __feature_type__ = 'FeatureMatrix'
            
    def __init__(self, save_directory=None, label=None, project=None, batch=None, variant=None, space=None, 
                 parent_label=None, matrix=None, matrix_filepath=None, matrix_type='sparse', columns=None, mappings=None):
        FeatureData.__init__(self, save_directory=save_directory, label=label, project=project, 
                             batch=batch, datatype='matrix', space=space)
        self.parent_label = parent_label 
        self.matrix = matrix
        self.matrix_file = matrix_filepath
        self.matrix_type = matrix_type
        self.column_names = list(columns)
        self.mappings = mappings
    
    def _getDefinition(self, print_out=False):
        definition = super()._getDefinition(print_out=print_out)
        definition['parent'] = self.parent_label
        definition['matrix'] = self.matrix
        definition['matrix_file'] = self.matrix_file
        definition['matrix_type'] = self.matrix_type
        definition['columns'] = self.column_names
        definition['mappings'] = self.mappings
        return definition
        
    def _setDefinition(self, status_dict):
        super()._setDefinition(status_dict=status_dict)
        self.parent_label = status_dict['parent']
        self.matrix = status_dict['matrix']
        self.matrix_file = status_dict['matrix_file']
        self.matrix_type = status_dict.get('matrix_type', 'sparse')
        self.column_names = status_dict['columns']
        self.mappings = status_dict['mappings']
        
    def _getMetadata(self, variant=None):
        metadata = super()._getMetadata(variant=variant)
        metadata['parent'] = self.parent_label
        metadata['matrix'] = self.matrix
        metadata['matrix_file'] = self.matrix_file
        metadata['matrix_type'] = self.matrix_type
        metadata['columns'] = list(self.column_names)
        metadata['mappings'] = self.mappings
        return metadata
        
    def getParent(self):
        return self.parent_label
    
    def getMappings(self):
        return self.mappings
    
    def columns(self):
        return list(self.column_names)
    
    def getShape(self):
        if self.matrix is not None:
            return self.matrix.shape
        return None
    
    # type=None: Return the same type as what's stored, otherwise 'csr', 'sparse' (which returns same as 'coo'), or 'dense'
    def getMatrix(self, row=None, col=None, type=None):
        if type is None:
            # Do not change the matrix type
            out_matrix = self.matrix
        elif type=='dense':
            # Turn the matrix into dense if it's sparse now, otherwise keep it as-is
            out_matrix = self.matrix.todense() if self.matrix_type=='sparse' else self.matrix
        elif type=='sparse' or type=='coo':
            # Turn the matrix into sparse if it's dense now, otherwise keep it as-is
            out_matrix = coo_matrix(self.matrix) if self.matrix_type=='dense' else self.matrix.tocoo() if isinstance(self.matrix, csr_matrix) else self.matrix
        elif type=='csr':
            out_matrix = csr_matrix(self.matrix) if self.matrix_type=='dense' else self.matrix.tocsr() if isinstance(self.matrix, coo_matrix) else self.matrix
                
        if row is None and col is None:
            return out_matrix
        elif row is not None:
            return out_matrix.getrow(row)
        elif col is not None:
            col_num = self.column_names.index(col) if isinstance(col, str) else col
            return out_matrix.getcol(col_num)
        
    # Return just the given set of columns from this matrix
    # type=None: Return the same type as what's stored, otherwise 'csr', 'sparse' (which returns same as 'coo'), or 'dense'
    def getColumns(self, columns, type=None):
        matrix_cols = self.columns()
        
        # Make sure all the target columns can be found in this FeatureMatrix
        missing_cols = [col for col in columns if col not in matrix_cols]
        if len(missing_cols)>0:
            self.out("ERROR: Some columns could not be found in the FeatureMatrix '{}': {}".format(self.label, missing_cols),
                     type='error')
            raise
            
        target_col_indexes = [matrix_cols.index(col) for col in columns if col in matrix_cols]
        matrix = self.getMatrix(type=type)
        if isinstance(matrix, coo_matrix):
            return matrix.tocsr()[:, target_col_indexes].tocoo()
        else:
            return matrix[:, target_col_indexes]
    
    def saveToFile(self, filepath):
        fullpath = os.path.join(filepath, 'matrix_{}.npz'.format(self.label))
        if isinstance(self.matrix, np.ndarray):
            self.out("Saving numpy array: {}".format(self.label))
            np.savez_compressed(fullpath, self.matrix)
            type = 'dense'
        else:
            self.out("Saving sparse matrix: {}".format(self.label))
            save_npz(fullpath, self.matrix)
            type = 'sparse'
        self.matrix_type = type
        coldata = {'columns':self.column_names,
                   'mappings':self.mappings,
                   'matrix_file':fullpath,
                   'matrix_type':type}
        coldata_path = os.path.join(filepath, 'metadata_{}.dll'.format(self.label))
        with open(coldata_path, 'wb') as fout:
            dill.dump(coldata, fout)
            
        # returning none to signify there's no change in the data as result of saving it
        return None
        
#         sparse.save_npz("yourmatrix.npz", your_matrix)
#         your_matrix_back = sparse.load_npz("yourmatrix.npz")
    
    #def loadFromFile(self, filepath, variant=None):
    def _loadDataFromFile(self, filepath, variant=None):
        # In this case the full filepath is provided, so don't need to look it up
        #filepath = self.getSaveDirectory(filename, variant=variant)
        
        self.out("Loading matrix from file: ", filepath)
        if self.matrix_type == 'sparse' or self.matrix_type is None:
            # Then try sparse first, backup to dense
            try:
                self.matrix = load_npz(filepath)
                self.matrix_type = 'sparse'
            except ValueError:
                numpy_file = np.load(filepath)
                numpy_first_file = numpy_file.files[0]
                self.matrix = numpy_file[numpy_first_file]
                self.matrix_type = 'dense'
        elif self.matrix_type == 'dense':
            numpy_file = np.load(filepath)
            numpy_first_file = numpy_file.files[0]
            self.matrix = numpy_file[numpy_first_file]
            
        self.out("...done. Found {} matrix of shape:{}".format(self.matrix_type, self.matrix.shape))
             
        self._updateLastUpdated()
        return True
    
    def _getDatatype(self):
        return "FeatureMatrix ({})".format(self.matrix_type)
    
    def head(self, n=5, num_cols=5):
        if self.matrix_type == 'sparse':
            # Make sure there are actually n rows, else this will crash unnecessarily
            matrix_height = self.matrix.shape[0]
            n = min(n, matrix_height)
            
            # Then concat together the first n rows as a DataFrame for viewing
            matrix_head = pd.DataFrame([self.matrix.getrow(i).toarray().flatten() for i in range(0,n)]).iloc[:,:num_cols]
        else:
            # Assume it's dense otherwise
            matrix_head = pd.DataFrame(self.matrix[:n,:num_cols])
        total_num_cols = min(num_cols, len(self.column_names))
        matrix_head.columns = self.column_names[:total_num_cols]
        return matrix_head
    
    # Return a new FeatureMatrix identical to this one
    # Note: This only returns the FeatureMatrix, it does not put it back into the FeatureSpace
    def copy(self):
#         matrix_copy = FeatureMatrix(self.label, 
#                                     self.matrix.copy(),
#                                     columns=self.getColumns(),
#                                     mappings=self.getMappings())
        columns = self.columns()
        mappings = self.getMappings()
        matrix_copy = FeatureMatrix(label=self.label, 
                                     project=self.project_label, 
                                     batch=self.batch, 
                                     space=self.space,
                                     parent_label=self.parent_label,
                                     matrix=self.matrix.copy(),
                                     matrix_type=self.matrix_type,
                                     columns=self.columns() if columns is not None else None, 
                                     mappings=mappings.copy() if mappings is not None else None)
        return matrix_copy
    
    def dataframe(self, type='pandas'):
        if type=='dask':
            # TODO: Don't fix this chunksize
            if self.matrix_type == 'sparse':
                df = dd.from_array(self.getMatrix().todense(), chunksize=500000)
            else:
                df = dd.from_array(self.getMatrix(), chunksize=500000)
            df.columns = self.columns()
            return df
        elif type=='pandas':
            if self.matrix_type == 'sparse':
                df = pd.DataFrame(data=self.getMatrix().todense(),
                                  columns=self.columns(),
                                  index=None)
            else:
                df = pd.DataFrame(data=self.getMatrix(),
                                  columns=self.columns(),
                                  index=None)
#             pd.DataFrame(data=data[1:,1:],    # values
# ...              index=data[1:,0],    # 1st column as index
# ...              columns=data[0,1:])
#             df.columns = self.getColumns()
            return df
        else:
            self.out("ERROR! Cannot convert FeatureMatrix into a '{}'".format(type), type='error')
            return None

    # Return true if this featureset is empty
    def isEmpty(self):
        curr_shape = self.getShape()
        
        if curr_shape is None or curr_shape=={} or curr_shape==[]:
            return True
        elif len(curr_shape)>0 and curr_shape[0]==0:
            return True
        elif len(curr_shape)>1 and curr_shape[1]==0:
            return True
        return False
        
    
    # NOTE TO SELF: When you allow FeatureMatrix to be first-class citizen (not just child of FeatureSet),
    # then you'll need to implement save().  When you do, remember to include this code commented out here.
#     def save(self, ...):
#         print("\nCalling FeatureSet '{}' save(variant={}, child={}, overwrite={}, save_to_disk={}, filetype={}, schema_changed={})".format(self.label, variant, child, overwrite, save_to_disk, filetype, schema_changed))
        
#         previous_filename = self.last_save_filenames[variant] if variant in self.last_save_filenames else None
#         super().save(variant=variant, file_prefix='data', filetype=filetype)
#         new_filename = self.last_save_filenames[variant] if variant in self.last_save_filenames else None

#         # PUT THE SAVE CODE HERE
        
#         # Need to call this so the FeatureSpace updates its metadata file with the latest children created here
#         self.space.updateLastUpdated()
#         self.space.updateFeatureSetList()
