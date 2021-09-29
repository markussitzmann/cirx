import subprocess
import datetime
import os
import time
import signal
import base64
import urllib

#_cactvs_loader = __import__(settings.CACTVS_PATH)
#Cactvs = _cactvs_loader.Cactvs
#Ens = _cactvs_loader.Ens
#Dataset = _cactvs_loader.Dataset
#Molfile = _cactvs_loader.Molfile



class ExternalResolver:
	
	connector_dir = os.path.dirname(__file__)
	
	def __init__(self, name, url_scheme):
		self.name = name
		self.connector = os.path.join(ExternalResolver.connector_dir, 'connector.py')
		self.url_scheme = url_scheme
		self.timeout = 5
	
	def resolve(self, identifier, representation):
		
		url = self.url_scheme % (urllib.quote(identifier), representation)
		url_base64 = base64.b64encode(url)
		
		cmd = '%s %s' % (self.connector, url_base64)
		
		response = ExternalResolverResponse()
		response['url'] = url
		
		process = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		start = datetime.datetime.now()
		
		try:
			while process.poll() is None:
				time.sleep(0.1)
				now = datetime.datetime.now()
				if (now - start).seconds > self.timeout:
					os.kill(process.pid, signal.SIGKILL)
					os.waitpid(-1, os.WNOHANG)
					raise ExternalResolverError('external resolver connection timeout')
			response['string'], response['error'] = process.communicate(input=None)
			if response['error']:
				response['status'] = False
			else:
				response['status'] = True
		except ExternalResolverError:
			response['status'] = False
		return response
	

class ExternalResolverResponse:
	
	def __init__(self):
		self.attributes = {'string': None, 'error': None, 'status': None}
		
	def __setitem__(self, key, item):
		self.attributes[key] = item
	
	def __getitem__(self, key):
		return self.attributes[key]

	def __str__(self):
		return str(self.attributes)

class ExternalResolverError(Exception):
	
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return repr(self.value)

