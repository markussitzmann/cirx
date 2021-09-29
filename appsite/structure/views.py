import os
import time
import datetime

from django.core.files import File
from django.views.decorators.vary import vary_on_headers
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.template import Template, Context
from django.conf import settings 
from django.http import *
from django.utils import simplejson

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout

from models import *
from forms import *

from dispatcher import URLmethod

import resolver
import ncicadd.identifier
import formula
import smiles
import usage

#print " 1 jeff /www/django/chemical/structure/views.py"

if not settings.TEST:
	if settings.JAVA:
		from jpype import JPackage,attachThreadToJVM,isThreadAttachedToJVM
		if not isThreadAttachedToJVM():
			attachThreadToJVM()
		opsin_package = JPackage("uk").ac.cam.ch.wwmm.opsin
		Opsin = opsin_package.NameToStructure.getInstance()
		OpsinConfig = opsin_package.NameToStructureConfig()

#@login_required
#def test(request, string):
#	#string = string.replace("\\n", '\n')
#	s = request.session
#	s['bla'] = 'blubber'
#	string = "%s %s %s %s :: %s" % (request.user.first_name, request.user.last_name, request.user.email, request.user.last_login, request.session)
#	return HttpResponse(string, mimetype = 'text/plain')

#def test(request):
	##from cactvs.cactvs import *
	##c = Cactvs()
	##e = Ens(c, "CCO")
	##s = e.get('molfilestring', parameters={'get3d': True})
	##s = c.cmd('set cactvs(version)')
	#return HttpResponse(s, mimetype = 'text/plain')

#def logout_view(request):
	#logout(request)
	#return HttpResponse('Done', mimetype = 'text/plain')

#def test_view(request):
	#return render_to_response('test_view.template')

#def name(request, string=None):
	#if request.method == 'POST':
		#form = ChemicalNameInput(request.POST)
		#if form.is_valid():
			#nameString = form.cleaned_data['nameString']
			#redirectedURL = '%s/name/%s' % (settings.STRUCTURE_BASE_URL, nameString, )
			#return HttpResponseRedirect(redirectedURL)
	#else:
		#if string:
			#form = ChemicalNameInput({'nameString': string,})
			#resolved_names = resolver.ChemicalName(pattern = string)
			#structure_names = resolved_names.structure_names
			#metadata = resolved_names.metadata
			#return render_to_response('name_list.template', {'form': form, 'string': string, 'resolved': resolved_names, 'structure_names': structure_names, 'metadata': metadata})
		#else:
			#form = ChemicalNameInput()
			#structure_names = []
			#metadata = []
			#return render_to_response('name.template', {'form': form,})

#def structure_documentation(request, dummy=None, string=None):
	#return render_to_response('structure_documentation.template')

def twirl_cache(request, string, dom_id):
	parameters = request.GET.copy()
	parameters.__setitem__('dom_id', dom_id)
	request.GET = parameters
	response = identifier(request, string, 'twirl')
	return response

def chemdoodle_cache(request, string, dom_id):
	parameters = request.GET.copy()
	parameters.__setitem__('dom_id', dom_id)
	request.GET = parameters
	response = identifier(request, string, 'chemdoodle')
	return response


def identifier(request, string, representation, operator = None, format = 'plain'):
#	print " 2 jeff /www/django/chemical/structure/views.py"
	#try:
	#	counter = usage.Counter()
	#	exceeded = counter.exceeded(request, slow_down = False)
	#except:
	#	raise Http404
	#if settings.TEST:
#	if False:
	return resolve_to_response(request, string, representation, operator = None, format = format)
#	else:
#		try:
#			return resolve_to_response(request, string, representation, operator = None, format = format)
#		except:
#			raise Http404
#	return
	
def opsin_resolver(request, name):
#	print " 3 jeff /www/django/chemical/structure/views.py"
	try:
		opsin_result = Opsin.parseChemicalName(name, OpsinConfig)
	except:
		raise Http404
	smiles = opsin_result.getSmiles()
	if not smiles:
		raise Http404
	return HttpResponse(smiles, mimetype = 'text/plain')
	

def structure(request, string=None):
#	print " 4 jeff /www/django/chemical/structure/views.py"
	if request.is_secure():
#		print " 4.1 jeff /www/django/chemical/structure/views.py"
		host_string = 'https://' + request.get_host()
#		host_string = 'https://fr-s-ccr-cactusweb-d.ncifcrf.gov'
	else:
#		print " 4.2 jeff /www/django/chemical/structure/views.py"
		host_string = 'http://' + request.get_host()
	
#	print " 4.3 jeff /www/django/chemical/structure/views.py"
	query = request.GET.copy()
#	print " 4.4 jeff /www/django/chemical/structure/views.py"
		
	if query.has_key('string') and query.has_key('representation'):
#		print " 4.5 jeff /www/django/chemical/structure/views.py"
		return identifier(
			request, 
			query['string'], 
			query['representation'], 
			operator = query.get('operator', None), 
			format = query.get('protocol', 'plain')
		)
	
#	print " 4.6 jeff /www/django/chemical/structure/views.py"
	if request.method == 'POST':
#		print " 4.7 jeff /www/django/chemical/structure/views.py"
		form = ChemicalResolverInput(request.POST)
		if form.is_valid():
			string = form.cleaned_data['string'].replace('#', '%23')
			representation = form.cleaned_data['representation']
			redirectedURL = '%s/%s/%s' % (settings.STRUCTURE_BASE_URL, identifier, representation)
			return HttpResponseRedirect(redirectedURL)
	else:
#		print " 4.8 jeff /www/django/chemical/structure/views.py"
		if string:
			form = ChemicalResolverInput({'identifier': string, 'representation': 'stdinchikey'})
		else:
			form = ChemicalResolverInput()
#	print " 4.9 jeff /www/django/chemical/structure/views.py"
#	print " 4.9 jeff base_url = ",settings.STRUCTURE_BASE_URL
#	print " 4.9 jeff host = ",host_string
#	host_string = "https://fr-s-ccr-cactusweb-t.ncifcrf.gov"
##	print " 4.9.2 jeff host = ",host_string
	return render_to_response('structure.template', {
		'form': form,
		'base_url': settings.STRUCTURE_BASE_URL,
		'host': host_string, 
	})
#	print " 4.10 jeff /www/django/chemical/structure/views.py"

#def editor(request):
	#form = ChemicalResolverInput()
	#form.editor_button = 'editor-button'
	#form.structure_input_field = 'id_identifier'
	#return render_to_response('editor_test.template', {
		#'form': form,
		#'base_url': settings.STRUCTURE_BASE_URL,
		#'host': host_string,
	#})


def structure_documentation(request, dummy=None, string=None):
	return render_to_response('structure_documentation.template')
#	print " 10 jeff /www/django/chemical/structure/views.py"
	

#def statistics(request):
	#data = simplejson.dumps(UsageMonth.get_data_dictionary())
	#return render_to_response('statistics.template', {'data': data})


#def statistic_seconds(request):
	#data = UsageSeconds.objects.all()[0].requests
	#return HttpResponse(data, mimetype = 'text/plain')


#######

def resolve_to_response(request, string, representation, operator = None, format = 'plain'):
	parameters = request.GET.copy()
	
	if parameters.has_key('operator'):
		operator = parameters['operator']
	
	if operator:
		string = "%s:%s" % (operator,string)
		
	speed_factor = 3
#	print " 5 jeff /www/django/chemical/structure/views.py Paul's test - resolve_to_response " + string + " " + str(operator) + " " + format + " " + str(request.GET) + " " + representation
        now = datetime.datetime.now()
        one_minute = datetime.timedelta(minutes = 1)
        one_hour = datetime.timedelta(minutes = 60)
#	print " 6 jeff /www/django/chemical/structure/views.py PAUL Creating accessHost " + request.META['REMOTE_ADDR']
	try:
        	host, new_host = AccessHost.objects.get_or_create(string = request.META['REMOTE_ADDR'])
	except Exception as inst:
                print type(inst)
                print inst
                raise inst
        
#	print " 7 jeff /www/django/chemical/structure/views.py PAUL Created AccessHost"
	try:
	 	client, new_client = AccessClient.objects.get_or_create(string = request.META['HTTP_USER_AGENT'])
	except:
#		print " 8 jeff /www/django/chemical/structure/views.py PAUL AccessClient exception"
		client, dummy = AccessClient.objects.get_or_create(string = "None")
	host, new_host = AccessHost.objects.get_or_create(string = request.META['REMOTE_ADDR'])
	access = Access(host = host, client = client, timestamp = now)
	access.save()

	host_access_count_one_minute = Access.objects.filter(host = host, timestamp__gte = (now - one_minute)).count()
	host_access_count_one_hour = Access.objects.filter(host = host, timestamp__gte = (now - one_hour)).count()
	sleep_period_1m = host_access_count_one_minute / (60 * speed_factor)
	sleep_period_1h = host_access_count_one_hour / (3600 * speed_factor)

	try:
		host_time_limit_exceeded = (now - host.lock_timestamp).seconds > 10
	except TypeError:
		host_time_limit_exceeded = True
	if (not host.blocked) or (host_time_limit_exceeded):
		host.blocked = 1
		host.lock_timestamp = now
		host_blocked = True
		time.sleep(sleep_period_1h)
	else:
		host_blocked = False
		time.sleep(sleep_period_1m)
	host.save()

#	print " 9 jeff /www/django/chemical/structure/views.py PAUL Got to URLMethod"
	url_method = URLmethod(representation = representation, request = request, output_format = format)
	resolved_string, representation, response, mime_type = url_method.parser(string)
	if request.is_secure():
		host_string = 'https://' + request.get_host()
	else:
		host_string = 'http://' + request.get_host()
		
	if host_blocked:
		host.blocked = 0
		host.save()

	if request.META.has_key('QUERY_STRING'):
		url_parameter_string = request.META['QUERY_STRING']
	else:
		url_parameter_string = None
	
	if representation == 'twirl' or representation == 'chemdoodle':
		if not parameters.has_key('width'):
			parameters['width'] = 1000
		if not parameters.has_key('height'):
			parameters['height'] = 700
		if parameters.has_key('div_id') or parameters.has_key('dom_id'):
			if parameters.has_key('div_id') and not parameters.has_key('dom_id'):
				parameters['dom_id'] = parameters['div_id']
			mime_type = 'text/javascript'
		else:
			mime_type = 'text/html'
		return render_to_response('3d.template', {
			'library': representation,
			'string': string,
			'response': url_method.response_list,
			'parameters': parameters,
			'url_parameter_string': url_parameter_string,
			'base_url': settings.STRUCTURE_BASE_URL,
			'host': host_string}, 
			mimetype = mime_type)
	
	if format == 'plain':
#		print " 10 jeff /www/django/chemical/structure/views.py PAUL Got to if format == plain"
		if repr(url_method) == '':
			raise Http404	
		return HttpResponse(repr(url_method), mimetype = mime_type)
	elif format == 'xml':
		return render_to_response('structure.xml', {
			'response': response,
			'string': resolved_string,
			'representation': representation,
			'base_url': settings.STRUCTURE_BASE_URL,
			'host': host_string }, 
			mimetype = "text/xml")
			

def structureImage(ensemble, height=240, width=280, fontsize=10, linewidth=1, MIN_WIDTH=240, MAX_WIDTH=280):
	#pdb.set_trace()
	if str(width) == "auto":
		#try:
		smiles_length = len(ensemble['smiles'])
		ring_atoms_cmd = 'ens atoms %s ringatom count' % ensemble.cs_handle
		ring_atom_count = int(ensemble.cs_client_object.cmd(ring_atoms_cmd))
		width = (smiles_length * 15) - (15 * ring_atom_count)
		#except:
		#	width = MAX_WIDTH
	if width <= MIN_WIDTH: width = MIN_WIDTH
	if width >= MAX_WIDTH: width = MAX_WIDTH
	
	hashisy = ensemble['hashisy']
	filename = os.path.join("tmp", "structure_%s_%s_%s_%s_%s_%s_%s.gif" % (hashisy,height,width,fontsize,linewidth,MIN_WIDTH,MAX_WIDTH))
	
	image = ensemble.get_image(
		www_media_path=settings.MEDIA_ROOT,
		filename=filename, 
		parameters={'height': height, 'width': width, 'symbolfontsize': fontsize, 'linewidth': linewidth}
	)
	
	#fname = os.path.join("tmp", "structure_%s_%s_%s_%s_%s_%s_%s.gif" % (hashisy,height,width,fontsize,linewidth,MIN_WIDTH,MAX_WIDTH))
	#imageFileName = os.path.join(settings.MEDIA_ROOT, fname)
	#f = open(imageFileName, 'w')
	#imageFile = File(f)
	#imageFile.write(image.image)
	#imageFile.close()
	#imageFile.url = os.path.join(settings.MEDIA_URL, image.filename[1:])
	image.url = os.path.join(settings.MEDIA_URL, filename)
	image.height = height
	image.width = width
	image.fontsize = fontsize
	image.linewidth = linewidth
	
	return image
	




