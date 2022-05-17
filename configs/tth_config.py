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

def TTHVars(p1,p2,beta=None):
    qp1 = Unit3(ProtonP4(True,beta))
    qp2 = Unit3(ProtonP4(False,beta))
    if beta:
        p1 = p1.boost(beta)
        p2 = p2.boost(beta)
    q1 = Unit3(p1)
    q2 = Unit3(p2)

    b1 = Cos(q1.cross(qp1),q2.cross(qp1))
    b2 = (q1.Cross(qp1)).dot(q2.cross(qp1))
    b3x = q1.x*q2.x/(abs(q1.cross(qp1)*abs(q2.cross(qp2))))
    b4 = (q1.dot(qp1))*(q2.dot(qp2))
    b5 = TripleProd(qp1,q1,q2)
    b6 = TripleProd(qp1,q1,q2)/(abs(q1.cross(qp1))*abs(q2.cross(qp2)))
    b7 = TripleProd(qp1,q1,q2)/abs(q1.cross(q2))
    b8 = (qp1.Cross(qp2)).dot(p1.Cross(p2))
    return (b1,b2,b3x,b4,b5,b6,b7,b8)

def PhiC(p1,p2,pH):
    beta = BetaV3(pH)
    qp1 = Unit3(ProtonP4(True,beta))
    qp2 = Unit3(ProtonP4(False,beta))
    p1 = p1.boost(beta)
    p2 = p2.boost(beta)
    q1 = Unit3(p1)
    q2 = Unit3(p2)
    return np.arccos(Cos(q1.Cross(q2),qp1.Cross(qp2)))/np.pi


tname = 'tth_observables'
general_settings = {}

Directory = os.getcwd() + '/../data/'
general_settings['JobName'] = ''
general_settings['OutDir'] = '../PythiumTest1/'
general_settings['SkipMissingFiles'] = True
general_settings['DumpToFormat'] = 'H5'
general_settings['tree_name'] = tname

sample_SM = 'DIM6TOP_LO_tth_SM_2021-12-16/Events/run_01'
sample_runs = {
    'ctp'    : 'run_01',
    'ctpI'   : 'run_02',
    'ctG'    : 'run_03',
    'ctGI'   : 'run_04',
    'ctW'    : 'run_05',
    'ctWI'   : 'run_06',
    'ctZ'    : 'run_07',
    'ctZI'   : 'run_08',
    'cpQM'   : 'run_10',
    'cpt'    : 'run_11'
}

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

samples = [Sample(name = "TTH_SM", tag = ['run_01_tree'], 
                  where = Directory + 'DIM6TOP_LO_tth_SM_2021-12-16/Events/run_01',branches = branches)]

for param, run in sample_runs.items():
    samples.append(Sample(name = "TTH_INT_"+param, 
                  tag = [run+'_tree'],
                  where = Directory + 'DIM6TOP_LO_tth_dim6_eq1_dim6sqr_eq1_2022-02-16/Events/'+run,
                  branches = branches)
                )
    samples.append(Sample(name = "TTH_SQR_"+param, 
                  tag = [run+'_tree'],
                  where = Directory + 'DIM6TOP_LO_tth_dim6_eq1_dim6sqr_eq2_2022-02-16/Events/'+run,
                  branches = branches)
                )

#Legacy code. example for selection cuts
#def preselec(njets,nbjets,lep_tight, foam,taus_pt):
#    no_taus = (count_jagged(taus_pt,axis=1)==0)
#    preselection = (~((njets >= 5) & (nbjets >= 4)) & lep_tight & (foam==0.5) & no_taus)
#    return preselection
#presel_args = {tname: ['njets','nbjets','lep_tight','foam','taus_pt']}
#presl_cut_label = [r'!($N_{jets}\geq5 && N^{b}_{jets}\geq4$)',r'$N^{PLIVTight}_{lep}=1$',r'$N^{b@70}_{jets}\geq3',r'$E^{miss}_T\geq25$ GeV',r'$N_{\tau}=0$']
#Sample(name = "data", tag = ['data'], branches = data_branches,
#                  selec=Selection(preselec, presel_args,presl_cut_label) )  
        