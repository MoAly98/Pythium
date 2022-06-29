# from utils.histogramming.cross_product_backend import *
# from utils.histogramming.config import get_sklim_samples
# from hist.axis import Variable, Regular

from utils.histogramming.objects import Region, Observable, RegBin, VarBin, NTupSyst, TreeSyst, WeightSyst
from utils.common.selection import Selection

# ===========================================
# ================= Settings ================
# ===========================================
general = {}
general['OutDir'] = '/Users/moaly/Work/phd/pythium/Pythium/tests/histogramming/histograms_nonsync/'
general['inDir']  = "/Users/moaly/Work/phd/pythium/Pythium/tests/sklimming/"
general['inFormat']  = 'parquet'
general['FromPythium']  = True
general['dask']  = True
general['view']  = False
# ===========================================
# ================= Samples =================
# ===========================================
from configs.tth_ICvSM_config import samples
# user might want to specify samples that are data using [s.isdata = True for s in samples if s.name == 'pain']
# ===========================================
# =============== Observables ===============
# ===========================================
observables = []
partons = ['top','tbar','higgs']
for ptag in partons:
    pt = Observable( var = ptag+'_pt', name = ptag+'_pt', 
                     binning = RegBin(low=0, high=1000, nbins = 50), 
                     dataset = 'tth_observables',label = rf'{ptag} $p_T$[GeV]')
    eta = Observable( ptag+'_eta', ptag+'_eta', 
                      binning = RegBin(low=-2.5, high=2.5, nbins = 20), 
                      dataset = 'tth_observables', label = rf'{ptag} $\eta$[GeV]')

    pt_eta = Observable( [ptag+'_pt', ptag+'_eta'], ptag+'_pt_eta', 
                         binning = [RegBin(low=0, high=1000, nbins = 50), RegBin(low=-2.7, high=2.7, nbins = 25, axis= 1)], 
                         dataset = 'tth_observables' , label = rf'{ptag} $\eta$-$p_T$[GeV]')

    pt_sq = Observable.fromFunc( ptag+'_pt_sq',
                                 lambda pt: pt**2, args = [ptag+'_pt'],  
                                 binning = RegBin(low=0, high=10000, nbins = 50), 
                                 dataset = 'tth_observables', label = rf'{ptag} $\p^2_T$[GeV]')
    pt_cube = Observable.fromStr( ptag+'_pt_cub',
                                f'{ptag}_pt**3',
                                 binning = RegBin(low=0, high=100000, nbins = 50), 
                                 dataset = 'tth_observables', label = rf'{ptag} $\p^2_T$[GeV]')                                     
    observables.extend([pt, eta, pt_sq, pt_cube, pt_eta])

# ===========================================
# ================= Regions =================
# ===========================================
inclusive = Selection(lambda h_pt: h_pt>=0, args = ['higgs_pt'], )
signal_region = Selection(lambda h_pt: h_pt>=10, args = ['higgs_pt'], )
control_region = Selection.fromStr('higgs_pt>100' )

regions = [
            Region(name = 'Inclusive', selection = inclusive),
            Region(name = 'SR', selection = signal_region),
            Region(name = 'CR', selection = control_region),
          ]

# Allow systematic up/down to take a function or string computation with overrides of __init__. 
systematics = [
                TreeSyst("FakeTreeVar", 'shapenorm', up = 'treevar_UP', down = 'treevar_DOWN', ), 
                NTupSyst("FakeNTupVar", 'shapenorm', up = 'alt_sample', 
                        where = "/Users/moaly/Work/phd/pythium/Pythium/tests/sklimming/", 
                        symmetrize= True),
                WeightSyst.fromFunc("FakeWeightVarFromFunc", 'shapenorm', 
                                    up = dict(func=lambda x,y : x/y, args = ['higgs_pt','top_pt']), 
                                    down = dict(func=lambda x,y : y/x, args = ['higgs_pt','top_pt']),
                                    ),#exclude_observables = ['.*_pt_eta']),
                WeightSyst.fromStr("FakeWeightVarFromStr", 'shapenorm', up = 'higgs_pt/top_pt', down = 'top_pt/higgs_pt')#,exclude_observables = ['.*_pt_eta']),
                ]

# observables = {}
# partons = ['top','tbar','higgs']
# for ptag in partons:
#     observables[ptag+'_pt'] = Regular(50, 0, 1000, name=ptag+'_pt', label=r'{} $pT$[GeV]'.format(ptag))
#     observables[ptag+'_eta'] = Regular(20, -2.5, 2.5, name=ptag+'_eta', label=r'{} $\eta$[GeV]'.format(ptag))

# client_params = {
#     "n_workers" : 4,
#     "memory_limit" : '5GB',
#     "threads_per_worker" : 1
# }

# file_list = {
#     "top_directory" : os.getcwd() + '/../run/HC_LO_5FS_pp2x0ttx_ICvSM/',
#     "file_regex" : '(?=^[^.].)(.*gammajet_210921.*|.*15.*)(.*h5$)'
# }

# computation_params = {
#     "chunk_size" : 100, 
#     "histogram_variables" : observables
# }

# out_dir = file_list["top_directory"] + 'output/'




# Regions = [ #write switch function
#     XP_Region(name = 'Inclusive', filter = 'higgs_pt>=0')
# ]

# Systematics = [ #do weights systematic
#     XP_Overall(name = 'Nominal', Adjustment = 0.)
#     #XP_Overall(name = 'another_test', Adjustment = 0.5),
#     #XP_Histo(name = 'ATLAS_PRW_DATASF', Formula = histo)
# ]

