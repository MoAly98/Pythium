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
import configs.histogramming_config as hist_config
import configs.sklim_config as sklim_config

def run():

    helper = storage_functions.HistoMaker()

    print("Histomaker initialized")

    client = helper.client_start(**hist_config.client_params)

    print(f'Client Dashboard: {client.dashboard_link}')

    delayed_structure, names_structure, delayed_linear, names_linear = cross_product.fill_all()

    filled_histograms = dask.compute(delayed_linear)[0]

    named_filled_histograms = cross_product.combine_samples(filled_histograms,names_linear)

    for Sample in named_filled_histograms.keys():

        for Region in named_filled_histograms[Sample].keys():

            for Systematic in named_filled_histograms[Sample][Region].keys():

                for Observable in named_filled_histograms[Sample][Region][Systematic].keys():

                    histogram_to_save = named_filled_histograms[Sample][Region][Systematic][Observable]

                    with open(f"{hist_config.out_dir}/{Sample}_{Region}_{Systematic}_{Observable}_file.pkl", "wb") as f:
                            pickle.dump(histogram_to_save, f)
                
if __name__ == '__main__':
    run()