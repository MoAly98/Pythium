import os
import dask
from distributed import Client
import numpy as np
import pandas as pd
import hist
import re
import subprocess

import sys
sys.path.append(os. getcwd()+'/Histogramming')

import hist_vars as hist_vars
import histogramming_config as hc
import storage_functions as sf

# for region:
#   for samples: (files of slimmed data)
#       for systematics: 
#           for observable:
#               fill

def fill_all():

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
            out[i].append([])
            k = 0

            for R in hc.Regions: 

                out[i][j].append([])
                naming[i][1][j][1].append((R.name,[]))

                for Sys in hc.Systematics:

                    naming[i][1][j][1][k][1].append(Sys.name)
                    filtering = R.filter
                    temp = helper.fill(data.query(filtering),hc.var_dict)
                    out[i][j][k].append(temp)

                k = k + 1
            
            j = j + 1

        i = i + 1

        
    #result = dask.compute(out)[0]


    return out, client, naming






