'''
author: Mohamed Aly (maly@cern.ch)
Brief: This is the steering script for the sklimming code. It calls all necessary methods to parse a config
file, read a sample, then dump out the data to specified file format. 
'''

#============== System and Python Imports
import os,sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
#============ thbbanalysis Imports
import utils.sklimming as sklim
from utils.common import tools
#=========== Pythonic Imports 
import numpy as np
from argparse import ArgumentParser, ArgumentTypeError

_CFG_HELP = 'The full path to the configuration file to process'
_OUTDIR_HELP = 'Directory to save outputs'
_SKIP_MISS_HELP = 'Bool to determine if corrupt files should be skipped or break code'

def get_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-c', '--cfg', required=True, help=_CFG_HELP)
    parser.add_argument('-o', '--outdir', help=_OUTDIR_HELP)
    parser.add_argument('-s', '--skip-missing-files', help=_SKIP_MISS_HELP)
    return parser.parse_args()

def main():
    args = get_args() 
    cfg_path = args.cfg
    cfg = sklim.config.process(cfg_path)
    cfg = sklim.config.update(cfg, args)
    samples = []
    for sample_name, sample in cfg["samples"].items():
        sklim.reader.process_sample(sample, cfg)

if __name__ == '__main__':
    main()



