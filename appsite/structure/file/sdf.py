import re

class SDFile:
	
	def __init__(self, string = None):
		self._set(string = string)
		
	def _set(self, string = None):
		self._reset()
		if self._test_sdf(string):
			pass
		else:
			raise SDFileError('string is not resolvable')
		raw_records = self.string.strip().split('$$$$')
		# dirty hack (fix for the dirty SDF files that ChemSpider delivers)
		clean_records = []
		for raw in raw_records:
			split_records = raw.strip().split('M  END')
			#print split_records
			for split_record in split_records:
				if not split_record:
					continue
				if split_record[1] == '>':
					continue
				split_record += 'M  END\n'
				#print '++++ %s' % split_record
				clean_records.append(split_record)
		for record in clean_records:
			record += '$$$$\n'
			self.records.append(record.strip()) 
		
	def _reset(self):
		self.string = None
		self.unescaped_string = None
		self.records = []

	def _test_sdf(self, string):
		#patternString = '0999 V2000(.+)'
		#TODO: improve regular expressen
		pattern = re.compile(r'.+V2000')
		match = pattern.search(string)
		if match:
			self.string = string
			self.unescaped_string = self.string.replace("\\n", '\n')
			return True
		return False


class SDFileError(Exception):
	
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return repr(self.value)
