from utils.histogramming.cross_product_backend import *
from utils.histogramming.config import get_sklim_samples
from hist.axis import Variable, Regular

#TODO:
#tree_name in histogramming config? (move from cross_product_functions l101)


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
    "top_directory" : os.getcwd() + '/../run/HC_LO_5FS_pp2x0ttx_ICvSM/',
    "file_regex" : '(?=^[^.].)(.*gammajet_210921.*|.*15.*)(.*h5$)'
}

computation_params = {
    "chunk_size" : 100, 
    "histogram_variables" : observables
}

out_dir = file_list["top_directory"] + 'output/'

sklim_config_path = 'configs/tth_ICvSM_config.py'

Samples_XP = get_sklim_samples(sklim_config_path, file_list['top_directory'])
#sklim_module = importfile(sklim_config_path)
#sklim.config.validate_samples(sklim_module)
#sklim_samples = sklim_module.samples
#for item in sklim_samples:
#    Samples_XP.append(XP_Sample(name = item.name, regex=True, top_directory = file_list['top_directory'], file_regex = item.name+'_chunk0.h5'))
#
Regions = [ #write switch function
    XP_Region(name = 'Inclusive', filter = 'higgs_pt>=0')
]

Systematics = [ #do weights systematic
    XP_Overall(name = 'Nominal', Adjustment = 0.)
    #XP_Overall(name = 'another_test', Adjustment = 0.5),
    #XP_Histo(name = 'ATLAS_PRW_DATASF', Formula = histo)
]

