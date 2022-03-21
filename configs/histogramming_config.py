import utils.histogramming.storage_functions as sf
import configs.hist_vars as hist_vars
from utils.histogramming.cross_product_backend import XP_Sample, XP_Region, XP_Systematics


var_dict = sf.combine_dicts([hist_vars.var_main, hist_vars.var_series, hist_vars.var_beta, 
                               hist_vars.var_ecf_beta, hist_vars.var_dichoric, hist_vars.var_ecfg])

client_params = {
    "n_workers" : 4,
    "memory_limit" : '5GB',
    "threads_per_worker" : 1
}

file_list = {
    "top_directory" : '/eos/atlas/atlascerngroupdisk/perf-jets/JSS/WTopBackgroundSF2019/UFO_test/slimmed_SEP/',
    "file_regex" : '(?=^[^.].)(.*gammajet_210921.*|.*15.*)(.*h5$)'
}

computation_params = {
    "chunk_size" : 100, 
    "histogram_variables" : var_dict
}

out_dir = '/tmp/kmalirz'


Samples = [
    XP_Sample(regex = True, top_directory = file_list['top_directory'], 
    file_regex = '(?=^[^.].)(.*gammajet_210921.*)(.*15.*)(.*h5$)', name = 'test1'),
    XP_Sample(regex = True, top_directory = file_list['top_directory'], 
    file_regex = '(?=^[^.].)(.*gammajet_210921.*)(.*16.*)(.*h5$)', name = 'test2')
]

Regions = [ #write switch function
    XP_Region(name = 'high_pt', filter = 'rljet_pt_comb > 4*10**5'),
    XP_Region(name = 'low_pt', filter = 'rljet_pt_comb <= 4*10**5'),
    XP_Region(name = 'default', filter = 'rljet_pt_comb >= 0'),
    XP_Region(name = 'test1', filter = 'rljet_pt_comb >= 0'),
    XP_Region(name = 'test2', filter = 'rljet_pt_comb >= 10**5'),
    XP_Region(name = 'test3', filter = 'rljet_pt_comb >= 2*10**5'),
    XP_Region(name = 'test4', filter = 'rljet_pt_comb >= 20'),
    XP_Region(name = 'test5', filter = 'rljet_pt_comb >= 0')
]

Systematics = [ #do weights systematic
    XP_Systematics(name = 'test', weighting = 1)
]

def functional_XP(sample,region,systematic):

    if region == 'default':

        skip = True
    
    else:

        skip = False

    return (None,None,None,skip) #return region_filter, sample_filter, systematic_weight, skip bool