import numpy as np
import pandas as pd
import dask.dataframe as dd
import dill
from scipy.sparse import coo_matrix, save_npz, load_npz
import os
import matplotlib.pyplot as plt

from dsphere.FeatureSpace.feature_structures.feature_data import FeatureData 
from dsphere.FeatureSpace.feature_structures.feature_set import FeatureSet
from dsphere.FeatureSpace.feature_structures.feature_view import FeatureView
        
class FeatureChart(FeatureView):
    _DEFAULT_CHART_TYPE = 'bar'
    _DEFAULT_CHART_SIZE = 10
    _DEFAULT_LABEL_FORMAT = '0.0f'
    _DEFAULT_SHOW_LEGEND = False
    __feature_type__ = 'FeatureChart'

    def __init__(self, save_directory=None, label=None, project=None, batch=None, space=None,
                 type=_DEFAULT_CHART_TYPE, 
                 data_featureset=None, data_child=None, data_variant=None, parameters=None):
        FeatureView.__init__(self, save_directory=save_directory, label=label, project=project, batch=batch, space=space,
                            data_featureset=data_featureset, data_child=data_child, data_variant=data_variant,
                            datatype='chart', parameters=parameters)
        #self.parent_view = parent
        self.chart_type = type
        self.plot = None
        self.fig = None
        self.chart_filepath = None
        self.chart_filename = None
        
        # Store multiple chart images if needed
        self.all_images = {}
        
        # Default mode for now is to save every new plot to disk too as an image
        self.save_to_disk = True
        
    
    def _getDefinition(self, print_out=False):
        definition = super()._getDefinition(print_out=print_out)
        #definition['parent'] = self.parent_view
        definition['chart_type'] = self.chart_type
        definition['chart_filepath'] = self.chart_filepath
        definition['chart_filename'] = self.chart_filename
        return definition
        
    def _setDefinition(self, status_dict):
        super()._setDefinition(status_dict=status_dict)
        #self.parent_view = status_dict['parent']
        self.chart_type = status_dict.get('chart_type', self._DEFAULT_CHART_TYPE)
        self.chart_filepath = status_dict.get('chart_filepath', None)
        self.chart_filename = status_dict.get('chart_filename', None)
    
    def _getDatatype(self):
        return "FeatureChart"
    
    def view(self, **kwargs):
        # Get the latest data for the featureset
        # TODO: Track variants
        data = self.space.Data(self.data_featureset, child=self.data_featureset_child, variant=self.data_featureset_variant)
        
        axes = kwargs.get('axes', None)
        chart_type = kwargs.get('type', self._DEFAULT_CHART_TYPE)
        print("Chart type:", chart_type)
        
        # Pick which image version this is storing
        tag = kwargs.get('tag', None)
        
        # Decide whether to save to disk or not
        save_to_disk = kwargs.get('save_to_disk', False)
        save_path = kwargs.get('save_path', None) 
        save_filename = kwargs.get('save_filename', None)
        if save_filename is not None:
            save_to_disk = True
            
        chart_size = kwargs.get('size', self._DEFAULT_CHART_SIZE)
        show_legend = kwargs.get('legend', self._DEFAULT_SHOW_LEGEND)
        label_format = kwargs.get('label_format', self._DEFAULT_LABEL_FORMAT)
        
        # Apply optional where conditions to filter the data down that's visualized
        # 'where' can be a string 'var1==val2', a list ['var1==val2', 'var2>val3'], or a dict {'var1':'val2'}
        # Note: can't do complex combinations yet like [{'var1':'val2'}, 'var2>val3']
        if data is not None:
            where_conditions = kwargs.get('where', self.parameters.get('where', None))
            print("...where conditions:", where_conditions)
            if where_conditions is not None:
                print("Data shape initially:", data.shape)
                if isinstance(where_conditions, dict):
                    for where_var, where_val in where_conditions.items():
                        if isinstance(where_val, list) or isinstance(where_val, tuple):
                            # Then allow the where_var to be any in this list of where_vals
                            print("Applying where condition: {} in {}".format(where_var, where_val))
                            data = data[data[where_var].isin(where_val)]                        
                        else:
                            # Subset only when the where_var == where_val
                            print("Applying where condition: {}=={}".format(where_var, where_val))
                            data = data[data[where_var]==where_val]
                        print("...result has shape:", data.shape)                    
                else:
                    where_conditions = [where_conditions] if isinstance(where_conditions, str) else where_conditions
                    for where in where_conditions:
                        data = data.query(where)
                        print("...result has shape:", data.shape)


            # Apply optional sort condition to order the list to 
            # -- can pass in either 'var1', ['var1', 'var2'], or {'var1':True, 'var2':False} (True/False indicating ascending)
            if 'sort' in kwargs:
                sort_conditions = kwargs.get('sort', None)
                sort_by = None
                ascending = None
                if isinstance(sort_conditions, str):
                    sort_by = [sort_conditions]
                elif isinstance(sort_conditions, list):
                    sort_by = sort_conditions
                elif sort_conditions is not None:
                    # Assume it's a dict
                    sort_by = [var for var in sort_conditions]
                    ascending = [sort_conditions[var] for var in sort_conditions]
                if sort_by is not None:
                    data_sorted = data.sort_values(sort_by).reset_index(drop=True) if ascending is None else data.sort_values(sort_by, ascending=ascending).reset_index(drop=True)
                else:
                    data_sorted = data.reset_index(drop=True)
            else:
                data_sorted = data.reset_index(drop=True)
        else:
            data_sorted = None
            
        if data_sorted is not None and data_sorted.shape[0]>0 and axes is not None:
            # Optional grouping by series
            series_var = kwargs.get('series', None)
            if series_var is not None:
                series_unique_vals = list(data_sorted[series_var].unique())

            fig, ax = plt.subplots(figsize=(chart_size, chart_size))
            print("...creating fig and ax")
            data_min_yvalue = data_sorted[axes[1]].min()
            data_max_yvalue = data_sorted[axes[1]].max()
            data_min_xvalue = data_sorted[axes[0]].min()
            data_max_xvalue = data_sorted[axes[0]].max()
            
            # Horizontal bar charts
            if chart_type == 'bar':
                if not isinstance(axes, list) and not isinstance(axes, tuple):
                    print("ERROR: axes parameter for bar charts must be a list")
                    return None
                ax.barh(data_sorted[axes[0]], data_sorted[axes[1]])
                rects = ax.patches
                print("...created bar chart")
                
                
                # Optional bar labels
                if 'labels' in kwargs:
                    label_col = kwargs['labels']
                    label_vals = data_sorted[label_col]
                    if 'label_format' in kwargs:
                        label_format = kwargs['label_format']
                        label_format_str = "{"+":{}".format(label_format)+"}"
                        label_val_strings = [label_format_str.format(i) for i in label_vals]
                    else:
                        label_val_strings = label_vals.values

                    # Output each bar label in the middle and to the right of the bar
                    bar_dims = []
                    for rect, label in zip(rects, label_val_strings):
                        width = rect.get_width()
                        bar_height = rect.get_height()
                        height = rect.get_y()
                        if width is not None and not np.isnan(width) and height is not None and not np.isinf(height):
                            # Only show the label if we can
                            bar_dims.append((width, height,label))

                    max_width = np.max([w for (w,h,l) in bar_dims])
                    fixed_width_of_text = 0.005 * max_width
                    for width,height,label in bar_dims:
                        ax.text(width+fixed_width_of_text, height+bar_height/2 ,label, #+ rect.get_height() / 2
                                        ha='left', va='center')

            elif chart_type == 'line' or chart_type == 'scatter':
                #series_labels = []
                last_y_values = []
                if series_var is None:
                    # If just one series to plot
                    if isinstance(axes[0], str):
                        if chart_type == 'line':
                            ax.plot(data_sorted[axes[0]], data_sorted[axes[1]])
                        else:
                            ax.scatter(data_sorted[axes[0]], data_sorted[axes[1]])
                            
                        # Keep track of the y-value at the end of the x-axis
                        last_x_value = data_sorted[axes[0]].max()
                        last_index = data_sorted[axes[0]].argmax()
                        last_y_value = data_sorted.loc[last_index, axes[1]]
                        last_y_values.append(last_y_value)

                        # Print a label of the last data point in each series
                        if label_format is not None:
                            label_format_str = "{"+":{}".format(label_format)+"}"
                            last_y_value_str = label_format_str.format(last_y_value)
                        else:
                            last_y_value_str = str(last_y_value)
                        ax.text(last_x_value, last_y_value, last_y_value_str)
                    elif isinstance(axes[0], list) or isinstance(axes[0], tuple):
                        for sub_axes in axes:
                            print("sub-axes:", sub_axes)
                            if chart_type=='line':
                                ax.plot(data_sorted[sub_axes[0]], data_sorted[sub_axes[1]])
                            else:
                                ax.scatter(data_sorted[sub_axes[0]], data_sorted[sub_axes[1]])
                                
                            # Keep track of the y-value at the end of the x-axis
                            last_x_value = data_sorted[sub_axes[0]].max()
                            last_index = data_sorted[sub_axes[0]].argmax()
                            last_y_value = data_sorted.loc[last_index, sub_axes[1]]
                            last_y_values.append(last_y_value)

                            # Print a label of the last data point in each series
                            if label_format is not None:
                                label_format_str = "{"+":{}".format(label_format)+"}"
                                last_y_value_str = label_format_str.format(last_y_value)
                            else:
                                last_y_value_str = str(last_y_value)
                            ax.text(last_x_value, last_y_value, sub_axes[1]+'\n'+last_y_value_str)


                else:
                    # Iterate through each series, sub-setting the data and plotting that
                    # Note currently don't support series + multiple axes
                    for series_val in series_unique_vals:
                        data_subset = data_sorted[data_sorted[series_var]==series_val].reset_index(drop=True)
                        if chart_type=='line':
                            ax.plot(data_subset[axes[0]], data_subset[axes[1]], label=series_val)
                        else:
                            ax.scatter(data_subset[axes[0]], data_subset[axes[1]], label=series_val)
                            
                        # Keep track of the y-value at the end of the x-axis
                        last_x_value = data_subset[axes[0]].max()
                        if last_x_value != np.nan: 
                            last_index = data_subset[axes[0]].argmax()
                            last_y_value = data_subset.loc[last_index, axes[1]]
                            last_y_values.append(last_y_value)
                            #series_labels.append((series_val,last_value))

                            # Print a label of the last data point in each series
                            if label_format is not None:
                                label_format_str = "{"+":{}".format(label_format)+"}"
                                last_y_value_str = label_format_str.format(last_y_value)
                            else:
                                last_y_value_str = str(last_y_value)
                            ax.text(last_x_value, last_y_value, series_val+'\n'+last_y_value_str)

    #                 max_width = np.max([w for (w,h,l) in bar_dims])
    #                 fixed_width_of_text = 0.03 * max_width
    #                 for width,height,label in bar_dims:
    #                     ax.text(width+fixed_width_of_text, height+.025 ,label, #+ rect.get_height() / 2
    #                                     ha='center', va='center')

                    # Show the legend
                    if len(last_y_values) > 1 and show_legend:
                        handles, labels = ax.get_legend_handles_labels()#ax.get_legend_handles_labels()
                        handles_labels_maxvals = zip(handles, labels, last_y_values)
                        handles_labels_maxvals_sorted = sorted(handles_labels_maxvals, key=lambda x: x[2], reverse=True)
                        handles_sorted = [x[0] for x in handles_labels_maxvals_sorted]
                        labels_sorted = [x[1] for x in handles_labels_maxvals_sorted]
                        ax.legend(handles_sorted, labels_sorted) #, bbox_to_anchor=(1.1, 1.0))

            # Optional axis settings
            if 'xaxis' in kwargs:
                ax.set_xlabel(kwargs['xaxis'])
            if 'yaxis' in kwargs:
                ax.set_ylabel(kwargs['yaxis'])
            
            # Set the y-axis range
            if 'ymax' in kwargs:
                if 'ymin' in kwargs:
                    ax.set_ylim([kwargs['ymin'], kwargs['ymax']])
                else:
                    ax.set_ylim([data_min_yvalue, kwargs['ymax']])
            elif 'ymin' in kwargs:
                ax.set_ylim([kwargs['ymin'], data_max_yvalue]) 
            
            # Set the x-axis range
            if 'xmax' in kwargs:
                if 'xmin' in kwargs:
                    ax.set_xlim([kwargs['xmin'], kwargs['xmax']])
                else:
                    ax.set_xlim([data_min_xvalue, kwargs['xmax']])
            elif 'xmin' in kwargs:
                ax.set_xlim([kwargs['xmin'], data_max_xvalue]) 
                
            #plt.ylim([0,2.5])
            #plt.xlim([pd.to_datetime('2020-01-01'), pd.to_datetime('2020-04-01')])
            #fig.add_axes([2010, 2021, 0, 2.5])
             
            # Update the matplotlib plot object stored in memory with this FeatureChart
            self.plot = plt
            self.fig = fig
                
            # Save to disk
            if save_to_disk:
                self.save(**kwargs)
                #self.save(save_path=save_path, save_filename=save_filename, tag=tag)
                
            plt.show()
            return plt
        
        return None
    
    def save(self, save_path=None, save_filename=None, variant=None, file_prefix='view', filetype='png', **kwargs):
        plt = self.plot
        fig = self.fig
        tag = kwargs.get('tag', None)
        
        if plt is not None:
            chart_size = kwargs.get('size', self._DEFAULT_CHART_SIZE)
            #fig, ax = plt.subplots(figsize=(chart_size, chart_size))
            # Call the super class save to save the image file to the metadata
            super().save(variant=variant, file_prefix=file_prefix, filetype=filetype)
            if save_filename is None:
                new_filepath = self.last_save_filepaths.get(variant, None)                
                print("Saving plot to disk:", new_filepath)
                chart_filename = 'chart_{}.png'.format(self.label)
                plot_file = os.path.join(new_filepath, chart_filename)
                fig.savefig(plot_file, transparent=False, bbox_inches='tight')
                self.chart_filepath = plot_file
                self.chart_filename = chart_filename
                
                # For now store this chart path/filename for each tag too
                self.all_images[tag] = {'path': plot_file,
                                        'filename': chart_filename}
     
            else:
                chart_filepath = os.path.join(save_path, save_filename) if save_path is not None else save_filename
                print("Saving plot to given filepath:", chart_filepath)
                fig.savefig(chart_filepath, transparent=False, bbox_inches='tight')
                self.chart_filepath = chart_filepath
                self.chart_filename = save_filename
                self.all_images[tag] = {'path': chart_filepath,
                                        'filename': save_filename}
            
            # Option to copy the file to another destination 
            if 'copy_to' in kwargs:
                copy_to = kwargs['copy_to']
                print("...copy to:", copy_to)
                copy_to_destination = copy_to.get('destination', None)
                copy_to_filename = copy_to.get('filename', self.all_images[tag]['filename'])
                copy_to_path = copy_to.get('path', '')
                
                # Can write to an external destination
                if copy_to_destination is not None:
                    if copy_to_destination in self.space.connectors:
                        copy_connector = self.space.connectors[copy_to_destination]
                        copy_from_path = self.all_images[tag]['path']
                        copy_from_filename = self.all_images[tag]['filename']
                        print("Copying from {} to destination: {}".format(copy_from_path, copy_to_destination))
                        
                        # Using this connector's "write" function (only works for FTP at the moment 4/17/20)
                        copy_connector.write(copy_from_path,
                                             copy_to_path,
                                             copy_to_filename)
                        
                        
            plt.close()  
        
            # Update the metadata file to store the latest image filepath
            # TODO: Take out the redundant call of this inside FeatureData.save() too -- it's called twice in succession
            self._saveMetadata(variant=variant, filetype=filetype)

            # Update the last updated timestamp
            self._updateLastUpdated()

            # Need to update the FS metadata to point to this new featureset
            self.space._updateFeatureSetMetadata()


    def _getMetadata(self, variant=None):
        metadata = super()._getMetadata(variant=variant)
        metadata['chart_filepath'] = self.chart_filepath
        metadata['chart_filename'] = self.chart_filename
        metadata['images'] = self.all_images
        return metadata        
        
    # Default is parquet / pyarrow, but can also specify 'fastparquet' or 'csv'
    def _loadDataFromFile(self, folder, path=None, filename=None, variant=None, filetype='png'):
        if path is None:
            filepath = self.getSaveDirectory(folder, variant=variant)
        else:
            filepath = path
        return True
         
