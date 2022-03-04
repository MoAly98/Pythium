''' 
author: Mohamed Aly (maly@cern.ch)
Brief: Functions to take in awkward arrays and set them out to be dumped to various formats

The main way that is supported is saving to HDF5 files and ROOT files
'''
import awkward as ak
import h5py
from pathlib import Path

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
    if ext == 'H5':        
        outfile = f"{outdir}/{sample_name}{suffix}.h5"
        file = h5py.File(outfile, "w")
        sample_group = file.create_group(sample_name)
        sample_group.attrs["sel"] = sel_label
        for tree, data in sample_data.items():
            packed_data = ak.packed(data)
            group = sample_group.create_group(tree)
            form, length, container = ak.to_buffers(packed_data, container=group)
            group.attrs["form"] = form.tojson()
            group.attrs["length"] = length
    elif ext == 'root':
        pass 
    elif ext == 'parquet':
        # for tree, data in sample_data.items():
        #     print(tree, len(data))
        # out = ak.zip({tree: data for tree, data in sample_data.items()}, depth_limit=1)  
        # print(out)      
        # exit(0)
        pass
    
    return outfile
