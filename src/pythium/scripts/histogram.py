#============== System and Python Imports
import os,sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
#============ Pythium Imports
import pythium.histogramming as hist
from pythium.common import tools
from pythium.common.logger import ColoredLogger
#=========== Pythonic Imports 
import numpy as np
import dask
from distributed import Client
import time
from argparse import ArgumentParser

#'/Users/moaly/Work/phd/pythium/Pythium/configs/StreamlineHistogrammingConfig.py'

_CFG_HELP = 'The full path to the configuration file to process'
_OUTDIR_HELP = 'Directory to save outputs'
_SAMPLES_HELP = 'Names of samples to keep'
_OBSERVABLES_HELP = 'Names of observables to keep'
_REGIONS_HELP = 'Names of regions to keep'
_SYSTEMATICS_HELP = 'Names of systematics to keep'
_EXCLUDE_HELP = 'Names of samples/regions/systematics to drop'
_SKLIM_HELP = 'Path to sklimming config to retrieve samples from'

def get_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-c', '--cfg', required=True, help=_CFG_HELP)
    parser.add_argument('-o', '--outdir',   nargs = '+',  help=_OUTDIR_HELP)
    parser.add_argument('--samples',        nargs = '+',  help=_SAMPLES_HELP)
    parser.add_argument('--observables',    nargs = '+',  help=_OBSERVABLES_HELP)
    parser.add_argument('--regions',        nargs = '+',  help=_REGIONS_HELP)
    parser.add_argument('--systematics',    nargs = '+',  help=_SYSTEMATICS_HELP)
    parser.add_argument('--exclude',        nargs = '+',  help=_EXCLUDE_HELP)
    parser.add_argument('--sklimconfig',                  help = _SKLIM_HELP)
    return parser.parse_args()

logger = ColoredLogger()

def main():
    args = get_args()
    cfg = hist.config.Config(args.cfg).process(args)
 
    if not cfg["general"]["dask"]:  scheduler = "synchronous" # Processes slower for 360histograms???
    else:
        cl = Client(**cfg["general"]["dasksettings"])
        logger.info(f'Client Dashboard: {cl.dashboard_link}')
        scheduler = cl

    procer = hist.processor.Processor(cfg, scheduler)
    procer.create()
    hists_dict = procer.run()
    procer.save(hists_dict)
    if isinstance(scheduler, Client):   cl.close()

if __name__ == '__main__':
    main()