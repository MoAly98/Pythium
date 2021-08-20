'''
Author: Mohamed Aly
Email: maly@cern.ch
Description:

This script contains various cpython objects which are used to slim-down Ntuples as part of the
pythium framework. The objects will be filled byt he user in a configuration file, and instances
are created in-place. The instances are stored and the information is retrieved in separate scripts
to perform the slimming with Uproot4

'''


# This is the highest-level class -- hidden from user
class NtupleFile:
	def __init__(self, file_path, tree_name='nominal_Loose', branches_on=[], branches_off=[]):
		self.file_path = file_path
		self.tree = tree_name
		self.branches_on = branches_on
		self.branches_off = branches_off

	def get_uproot_args(self):
		branches_on = self.branches_on
		branches_off = self.branches_off
		fp = self.file_path
		tree_name = self.tree_name
		any_not_off_branch = '(' + f'/^(?!.*_({ branches_off.join('|')})).*' + ')'
		any_on_branch = '(' + branches_on.join('|') + ')'
		branches_filter = any_on_branch+'|'+any_not_off_branch
		files = file_path+":"+tree_name
		return files, branches_filter


# This is a lower-level class -- filled by user in config
class Sample:
	# can pass sth like
	# {nominal_loose: [(branch_name, on), (branch_name2, on), (branch_name3, off)]} # before logoff on Fri 20.08
	def __init__(self, dsid_to_filepaths_map, trees_to_keep=[], branches_on=[], branches_off=[]):

		full_paths = self.make_full_filepaths(type(dsid_to_filepaths_map))
		self.ntuplefile = {tree: NtupleFile(full_paths, tree, ) for tree in trees_to_keep}
		
		self.file_path = self.make_full_filefile_path
		self.trees = trees_to_keep
		self.keep_branches = branches_on
		self.drop_branches = branches_off

	def make_full_filepaths(self, mapping_type):
		if isinstance(dsid_to_filepaths_map, dict):
			# Do dict magic?
			pass
		elif isinstance(dsid_to_filepaths_map, str):
			# Lad is giving a file?
			if ".txt" in dsid_to_filepaths_map:
				# Deal with it as text
				pass
			elif ".csv" in dsid_to_filepaths_map:
				# Deal with it as CSV
				pass
			elif ".json" in dsid_to_filepaths_map:
				# Deal with it as JSON
				pass
			else:
				# Logging here to give error of unsupported mapping file
				pass
		else:
			# Logging here to give error of unupported mapping type
			pass

		dsid_to_filepaths_map = self.dsid_to_filepaths_map
		full_paths = [fp+dsid+"*" for dsid, fp in dsid_to_filepaths_map.items()]
		return full_paths