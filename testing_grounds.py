
import os
import sys
import dask
import uproot4
import numpy as np
import pandas as pd
from hist import Hist
import hist
import uproot4 as uproot
from dask.array import histogram as ds_hist
import dask.dataframe as dd
import timeit
from dask.distributed import Client
import storage_functions as sf
import time
##procedurre to make client dask work
# read hdf data convert it to csv and save it, then read csv with dask data frame
# or just reset index and then go from there

h_names = []
file_names = []
temp = pd.read_hdf("Skl_Data/test12345.h5")


for i in range(0,10):
    h_names.append(f"h{i}")
    file_names.append(f"test{i}.h5")
    #if os.path.isfile(f"Skl_Data/test{i}.h5"): os.remove(f"Skl_Data/test{i}.h5")
    #temp.to_hdf(f"Skl_Data/test{i}.h5", key="branches")

histogramming = sf.HistoMaker()	


folder = 'Skl_Data'
f_list = file_names
temp = histogramming.load_data(folder_name = folder,file_list =f_list ,drop_existing= True).compute()


h_params = {'bins': 100, 'start' : 0, 'stop': 1*10**6,'name': 'test'}
histogramming.create_histograms(drop_existing = True, histogram_names = h_names, histogram_params = h_params)

t1 = time.time()
histogramming.fill_histograms('leptons_pt').compute()
t2 = time.time()
print("fill time:", t2-t1)

t1 = time.time()
histogramming.fill_histograms('leptons_pt')
t2 = time.time()
print("fill time:", t2-t1)

print(histogramming.histograms['h9'])