import os
import sys
import dask
import numpy as np
import pandas as pd
import hist
import timeit
from hist import Hist
import time
import gc
from dask.distributed import get_client
import re
import subprocess
import hist_vars

class HistoMaker:

    def __init__(self,**kwargs):
        
        self.file_list = kwargs.get('file_list',None)
        self.client_params = kwargs.get('client_params',{}) ## no params by default
        self.worker_number = 1 # default
        self.histograms_computed = []
        self.histogram_variables = kwargs.get('histogram_variables',hist_vars.var_main)
        
    def get_att(self):
        return vars(self)

    def create_file_list(self,top_directory = os.getcwd(),file_regex = '(?=^[^.].)(.*pkl$)',dir_regex = '(?=^[^.].)',**kwargs): #defaults to h5
        regex = re.compile(file_regex)
        dir_regex = re.compile(dir_regex)
        file_names = []

        for root, dirs, files in os.walk(top_directory,topdown = True):
            dirs[:] = [d for d in dirs if dir_regex.match(d)]
            for file in files:
                if regex.match(file):
                    file_names.append(root+file)

        self.file_list = file_names

        return file_names

    def client_start(self,**kwargs):
        for key in kwargs:
            if self.client_params.get(key) != kwargs[key]:
                self.client_params[key] = kwargs[key]

        cl = dask.distributed.Client(**self.client_params)
        self.worker_number = len(cl.scheduler_info()['workers'])
        return cl
   
    @dask.delayed
    def load_h5(self,file_path):
        temp = pd.read_hdf(file_path)
        return temp
    
    @dask.delayed
    def load_pkl(self,file_path):
        temp = pd.read_pickle(file_path)
        return temp
    
    @dask.delayed
    def fill(self,data,hist_dict):
        column_list = list(data.columns)
        histograms_to_fill = []
        data_columns = []
        histograms_filled = []

        for col in column_list:
            if isinstance(hist_dict.get(col),(hist.axis.Regular,hist.axis.Variable)):
                temp = Hist(hist_dict[col])
                histograms_to_fill.append(temp)
                data_columns.append(col)
        
        for (histogram,data_column) in zip(histograms_to_fill,data_columns):
            histograms_filled.append(histogram.fill(data[data_column]))

        return histograms_filled
    
    def load_and_fill(self,file_list = [],**kwargs):
        ## change that to something better in the future
        
        results = []
        for f in file_list:
                
            data = self.load_pkl(f)
            result = self.fill(data,self.histogram_variables)
            results.append(result)
                
        return results
    
    def compute_histograms(self,data_column = '',chunk_size = 8,file_list = [],**kwargs):
        output = []
        
        for i in range(int(len(file_list)/chunk_size)+1):
            if i == int(len(file_list)/chunk_size):
                file_chunk = file_list[(i+1)*chunk_size-1:]
            else:
                file_chunk = file_list[i*chunk_size:(i+1)*chunk_size-1]

            histogram_chunk = dask.compute(self.load_and_fill(file_list = file_chunk))
            
            for item in histogram_chunk[0]:
                #we can create histogram wrapper objects here and add newly computed histograms here
                output.append(item)   

        return output



class Histogram_wrapper(hist.Hist):
    # looks like I will need to update python version, name and label are not supported in hist 2.4 
    def __init__(self, *args, storage = None, metadata = None, data = None):
        
        super().__init__(*args, storage = None, metadata = None, data = None)
        #print(self.label)


class Computation:

    def __init__(self,**kwargs):
        self.delayed_array = kwargs.get('delayed_array', [])
        self.histograms = kwargs.get('histograms',{})





def combine_dicts(dict_list):
    
    pass



