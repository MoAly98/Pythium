#!/usr/bin/env python3
# Prototype config
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
sys.path.append(os.path.dirname(parentdir))
from sklimming.slimming_classes import Sample
from common.common_classes import Branch

common_branches = [
					Branch('leptons_pt', status='on', index_by='lep'),
					Branch('BDT', status='on', index_by='bdt'),
					Branch('jets_pt', status='on', index_by='jet'),
					Branch('weight_mc', status='on', index_by='event'),
					Branch('runNumber', status='on', index_by='event'),
				  ]

common_args = {
			'common_branches': {
								  'nominal_Loose':	common_branches,
								 },
			'where_ntuples_at':	 ['/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v31_minintuples_v3/mc16a_nom/'],
		}

ttbar_file = Sample('ttbar', ids=['410470_AFII_user.nbruscin.22889431._000017'], **common_args)

sample_list = [ttbar_file]


