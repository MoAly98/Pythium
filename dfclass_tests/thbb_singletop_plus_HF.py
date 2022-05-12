'''
Author: Mohamed Aly
Email: maly@cern.ch
Description:

This script is responsible for loading slimmed Ntuples and plotting requested
variables for one process but different generators in various PS regions. This script
CANNOT be used with real DATA.

  - The path to the slimmed datasets -- same as output path form thbb_slimming.py
  - The process to be studied
  - The variables to plot
  - The MC generators
  - PS regions to make the plots in.
  - The path where the plots should be saved

'''

import uproot4 as uproot
from argparse import ArgumentParser, ArgumentTypeError
import sys
import os
import numpy as np
import pandas as pd
import h5py
import glob
import awkward as ak
from termcolor import cprint
from pathlib import Path
from tools.common import dhelp, REGION_TO_REGION_NAME_MAP
from tools.input_studies_common import (PROC_TO_AVAIL_GENS_MAP, PROC_TO_AVAIL_SIM_MAP,
                                        GEN_IN_ARG_TO_GEN_NAME_MAP, get_proc_dsid,
                                        process_type)
from tools.var_getters import VAR_TO_BRANCH_NAME_MAP, VAR_TO_EDGES_MAP
from tools.selectors import filter_by_region, get_sample_req
from tools.style import GEN_TO_COLOR_MAP, GEN_TO_PRETTY_NAME, VAR_TO_PRETTY_NAME, PROC_TO_PRETTY_NAME
from tools.plotting import (Canvas, atlas_style, add_atlas_label, apply_plot_settings,
                            stick_text_on_plot, add_presel_cuts)


# ==================================================================
# Get arguments from CL
# ==================================================================
# Help messages
# ================
_OUTDIR_HELP = dhelp('Path to directory where output files will be stored ')
_INPUT_HELP = dhelp('The directory where the NTuples are stored')
_CAMPAIGNS_HELP = dhelp('The campaigns to check')
_REGIONS_HELP = dhelp('The Phase-Space regions to make plots in')
# ================
# Defaults
# ================

DEFAULT_IN_DIR = '/eos/atlas/atlascerngroupdisk/phys-higgs/HSG8/tH_v31_minintuples_v3/'
DEFAULT_OUT_DIR = './output/single_top_truth/'
DEFAULT_CAMPAIGNS = ['mc16a', 'mc16d', 'mc16e']
DEFAULT_REGIONS = ['preselec', 'tH', 'ttb', 'ttc', 'ttlight', 'others']

def get_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--indir', default=DEFAULT_IN_DIR, help=_INPUT_HELP)
    parser.add_argument('--outdir', type=Path, default=DEFAULT_OUT_DIR, help=_OUTDIR_HELP)
    parser.add_argument('--campaigns', nargs="+", default=DEFAULT_CAMPAIGNS, help=_CAMPAIGNS_HELP)
    parser.add_argument('--regions', nargs="+", choices=REGION_TO_REGION_NAME_MAP.keys(), default=DEFAULT_REGIONS, help=_REGIONS_HELP)
    parser.add_argument('--verbose', action='store_true')
    return parser.parse_args()

# ================
# Main
# ================
def run():

	# arrays = [
	#     np.array([0,0,0]),
	#     np.array([0,1,2]),]
	# arrays_2 = [
	#     np.array([0,0]),
	#     np.array([0,1]),]
	# df1 = pd.DataFrame(np.random.randn(3, 1), index=arrays)
	# print(list(set([multindex[0] for multindex in list(df1.index)])))
	# df2 = pd.DataFrame(np.random.randn(2, 1), index=arrays_2)
	# df = df1.append(df2, ignore_index=True)
	# #print(df)
	# exit(0)
	# ======================
	# Prepare args
	# ======================
	args = get_args()
	# Be Verbose ?
	verbose = args.verbose
	# Ntuples Directory
	in_dir = args.indir
	# Slimmed files directory
	out_dir = args.outdir
	# The PS regions to compare
	regions = args.regions
	out_dir.mkdir(parents=True, exist_ok=True)
	# The campaigns to process
	nude_campaigns = args.campaigns
	if len(nude_campaigns) == 1 and nude_campaigns[0] == 'none':
		# If 'none' given, data is assumed to be given
		nude_campaigns = []
	variables = ['jets_truth_flav', 'jets_truth_label']
	procs_details = [('singletop_Wtchannel','nominal', 'FS')]#,('singletop_tchannel','nominal', 'FS'),('singletop_schannel','nominal', 'FS')]
	proc_gen_to_vars_map = {}
	# Start a loop over processes requested
	for one_proc_details in procs_details:
		# ======================
		# Prepare some diagnostic info for benchmarking
		# ======================
		# Read the proc_name, generator and sim type from the parsed tuples
		proc_name = one_proc_details[0]
		proc_gen = one_proc_details[1]
		proc_sim = one_proc_details[2]
		# Get the DSIDs for the requested process details
		dsids = get_proc_dsid(proc_name, which_gen=proc_gen, which_sim=proc_sim)
		# Get the cuts which define the sample (mainly relevant for ttbar)
		sample_req = get_sample_req(proc_name)
		# Get the campaign directory name.
		campaigns = get_correct_campaign_dir(nude_campaigns, proc_sim)
		# The variables to be included in the slimmed files
		og_branches = [VAR_TO_BRANCH_NAME_MAP[var] for var in variables]
		clubcard_branches = ['foam[:,1]', 'njets', 'nbjets', 'leptons_tight[:,0]']
		mc_weight_branches = ['weight_mc*xsec_weight*weight_pileup*weight_bTagSF_DL1r_Continuous*weight_jvt*weight_forwardjvt/totalEventsWeighted*weight_leptonSF', 'runNumber']

		# Need requested branches, obligaotry branches and weight branches
		branches = og_branches+clubcard_branches+mc_weight_branches
		files = [in_dir+campaign+dsid+"*" for campaign in campaigns for dsid in dsids]
		data_list = []

		# Loop over directories where Ntuples are stored
		for files_dir in files:
			if verbose:
				cprint(f'INFO:: Slimming {files_dir}', 'green')

			for data_uproot in uproot.iterate(files_dir+':nominal_Loose', branches, cut=sample_req, step_size='4 GB'):
				# Turn data into pandas dataframe
				df = ak.to_pandas(data_uproot)
				data_list.append(df)

		new_data_list = [data_list[0]]
		for idx, data in enumerate(data_list):
			if idx != 0:
				new_data = data
				new_data.reset_index(inplace=True)
				num_evts_in_dfs = []
				# for dfs_done in new_data_list:
				# 	num_evts_in_dfs.extend(list(set([multindex[0] for multindex in list(dfs_done.index) ])))
				new_data["entry"] += get_multidx_df_length(new_data_list, level=0)
				new_data.set_index(["entry", "subentry"], inplace=True)
				new_data_list.append(new_data)
		final_data = pd.concat(new_data_list)
		# Rename the variables columns titles to match the simple naming system made for user
		for idx, branch in enumerate(og_branches):
			final_data.rename(columns={branch: variables[idx]}, inplace=True)
		final_data = sort_out_weights(final_data)
		proc_gen_to_vars_map[proc_name+'_'+proc_gen] = final_data

	# Loop over the regions of phase-space to make plots in
	for region in regions:
		# Get the region name as used in the analysis configuration
		proper_region = REGION_TO_REGION_NAME_MAP[region]
		if verbose:
			cprint(f'INFO:: Processing the following region: {proper_region}', 'green')
		# Loop over the generators
		for proc_gen, data_all_regions in proc_gen_to_vars_map.items():
			# Filter the data to select the current region
			data = filter_by_region(data_all_regions, proper_region)

			n_stop_light_evts_pl = 0
			n_stop_b_evts_pl = 0
			n_stop_c_evts_pl = 0
			stop_b_pl = data[(data.jets_truth_label == 21) & (data.jets_truth_flav == 5)]
			n_stop_b_evts_pl = stop_b_pl.groupby(level=0)['weights'].nth(0).sum()
			stop_b_pl_idxs = get_multidx_df_idx_list(stop_b_pl)
			stop_c_pl = data[(data.jets_truth_label == 21) & (data.jets_truth_flav == 4)]
			stop_c_pl = stop_c_pl.drop(stop_b_pl_idxs, level=0)
			stop_c_pl_idxs = get_multidx_df_idx_list(stop_c_pl)
			n_stop_c_evts_pl = stop_c_pl.groupby(level=0)['weights'].nth(0).sum()
			stop_light_pl = data.drop(stop_b_pl_idxs+stop_c_pl_idxs, level=0)
			stop_light_pl_idxs = get_multidx_df_idx_list(stop_light_pl)
			n_stop_light_evts_pl = stop_light_pl.groupby(level=0)['weights'].nth(0).sum()

			# Repeat for Turth flavour only

			n_stop_light_evts_tf = 0
			n_stop_b_evts_tf = 0
			n_stop_c_evts_tf = 0

			# Filter based on length of subentry
			stop_b_tf = data[(data.jets_truth_flav == 5)].groupby(level=0).filter(lambda x: len(x) > 2)
			stop_b_tf_idxs = get_multidx_df_idx_list(stop_b_tf)
			n_stop_b_evts_tf = stop_b_tf.groupby(level=0)['weights'].nth(0).sum()
			if ('Wtchannel' in proc_gen):
				stop_c_tf = data[(data.jets_truth_flav == 4)].groupby(level=0).filter(lambda x: len(x) > 1)
			else:
				stop_c_tf = data[(data.jets_truth_flav == 4)].groupby(level=0).filter(lambda x: len(x) > 0)
			
			stop_c_tf = stop_c_tf.drop(stop_b_tf_idxs, level=0)
			stop_c_tf_idxs = get_multidx_df_idx_list(stop_c_tf)
			n_stop_c_evts_tf = stop_c_tf.groupby(level=0)['weights'].nth(0).sum()
			
			stop_light_tf = data.drop(stop_b_tf_idxs+stop_c_tf_idxs, level=0)
			stop_light_tf_idxs = get_multidx_df_idx_list(stop_light_tf)
			n_stop_light_evts_tf = stop_light_tf.groupby(level=0)['weights'].nth(0).sum()


			if 'Wtchan' in proc_gen:
				colors = ['steelblue', 'dodgerblue','deepskyblue'] 
			elif 'tchan' in proc_gen:
				colors = ['goldenrod', 'darkorange','orange'] 
			else:
				colors = ['forestgreen', 'limegreen','mediumspringgreen'] 
			with Canvas(out_dir/f'{proc_gen}_{proper_region}_extrajets_fracs_PLandTF.pdf') as can:
				can.ax.pie([n_stop_b_evts_pl, n_stop_c_evts_pl, n_stop_light_evts_pl], 
					       labels=[r"SingleTop + $\geq$ 1b", r"SingleTop + $\geq$ 1c", r"SingleTop + $\geq$ 0 light"], 
					       autopct='%1.1f%%',
					       labeldistance=1.05,
					       colors = colors,
					       wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'},
					       textprops={'fontsize': 28, 'weight': "bold" })
				# Get the generator name and proc name (same per script run)
				gen = proc_gen.split("_")[-1]
				proc = ''.join(proc_gen.split("_")[:-1])
				# Make plots pretty with latex names and nice colors
				proc_name = PROC_TO_PRETTY_NAME[proc]
				can.ax.text(x=0.3, y=0.98, s=f'{proc_name} in {proper_region}', transform=can.ax.transAxes, fontsize=32, weight="bold")
			# Same plot with TruthFlav only
			with Canvas(out_dir/f'{proc_gen}_{proper_region}_extrajets_fracs_TFonly.pdf') as can:
				can.ax.pie([n_stop_b_evts_tf, n_stop_c_evts_tf, n_stop_light_evts_tf], 
					       labels=[r"SingleTop + $\geq$ 1b", r"SingleTop + $\geq$ 1c", r"SingleTop + $\geq$ 0 light"], 
					       autopct='%1.1f%%',
					       labeldistance=1.05,
					       colors = colors,
					       wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'},
					       textprops={'fontsize': 28, 'weight': "bold" })
				# Get the generator name and proc name (same per script run)
				gen = proc_gen.split("_")[-1]
				proc = ''.join(proc_gen.split("_")[:-1])
				# Make plots pretty with latex names and nice colors
				proc_name = PROC_TO_PRETTY_NAME[proc]
				can.ax.text(x=0.3, y=0.98, s=f'{proc_name} in {proper_region}', transform=can.ax.transAxes, fontsize=32, weight="bold")


# ====================================================================================================
# Calculate the length of a multindex dataframe based on level of dataframe
# ====================================================================================================
def get_multidx_df_length(dfs, level=0):
	if type(dfs) is list:
		list_of_evt_nums = []
		for df in dfs:
			list_of_evt_nums.extend(list(set([multindex[level] for multindex in list(df.index) ])))	
		return len(list_of_evt_nums)
	elif isinstance(dfs, pd.DataFrame):
		list_of_evt_nums = list(set([multindex[level] for multindex in list(dfs.index) ]))
		return len(list_of_evt_nums)
# ====================================================================================================
# Get indicies from a particular level
# ====================================================================================================
def get_multidx_df_idx_list(dfs, level=0):
	if type(dfs) is list:
		list_of_evt_nums = []
		for df in dfs:
			list_of_evt_nums.extend(list(set([multindex[level] for multindex in list(df.index)])))
		return list_of_evt_nums
	elif isinstance(dfs, pd.DataFrame):
		list_of_evt_nums = list(set([multindex[level] for multindex in list(dfs.index) ]))
		return list_of_evt_nums
# ====================================================================================================
# Apply weight factor due to runNumber, rename MC weight column and drop excessive weight columns
# ====================================================================================================
def sort_out_weights(data):
	data.rename(columns={'weight_mc*xsec_weight*weight_pileup*weight_bTagSF_DL1r_Continuous*weight_jvt*weight_forwardjvt/totalEventsWeighted*weight_leptonSF': "weights"}, inplace=True)

	data['weights'] = np.where(data['runNumber'] < 290000.,
                               data['weights'] * 36207.66,
                               data['weights'])
	data['weights'] = np.where(data['runNumber'] >= 310000.,
                               data['weights'] * 58450.1,
                               data['weights'])
	data['weights'] = np.where(np.logical_and(data['runNumber'] < 310000., data['runNumber'] >= 290000.),
                               data['weights'] * 44307.4,
                               data['weights'])
	data.drop(columns=['runNumber'], inplace=True)
	return data


# ====================================================================================================
# Get the correct campaign directory containing the files to be slimmed down
# ====================================================================================================
def get_correct_campaign_dir(nude_campaigns, sim_type):

	# Decide where to look for the files (nom-only or syst directories)
	if(sim_type == 'AFII'):
		campaigns = [campaign+'_nom/' for campaign in nude_campaigns]
	else:
		campaigns = [campaign+'_syst/' for campaign in nude_campaigns]

	return campaigns













# # ==================================================================
# # Get arguments from CL
# # ==================================================================
# # Help messages
# # ================
# _OUTDIR_HELP = dhelp('Path to directory where output files will be stored ')
# _INPUT_HELP = dhelp('The directory where the slimmed json files are stored')
# _PROCESSES_HELP = dhelp('The samples to check in form: proc_name,(optional)gen,(optional)FS/AFII')
# _GENS_HELP = dhelp('The generators to compare')
# _VARS_HELP = dhelp('The branch to load from the Ntuples')
# _REGIONS_HELP = dhelp('The Phase-Space regions to make plots in')
# # ================
# # Defaults
# # ================

# DEFAULT_IN_DIR = '/eos/user/m/maly/thbb/analysis_files/slimmed_Ntuples/'
# DEFAULT_OUT_DIR = './output/overlay_generators/'
# DEFAULT_PROC = 'ttb'
# DEFAULT_GENS = 'nominal'
# DEFAULT_VARS = 'bdt_tH'
# DEFAULT_REGIONS = ['preselec', 'tH', 'ttb', 'ttc', 'ttlight', 'others']


# def get_args():
#     parser = ArgumentParser(description=__doc__)
#     parser.add_argument('--indir', default=DEFAULT_IN_DIR, help=_INPUT_HELP)
#     parser.add_argument('--outdir', type=Path, default=DEFAULT_OUT_DIR, help=_OUTDIR_HELP)
#     parser.add_argument('--procs', nargs="+", choices=PROC_TO_AVAIL_GENS_MAP.keys(), default=DEFAULT_PROC, help=_PROCESSES_HELP)
#     parser.add_argument('--generator', choices=GEN_IN_ARG_TO_GEN_NAME_MAP.keys(), default=DEFAULT_GENS, help=_GENS_HELP)
#     parser.add_argument('--regions', nargs="+", choices=REGION_TO_REGION_NAME_MAP.keys(), default=DEFAULT_REGIONS, help=_REGIONS_HELP)
#     parser.add_argument('--proc_category', type=str)
#     parser.add_argument('--var', choices=VAR_TO_BRANCH_NAME_MAP.keys(), default=DEFAULT_VARS, help=_VARS_HELP)
#     parser.add_argument('--verbose', action='store_true')
#     parser.add_argument('--unweight', action='store_true')
#     return parser.parse_args()


#   

if __name__ == '__main__':
    run()
