#============== System and Python Imports
import os,sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
#============ thbbanalysis Imports
import utils.histogramming as hist
from utils.common import tools
#=========== Pythonic Imports 
import numpy as np
import dask
from distributed import Client
import time

cfg_path = '/Users/moaly/Work/phd/pythium/Pythium/configs/StreamlineHistogrammingConfig.py'

cfg = hist.config.Config(cfg_path).process()
if __name__ == '__main__':
    if not cfg["general"]["dask"]:
        #dask.config.set({"multiprocessing.context": "fork"})
        scheduler = "threads"
    else:
        client_params = {
                        "n_workers" : 7,
                        "memory_limit" : '3GB',
                        "threads_per_worker" : 1
                        }

        cl = Client(**client_params)
        print(f'Client Dashboard: {cl.dashboard_link}')
        scheduler = cl

    procer = hist.processor.Processor(cfg, scheduler)
    procer.create()
    hists_dict = procer.run()
    procer.save(hists_dict)
    if isinstance(scheduler, Client):
        cl.close()

