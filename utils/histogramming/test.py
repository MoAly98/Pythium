import os
import dask
from distributed import Client
import numpy as np
import pandas as pd
import hist
import re
import subprocess
import dask.dataframe as dd

import sys
sys.path.append(os. getcwd()+'/Histogramming')

import hist_vars as hist_vars
import histogramming_config as hc
import storage_functions as sf
import cross_product_backend as back

# for region:
#   for samples: (files of slimmed data)
#       for systematics: 
#           for observable:
#               fill

@dask.delayed
def dask_query(data, filter):

    return data.query(filter)

def get_functional_def(var, function_var):

    if function_var == None:

        return var
    
    else:

        return function_var

def fill_all():

    helper = sf.HistoMaker()

    client = helper.client_start(**hc.client_params)

    print(f'Client Dashboard: {client.dashboard_link}')

    out = []
    out_linear = []
    naming = []
    naming_linear = []
    i = 0
    
    for S in hc.Samples:

        out.append([])
        naming.append((S.name,[]))
        j = 0

        for f in S.file_list:
            
            naming[i][1].append((f,[]))
            data = helper.load_h5(f)            
            out[i].append([])
            k = 0
            
            for R in hc.Regions: 

                out[i][j].append([])
                naming[i][1][j][1].append((R.name,[]))

                for Sys in hc.Systematics:
                    # add systematic data join
                    function_filter, sample_filter, systematic_weight, skip = hc.functional_XP(S.name, R.name, Sys.name) # functional definition
                    
                    if skip:
                        
                        naming[i][1][j][1][k][1].append(Sys.name)                    
                        out[i][j][k].append(None)
                    
                    else:   
                        
                        filtering = get_functional_def(R.filter,function_filter)
                        systematic_weight = get_functional_def(Sys.weighting,systematic_weight)

                        temp = helper.fill(dask_query(data,filtering),hc.var_dict)
                        naming[i][1][j][1][k][1].append(Sys.name)                    
                        out[i][j][k].append(temp)

                        out_linear.append(temp)

                        name = back.Named_hists(name = 'x', sample = S.name, region = R.name, systematic = Sys.name, file = f)

                        naming_linear.append(name)

                k = k + 1
            
            j = j + 1

        i = i + 1


    return out, client, naming, out_linear, naming_linear

def combine_samples(output,naming): #both need to be linear

    out = [] # list of samples that contains the rest of the junk
    dict_out = {}
    obs_list = list(hc.var_dict)
    
    for output_element, naming_element in zip(output,naming):

        if dict_out.get(naming_element.sample) == None:

            dict_out[naming_element.sample] = {}
        
        if dict_out[naming_element.sample].get(naming_element.region) == None:

            dict_out[naming_element.sample][naming_element.region] = {}

        if dict_out[naming_element.sample][naming_element.region].get(naming_element.systematic) == None:

            dict_out[naming_element.sample][naming_element.region][naming_element.systematic] = {}
        
        for i in range(len(output_element)):

            observable = obs_list[i]

            if dict_out[naming_element.sample][naming_element.region][naming_element.systematic].get(observable) == None:

                dict_out[naming_element.sample][naming_element.region][naming_element.systematic][observable] = output_element[i].copy()
            
            else:
                
                dict_out[naming_element.sample][naming_element.region][naming_element.systematic][observable] += output_element[i]
                

    return dict_out

#def 

# out[i] : ith sample
# out[i][j] : jth file
# out[i]][j][k] : kth region
# out[i][j][k][n] : nth systematic
# out[i][j][k][n][m] : mth histogram
# out[i][j][k][n][m][l] : lth partiton (not implemented)

# name[i][0] : ith sample
# name[i][1][j][0] : jth file
# name[i][1][j][1][k][0] : kth region
# name[i][1][j][1][k][1][n][0] : nth systematic
# further naming is given by hist_vars file

#########################################################
#################### Junk, ignore it ####################
#########################################################

def combine(out,naming):

    return 0

def combine_partitions(data):

    for sample in data:
        for f in sample:
            for region in f:
                for systematic in region:
                    for m in range(len(systematic)):
                        combined_hist = systematic[m][0]
                        for l in range(1,len(systematic[m])):
                            combined_hist = combined_hist + systematic[m][l]
                        
                        systematic[m] = combined_hist
    
    return data


##########################################################
## experimental way of doing this, broken at the moment ##
##########################################################


@dask.delayed
def convert_to_dd(data): # fix needed

    return dd.from_pandas(data, npartitions = 3) #make this dynamic later

@dask.delayed
def index_reset(data): # helper function

    return data.reset_index()

@dask.delayed
def fill_dd(data,hist_dict,filter): # broken will try to fix later
   
    out = []

    column_list = list(data.partitions[0].columns)
    column_dict = {}

    for col in column_list:
        column_dict[col] = 'present'

    histograms_to_fill = []
    data_columns = []
    histograms_filled = []

    for col in hist_dict:
        if col in column_dict:
            temp = hist.Hist(hist_dict[col])
            histograms_to_fill.append(temp)
            data_columns.append(col)
            
        else:
            pass
            #flag a warning

    for partition in data.partitions:

        temp = partition.query(filter)

        for (histogram,data_column) in zip(histograms_to_fill,data_columns):
            histogram.fill(temp[data_column])
        
    histograms_filled = histograms_to_fill

    return histograms_filled


def fill_all_experimental(multiindex_data = True): # function to play around

    helper = sf.HistoMaker()

    client = helper.client_start(**hc.client_params)

    print(f'Client Dashboard: {client.dashboard_link}')

    out = []
    naming = []
    i = 0
    
    for S in hc.Samples:

        out.append([])
        naming.append((S.name,[]))
        j = 0

        for f in S.file_list:
            
            naming[i][1].append((f,[]))
            data = helper.load_h5(f)
            if not multiindex_data: # for testing
                data = index_reset(data)
                data = convert_to_dd(data)
            
            out[i].append([])
            k = 0
            
            for R in hc.Regions: 

                out[i][j].append([])
                naming[i][1][j][1].append((R.name,[]))

                for Sys in hc.Systematics:
                    
                    filtering = R.filter
                    #add systematic function join to get weights
                    if multiindex_data: # for testing for now helper.fill is the prefered method
                        temp = helper.fill(dask_query(data,filtering),hc.var_dict)
                    else:
                        temp = fill_dd(data,hc.var_dict,filtering)

                    naming[i][1][j][1][k][1].append(Sys.name)                    
                    out[i][j][k].append(temp)

                k = k + 1
            
            j = j + 1

        i = i + 1

