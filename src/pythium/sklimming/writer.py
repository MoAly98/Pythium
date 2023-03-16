'''
author: Mohamed Aly (maly@cern.ch)
Brief: Functions to take in awkward arrays and set them out to be dumped to various formats

The main way that is supported is saving to HDF5 files and ROOT files
'''
import awkward as ak
import h5py
from pathlib import Path
import numpy as np

def write_sample(sample_data, sample, cfg, ext='H5', suffix=''):
    sample_name = sample.name
    sample_sel = sample.selec
    if sample_sel is not None:
        sel_label = sample_sel.combined_label()
    else:
        sel_label = ''

    outdir = Path(cfg['settings']['outdir'])
    ext = cfg['settings']['dumptoformat']
    outdir.mkdir(parents=True, exist_ok=True)
    outfile =  f"{outdir}/{sample_name}{suffix}"
    if ext == 'h5':
        for tree, data in sample_data.items():
            outfile += f"__{tree}.h5"
            with h5py.File(outfile, "w") as file:
                packed_data = ak.packed(data)
                group = file.create_group(tree)
                form, length, container = ak.to_buffers(packed_data, container=group)
                group.attrs["form"] = form.tojson()
                group.attrs["length"] = length
                group.attrs["sel"] = "MySel"
            outfile = outfile.replace(f"__{tree}.h5", "")
    elif ext == 'root':
        pass
    elif ext == 'parquet':
        for tree, data in sample_data.items():
            outfile += f"__{tree}.parquet"
            data = data[~ak.is_none(data)]
            ak.to_parquet(data, outfile)
            outfile = outfile.replace(f"__{tree}.parquet", "")
    elif ext == "json":
        for tree, data in sample_data.items():
            outfile += f"__{tree}.json"
            ak.to_json(data, outfile)
            outfile = outfile.replace(f"__{tree}.json", "")

    return outfile
