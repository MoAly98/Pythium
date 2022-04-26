import os,sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import pickle
import utils.histogramming.storage_functions as sf
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
    hc = config.process(cfg_path)
    hc = config.update(hc, args)
    
    histogramming = sf.HistoMaker()

    client = histogramming.client_start(**hc['client_params'])

    print(f'Client Dashboard: {client.dashboard_link}')

    x = histogramming.create_file_list(**hc['file_list'])

    print (f"n_of_files = {len(x)}")

    histogramming.compute_histograms(**hc['computation_params'])

    histograms_list, histograms_dict = histogramming.combine_histograms()

    print('histogram of rljet_pt_comb')
    print(histograms_dict['rljet_pt_comb'])

    outdir = hc['out_dir']

    for key in histograms_dict:

        with open(f"{outdir}/{key}_file.pkl", "wb") as f:
            pickle.dump(histograms_dict[key], f)

    print (f'files saved at {outdir}')

    print (f'read rljet_pt_comb')

    with open(f"{outdir}/rljet_pt_comb_file.pkl", "rb") as f:
        h1 = pickle.load(f)

    print (h1)

    return 0




if __name__ == '__main__':
    run()

