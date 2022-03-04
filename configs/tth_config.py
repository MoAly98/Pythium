import os,sys
from utils.common.samples import *
from utils.common.branches import *
from utils.common.selection import *
from utils.common.user_tools import *
import numpy as np
import misc.lorentz_functions as VF
import vector
import awkward as ak

vector.register_awkward()

tname = 'nominal_Loose'
general_settings = {}

Directory = os.getcwd() + '../data/DIM6TOP_LO_tth_SM_2021-12-16'
general_settings['JobName'] = ''
general_settings['OutDir'] = Directory + '/Events/run_01/'
general_settings['SkipMissingFiles'] = True
general_settings['DumpToFormat'] = 'H5'

sample_dir = [Directory + '/Events/run_0{}/'.format(i) for i in range(1,9)]
sample_dir.extend([Directory + '/Events/run_{}/'.format(i) for i in range(10,12)])
      
branches = {}
parton_tags = ['top','tbar','higgs']
branchList = [Branch('evtWeight','evtWeight')]
for ptag in parton_tags:
      branchList.extend([
            #Branch(ptag+'_Px',ptag+'_Px'),
            #Branch(ptag+'_Py',ptag+'_Pz'),
            #Branch(ptag+'_Pz',ptag+'_Py'),
            #Branch(ptag+'_E', ptag+'_E'),
            Branch(ptag+'_p4', VF.Vector4D, args = [ptag+'_Px',ptag+'_Py',ptag+'_Pz',ptag+'_E'],
                        args_types=[Branch,Branch,Branch,Branch],drop=True),
            Branch(ptag+'_eta',VF.Eta, args = [ptag+'_p4'],
                        args_types=[Branch]),
            Branch(ptag+'_pt',VF.Pt, args = [ptag+'_p4'],
                        args_types=[Branch])
      ])
branchList.extend([
      Branch('ttbar_dphi',VF.DeltaPhi, args = ['top_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('ttbar_deta',VF.DeltaEta, args = ['top_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('ttbar_dR',VF.DeltaR, args = ['top_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('ttbar_M',VF.InvMass, args = ['top_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('htbar_dphi',VF.DeltaPhi, args = ['higgs_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('htbar_deta',VF.DeltaEta, args = ['higgs_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('htbar_dR',VF.DeltaR, args = ['higgs_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('htbar_M',VF.InvMass, args = ['higgs_p4','tbar_p4'], args_types=[Branch,Branch]),
      Branch('ht_dphi',VF.DeltaPhi, args = ['higgs_p4','top_p4'], args_types=[Branch,Branch]),
      Branch('ht_deta',VF.DeltaEta, args = ['higgs_p4','top_p4'], args_types=[Branch,Branch]),
      Branch('ht_dR',VF.DeltaR, args = ['higgs_p4','top_p4'], args_types=[Branch,Branch]),
      Branch('ht_M',VF.InvMass, args = ['higgs_p4','top_p4'], args_types=[Branch,Branch]),
      Branch('httbar_M',VF.InvMass, args = ['higgs_p4','top_p4','tbar_p4'], args_types=[Branch,Branch,Branch])
])
branches[tname] = branchList

#Dictionary for sample names : directories?

samples = [Sample(name = "ttb", tag = ['410470_user'], 
                  where = sample_dir,branches = branches),
            Sample(name = "ttc", tag = ['410470_user'], 
                  where = sample_dir,branches = branches),
            Sample(name = "ttlight", tag = ['410470_user'], 
                  where = sample_dir,branches = branches),   
            Sample(name = "sgtop_Wtchan", tag = ['410646_user', '410647_user'], 
                  where = sample_dir,branches = branches),
            Sample(name = "sgtop_Wtchan", tag = ['410658_user', '410659_user'], 
                  where = sample_dir,branches = branches)
            ]

#Legacy code. example for selection cuts
#def preselec(njets,nbjets,lep_tight, foam,taus_pt):
#    no_taus = (count_jagged(taus_pt,axis=1)==0)
#    preselection = (~((njets >= 5) & (nbjets >= 4)) & lep_tight & (foam==0.5) & no_taus)
#    return preselection
#presel_args = {tname: ['njets','nbjets','lep_tight','foam','taus_pt']}
#presl_cut_label = [r'!($N_{jets}\geq5 && N^{b}_{jets}\geq4$)',r'$N^{PLIVTight}_{lep}=1$',r'$N^{b@70}_{jets}\geq3',r'$E^{miss}_T\geq25$ GeV',r'$N_{\tau}=0$']
#Sample(name = "data", tag = ['data'], branches = data_branches,
#                  selec=Selection(preselec, presel_args,presl_cut_label) )  
        