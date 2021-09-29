import re

class String:
	
	def __init__(self, string = None):
		self._set(string = string)
		
	def _set(self, string = None):
		self._reset()
		if self._test_cas(string):
			pass
		else:
			raise StringError('string is not resolvable')
			
		
	def _reset(self):
		self.part1 = None
		self.part2 = None
		self.checkdigit = None
		
	def _test_cas(self, string):
		pattern = re.compile('(?P<part1>^\d{1,7})-(?P<part2>\d{2})-(?P<checkdigit>\d{1}$)')
		match = pattern.search(string)
		if match:
			number = match.groupdict()
			self.part1 = int(number["part1"])
			self.part2 = int(number["part2"])
			self.checkdigit = int(number["checkdigit"])
			n = str(self.part1) + str(self.part2)
			l = range(len(n))
			l.reverse()
			f = 1
			c = 0
			for i in l:
				m = int(n[i]) * f
				c = c + m
				f = f + 1
			correct_checkdigit = c % 10
			if self.checkdigit == correct_checkdigit or self.checkdigit == 0:
				return True
		return False
	
class StringError(Exception):
	
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return repr(self.value)