import urllib2
import urllib
import random
import time

url_pattern = 'http://81.169.173.47/chemical/structure/%s/%s'
url_pattern_2 = 'http://81.169.173.47/chemical/structure/%s/%s/xml'
url_methods = [
	('smiles',True),
	('ficus',True),
	('ficts',True),
	('stdinchikey',True),
#	('image',False),
	('sdf',False),
	('iupac_name',True),
	('names',False),
	('ringsys_count',False),
	('ncicadd_cid',False),
	('emolecules_vid',False),
	('pubchem_sid',False),
	('chemnavigator_sid',False),
	('nsc_number',False),
	('rule_of_5_violation_count',False),
	('pack',False),
	('urls',False)
]


def random_number():
	return int(random.random() * 90000000) 

i = 1
while i < 1000000:

	n = random_number()
	for m, test in url_methods:
		r = 'NCICADD:CID=%s' % n
		
		url = url_pattern % (r, m)
		url_2 = url_pattern_2 % (r, m)
		
		print "-------------------------------------------------"
				
		try:
			t0 = time.time()
			resolver = urllib2.urlopen(url)
			response = resolver.read()
			print "* ok : %0.3f %s" % (time.time() - t0, url)
			
			if test:
				url = url_pattern % (urllib.quote(response), 'ncicadd_cid')
				t0 = time.time()
				resolver = urllib2.urlopen(url)
				response = resolver.read()
				if response == r:
					print "  ok : %0.3f %s" % (time.time() - t0, url)
				else: 
					print ">>>> : %0.3f %s" % (time.time() - t0, url)
		except:
			response = None
			print "  !! : %0.3f %s" % (time.time() - t0, url)
			time.sleep(1)
		#print response
	
		try:
			t0 = time.time()
			resolver = urllib2.urlopen(url_2)
			response = resolver.read()
			print "x ok : %0.3f %s" % (time.time() - t0, url_2)
		except:
			response = None
			print "  !! : %0.3f %s" % (time.time() - t0, url_2)
			time.sleep(1)
	
	
	i += 1




