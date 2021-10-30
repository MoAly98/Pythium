from slimming_proto_config import sample_list
from example_slimming_config import sample_list
from common_tools import branch_expr_to_df_expr
from argparse import ArgumentParser, ArgumentTypeError
import uproot4 as uproot
import awkward1 as ak
import pandas as pd
import time
# ==================================================================
# Get arguments from CL
# ==================================================================
# Help messages
# ================
# _OUTDIR_HELP = dhelp('Path to directory where output files will be stored ')
# _INPUT_HELP = dhelp('The directory where the NTuples are stored')
# _PROCESSES_HELP = dhelp('The samples to check in form: proc_name,(optional)gen,(optional)FS/AFII')
# _CAMPAIGNS_HELP = dhelp('The campaigns to check')
# _VARS_HELP = dhelp('The branches to load from the Ntuples')
# _DATA_HELP = dhelp('Slim data')
# # ================
# # Defaults
# # ================
# DEFAULT_OUT_DIR = '/eos/user/m/maly/thbb/analysis_files/slimmed_Ntuples/tmp_06_08_21'
# DEFAULT_PROC = [('ttb', 'nominal', 'AFII'), ('ttb', 'PH7new', 'AFII'), ('ttb', 'PH7old', 'AFII')]
# DEFAULT_VARS = ['bdt_tH', 'bdt_ttb', 'bdt_ttc', 'bdt_ttlight', 'bdt_others']


# def get_args():
#     parser = ArgumentParser(description=__doc__)
#     parser.add_argument('--outdir', type=Path, default=DEFAULT_OUT_DIR, help=_OUTDIR_HELP)
#     parser.add_argument('--campaigns', nargs="+", default=DEFAULT_CAMPAIGNS, help=_OUTDIR_HELP)
#     parser.add_argument('--processes', nargs="+", type=process_type, default=DEFAULT_PROC, help=_PROCESSES_HELP)
#     parser.add_argument('--variables', nargs="+", choices=VAR_TO_BRANCH_NAME_MAP.keys(), default=DEFAULT_VARS, help=_VARS_HELP)
#     parser.add_argument('--data', action='store_true', help=_DATA_HELP)
#     parser.add_argument('--verbose', action='store_true')
#     return parser.parse_args()

def run():
	for sample in sample_list:
		for ntuple_args in sample.get_uproot_args():
			t1 = time.time()
			slimmed_df = slimit(ntuple_args)
			t2 = time.time()
			print("Slimming time:", t2-t1)
			slimmed_df.to_hdf('Skl_Data/test.h5', key='branches')
			t3 = time.time()
			print("Dumping time:", t3-t2)
			df_from_hdf = pd.read_hdf('Skl_Data/test.h5', key='branches')
			t4 = time.time()
			print("Re-reading time:", t4-t3)
			# If user dropping branches, will get back a list of dfs to avoid
			# indexing problems
			if(isinstance(slimmed_df, dict)):
				# Do some sort of COMBO of individual branch dataframes
				pass
			else:
				print('byebye')


def slimit(uproot_args):

	files = uproot_args.files
	cuts = uproot_args.cuts
	filter_name = uproot_args.filter_name
	extra_branches = uproot_args.extra_branches
	new_branches = uproot_args.new_branches
	#if len(new_branches) != 0:
	new_branches_names = [br.name for br in new_branches]
	branches_by_index = uproot_args.branches_by_index
	stepsize = uproot_args.stepsize

	# If user is dropping branches -- no indexing is defined, need to process branches one by one into individual DFs
	if (list(branches_by_index) == ['None']):
		for chunck in uproot.iterate(files, filter_name=filter_name, step_size=stepsize, library='ak'):
			df_chain = []
			br_to_df = {branch: pd.DataFrame() for branch in chunck.fields}
			# Maybe better to only make individual dataframes to vector branches ?
			# non-vector branches can be kept together
			for branch in chunck.fields:
				br_to_df[branch] = br_to_df[branch].append(ak.to_pandas(chunck[branch]))
		return br_to_df
	# If user is dropping some branches, but also "making" some branches
	elif('None' in list(branches_by_index) and list(branches_by_index) != ['None']):
		raise ValueError("Supplying branches to drop and branches to make at same time is not supported yet..")
		exit(0)
	# If we are only dealing with new/keep branches (04.10.21 this is the most complete part for MPhys)
	else:
		df_per_idx = []
		for br_idx, br_filters in branches_by_index.items():
			batch_dfs = []
			# Do we need to specify exact number of entries in step size? BUT IF TOO SMALL WILL MISS EVENTS
			generator = uproot.iterate(files, filter_name=br_filters, step_size=4000, library='pd')
			for chunck_df in generator:
				if len(list(chunck_df.index.names)) == 1:
					chunck_df.index.names = [br_idx]
				else:
					chunck_df.index.names = ['event', br_idx]
				batch_dfs.append(chunck_df)
			all_batches_df = pd.concat(batch_dfs)
			df_per_idx.append(all_batches_df)

		mega_df = df_per_idx[0]
		for idx, df in enumerate(df_per_idx):
			if idx == 0:
				continue
			mega_df = mega_df.join(df)
		new_branches_expressions = [br.expression for br in new_branches]
		for idx, new_br in enumerate(new_branches_names):
			mega_df[new_br] = eval(branch_expr_to_df_expr('mega_df', new_branches_expressions[idx]))
		mega_df.drop(columns=extra_branches, inplace=True)
		return mega_df


	# Get the Uproot Arguments
	# uproot_args = sample.get_uproot_args()

	# Now loop over all sample files and slim them
	# slimmed_df = sample.sliimit(uproot_args)

	# Finally right out the dataframe
	# serialise(slimmed_df, file_ext=cmd_args.out_type)


# def serialise(df, file_ext='.h5'):
# 	with SlimmedFile(file_name, file_ext) as outfile:
# 		SlimmedFile.save(df)


if __name__ == '__main__':
	run()


# branches = uproot_args.branches
# branches_from_expr = [br.name for br in branches if br.parent is not None]
# branches_requested = [br.filter for br in branches if br.parent is None]
# branches_to_drop = set(branches_from_expr) - set(branches_requested)
# branch_idxs = set([br.index for br in branches])
# branches_by_idx = {br_idx: [branch.filter for branch in branches if branch.index == br_idx and branch.status not in ['new', 'off']] for br_idx in branch_idxs}
# new_branches_names = set([branch.parent.name for branch in branches if branch.parent is not None])
# df_per_idx = []
# for br_idx in branch_idxs:
# 	batch_dfs = []
# 
# 	generator = uproot.iterate(files, filter_name=filter_name, step_size=1, library='pd')
# 	for tm_df in generator:
# 		print(tmp_df)
# 		if len(list(tmp_df.index.names)) == 1:
# 			tmp_df.index.names = [br_idx]
# 		else:
# 			tmp_df.index.names = ['event', br_idx]
# 		batch_dfs.append(tmp_df)
# 	all_batches_df = pd.concat(batch_dfs)
# 	df_per_idx.append(all_batches_df)
# mega_df = df_per_idx[0]
# for idx, df in enumerate(df_per_idx):
# 	if idx == 0:
# 		continue
# 	mega_df = mega_df.join(df)
# new_branches_expressions = list(set([branch.parent.expression for branch in branches if branch.parent is not None]))
# for idx, new_br in enumerate(new_branches_names):
# 	mega_df[new_br] = eval(branch_expr_to_df_expr('mega_df', new_branches_expressions[idx]))
# mega_df.drop(columns=extra_branches, inplace=True)
#return mega_df