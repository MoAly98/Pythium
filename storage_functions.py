import os
import sys
import dask
import uproot4
import numpy as np
import pandas as pd
import hist
import uproot4 as uproot
from dask.array import histogram as ds_hist
import dask.dataframe as dd
import timeit
from hist import Hist



class HistoMaker:

    def __init__(self,**kwargs):
        self.histograms = {}
        self.folder_name = kwargs.get('folder_name',None)
        self.file_list = kwargs.get('file_list',None)
        self.client_params = kwargs.get('client_params',{}) ## no params by default
        self.dask_dfs = kwargs.get('dask_data_frames',[]) ## no data frames present by default
        self.hist_names = kwargs.get('histogram_names',[])
        self.hist_params = kwargs.get('histogram_params',{})
    
    def get_att(self):
        return vars(self)

    def clear_data(self):
        self.histograms = {}
        self.dask_dfs = []

    def client_start(self,**kwargs):
        for key in kwargs:
            if self.client_params.get(key) != None:
                client_params[key] = kwargs[key]

        cl = dask.distributed.Client(**self.client_params)
        return cl

    @dask.delayed
    def load_data(self,**kwargs):
        ## change that to something better in the future
        if kwargs.get('folder_name',None) != None: self.folder_name = kwargs.get('folder_name',None)
        if kwargs.get('file_list',None) != None: self.file_list = kwargs.get('file_list',None)
        if kwargs.get('drop_existing',False) == True: self.dask_dfs = [] ##in the future expand on these options

        for f in self.file_list:
            temp = pd.read_hdf( self.folder_name + '/' + f)
            temp.reset_index(inplace = True)
            temp = dd.from_pandas(temp,npartitions=1) ##change to variable with list option or just one value
            self.dask_dfs.append(temp)

        return self.dask_dfs

    def create_histograms(self,**kwargs):
        if kwargs.get('histogram_names',None) != None: self.hist_names = kwargs.get('histogram_names',None)
        if kwargs.get('histogram_params',None) != None: self.hist_params = kwargs.get('histogram_params',None)
        if kwargs.get('drop_existing',False) == True: self.histograms = {}

        for name in self.hist_names:
            self.histograms[name] = Hist(hist.axis.Regular(**self.hist_params)) #bins=10, start=0, stop=1, name="x"

        return self.histograms

    @dask.delayed
    def fill_histograms(self,col_name,**kwargs): ##change that later
        counter = 0
        for key in self.histograms:
            self.histograms[key].fill(self.dask_dfs[counter][col_name])
            counter += 1

        return self.histograms




file_list = ["test0.h5","test1.h5","test12345.h5"]
folder = "Skl_Data"
storage_path = "Skl_Data/storage_test.h5"





