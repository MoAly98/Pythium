import os
import sys
import dask
import numpy as np
import pandas as pd
import hist
import uproot4 as uproot
from dask.array import histogram as ds_hist
import dask.dataframe as dd
import timeit
from hist import Hist
import time
import gc
import psutil
from dask.distributed import get_client

class HistoMaker:

    def __init__(self,**kwargs):
        self.histograms = {}
        self.folder_name = kwargs.get('folder_name',None)
        self.file_list = kwargs.get('file_list',None)
        self.client_params = kwargs.get('client_params',{}) ## no params by default
        self.hist_names = kwargs.get('histogram_names',[])
        self.hist_params = kwargs.get('histogram_params',{})
        self.worker_number = 1 # default
        
    
    def get_att(self):
        return vars(self)

    def clear_data(self):
        self.histograms = {}
        self.dask_dfs = []

    def client_start(self,**kwargs):
        for key in kwargs:
            if self.client_params.get(key) != kwargs[key]:
                self.client_params[key] = kwargs[key]

        cl = dask.distributed.Client(**self.client_params)
        self.worker_number = len(cl.scheduler_info()['workers'])
        return cl
    
    @dask.delayed
    def load(self,file_path):
        temp = pd.read_hdf(file_path)
        return temp
    
    @dask.delayed
    def fill(self,histogram,data):
        histogram.fill(data)
        return histogram
    
    def load_data(self,**kwargs):
        ## change that to something better in the future
        if kwargs.get('folder_name',None) != None: self.folder_name = kwargs.get('folder_name',None)
        if kwargs.get('file_list',None) != None: self.file_list = kwargs.get('file_list',None)
        
        counter = 1
        results = []
        key_list = list(self.histograms.keys())
          
        for f in self.file_list:
                
            load_result = self.load(self.folder_name + '/' + f)
            result = self.fill(self.histograms[key_list[counter - 1]],load_result[kwargs['data_col']])
            results.append(result)
            counter += 1
                
        return results
    
    
    def create_histograms(self,**kwargs):
        if kwargs.get('histogram_names',None) != None: self.hist_names = kwargs.get('histogram_names',None)
        if kwargs.get('histogram_params',None) != None: self.hist_params = kwargs.get('histogram_params',None)
        if kwargs.get('drop_existing',False) == True: self.histograms = {}

        for name in self.hist_names:
            self.histograms[name] = Hist(hist.axis.Regular(**self.hist_params)) #bins=10, start=0, stop=1, name="x"

        return self.histograms
    




