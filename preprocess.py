from config_file import sample_list
from argparse import ArgumentParser, ArgumentTypeError

# ==================================================================
# Get arguments from CL
# ==================================================================
# Help messages
# ================
_OUTDIR_HELP = dhelp('Path to directory where output files will be stored ')
_INPUT_HELP = dhelp('The directory where the NTuples are stored')
_PROCESSES_HELP = dhelp('The samples to check in form: proc_name,(optional)gen,(optional)FS/AFII')
_CAMPAIGNS_HELP = dhelp('The campaigns to check')
_VARS_HELP = dhelp('The branches to load from the Ntuples')
_DATA_HELP = dhelp('Slim data')
# ================
# Defaults
# ================
DEFAULT_OUT_DIR = '/eos/user/m/maly/thbb/analysis_files/slimmed_Ntuples/tmp_06_08_21'
DEFAULT_PROC = [('ttb', 'nominal', 'AFII'), ('ttb', 'PH7new', 'AFII'), ('ttb', 'PH7old', 'AFII')]
DEFAULT_VARS = ['bdt_tH', 'bdt_ttb', 'bdt_ttc', 'bdt_ttlight', 'bdt_others']


def get_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path, default=DEFAULT_OUT_DIR, help=_OUTDIR_HELP)
    parser.add_argument('--campaigns', nargs="+", default=DEFAULT_CAMPAIGNS, help=_OUTDIR_HELP)
    parser.add_argument('--processes', nargs="+", type=process_type, default=DEFAULT_PROC, help=_PROCESSES_HELP)
    parser.add_argument('--variables', nargs="+", choices=VAR_TO_BRANCH_NAME_MAP.keys(), default=DEFAULT_VARS, help=_VARS_HELP)
    parser.add_argument('--data', action='store_true', help=_DATA_HELP)
    parser.add_argument('--verbose', action='store_true')
    return parser.parse_args()


for sample in sample_list:
	for ntuple_args in sample.get_uproot_args():
		files = ntuple_args.files
		cuts = ntuple_args.cuts
		filter_name = ntuple_args.filter_name
		stepsize = ntuple_args.stepsize
		branches = ntuple_args.branches
		for uproot_data in uproot.iterate(files, cuts=cuts, filter_name=filter_name, step_size=stepsize):
			df = ak.to_pandas(uproot_data)
			new_branches_long_names = [br.expression for br in branches if br.status == 'new']
			new_branches_short_names = [br.name for br in branches if br.status == 'new']
			for idx, long_name in enumerate(new_branches_long_names):
				df.rename(columns={long_name: new_branches_short_names[idx]}, inplace=True)

	# Get the Uproot Arguments
	uproot_args = sample.get_uproot_args()

	# Now loop over all sample files and slim them
	slimmed_df = sample.sliimit(uproot_args)

	# Finally right out the dataframe
	serialise(slimmed_df, file_ext=cmd_args.out_type)


def serialise(df, file_ext='.h5'):
	with SlimmedFile(file_name, file_ext) as outfile:
		SlimmedFile.save(df)

