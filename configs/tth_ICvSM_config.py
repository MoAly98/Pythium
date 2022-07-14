import os,sys
from random import sample
from pythium.common.samples import *
from pythium.common.branches import *
from pythium.common.selection import *
from pythium.common.user_tools import *
import numpy as np
import vector
import awkward as ak

vector.register_awkward()

tname = 'tth_observables'
general_settings = {}

general_settings['JobName'] = ''
general_settings['OutDir'] = '/Users/moaly/Work/phd/pythium/Pythium/tests/sklimming/'
general_settings['SkipMissingFiles'] = True
general_settings['DumpToFormat'] = 'parquet'

sample_path = '/Users/moaly/Work/phd/pythium/Pythium/tests/sklimming/'
sample_name = 'TTH_ICt'

branches = {}
parton_tags = ['top','tbar','higgs']
branchList = [Branch('evtWeight','evtWeight')]
for ptag in parton_tags:
      branchList.extend([
            Branch(ptag+'_p4', momentum_4d, args = [ptag+'_Px',ptag+'_Py',ptag+'_Pz',ptag+'_M'], args_types=[Branch]*4,drop=True),
            Branch(ptag+'_eta','eta', args = [ptag+'_p4'], args_types=[Branch],isprop=True),
            Branch(ptag+'_pt','pt', args = [ptag+'_p4'], args_types=[Branch],isprop=True)
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
                  where = sample_path,branches = branches)]

