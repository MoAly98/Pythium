#!/usr/bin/env python3
'''
Author: Mohamed Aly
Email: maly@cern.ch
Description:

This script contains various cpython objects which are used to slim-down Ntuples as part of the
pythium framework. The objects will be filled byt he user in a configuration file, and instances
are created in-place. The instances are stored and the information is retrieved in separate scripts
to perform the slimming with Uproot4

'''
# Pre-defined tools and classes which are needed for slimming
from common_tools import combine_dicts, branches_from_expr, indexing_from_expr
from common_classes import Branch
from utils.logger import ColoredLogger
import sys



class SampleTree:
	"""
	For each sample, there will be a collection of Tree objects, one for each tree in the Sample.
	The Tree object will construct the full path to the files relevant for the given Sample, incl
	the TTree name added to end of path (/path/to/files:tree). The Tree object is also aware
	of the branches to keep, make or drop from its tree.. Based on the user specified branches, a regex
	filter to select/deselect a branch will be built.
	If a branch is new and constructed from an expression, the Tree object will breakdown the expr
	to extract the branches used to calculate it. The breakdown of expression assumes the branch names in
	the expression are exact -- no regex is allowed in expressions.
	"""
	# Constructor
	def __init__(self, ntuples_dirs, ids, exclude_files=[], tree_name='', branches_to_keep=[], branches_to_drop=[], branches_to_make=[]):
		# Get the paths to all files for the given sample
		self.paths = self.get_paths(ntuples_dirs, ids, excluded_files=exclude_files)
		self.tree = tree_name
		# Include the tree-name to the path
		self.paths = [path+':'+tree_name for path in self.paths]  # Need to make check if tree is in file somewhere..
		self.logger = ColoredLogger()
		# Maybe we allow it, except for when there is a contradiction?
		if len(branches_to_keep) != 0 and len(branches_to_drop) != 0:
			self.logger.error("Either choose branches to keep or branches to drop from Sample Tree")
			# Exit
			sys.exit()
		# Get filter expressions for all branches to be kept/lost/made as specified by  user
		self.branches = self.get_branches_filter(branches_to_keep, branches_to_drop, branches_to_make)

	#  Build the list of paths to sample from globs
	def get_paths(self, dirs, ids, excluded_files=[]):
	    from glob import glob
	    paths = []
	    # Loop over directories where sample ntuples are stored
	    for directory in dirs:
	    	# Loop ver all unqique IDs for this sample (to select it's files from other files)
	        for an_id in ids:
	        	# Turn the path+ID combo into a glob (opens directory and gets all files with pattern)
	            general_path = glob(directory + '*' + an_id + '*')
	            # Get a unique list of paths
	            paths_to_keep = set(general_path)
	            # If user asked to drop specific files in the directory, remove the path to it
	            for excluded_file in excluded_files:
	            	# Get a list of all files with IDs to be excluded
	                excluded_dir = glob(directory + '*' + excluded_file + '*')
	                # Turn those into a set and take them out from the original list of files
	                paths_to_keep -= set(excluded_dir)
	            # Cast set onto a list to be used further
	            paths_to_keep = list(paths_to_keep)
	            # Save the paths to be kept from the current directory for the given ID
	            paths.extend(paths_to_keep)
	    # Return a list of paths to all Sample files (in any dir with any ID)
	    return paths

	# Build regex filters for various branches, to be fed to Uproot in filter_name arg
	# The filter pattern is an attribute of the Branch object, set by a setter.
	# Since we use regex patterns to select branches via uproot, we can't pass
	# expressions for new branches at same time. This function will breakdown an
	# expression and save the component branches with a "parent branch" being the new branch
	# then we read the individual branches via uproot and compute the new branch at run-time
	def get_branches_filter(self, branches_to_keep, branches_to_drop, branches_to_make):
		branches = []

		# Process all branches user requested to keep
		for idx, branch in enumerate(branches_to_keep):
			name = branch.name
			# Check for wildcard in name
			# Turn any naked wildcard to a dressed one to be passed to regex
			if "*" in name and ".*" not in name:
				name = name.replace("*", ".*")
				# Update branch name
				branch.set_name(name)
			# If no wildcard in branch name (i.e. it is exact)
			if "*" not in name:
				# Branch filter is the branch name
				branch.set_filter(name)
			# If there is a wildcard in name
			else:
				# Put filter inside regex enviroment /pattern/i
				positive_regex = '/^'  # ^ means start of line
				positive_regex += name
				positive_regex += '$/i'  # $ means end of line
				# Set the filer to branch
				branch.set_filter(positive_regex)
			branches.append(branch)

		# Process all branches user requested to drop
		for idx, branch in enumerate(branches_to_drop):
			name = branch.name
			# Use negative look-ahead to drop a branch
			negative_regex = '/^(?!'
			# Turn any naked wildcard to a dressed one to be passed to regex
			if "*" in name and ".*" not in name:
				name = name.replace("*", ".*")
				# Update branch name
				branch.set_name(name)
			negative_regex += name
			negative_regex += ').*$/i'
			# Set filter to branch
			branch.set_filter(negative_regex)
			branches.append(branch)

		# Process all new branches to be made
		for branch in branches_to_make:
			# Get the expression to be used in evaluating branch
			recipe = branch.expression
			# Get all the branches involved in the expression
			list_of_branches = branches_from_expr(recipe)
			list_of_indexes = indexing_from_expr(branch.index)
			# Simple check that the index expression has some number
			# of index types as there is branches in maths expression
			if len(list_of_branches) != len(list_of_indexes):
				self.logger.error(f"New branch [{branch.name}] expression [{recipe}] doesn't match its indexing expression [{branch.index}]")
				sys.exit()
			# For each of the participating branches, make a new Branch object
			for idx, component in enumerate(list_of_branches):\
				# The new branch objects must know who the parent branch is which gave rise to them
				new_br = Branch(component, status='on', parent=branch, index_by=list_of_indexes[idx])
				# Assume no wildcards/regex inside math expression
				new_br.set_filter(component)
				branches.append(new_br)
			# Use a set to remove repeated branches
			branches = list(set(branches))
		return branches


'''
This is the object which the user interacts with. It encompasses
information about one Sample -- where this sample is, what is it's
unique identifier and which trees and branches to get from it. It will
also be aware of Systematics affecting the given Sample.
'''


class Sample:
	# Constructor
	def __init__(self, name, where_ntuples_at=[], exclude_files=[], common_branches={},
				          ids=[], cuts=[], add_branches={},
				          branch_like_nom=False, systematics={}):

		# All directories where Ntuples for this sample are stored
		self.location = where_ntuples_at
		# Any ID of files to ignore (e.g. some Regex)
		self.ignored_files = exclude_files
		# The unique identifier for files relevant to this sample (e.g. DSID)
		self.ids = ids
		# Any selection cuts to apply when reading this sample
		self.cuts = cuts
		# Make a dictionary from trees to branches for this sample
		# Combine
		self.trees_to_branches_map = combine_dicts(dicts=[common_branches, add_branches])  # Need later check that new branches have expressions
		self.all_like_nominal = branch_like_nom
		self.ntuples = []

		for tree, branches in self.trees_to_branches_map.items():
			br_to_keep = [br for br in branches if br.status == 'on']
			br_to_drop = [br for br in branches if br.status == 'off']
			br_to_make = [br for br in branches if br.status == 'new']
			ntuple_obj = SampleTree(self.location, self.ids, exclude_files=self.ignored_files, tree_name=tree, branches_to_keep=br_to_keep, branches_to_drop=br_to_drop, branches_to_make=br_to_make)
			self.ntuples.append(ntuple_obj)
		self.args = self.get_uproot_args()

	def get_uproot_args(self):
		all_sample_args = []
		for ntuple in self.ntuples:
			paths = ntuple.paths
			tree_name = ntuple.tree
			branches = ntuple.branches
			args = UprootArgs(paths, branches, self.cuts)
		all_sample_args.append(args)

		return all_sample_args

	# If a new branch is defined, we may want to update its name from
	# the expression to the name specified in config
	def update_new_branch_name(self, branch, new_name):
		if not isinstance(branch, Branch):
			raise ValueError("Must pass a Branch object")
		return 1

	def add_branch(self, branch):

		if not isinstance(branch, Branch):
			raise ValueError("Branch name must be a string")

		return 1

	def remove_branch(self, branch_name):

		if not isinstance(branch, str):
			raise ValueError("Branch name must be a string")

		return 1


class UprootArgs:

	def __init__(self, files, branches, cuts, step_size='4 GB'):
		self.files = files
		self.cuts = cuts
		self.filter_name = self.get_universal_branch_filters(branches)
		self.extra_branches = self.get_extra_branches(branches)
		self.new_branches = self.get_new_branches(branches)
		self.branches_by_index = self.get_branches_by_index(branches)
		self.stepsize = step_size
		#self.dropping_branches = dropping_branches

	def get_branches_by_index(self, list_of_branches):
		branch_idxs = set([br.index for br in list_of_branches])
		branches_filter_by_idx = {br_idx: [branch.filter for branch in list_of_branches if branch.index == br_idx
						   		  and branch.status not in ['off']] for br_idx in branch_idxs}
		return branches_filter_by_idx

	def get_new_branches(self, list_of_branches):
		new_branches = list(set([br.parent for br in list_of_branches if br.parent is not None]))
		return new_branches

	def get_extra_branches(self, list_of_branches):
		# Branches due to expression
		branches_from_expr = [br.name for br in list_of_branches if br.parent is not None]
		# Branches user requested to keep
		branches_requested = [br.filter for br in list_of_branches if br.parent is None]
		# Get the branches that are only needed to evaluate new branches
		extra_branches = set(branches_from_expr) - set(branches_requested)
		return extra_branches

	def get_regex_for_drop_branches(self, list_of_branches):
		universal_regex = '/^(?!('
		for idx, branch in enumerate(list_of_branches):
			if idx == len(list_of_branches)-1:
				universal_regex += branch.name
			else:
				universal_regex += branch.name+'|'
		universal_regex += ')).*$/i'

		return [universal_regex]

	def get_universal_branch_filters(self, list_of_branches):
		to_drop = []
		to_keep = []
		for branch in list_of_branches:
			if branch.status == 'off':
				to_drop.append(branch)
			else:
				# This includes branches to be kept for evaluating
				# new branches via expressions
				to_keep.append(branch)

		# Can have user ask to drop some columns, and still make a new branch
		if(len(to_keep) != 0 and len(to_drop) != 0):
			dropping_regex = self.get_regex_for_drop_branches(to_drop)
			filters = [br.filter for br in to_keep]+dropping_regex
		elif(len(to_keep) == 0 and len(to_drop) != 0):
			dropping_regex = self.get_regex_for_drop_branches(to_drop)
			filters = dropping_regex
		elif(len(to_drop) == 0):
			filters = [br.filter for br in to_keep]

		return filters
