import re

class String:
	
	"""
		unfinishehed
	"""
	
	DEFAULT_VERSION = '1'
	DEFAULT_PREFIX = "InChI="
	
	def __init__(self, string = None):
		self._set(string = string)
		
	def _set(self, string = None, prefix = None, version = DEFAULT_VERSION, layer = None):
		self._reset()
		if self._test_prefix_inchi(string):
			pass
		else:
			if self._test_inchi(string):
				pass
			else:
				raise IdentifierError('string is not resolvable')
			
		
	def _reset(self):
		self.prefix = None
		self.version = None
		self.layers = None
		self.is_standard = False
		self.well_formatted = ''
		self.html_formatted = ''
		
	def _test_prefix_inchi(self, string, prefix = DEFAULT_PREFIX):
		patternString = '^(?P<prefix>%s)(?P<version>.{1,2})/(?P<layers>.+$)' % prefix
		pattern = re.compile(patternString)
		match = pattern.search(string)
		if match:
			identifier = match.groupdict()
			self.prefix = identifier["prefix"]
			self.version = identifier["version"]
			self.layers = identifier["layers"]
			self.string = string
			if self.version[-1:] == 'S':
				self.is_standard = True
			self.well_formatted = '%s%s/%s' % (self.prefix, self.version, self.layers)
			self.html_formatted = self.well_formatted.replace('-','-<wbr>')
			return True
		return False
		
	def _test_inchi(self, string, prefix = DEFAULT_PREFIX):
		patternString = '^(?P<version>.{1,2})/(?P<layers>.+$)'
		pattern = re.compile(patternString)
		match = pattern.search(string)
		if match:
			identifier = match.groupdict()
			self.prefix = prefix
			self.version = identifier["version"]
			self.layers = identifier["layers"]
			self.string = string
			if self.version[-1:] == 'S':
				self.is_standard = True
			self.well_formatted = '%s%s/%s' % (self.prefix, self.version, self.layers)
			self.html_formatted = self.well_formatted.replace('-','-<wbr>')
			return True
		return False
		
	def query(self):
		d = {}
		d['string'] = self.well_formatted
		return d
	
class Key:
	
	DEFAULT_PREFIX = "InChIKey="

	def __init__(self, key = None, prefix = DEFAULT_PREFIX, layer1 = None, layer2 = None, layer3 = None, version=None):
		self._set(key = key, prefix = prefix, layer1 = layer1, layer2 = layer2, layer3 = layer3, version = version)
		
	def _set(self, key = None, prefix = DEFAULT_PREFIX, layer1 = None, layer2 = None, layer3 = None, version=None):
		
		self._reset()	
		resolver_list = []

		if key and not layer1 and not layer2 and not layer3:
			resolver_list = ['_test_prefix_standard_inchikey', '_test_standard_inchikey', '_test_long_prefix_inchikey', '_test_short_prefix_inchikey', '_test_long_inchikey', '_test_short_inchikey']
			arg = "%s" % key
		elif layer1 and layer2 and not layer3 and not key:
			resolver_list = ['_test_long_prefix_inchikey', '_test_short_prefix_inchikey', '_test_long_inchikey', '_test_short_inchikey']
			arg = "%s-%s" % (layer1,layer2)
		elif layer1 and layer2 and layer3 and not key:
			resolver_list = ['_test_prefix_standard_inchikey', '_test_standard_inchikey']
			arg = "%s-%s-%s" % (layer1,layer2,layer3)
		elif layer1 and not layer2 and not layer3 and not key:
			resolver_list = ['_test_short_prefix_inchikey', '_test_short_inchikey']
			arg = "%s" % layer1
		else:
			raise IdentifierError('key is not resolvable')
				
		resolved = False
		for resolver in resolver_list:
			
			#try:
			test = getattr(self, resolver)
			if test(arg):
				resolved = True
				break
			#except:
			#	pass
		
		if resolved:
			pass
		else:
			raise IdentifierError('key is not resolvable')
		
		
	def _reset(self):
		self.prefix = None
		self.layer1 = None
		self.layer2 = None
		self.layer3 = None
		self.is_standard = False
		self.version = None
		self.well_formatted = ''
		self.html_formatted = self.well_formatted.replace('-','-<wbr>')
	
	def _test_prefix_standard_inchikey(self, key, prefix = DEFAULT_PREFIX):
		patternString = '(?P<prefix>^%s)(?P<layer1>[A-Z]{14})-(?P<layer2>[A-Z]{8}S[A-Z]{1})-(?P<layer3>[A-Z]{1}$)' % prefix
		pattern = re.compile(patternString)
		match = pattern.search(key)
		if match:
			identifier = match.groupdict()
			self.prefix = identifier["prefix"]
			self.layer1 = identifier["layer1"]
			self.layer2 = identifier["layer2"]
			self.layer3 = identifier["layer3"]
			self.key = key
			self.is_standard = True
			self.version = self.layer2[-1:]
			self.well_formatted_no_prefix = '%s-%s-%s' % (self.layer1, self.layer2, self.layer3)
			self.well_formatted = '%s%s-%s-%s' % (prefix, self.layer1, self.layer2, self.layer3)
			self.html_formatted = self.well_formatted.replace('-','-<wbr>')
			return True
		return False
	
	def _test_standard_inchikey(self, key, prefix = DEFAULT_PREFIX):
		patternString = '(?P<layer1>[A-Z]{14})-(?P<layer2>[A-Z]{8}S[A-Z]{1})-(?P<layer3>[A-Z]{1}$)'
		pattern = re.compile(patternString)
		match = pattern.search(key)
		if match:
			identifier = match.groupdict()
			self.layer1 = identifier["layer1"]
			self.layer2 = identifier["layer2"]
			self.layer3 = identifier["layer3"]
			self.key = key
			self.is_standard = True
			self.version = self.layer2[-1:]
			self.well_formatted_no_prefix = '%s-%s-%s' % (self.layer1, self.layer2, self.layer3)
			self.well_formatted = '%s%s-%s-%s' % (prefix, self.layer1, self.layer2, self.layer3)
			self.html_formatted = self.well_formatted.replace('-','-<wbr>')
			return True
		return False
	
	def _test_long_prefix_inchikey(self, key, prefix = DEFAULT_PREFIX):
		patternString = '(?P<prefix>^%s)(?P<layer1>[A-Z]{14})-(?P<layer2>[A-Z]{10}$)' % prefix
		pattern = re.compile(patternString)
		match = pattern.search(key)
		if match:
			identifier = match.groupdict()
			self.prefix = identifier["prefix"]
			self.layer1 = identifier["layer1"]
			self.layer2 = identifier["layer2"]
			self.key = key
			self.well_formatted_no_prefix = '%s-%s' % (self.layer1, self.layer2)
			self.well_formatted = '%s%s-%s' % (prefix, self.layer1, self.layer2)
			self.html_formatted = self.well_formatted.replace('-','-<wbr>')
			return True
		return False
	
	def _test_short_prefix_inchikey(self, key, prefix = DEFAULT_PREFIX):
		patternString = '(?P<prefix>^%s)(?P<layer1>[A-Z]{14}$)' % prefix
		pattern = re.compile(patternString)
		match = pattern.search(key)
		if match:
			identifier = match.groupdict()
			self.prefix = identifier["prefix"]
			self.layer1 = identifier["layer1"]
			self.key = key
			self.well_formatted_no_prefix = '%s' % (prefix, self.layer1)
			self.well_formatted = '%s%s' % (prefix, self.layer1)
			self.html_formatted = self.well_formatted.replace('-','-<wbr>')
			return True
		return False
	
	def _test_long_inchikey(self, key, prefix = DEFAULT_PREFIX):
		pattern = re.compile('(?P<layer1>^[A-Z]{14})-(?P<layer2>[A-Z]{10}$)')
		match = pattern.search(key)
		if match:
			identifier = match.groupdict()
			self.layer1 = identifier["layer1"]
			self.layer2 = identifier["layer2"]
			self.key = key
			self.well_formatted_no_prefix = '%s-%s' % (prefix, self.layer1, self.layer2)
			self.well_formatted = '%s%s-%s' % (prefix, self.layer1, self.layer2)
			self.html_formatted = self.well_formatted.replace('-','-<wbr>')
			return True
		return False
	
	def _test_short_inchikey(self, key, prefix = DEFAULT_PREFIX):
		pattern = re.compile('(?P<layer1>^[A-Z]{14}$)')
		match = pattern.search(key)
		if match:
			identifier = match.groupdict()
			self.layer1 = identifier["layer1"]
			self.key = key
			self.well_formatted = '%s' % (self.layer1)
			self.well_formatted = '%s%s' % (prefix, self.layer1)
			self.html_formatted = self.well_formatted.replace('-','-<wbr>')
			return True
		return False
	
	def __str__(self):
		return self.well_formatted
	
	def query(self):
		d = {}
		d['key_layer1'] = self.layer1
		try:
			if self.layer2:
				d['key_layer2'] = self.layer2
		except:
			pass
		try:
			if self.layer3:
				d['key_layer3'] = self.layer3
		except:
			pass
		return d


class IdentifierError(Exception):
	
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return repr(self.value)
	
class KeyError(Exception):
	
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return repr(self.value)