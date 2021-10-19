#!/usr/bin/env python3
class Branch:

	def __init__(self, name, status, expression='', index_by='event', parent=None):
		self.name = name
		if status != 'on' and status != 'off' and status != 'new':
			raise ValueError("Invalid Branch Status")
		else:
			self.status = status
		if status == 'off':
			self.index = 'None'
		else:
			self.index = index_by
		if status == 'new' and expression == '':
			raise ValueError("New Branch declared but no expression given")
		elif status != 'new' and expression != '':
			raise ValueError("Expression given but Branch not declared as new")
		elif status == 'new' and expression != '':
			self.expression = expression
		else:
			self.expression = None
		self.filter = None  # To be set with a setter.
		self.parent = parent  # A new branch for which these two are needed

	def set_filter(self, filter_expression):
		self.filter = filter_expression

	def get_parent(self):
		return self.parent

	def set_name(self, name):
		self.name = name
# class Systematic:

# Pythium DataFrame
class PythiumDF:
	def __init__(self, pandas_dataframe):
		self.pd_df = pandas_dataframe
	# Some methods to handle multindex dataframes needed
