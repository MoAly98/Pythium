import sys, os
import time
import dask
import pickle

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import utils.histogramming.cross_product_functions as cross_product
import utils.histogramming.cross_product_backend as backend
import utils.histogramming.storage_functions as storage_functions
import utils.histogramming.config as config
from argparse import ArgumentParser

_CFG_HELP = 'The full path to the histogramming configuration file'
_OUTDIR_HELP = 'Directory to save outputs'
_SKCFG_HELP = 'The full path to the sklimming configuration file'

def get_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-c','--cfg', required=True, help=_CFG_HELP)
    parser.add_argument('-sc','--skcfg', help=_SKCFG_HELP)
    parser.add_argument('-o', '--outdir', help=_OUTDIR_HELP)
    return parser.parse_args()

def run():

    args = get_args() 
    cfg_path = args.cfg
    hist_config = config.process(cfg_path,args.skcfg)
    hist_config = config.update(hist_config, args)
    helper = storage_functions.HistoMaker()
    print(hist_config)

    print("Histomaker initialized")

    client = helper.client_start(**hist_config['client_params'])

    print(f'Client Dashboard: {client.dashboard_link}')

    delayed_structure, names_structure, delayed_linear, names_linear = cross_product.fill_all(hist_config)

    filled_histograms = dask.compute(delayed_linear)[0]

    named_filled_histograms = cross_product.combine_samples(hist_config,filled_histograms,names_linear)
    
    # histo subtraction part of the process 
## combine files per observable in dict
## use /eos/user/m/maly
## jk dev check it out
    hist_save_dict = {}

    for Sample in named_filled_histograms.keys():

        for Region in named_filled_histograms[Sample].keys():

            for Systematic in named_filled_histograms[Sample][Region].keys():

                for Observable in named_filled_histograms[Sample][Region][Systematic].keys():

                    if hist_save_dict.get(Observable) == None:

                        hist_save_dict[Observable] = {}

                    histogram_to_save = named_filled_histograms[Sample][Region][Systematic][Observable]

                    hist_save_dict[Observable][f'{Sample}_{Region}_{Systematic}'] = histogram_to_save


    for obs in hist_save_dict.keys():

        with open(f"{hist_config['out_dir']}/{obs}_file.pkl", "wb") as f:
            pickle.dump(hist_save_dict[obs], f)

                
if __name__ == '__main__':
    run()