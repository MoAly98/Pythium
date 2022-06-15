from collections import defaultdict
from itertools import chain
from operator import methodcaller
import h5py
import awkward as ak
import numpy as np
#import dask_awkward as dak
import types

def combine_list_of_dicts(list_of_dicts):
    # initialise defaultdict of lists
    dd = defaultdict(list)
    # iterate dictionary items
    dict_items = map(methodcaller('items'), list_of_dicts)
    for tree, df in chain.from_iterable(dict_items):
        dd[tree].append(df)
    return dd

def h5py_to_ak(infile, req_branches = None):
    with h5py.File(infile, "r") as file:
        if len(file.keys()) > 1:    raise IOError("H5 file Invalid as it contains more than one group (i.e. tree)") 
        tree = file[list(file.keys())[0]]
        
        data = ak.from_buffers(
                                ak.forms.Form.fromjson(tree.attrs["form"]),
                                tree.attrs["length"],
                                {k: np.asarray(v) for k, v in tree.items()},
                                )
        
        if req_branches is None:    req_branches = data.fields
        data = data[[f for f in req_branches]]
        cuts = tree.attrs["sel"]
    
    return data, cuts

def json_to_ak(infile, req_branches = None):
    data = ak.from_json(infile)           
    if req_branches is None:    req_branches = data.fields
    data = data[[f for f in req_branches]]
    return data, None

def parquet_to_ak(infile, req_branches = None):
    return ak.from_parquet(infile, lazy=True, columns = req_branches), None

def func_deepcopy(f, name=None):
    '''
    return a function with same code, globals, defaults, closure, and 
    name (or provide a new name)
    '''
    fn = types.FunctionType(f.__code__, f.__globals__, name or f.__name__,
        f.__defaults__, f.__closure__)
    # in case f was given attrs (note this dict is a shallow copy):
    fn.__dict__.update(f.__dict__) 
    return fn