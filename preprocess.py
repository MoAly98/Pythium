from slimming_proto_config import sample_list
from common_tools import branch_expr_to_df_expr
from argparse import ArgumentParser, ArgumentTypeError
import uproot4 as uproot
import awkward1 as ak
import pandas as pd
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


print("""\
MMMMMMMMMMMMMMMMNmdhhyyyyyyyyyhddmNMMMMMMMMMMMMMMM
MMMMMMMMMMMMmdhyyyyyyyyyyyyyyyyyyyyyhmNMMMMMMMMMMM
MMMMMMMMMNdyyyyyyyyyyyyyyyyyyyyyyyyyyyyhmMMMMMMMMM
MMMMMMMmhyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyydMMMMMMM
MMMMMNhyyyyyyyyyyyyyyyyyyydddhhhhhhhhhhhhhhdNMMMMM
MMMMmyyyyyyyyyyyyyyyyyyyydMmoooyMMM++++//////oNMMM
MMMdyyyyyyyyyyyyyyyyyyyyyNMo----dMN-----------/mMM
MMdyyyyyyyyyyyyyyyyyyyyyyMM:----:NN------shy:--/NM
MmyyyyyyyyyyyyyyyyyyyyyydMm------om-----/MMMy---/M
NyyyyyyyyyyyyyyyyyyyyyyymMs-------s------+so:----y
dyyyyyyyyyyyyyyyyyyyyyyyMM/----------------------:
hyyyyyyyyyyyyyyyyyyyyyyhMm------------------------
yyyyyyyyyyyyyyyyyyyyyyymMy------------------------
yyyymMMdyyyyyyyyyyyyyyyMM/------------------------
yyyyNMMdyyyyyhmNmyyyyyhMN-------------------------
dyyyyyyyyydmNmhNMmyyyymMy------------------------:
Nyyyyyhdmdho/:-+MMdyyyMM+------------------------s
Mdyhdhyo::------oMMdyhMN------------------------/N
MMd+:------------sMMhmMh-----------------------:mM
MMN+--------------yMMMMo----------------------:dMM
MMMNs--------------yMMM:---------------------+mMMM
MMMMMd/-------------hMd--------------------:yNMMMM
MMMMMMNy/------------ds------------------:omMMMMMM
MMMMMMMMMh+-----------:----------------/ymMMMMMMMM
MMMMMMMMMMMNh+:---------------------/sdMMMMMMMMMMM
MMMMMMMMMMMMMMMmhs+/:---------:+oydNMMMMMMMMMMMMMM
		""")
for sample in sample_list:
	for ntuple_args in sample.get_uproot_args():
		files = ntuple_args.files
		cuts = ntuple_args.cuts
		filter_name = ntuple_args.filter_name
		stepsize = ntuple_args.stepsize
		branches = ntuple_args.branches
		branches_from_expr = [br.name for br in branches if br.parent is not None]
		branches_requested = [br.name for br in branches if br.parent is None]
		branches_to_drop = set(branches_from_expr) - set(branches_requested)
		branch_idxs = set([br.index for br in branches])
		branches_by_idx = {br_idx: [branch.name for branch in branches if branch.index == br_idx and branch.status not in ['new', 'off']] for br_idx in branch_idxs}
		new_branches_names = set([branch.parent.name for branch in branches if branch.parent is not None])

		df_per_idx = []
		for br_idx in branch_idxs:
			batch_dfs = []
			generator = uproot.iterate(files, filter_name=branches_by_idx[br_idx], step_size=stepsize, library='pd')
			for tmp_df in generator:
				if len(list(tmp_df.index.names)) == 1:
					tmp_df.index.names = [br_idx]
				else:
					tmp_df.index.names = ['event', br_idx]
				batch_dfs.append(tmp_df)
			all_batches_df = pd.concat(batch_dfs)
			df_per_idx.append(all_batches_df)

		mega_df = df_per_idx[0]
		for idx, df in enumerate(df_per_idx):
			if idx == 0:
				continue
			mega_df = mega_df.join(df)

		new_branches_expressions = list(set([branch.parent.expression for branch in branches if branch.parent is not None]))
		for idx, new_br in enumerate(new_branches_names):
			mega_df[new_br] = eval(branch_expr_to_df_expr('mega_df', new_branches_expressions[idx]))
		mega_df.drop(columns=branches_to_drop, inplace=True)
		print(mega_df)

	# # Get the Uproot Arguments
	# uproot_args = sample.get_uproot_args()

	# # Now loop over all sample files and slim them
	# slimmed_df = sample.sliimit(uproot_args)

	# # Finally right out the dataframe
	# serialise(slimmed_df, file_ext=cmd_args.out_type)


# def serialise(df, file_ext='.h5'):
# 	with SlimmedFile(file_name, file_ext) as outfile:
# 		SlimmedFile.save(df)

