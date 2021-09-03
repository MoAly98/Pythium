class Branch:

	def __init__(self, name, status, expression='', index_by='event', parent=None):
		self.name = name
		self.index = index_by
		if status != 'on' and status != 'off' and status != 'new':
			raise ValueError("Invalid Branch Status")
		else:
			self.status = status

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
# class Systematic: