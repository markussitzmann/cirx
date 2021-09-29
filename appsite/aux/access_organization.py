import subprocess
import urllib2
import urllib
import json

from chemical.structure.models import *


f = open('/work3/sitzmann/projects/hosts/ip_list.txt')

addresses = f.read()

i = 1
for address in addresses.split('\n')[1:]:

	host_id, host_ip = address.split()
	
	url = "http://whois.arin.net/rest/ip/%s" % host_ip
	header = {'Accept': 'application/json'}

	request = urllib2.Request(url, None, header)
	resolver = urllib2.urlopen(request)
	response = resolver.read()

	#print response

	data = json.loads(response)

	print '---------------'

	try:
		if data['net'].has_key('parentNetRef'):
			name=data['net']['orgRef']['@name']
			host = AccessHost.objects.get(id=host_id)
			organization_object, dummy = AccessOrganization.objects.get_or_create(string=name)
			access_host_organization = AccessHostOrganization.objects.get_or_create(host=host, organization=organization_object)
			#host.accesshostorganization_set.add(access_host_organization)
			print data['net']['orgRef']['@name'] 
	except:
		for k,v in data['net'].items():
			print "   %s : %s" % (k,v)
		print 'failed'
		pass
	i += 1


