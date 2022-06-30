import os

import dask
from distributed import Client
import numpy as np
import pandas as pd
import hist
import re
import subprocess

import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from utils.common.samples import Sample


class XP_Sample:

    def __init__(self,**kwargs):

        self.file_list = kwargs.get('file_list',[])
        self.name = kwargs.get('name',None)
        self.top_directory = kwargs.get('top_directory',os.getcwd())
        self.sample_obj = kwargs.get('Sklim_Sample', None)
        self.file_regex = kwargs.get('file_regex','(?=^[^.].)(.*pkl$)|(?=^[^.].)(.*h5$)')

        if isinstance(kwargs.get('Sklim_Sample'), Sample):

            self.name = self.sample_obj.name
            self.regex = True
            self.file_regex = f'(.*{self.name}_chunk.*)(.*h5$)' 
            
        if kwargs.get('regex') == True or self.regex == True:
            
            self.file_list = create_file_list(top_directory = self.top_directory,
            file_regex = self.file_regex, dir_regex = kwargs.get('dir_regex','(?=^[^.].)'))

class XP_Region:

    def __init__(self,**kwargs):

        self.filter = kwargs.get('filter',None)
        self.name = kwargs.get('name',None)

class XP_Systematics: #base systematic class

    def __init__(self,**kwargs):

        self.name = kwargs.get('name',None)
        self.weighting = kwargs.get('weight',1)
        

    def output_weights(self,*args):

        return None

class XP_Overall(XP_Systematics): 

    def __init__(self,**kwargs):

        super().__init__(**kwargs)

        self.change = kwargs.get('Adjustment', 0)
        self.Excludes = kwargs.get('Excludes', '')
    
    def output_weights(self,column_data):

        weights = np.ones(len(column_data))*(1+float(self.change))
        return weights

class XP_Formula(XP_Systematics):

    def __init__(self,**kwargs):

        super().__init__(**kwargs)

        self.formula = kwargs.get('Formula') #pass a lambda function with a dataframe as an input
        self.Excludes = kwargs.get('Excludes')

    def output_weights(self,column_data):

        weights = self.formula(column_data).to_numpy()

        return weights

class XP_Histo(XP_Systematics):

    def __init__(self,**kwargs):

        super().__init__(**kwargs)

        self.hist_to_subtract = kwargs.get('name_of_hist') # Named_hist class object


class Named_hists:

    def __init__(self,**kwargs):

        self.name = kwargs.get('name')
        self.sample = kwargs.get('sample')
        self.region = kwargs.get('region')
        self.systematic = kwargs.get('systematic')
        self.file = kwargs.get('file')
        self.systematic_object = kwargs.get('systematic_obj')

        

def create_file_list(top_directory = os.getcwd(),file_regex = '(?=^[^.].)(.*pkl$)|(?=^[^.].)(.*h5$)',dir_regex = '(?=^[^.].)'): 

        regex = re.compile(file_regex)
        dir_regex = re.compile(dir_regex)
        file_names = []
        #consider list comperhension for file loop
        for root, dirs, files in os.walk(top_directory,topdown = True):
            dirs[:] = [d for d in dirs if dir_regex.match(d)]
            for file in files:
                if regex.match(file):
                    file_names.append(root+file)

        return file_names

def get_XP_components(region_name: str,region_list,systematic_name: str, systematic_list, sample_name: str, sample_list):

    region_object = None
    systematic_object = None
    sample_object = None

    for region in region_list:

        if region.name == region_name:
            region_object = region

    for systematic in systematic_list:

        if systematic.name == systematic_name:
            systematic_object = systematic

    for sample in sample_list:

        if sample.name == sample_name:
            sample_object = sample

    return region_object, systematic_obj, sample_object