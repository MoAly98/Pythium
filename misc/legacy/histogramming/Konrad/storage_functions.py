import os
import sys
import dask
from distributed import Client
import numpy as np
import pandas as pd
import hist
import re
import subprocess


class HistoMaker:
    """
    A class used as an interface to create histograms from pkl or hdf files
    ...

    Attributes
    ----------
    file_list : List[str]
        a list of full paths to files.

    client_params : dict
        parameters passed to the Dask client.

    worker_number : int
        number of worker nodes running.

    histograms_computed : List[List[Hist]]
        list of lists of hist objects such that histograms_computed[n].
        returns nth file that contains a number of hist objects such that, 
        histograms_computed[n][i] returns ith histogram.

    histogram_variables : dict
        dictionary that contains hist vars. Each key corresponds to column name 
        and each value contains hist object params for example
        'rljet_m_comb[:,0]' : Regular(20, 50e3, 500e3,  name='x', label='m [MeV]').

    Methods
    -------
    __init__(self,**kwargs)
        initialise the class and saves any passed arguments.

    create_file_list(top_directory = os.getcwd(),file_regex = '(?=^[^.].)(.*pkl$)|(?=^[^.].)(.*h5$)',dir_regex = '(?=^[^.].)',**kwargs))
        creates a list of files in directories under root directory that match regex strings.

    client_start(self,**kwargs)
        starts a Dask client with client parameters passed to this function or during init.

    load_h5(self,file_path)
        load and return hdf file as Dask.delayed object.

    load_pkl(self,file_path)
        load and return pickle file as Dask.delayed object.

    fill(self,data,hist_dict)
        fills a histogram for each column present in the histogram_variables dictionary 
        returns a list of Dask.delayed objects when computed these objects are hists.

    load_and_fill(self,file_list = [],**kwargs)
        combines load and fill to load and fill histograms for each file in the list
        returns a list of Dask.delayed objets.

    compute_histograms(self,chunk_size = 8,file_list = [],**kwargs)
        computes load_and_fill in chunks specified by chunk size
        divides file list into chunks and feeds them to load_and_fill. 
        it then executes Dask.compute on the batch and appends the results
        to histograms_computed. Once finished with all batches, it returns histograms_computed.
    """

    def __init__(self,**kwargs):
        """
        initializes the class and saves any input arguments

        Arguments
        -------
        **kwargs :
            keyword arguments

        Return
        -------
        None
        """
        
        self.file_list = kwargs.get('file_list',None)
        self.client_params = kwargs.get('client_params',{})
        self.worker_number = 1 # default
        self.histograms_computed = [] 
        self.histogram_variables = kwargs.get('histogram_variables',{})
        self.histograms_combined = {}
        
        

    def create_file_list(self,top_directory = os.getcwd(),file_regex = '(?=^[^.].)(.*pkl$)|(?=^[^.].)(.*h5$)',dir_regex = '(?=^[^.].)',**kwargs): 
        """
        creates a list of files in directories under root directory that match regex strings.

        Arguments
        -------
        top_directory : 
            directory from which user wants to start searching for files that match the pattern.
        
        file_regex :
            regex string used to match file names and their relative directory

        dir_regex : 
            regex string used to match directories with.

        **kwargs :
            keyword arguments

        Return
        -------
        List of full file paths
        """
        regex = re.compile(file_regex)
        dir_regex = re.compile(dir_regex)
        file_names = []
        #consider list comperhension for file loop
        for root, dirs, files in os.walk(top_directory,topdown = True):
            dirs[:] = [d for d in dirs if dir_regex.match(d)]
            for file in files:
                if regex.match(file):
                    file_names.append(root+file)

        self.file_list = file_names

        return file_names
    # error validation
    def client_start(self,**kwargs):
        """
        starts a Dask Client

        Arguments
        -------
        **kwargs :
            keyword arguments

        Return
        -------
        Client handler/object
        """
        for key in kwargs:
            if self.client_params.get(key) != kwargs[key]:
                self.client_params[key] = kwargs[key]

        cl = Client(**self.client_params)
        self.worker_number = len(cl.scheduler_info()['workers'])
        
        return cl
   
    @dask.delayed
    def load_h5(self,file_path):
        """
        loads data from hdf file

        Arguments
        -------
        file_path :
            full file path

        Return
        -------
        Pandas DataFrame object (delayed)
        """
        temp = pd.read_hdf(file_path)
        return temp
    
    @dask.delayed
    def load_pkl(self,file_path):
        """
        loads data from pickle file

        Arguments
        -------
        file_path :
            full file path

        Return
        -------
        Pandas DataFrame object (delayed)
        """
        temp = pd.read_pickle(file_path)
        return temp
    
    @dask.delayed
    def fill(self,data,hist_dict):
        """
        fills histograms with data from input DataFrame

        Arguments
        -------
        data :
            Pandas/Dask DataFrame
        
        hist_dict : 
            dictionary that contains hist vars. Each key corresponds to column name 
            and each value contains hist object params for example
            'rljet_m_comb[:,0]' : Regular(20, 50e3, 500e3,  name='x', label='m [MeV]').

        Return
        -------
        List of histogram objects (delayed)
        """
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
            histograms_filled.append(histogram.fill(data[data_column]))

        return histograms_filled
    
    def load_and_fill(self,file_list = [],**kwargs):
        """
        combines load and fill for a list of files

        Arguments
        -------
        file_list :
            list of files to load and fill 
        
        **kwargs : 
            keyword arguments

        Return
        -------
        List of delayed objects that contain load and fill functions
        """
        results = []
        for f in file_list:
            
            filename, file_extension = os.path.splitext(f)
            # chnage this to something better
            if file_extension == '.h5':
                data = self.load_h5(f)
            else:
                data = self.load_pkl(f)
            
            result = self.fill(data,self.histogram_variables)
            results.append(result)
                
        return results
    
    def compute_histograms(self,chunk_size = 8,file_list = [],**kwargs):
        """
        computes delayed objects in chunks and appends them to the histograms_computed variable

        Arguments
        -------
        chunk_size : 
            number of files to be loaded and filled in one batch

        file_list :
            list of files to load and fill 
        
        **kwargs : 
            keyword arguments

        Return
        -------
        list of lists of hist objects such that histograms_computed[n]
        returns nth file that contains a number of hist objects such that, 
        histograms_computed[n][i] returns ith histogram.
        """
        self.histograms_computed = []
        output = []

        if file_list == []: file_list = self.file_list
        if kwargs.get('histogram_variables') != None: self.histogram_variables = kwargs.get('histogram_variables')
        
        for i in range(int(len(file_list)/chunk_size)+1):
            if i == int(len(file_list)/chunk_size):
                file_chunk = file_list[(i+1)*chunk_size-1:]
            else:
                file_chunk = file_list[i*chunk_size:(i+1)*chunk_size-1]

            histogram_chunk = dask.compute(self.load_and_fill(file_list = file_chunk))
            
            for item in histogram_chunk[0]: #each item contains list of hist objects
                #we can create histogram wrapper objects here and add newly computed histograms here
                output.append(item)   

        self.histograms_computed = output

        return output

    def combine_histograms(self):

        combined_hists = self.histograms_computed[0]
        temp = {}

        for i in range(1,len(self.histograms_computed)):
            for j in range(0,len(self.histograms_computed[i])):

                combined_hists[j] = combined_hists[j] + self.histograms_computed[i][j]

        i = 0
        # change that later to something less error prone
        for key in self.histogram_variables:

            temp[key] = combined_hists[i]
            
            i = i + 1

        self.histograms_combined = temp

        return combined_hists, temp
    

def combine_dicts(dict_list):
    """
    combine dictionaries

    Arguments
    -------
    dict_list : 
        list of dictionaries to combine

    Return
    -------
    combined dictionary
    """
    out = {}
    for dictionary in dict_list:
        for key in dictionary:
            out[key] = dictionary[key]

    return out



