from pydoc import importfile
import utils.histogramming.storage_functions as sf
from utils.histogramming.cross_product_backend import *
from utils.sklimming.config import validate_samples
from hist.axis import Variable, Regular

#TODO:
# add configs as argparser args in histogramming.py
# validate config objects

observables = {}
partons = ['top','tbar','higgs']
for ptag in partons:
    observables[ptag+'_pt'] = Regular(50, 0, 1000, name=ptag+'_pt', label=r'{} $pT$[GeV]'.format(ptag))
    observables[ptag+'_eta'] = Regular(20, -2.5, 2.5, name=ptag+'_eta', label=r'{} $\eta$[GeV]'.format(ptag))

client_params = {
    "n_workers" : 4,
    "memory_limit" : '5GB',
    "threads_per_worker" : 1
}

file_list = {
    "top_directory" : os.getcwd() + '/../PythiumTest1/',
    "file_regex" : '(?=^[^.].)(.*gammajet_210921.*|.*15.*)(.*h5$)'
}

computation_params = {
    "chunk_size" : 100, 
    "histogram_variables" : observables
}

out_dir = os.getcwd() + '/../PythiumTest2/output/'

sklim_config_path = 'configs/tth_config.py'

Samples_XP = []
sklim_module = importfile(sklim_config_path)
validate_samples(sklim_module)
sklim_samples = sklim_module.samples
for item in sklim_samples:
    Samples_XP.append(XP_Sample(name = item.name, regex=True, top_directory = file_list['top_directory'], file_regex = item.name+'_chunk0.h5')
)

Regions = [ #write switch function
    XP_Region(name = 'Inclusive', filter = 'higgs_pt>=0')
]

# want user to do them in 
# define a weight varationa where my up histogram i 
# multipled by this column and my down would be multipled by another column
# like up = column and down = another column
#def histo(data):
#    weight = data['bdt_0']*1.5
#    return weight

Systematics = [ #do weights systematic
    XP_Overall(name = 'Nominal', Adjustment = 0.)
    #XP_Overall(name = 'another_test', Adjustment = 0.5),
    #XP_Histo(name = 'ATLAS_PRW_DATASF', Formula = histo)
]

def functional_XP(sample,region,systematic):

    if region == 'default':
        skip = True
    else:
        skip = False
    return (None,None,None,skip) #return region_filter, sample_filter, systematic_weight, skip bool