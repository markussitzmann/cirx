import hashlib
import random

class FileKey(object):
	
	def __init__(self):
		import random
		self.random_generator = random.SystemRandom()
		self.md5 = None
		
	def _number(self):
		return int(self.random_generator.random() * 10e16)
		
	def get(self):
		string = ""
		self.md5 = hashlib.md5()
		for i in range(0,4):
			string = string + "-" + str(self._number())
		self.md5.update(string)
		return self.md5.hexdigest()