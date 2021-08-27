'''
Author: Mohamed Aly
Email: maly@cern.ch
Description:

This script contains various cpython objects which are used to slim-down Ntuples as part of the
pythium framework. The objects will be filled byt he user in a configuration file, and instances
are created in-place. The instances are stored and the information is retrieved in separate scripts
to perform the slimming with Uproot4

'''

from common_tools import combine_dicts
from common_classes import Branch


# This is the LOWEST-level class -- hidden from user
class NtupleFile:
	def __init__(self, ntuples_dirs, dsids, exclude=[], tree_name='', branches_to_keep=[], branches_to_drop=[]):
		self.paths = self.get_path(ntuples_dirs, dsids, excluded_files=exclude)
		self.tree = tree_name
		self.branches = get_branches_filter(branches_to_keep, branches_to_drop)

	def get_paths(dirs, dsids, excluded_files=[]):
	    from glob import glob
	    paths = []
	    for directory in dirs:
	        for dsid in dsids:

	            general_path = glob(directory + '*' + dsid + '*')
	            paths_to_keep = set(general_path)
	            for excluded_file in excluded_files:
	                excluded_dir = glob(directory + '*' + excluded_file + '*')
	                paths_to_keep -= set(excluded_dir)
	            paths_to_keep = list(paths_to_keep)
	            paths.append(paths_to_keep)
	    return paths

	def get_branches_filter(branches_to_keep, branches_to_drop):
		branches = []
		for idx, branch in enumerate(branches_to_keep):
			name = branch.name
			positive_regex = '/'
			if "*" in name and ".*" not in name:
				name = name.replace("*", ".*")
			positive_regex += name
	    	positive_regex += '/i'
	    	branch.set_filter(positive_regex)
	    	branches.append(branch)

		for idx, branch in enumerate(branches_to_drop):
			name = branch.name
			negative_regex = '/^((?!'
			if "*" in name and ".*" not in name:
				name = name.replace("*", ".*")
			negative_regex += name
	    	negative_regex += ').)*$/i'
	    	branch.set_filter(negative_regex)
	    	branches.append(branch)

		for branch in branches_to_make:
			recipe = br.expression
			branch.set_filter(recipe)
			branches.append(branch)
		return branches


# This is a HIGHER-level class -- filled by user in config
class Sample:

	def __init__(self, where_ntuples_at=[], exclude_files=[], common_branches={},
				          dsids=[], cuts=[], add_branches={},
				          branch_like_nom=False, systematics={}):

		self.location = where_ntuples_at
		self.ignored_files = exclude_files
		self.dsids = dsids
		self.selection = cuts
		self.trees_to_branches_map = combine_dicts(dicts=[common_branches, add_branches])  # Need later check that new branches have epxressions
		self.all_like_nominal = branch_like_nom
		self.ntuples = []

		for tree, branches in self.trees_to_branches_map:
			br_to_keep = [br in branches if br.status == 'on']
			br_to_drop = [br in branches if br.status == 'off']
			br_to_make = [br in branches if br.status == 'new']
			ntuple_obj = NtupleFile(self.location, self.dsids, exclude=self.ignored_files, tree_name=tree, branches_to_keep=br_to_keep, branches_to_drop=br_to_drop, branches_to_make=br_to_make)
			self.ntuples.append(ntuple_obj)
		self.args = self.get_uproot_args()

	def get_uproot_args(self):
		all_sample_args = []
		for ntuple in ntuples:
			path_to_tree = []
			paths = ntuple.paths
			tree_name = ntuple.tree
			branches = ntuple.branches
			for path in paths:
				path_to_tree = path+':'+tree_name

			args = UprootArgs(paths, branches, cuts)
		all_sample_args.append(args)

		return all_sample_args

	# If a new branch is defined, we may want to update its name from
	# the expression to the name specified in config
	def update_new_branch_name(self, branch, new_name):
		if not isinstance(branch, Branch):
			raise ValueError("Must pass a Branch object")
		return pass

	def add_branch(self, branch):

		if not isinstance(branch, Branch):
			raise ValueError("Branch name must be a string")

		return pass

	def remove_branch(self, branch_name):

		if not isinstance(branch, str):
			raise ValueError("Branch name must be a string")

		return pass


class UprootArgs:
	def __init__(self, files, branches, cuts, step_size='4 GB'):
		self.files = files
		self.cuts = cuts
		self.filter_name = [br.filter for br in branches]
		self.branches = branches
		self.stepsize = step_size
