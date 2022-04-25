import os,sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import pickle
import configs.tth_histogramming_config as hf
import utils.histogramming.storage_functions as sf

def run():

    print('test')
    
    histogramming = sf.HistoMaker()

    client = histogramming.client_start(**hf.client_params)

    print(f'Client Dashboard: {client.dashboard_link}')

    x = histogramming.create_file_list(**hf.file_list)

    print (f"n_of_files = {len(x)}")

    histogramming.compute_histograms(**hf.computation_params)

    histograms_list, histograms_dict = histogramming.combine_histograms()

    print('histogram of rljet_pt_comb')
    print(histograms_dict['rljet_pt_comb'])

    for key in histograms_dict:

        with open(f"{hf.out_dir}/{key}_file.pkl", "wb") as f:
            pickle.dump(histograms_dict[key], f)

    print (f'files saved at {hf.out_dir}')

    print (f'read rljet_pt_comb')

    with open(f"{hf.out_dir}/rljet_pt_comb_file.pkl", "rb") as f:
        h1 = pickle.load(f)

    print (h1)

    return 0




if __name__ == '__main__':
    run()

