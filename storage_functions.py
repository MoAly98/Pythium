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
import re
import subprocess

class HistoMaker:

    def __init__(self,**kwargs):
        self.histograms = {}
        self.file_list = kwargs.get('file_list',None)
        self.client_params = kwargs.get('client_params',{}) ## no params by default
        self.hist_names = kwargs.get('histogram_names',[])
        self.hist_params = kwargs.get('histogram_params',{})
        self.worker_number = 1 # default
        
    def get_att(self):
        return vars(self)

    def clear_data(self):
        self.histograms = {}

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
        temp = pd.read_pickle(file_path.replace('.h5','.pkl'))
        return temp
    
    @dask.delayed
    def fill(self,histogram,data):
        histogram.fill(data)
        return histogram
    
    def load_and_fill(self,**kwargs):
        ## change that to something better in the future
        if kwargs.get('file_list',None) != None: self.file_list = kwargs.get('file_list',None)
        
        counter = 1
        results = []
        key_list = list(self.histograms.keys())
          
        for f in self.file_list:
                
            #load_result = self.load_h5(self.folder_name + '/' + f)
            #result = self.write_pkl(self.folder_name + '/' + f,load_result)
            load_again = self.load_pkl(f)
            result = self.fill(self.histograms[key_list[0]],load_again[kwargs['data_col']])
            #results.append(load_result)
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
    

class Computation:

    def __init__(self,**kwargs):
        self.delayed_array = kwargs.get('delayed_array', [])
        self.histograms = kwargs.get('histograms',{})

    



