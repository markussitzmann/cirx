import re

class Minimol:
	
	def __init__(self, string = None):
		self.string = None
		if not self._test_minimol(string = string):
			raise MinimolError('no valid minimol string')
		self.string = string

	def _test_minimol(self,string):
		
		expression = re.compile('^[A-Z0-9]+0000$')
		if expression.match(string):
			return True
		return False
	

class MinimolError(Exception):
	
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return repr(self.value)