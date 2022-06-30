import os
from pydoc import importfile
import dask
from distributed import Client
import numpy as np
import pandas as pd
import hist
import re
import subprocess
import awkward as ak
import dask.dataframe as dd


import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import utils.histogramming.storage_functions as sf
import utils.histogramming.cross_product_backend as back
import utils.histogramming.config as config
from utils.common.tools import h5py_to_ak 

# for region:
#   for samples: (files of slimmed data)
#       for systematics: 
#           for observable:
#               fill

@dask.delayed # try to change to selective tree loading
def dask_load(data_name, sample_name, tree_name):

    data = h5py_to_ak(data_name)
    data = data[0][sample_name][tree_name]
    data = ak.to_pandas(data) #return dict 
    return data

@dask.delayed
def dask_query(data, filter):

    return data.query(filter)

@dask.delayed
def dask_fill(data,hist_dict,systematic_object: back.XP_Systematics):

    column_list = list(data.columns)
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
    
    for (histogram,data_column) in zip(histograms_to_fill,data_columns):
        histograms_filled.append(histogram.fill(data[data_column],weight = systematic_object.output_weights(data))) ## add a systematic here

    return histograms_filled


def get_functional_def(var, function_var):

    if function_var == None:

        return var
    
    else:

        return function_var

def fill_all(cfg):


    out = []
    out_linear = []
    naming = []
    naming_linear = []
    i = 0
    
    for S in cfg['samples']:

        out.append([])
        naming.append((S.name,[]))
        j = 0

        #print(S.file_list)
        for f in S.file_list:
            
            naming[i][1].append((f,[]))
            tname = importfile(cfg['sklim_config']).general_settings['tree_name']
            data = dask_load(f,S.name,tname)           
            out[i].append([])
            k = 0
            
            for R in cfg['regions']: 

                out[i][j].append([])
                naming[i][1][j][1].append((R.name,[]))

                for Sys in cfg['systematics']:
                    # add systematic data join
                    # if this systematic does not apply to a particular tree then skip
                    function_filter, sample_filter, systematic_weight, skip = config.functional_XP(S.name, R.name, Sys.name) # functional definition
                    
                    filtering = get_functional_def(R.filter,function_filter)


                    if skip:
                        
                        naming[i][1][j][1][k][1].append(Sys.name)                    
                        out[i][j][k].append(None)
                    
                    else:   
                        # implement systematics

                        temp = dask_fill(dask_query(data,filtering),cfg['observables'],Sys)

                        naming[i][1][j][1][k][1].append(Sys.name)                    
                        out[i][j][k].append(temp)

                        out_linear.append(temp)

                        name = back.Named_hists(name = 'x', sample = S.name, region = R.name, systematic = Sys.name, file = f, systematic_obj = Sys)

                        naming_linear.append(name)

                k = k + 1
            
            j = j + 1

        i = i + 1


    return out, naming, out_linear, naming_linear

def combine_samples(cfg,output,naming): #both need to be linear

    out = [] # list of samples that contains the rest of the junk
    dict_out = {}
    obs_list = list(cfg['observables'])
    
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

def substract_histograms(histograms, naming_list: back.Named_hists):

    for item in naming_list:

        if isinstance(item.systematic_object, back.XP_Histo):

            hist_name_obj = item.systematic_object.hist_to_subtract
            for observable in histograms[item.sample][item.region][item.systematic].keys():

                histograms[item.sample][item.region][item.systematic][observable] -=  histograms[hist_name_obj.sample][hist_name_obj.region][hist_name_obj.systematic][observable]
            
        else:

            pass


    return histograms

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


def fill_all_experimental(cfg, multiindex_data = True): # function to play around

    helper = sf.HistoMaker()

    client = helper.client_start(**cfg['client_params'])

    print(f'Client Dashboard: {client.dashboard_link}')

    out = []
    naming = []
    i = 0
    
    for S in cfg['samples']:

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
            
            for R in cfg['regions']: 

                out[i][j].append([])
                naming[i][1][j][1].append((R.name,[]))

                for Sys in cfg['systematics']:
                    
                    filtering = R.filter
                    #add systematic function join to get weights
                    if multiindex_data: # for testing for now helper.fill is the prefered method
                        temp = helper.fill(dask_query(data,filtering),cfg['observables'])
                    else:
                        temp = fill_dd(data,cfg['observables'],filtering)

                    naming[i][1][j][1][k][1].append(Sys.name)                    
                    out[i][j][k].append(temp)

                k = k + 1
            
            j = j + 1

        i = i + 1

