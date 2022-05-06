import utils.histogramming.storage_functions as sf
import configs.hist_vars as hist_vars
from utils.histogramming.cross_product_backend import *
from hist.axis import Variable, Regular
from configs.sklim_config import samples as sklim_samples

simple_obs = sf.combine_dicts([hist_vars.var_main, hist_vars.var_series, hist_vars.var_beta, 
                               hist_vars.var_ecf_beta, hist_vars.var_dichoric, hist_vars.var_ecfg])

observables = {'bdt_0' :            Regular(20, 0, 1, name='x', label=r'$p_{T}$[MeV]'  )}


client_params = {
    "n_workers" : 7,
    "memory_limit" : '3GB',
    "threads_per_worker" : 1
}

file_list = {
    "top_directory" : '/eos/user/k/kmalirz/test_data/',
    "file_regex" : '(?=^[^.].)(.*gammajet_210921.*|.*15.*)(.*h5$)'
}

computation_params = {
    "chunk_size" : 100, 
    "histogram_variables" : simple_obs
}

out_dir = '/tmp/kmalirz'

## add additiona construcutro (overrride) for moes class
Samples_XP = [
    XP_Sample(Sklim_Sample = item, top_directory = file_list['top_directory']) for item in sklim_samples
] ## ignore for now


file_test = create_file_list(top_directory = '/eos/user/k/kmalirz/test_data/', file_regex = '(.*h5$)')

Samples_test_manual = [
]

Samples_test = [
    XP_Sample(name = 'ttb_PP8_AFII', regex = True, top_directory = file_list['top_directory'], 
    file_regex = '(.*ttb_PP8_AFII_chunk.*)(.*h5$)'),
    XP_Sample(name = 'tH', regex = True, top_directory = file_list['top_directory'], 
    file_regex = '(.*tH_chunk.*)(.*h5$)'),
    XP_Sample(name = 'ttb', regex = True, top_directory = file_list['top_directory'], 
    file_regex = '(.*ttb_chunk.*)(.*h5$)'),
    XP_Sample(name = 'Data', regex = True, top_directory = file_list['top_directory'], 
    file_regex = '(.*Data.*)(.*h5$)'),
    XP_Sample(name = 'Fakes_Matrix', regex = True, top_directory = file_list['top_directory'], 
    file_regex = '(.*Fakes_Matrix_chunk.*)(.*h5$)')
]

Regions = [ #write switch function
    XP_Region(name = 'high', filter = 'bdt_0 > 0.5'),
    XP_Region(name = 'low', filter = 'bdt_0 <= 0.5'),
    XP_Region(name = 'default', filter = 'bdt_0 >= 0')
]

# want user to do them in 
# define a weight varationa where my up histogram i 
# multipled by this column and my down would be multipled by another column
# like up = column and down = another column
def histo(data):

    weight = data['bdt_0']*1.5

    return weight

Systematics = [ #do weights systematic
    XP_Overall(name = 'test', Adjustment = 0.5),
    XP_Overall(name = 'another_test', Adjustment = 0),
    XP_Formula(name = 'ATLAS_PRW_DATASF', Formula = histo) #change the name to XP_Weight
]

def functional_XP(sample,region,systematic):

    if region == 'temp':

        skip = True
    
    else:

        skip = False

    return (None,None,None,skip) #return region_filter, sample_filter, systematic_weight, skip bool