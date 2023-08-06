import dsphere.Datasphere as ds
import matplotlib.pyplot as plt
import numpy as np

class Plot():
    label=None
    x_label=None
    y_label=None
    x=None
    y=None
    title=None


    def __init__(self, dsphere, title, label, x_label, y_label=None, *args, **kwargs):
        self.title=title
        self.label=label
        self.x_label=x_label
        
        
        data = dsphere.Data(label=label, *args, **kwargs)

        if (x_label not in data.columns):
            print("ERROR: " + x_label + " not in columns of " + label)
            return None
        self.x = data[x_label].to_numpy()

        if y_label is None:
            return None
        
        if (y_label not in data.columns):
            print("ERROR: " + y_label + " not in columns of " + label)
            return None
        self.y_label=y_label
        self.y = data[y_label].to_numpy()
        
        
#     def plot(self, *args, **kwargs):
#         plt.title(self.title)
#         plt.plot(self.x,self.y,*args,**kwargs)
        
#     def scatter(self, *args, **kwargs):
#         plt.title(self.title)
#         plt.scatter(self.x,self.y,*args,**kwargs)
        
#     def hist(self, *args, **kwargs):
#         plt.title(self.title)
#         plt.hist(self.x,*args,**kwargs)
        
#     def boxplot(self, *args, **kwargs):
#         plt.title(self.title)
#         plt.boxplot(self.x,*args,**kwargs)
        
# #     def bar(self, *args, **kwargs):
# #         dsphere.sort(label+'__temp__agg',
# #         label,
# #         self.x, ascending=False,
# #         group_by=[self.y]
# #         )
# #         data = dsphere.Data(label=label, *args, **kwargs)
        
# #         plt.title(self.title)
# #         plt.bar(range(len(self.y)),self.x,*args,**kwargs)
        #    def xlabel(self,label,*args, **kwargs):
#         plt.xlabel(label)
        
#     def ylabel(self,label,*args, **kwargs):
#         plt.ylabel(label)
        
#     def xticks(self,arr,*args, **kwargs):
#         plt.xticks(arr)
        
#     def yticks(self,arr,*args, **kwargs):
#         plt.yticks(arr)
       
#     def 




