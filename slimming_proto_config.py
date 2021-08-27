# Prototype config
from slimming_classes import Sample
from common_classes import Branch


common_branches = [
					Branch('weight_mc', status='on'), Branch('runNumber', status='on'),
					Branch('BDT[:,0]', status='on'),
					#Branch('*met*', status='on'), #Not Supported yet
				  ]

common_args = {
			'common_branches': {
								  'nominal_Loose':	common_branches,
								 },
			'where_ntuples_at':	 ['/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v31_minintuples_v3/mc16a_nom/'],
		}


ttbar_file = Sample('ttbar', dsids=['410470_AFII_user.nbruscin.22889431._000017'], **common_args)

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

