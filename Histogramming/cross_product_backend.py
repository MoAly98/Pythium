import os
import sys
import dask
from distributed import Client
import numpy as np
import pandas as pd
import hist
import re
import subprocess



class XP_Sample:

    def __init__(self,**kwargs):

        self.file_list = kwargs.get('file_list',[])
        self.name = kwargs.get('name',None)

        if kwargs.get('regex') == True:
            
            self.file_list = create_file_list(top_directory = kwargs.get('top_directory',os.getcwd()),
            file_regex = kwargs.get('file_regex','(?=^[^.].)(.*pkl$)|(?=^[^.].)(.*h5$)'), dir_regex = kwargs.get('dir_regex','(?=^[^.].)'))


class XP_Region:

    def __init__(self,**kwargs):

        self.filter = kwargs.get('filter',None)
        self.name = kwargs.get('name',None)

class XP_Systematics:

    def __init__(self,**kwargs):

        self.name = kwargs.get('name',None)
        self.weighting = kwargs.get('weigth',1)


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