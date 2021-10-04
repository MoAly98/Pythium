# Prototype config
from slimming_classes import Sample
from common_classes import Branch


common_branches = [
					# First index should always be the event
					# Branch('*jets*', status='off'),
					# Branch('BDT', status='off'),
					# Branch('*tau*', status='off'),
					# Branch('*moment*', status='off'),
					# Branch('*leptons*', status='off'),
					# Branch('*BDT*', status='off'),
					Branch('jets_eta', status='on', index_by='jet'),
					# # Branch('bdt_tH', expression = BDT[:,0], status='on', index_by='event'),
					# Branch('dummy', expression='weight_mc*runNumber', status='new'),
					Branch('leptons_pt', status='on', index_by='lep'),
					Branch('BDT', status='on', index_by='bdt'),
					Branch('jets_pt', status='on', index_by='jet'),
					Branch('weighted_jet_pt', status='new', expression='jets_pt*weight_mc', index_by='jet*event'),
					Branch('ht_sq', status='new', expression='Ht**2', index_by='event'),
					Branch('weight_mc', status='on', index_by='event'),
					# Branch('runNumber', status='on', index_by='event'),
				  ]

common_args = {
			'common_branches': {
								  'nominal_Loose':	common_branches,
								 },
			'where_ntuples_at':	 ['/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v31_minintuples_v3/mc16a_nom/'],
		}


ttbar_file = Sample('ttbar', ids=['410470_AFII_user.nbruscin.22889431._000017'], **common_args)

sample_list = [ttbar_file]







# common_branches = [
# 					Branch('weight_mc', state='on'), Branch('runNumber', state='on'),
# 					Branch('bdt_tH', state=1), Branch('bdt_tH', state=0),
# 				  ]

# common_args = {
# 			'common_branches': {
# 								  'nominal_loose':	common_branches,
# 								  'SystTree':		common_branches,
# 								 },
# 			'where_ntuples_at':	 ['/somewhere/on/eos/mc16a/', '/somewhere/on/eos/mc16d/'],
# 			'Exclude': '*xyz*'
# 		}

# tH_T2Bs = {
# 			'nominal_loose':	[Branch('MCWeight', state=' new', expression='weight_mc*another')],
# 			'SystTree':			[Branch('pT', state=' new', expression='px**2+py**2+pz**2')]
# 		  }
# # Can apply cut to define sample. If cut applied to a new branch, the new branch has to be created with
# # an expression in the add_branches or common_args tree_to_branches
# tH_sample = Sample('tHq', 	dsids=[12345, 56789], add_branches=tH_T2Bs, cuts=['X > Y'], **common_args)

# # Easy Mode Option 

# tttb_T2Bs = {
# 			'nominal_loose':	[Branch('MCWeight', state=' new', expression='weight_mc*another')],
# 			'SystTree':			[],
# 			'AnotherSystTree':	[],
# 		  }
# # Branch like nominal means use same branches as nominal tree from other trees
# ttb_sample = Sample('ttb',  dsids=[88888, 99999], , cuts=['X > A'], add_branches=tttb_T2Bs, branch_like_nom=True, **common_args)

# # Or if there is no new branches Easy Mode option becomes

# common_args = {
# 			'common_branches': {
# 								  'nominal_loose':	 common_branches,
# 								  'SystTree':		 [],
# 								  'AnotherSystTree': [],
# 								 },
# 			'where_ntuples_at':	 ['/somewhere/on/eos/mc16a/', '/somewhere/on/eos/mc16d/'],
# 		}
# ttb_sample = Sample('ttb',  dsids=[88888, 99999], , cuts=['X > A'], branch_like_nom=True, **common_args)

