from collections import defaultdict
from itertools import chain
from operator import methodcaller
import h5py
import awkward as ak
import numpy as np

def combine_list_of_dicts(list_of_dicts):
    # initialise defaultdict of lists
    dd = defaultdict(list)
    # iterate dictionary items
    dict_items = map(methodcaller('items'), list_of_dicts)
    for tree, df in chain.from_iterable(dict_items):
        dd[tree].append(df)
    return dd

def h5py_to_ak(infile):
    file = h5py.File(infile, "r")
    final_data = {}
    cuts = {}
    for sample_name, sample_group in file.items():
        final_data[sample_name] = {}
        try:
            sel = sample_group.attrs['sel']
        except KeyError:
            sel = None
        for tree_name, group in sample_group.items():
            data = ak.from_buffers(
                                    ak.forms.Form.fromjson(group.attrs["form"]),
                                    group.attrs["length"],
                                    {k: np.asarray(v) for k, v in group.items()},
                                )
            final_data[sample_name][tree_name] = data
        cuts[sample_name] = sel
    file.close()
    return final_data, cuts
