import utils.histogramming.storage_functions as sf
import configs.hist_vars as hist_vars
from utils.histogramming.cross_product_backend import XP_Sample, XP_Region, XP_Systematics, XP_Overall, XP_Histo
from hist.axis import Variable, Regular
from configs.sklim_config import samples as sklim_samples

var_dict = sf.combine_dicts([hist_vars.var_main, hist_vars.var_series, hist_vars.var_beta, 
                               hist_vars.var_ecf_beta, hist_vars.var_dichoric, hist_vars.var_ecfg])

observables = {'bdt_0' :            Regular(20, 0, 1, name='x', label=r'$p_{T}$[MeV]'  )}

client_params = {
    "n_workers" : 4,
    "memory_limit" : '5GB',
    "threads_per_worker" : 1
}

file_list = {
    "top_directory" : '/afs/cern.ch/user/k/kmalirz/pythium/temp/',
    "file_regex" : '(?=^[^.].)(.*gammajet_210921.*|.*15.*)(.*h5$)'
}

computation_params = {
    "chunk_size" : 100, 
    "histogram_variables" : var_dict
}

out_dir = '/tmp/kmalirz'

Samples_test = [
    XP_Sample(name = item.name, regex = True, top_directory = file_list['top_directory'], 
    file_regex = f'(.*{item.name}_chunk.*)(.*h5$)') for item in sklim_samples
] ## ignore for now

Samples_XP = [
    XP_Sample(name = 'ttb_PP8_AFII', regex = True, top_directory = file_list['top_directory'], 
    file_regex = '(.*ttb_PP8_AFII_chunk.*)(.*h5$)'),
    XP_Sample(name = 'tH', regex = True, top_directory = file_list['top_directory'], 
    file_regex = '(.*tH_chunk.*)(.*h5$)'),
    XP_Sample(name = 'ttb', regex = True, top_directory = file_list['top_directory'], 
    file_regex = '(.*ttb_chunk.*)(.*h5$)'),
    XP_Sample(name = 'Data', regex = True, top_directory = file_list['top_directory'], 
    file_regex = '(.*Data_chunk.*)(.*h5$)'),
    XP_Sample(name = 'Fakes_Matrix', regex = True, top_directory = file_list['top_directory'], 
    file_regex = '(.*Fakes_Matrix_chunk.*)(.*h5$)')
]

Regions = [ #write switch function
    XP_Region(name = 'high', filter = 'bdt_0 > 0.5'),
    XP_Region(name = 'low', filter = 'bdt_0 <= 0.5'),
    XP_Region(name = 'default', filter = 'bdt_0 >= 0')
]

def histo(data):

    weight = data['bdt_0']*1.5

    return weight

Systematics = [ #do weights systematic
    XP_Overall(name = 'test', Adjustment = 0.5),
    XP_Overall(name = 'another_test', Adjustment = 0),
    XP_Histo(name = 'ATLAS_PRW_DATASF', Formula = histo)
]

def functional_XP(sample,region,systematic):

    if region == 'default':

        skip = True
    
    else:

        skip = False

    return (None,None,None,skip) #return region_filter, sample_filter, systematic_weight, skip bool