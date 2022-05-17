import os,sys
from random import sample
from utils.common.samples import *
from utils.common.branches import *
from utils.common.selection import *
from utils.common.user_tools import *
import numpy as np
import vector
import awkward as ak

vector.register_awkward()

tname = 'tth_observables'
general_settings = {}

Directory = os.getcwd() + '/../data/'
general_settings['JobName'] = ''
general_settings['OutDir'] = '../run/HC_LO_5FS_pp2x0ttx_ICvSM/'
general_settings['SkipMissingFiles'] = True
general_settings['DumpToFormat'] = 'H5'
general_settings['tree_name'] = tname

sample_path = 'HC_LO_no-b-mass_5FS_pp2x0ttx_QED_leq4_Khtt_eqp1/Events/run_01'
sample_name = 'TTH_IC'

branches = {}
parton_tags = ['top','tbar','higgs']
branchList = [Branch('evtWeight','evtWeight')]
for ptag in parton_tags:
      branchList.extend([
            Branch(ptag+'_p4', momentum_4d, args = [ptag+'_Px',ptag+'_Py',ptag+'_Pz',ptag+'_M'],
                        args_types=[Branch]*4,drop=True),
            Branch(ptag+'_eta','eta', args = [ptag+'_p4'],
                        args_types=[Branch],isprop=True),
            Branch(ptag+'_pt','pt', args = [ptag+'_p4'],
                        args_types=[Branch],isprop=True)
      ])
branchList.extend([
      Branch('ttbar_dphi',DeltaPhi, args = ['top_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('ttbar_deta',DeltaEta, args = ['top_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('ttbar_dR',DeltaR, args = ['top_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('ttbar_M',InvMass, args = ['top_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('htbar_dphi',DeltaPhi, args = ['higgs_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('htbar_deta',DeltaEta, args = ['higgs_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('htbar_dR',DeltaR, args = ['higgs_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('htbar_M',InvMass, args = ['higgs_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('ht_dphi',DeltaPhi, args = ['higgs_p4','top_p4'], args_types=[Branch,Branch]),
      Branch('ht_deta',DeltaEta, args = ['higgs_p4','top_p4'], args_types=[Branch,Branch]),
      Branch('ht_dR',DeltaR, args = ['higgs_p4','top_p4'], args_types=[Branch,Branch]),
      Branch('ht_M',InvMass, args = ['higgs_p4','top_p4'], args_types=[Branch,Branch]),
      Branch('httbar_M',InvMass, args = ['higgs_p4','top_p4','tbar_p4'], args_types=[Branch]*3)
])
branches[tname] = branchList

samples = [Sample(name = sample_name, tag = ['run_01_tree'], 
                  where = Directory + sample_path,branches = branches)]


#Legacy code. example for selection cuts
#def preselec(njets,nbjets,lep_tight, foam,taus_pt):
#    no_taus = (count_jagged(taus_pt,axis=1)==0)
#    preselection = (~((njets >= 5) & (nbjets >= 4)) & lep_tight & (foam==0.5) & no_taus)
#    return preselection
#presel_args = {tname: ['njets','nbjets','lep_tight','foam','taus_pt']}
#presl_cut_label = [r'!($N_{jets}\geq5 && N^{b}_{jets}\geq4$)',r'$N^{PLIVTight}_{lep}=1$',r'$N^{b@70}_{jets}\geq3',r'$E^{miss}_T\geq25$ GeV',r'$N_{\tau}=0$']
#Sample(name = "data", tag = ['data'], branches = data_branches,
#                  selec=Selection(preselec, presel_args,presl_cut_label) )  
        