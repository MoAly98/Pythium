import os,sys
from utils.common.samples import *
from utils.common.branches import *
from utils.common.selection import *
from utils.common.user_tools import *
import numpy as np

general_settings = {}

general_settings['JobName'] = 'tHbb_boosted'
general_settings['OutDir'] = '/eos/user/k/kmalirz/test_data'
general_settings['SkipMissingFiles'] = True
general_settings['DumpToFormat'] = 'H5'

sample_dir = list(set(['/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v34_minintuples_v0/mc16a_nom/',
'/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v34_minintuples_v0/mc16d_nom/',
'/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v34_minintuples_v0/mc16e_nom/',
'/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v34_minintuples_v0/mc16a_syst/',
'/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v34_minintuples_v0/mc16d_syst/',
'/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v34_minintuples_v0/mc16e_syst/',
'/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v34_minintuples_v0/mc16a_syst/',
'/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v34_minintuples_v0/mc16d_syst/',
'/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v34_minintuples_v0/mc16e_syst/',
'/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v34_minintuples_v0/data_nom/',
'/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v34_minintuples_v0/data_nom/']))

xsec_file = "/afs/cern.ch/user/k/kmalirz/pythium/configs/XSection-MC15-13TeV.data"
nl = 'nominal_Loose'

def get_xsec(dsids, xsecs_file):
    with open(xsecs_file, "r") as f:
        lines = f.readlines()
    dsid = dsids[0]
    for line in lines:
        if "#" in line or not line.strip():
            continue
        line = line.split()
        if float(line[0]) != dsid: #dsid check
            continue
        xsec = float(line[1])
        kfact = float(line[2])
        break # only one dsid line per file 

    return xsec*kfact

def calc_nom_weights(weight_mc,weight_pileup, weight_bTagSF_DL1r_Continuous,weight_jvt,weight_forwardjvt,weight_leptonSF, runNumber):
    weight = (36207.66*(runNumber<290000.)+44307.4*((runNumber>=290000.) & (runNumber<310000.))+58450.1*(runNumber>=310000.))*weight_mc*weight_pileup*weight_bTagSF_DL1r_Continuous*weight_jvt*weight_forwardjvt*weight_leptonSF

    return weight

def calc_weights(nom_weights, xsec_weight, totalEventsWeighted):
    tow = np.sum(totalEventsWeighted)
    return nom_weights*xsec_weight[0]/tow

def jet4_pt(jet_pt):
    # jet_pt = [[pt1, pt2]_evt1, [pt3,pt4,pt5]_evt2, ....]
    # jet_pt[:,0] = [pt1_evt1, pt3_evt2, ....]
    # count_jagged(jet_pt) = [2,3,....]
    # count_jagged(jet_pt)>=4 = [False, True,...]
    # jet_pt[ [False, True,...] ] = [[pt3,pt4,pt5]_evt2, ...]
    return jet_pt[:,4]

def jet1p2_pt(jet_pt):
    jet_pt = mask(jet_pt, count_jagged(jet_pt)>=2)
    sum_j1j2_pt = jet_pt[:,0]+jet_pt[:,1]
    return sum_j1j2_pt

def deltaR(jets_phi, jets_eta):
    pass
def higgs_mass(jets_pt, jet_e):
    pass 

'''
safe way to filter while making new branches.  using user_tools mask! 
'''
nom_weight_branches = ['weight_mc','weight_pileup','weight_bTagSF_DL1r_Continuous','weight_jvt','weight_forwardjvt','weight_leptonSF','runNumber']

branches = {}
branches_temp = {}


branches["sumWeights"] = [Branch('TotalEventsWeighted','totalEventsWeighted',drop=True),
                          Branch('dsid','dsid', drop=True),
                          Branch('xsec_weight', get_xsec, args = ["dsid",xsec_file], args_types=[Branch, str]),]

# Add XbbScores, HFClassification 
branches[nl] = [
            
                Branch('bdt_0', lambda x: x[:,0], args = ["BDT"], args_types = [Branch]),
                Branch('njets', 'njets'),
                Branch('foam[1]', lambda x: x[:,1], args = ["foam"], args_types = [Branch])
                ]

branches_temp[nl] = [
                Branch('bdt_0', lambda x: x[:,0], args = ["BDT"], args_types = [Branch]), ##add foam and njest here,
                Branch('njets', 'njets'),
                Branch('foam[1]', lambda x: x[:,1], args = ["foam"], args_types = [Branch])
                ]

samples = [Sample(name = "ttb_PP8_AFII", tag = ['410470_AFII*'], 
                  where = sample_dir,branches = branches),
            Sample(name = "tH", tag = ['346676*'], 
                  where = sample_dir,branches = branches),
            Sample(name = "ttb", tag = ['410470_user*'], 
                  where = sample_dir,branches = branches),
            Sample(name = "Data", tag = ['data15*','data16*','data17*','data18*'], 
                  where = sample_dir,branches = branches_temp),
            Sample(name = "Fakes_Matrix", tag = ['data15*','data16*','data17*','data18*'], 
                  where = sample_dir,branches = branches_temp)        
          ]

