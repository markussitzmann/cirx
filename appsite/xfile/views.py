#import os
import time
import datetime
import base64
#import codecs

from django.utils import simplejson

from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.vary import vary_on_headers
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core import serializers
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.template import Template, Context
from django.conf import settings 
from django.http import *

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout

# A view to report back on upload progress:

from django.core.cache import cache
from django.http import HttpResponse, HttpResponseServerError 

from models import *
from chemical.file.base import *
from chemical.file.user_file_processor import *
from chemical.file.forms import *
from chemical.structure.resolver import *

#from chemical.aux.database import *

#from viewer import *

_cactvs_loader = __import__(settings.CACTVS_PATH, globals(), locals(), settings.CACTVS_FROMLIST)
Cactvs = _cactvs_loader.Cactvs
Ens = _cactvs_loader.Ens
Dataset = _cactvs_loader.Dataset
Molfile = _cactvs_loader.Molfile
CactvsError = _cactvs_loader.CactvsError

def test(request):
	return render_to_response('test.template')	

def preload(request, file_identifier='last'):
	session = request.session
	user = request.user
	user_file = get_user_file_from_session(session, user, file_identifier)
	if user_file:
		file = UserFileProcessor(user_file=user_file).preload()
		return HttpResponse(file.events_with_structures())
	return HttpResponse('failed')

def view(request, file_identifier=None):
	session = request.session
	user = request.user
	upload_key = FileKey().get()
	file_form = ChemicalFileUpload(request.POST, request.FILES)
	chemical_string_form = ChemicalStringInput()
	user_file = get_user_file_from_session(session, user, file_identifier)
	viewer = Viewer()
	file = UserFileProcessor(user_file=user_file)
	if user_file:
		file = UserFileProcessor(user_file=user_file).preload()
	return render_to_response('viewer.template', {
		'session': session,
		'user': user,
		'file': file,
		'file_list': session['user_file_dict'][user],
		'file_form': file_form,
		'chemical_string_form': chemical_string_form,
		'upload_key': upload_key,
		'base_url': settings.BASE_URL,
		'apps_base_url': settings.APPS_BASE_URL,
		'file_base_url': settings.FILE_BASE_URL,
		'forward_target': settings.FILE_BASE_URL,
		't': 'test'		
	})

def lookup(request, string):
	session, user = request.session, request.user
	user_file = get_user_file_from_session(session, user, 'result_file')
	structure_data_list = [string,]
	if not user_file:
		processor = UserFileProcessor(
			user=user,
			original_filename="search_results",
			display_name="Search Results",
			date_invalid=session.get_expiry_date(),
			result_file=True,
			structure_data_list=structure_data_list
		)
		user_file = processor.create_user_file().attach_to_session(session).user_file
	else:
		processor = UserFileProcessor(
			user_file=user_file,
			structure_data_list=structure_data_list,
		)
	event_string = 'Lookup by string "%s"' % (string,) 
	processor.attach_event(string=event_string)
	processor.resolve()
	processor.load_into_database()
	processor.normalize()

	return HttpResponse(user_file)


def add(request, file_identifier, chemical_string):
	session = request.session
	user = request.user
	user_file = get_user_file_from_session(session, user, file_identifier)
	upload = Upload(user_file=user_file, structure_data_list=[chemical_string])
	upload.resolve()
	upload.process()
	z = None	
	r = 'added %s %s' % (file_identifier, z)
	return HttpResponse(r)
	

def delete(request, file_identifier):
	session = request.session
	user = request.user
	user_file = get_user_file_from_session(session, user, file_identifier)
	user_file.delete()
	session['user_file_list'].remove(user_file)
	return HttpResponse('deleted')





#def database_tab(request, file_identifier):
	#session = request.session
	#user = request.user
	#user_file = get_user_file_from_session(session, user, file_identifier)
	#viewer=None
	
	#t = user_file.databases.all()
	
	#return render_to_response('viewer-database-tab.template', {'t': t})


#def identifier_tab(request, file_identifier):
	#session = request.session
	#user = request.user
	
	#viewer = Viewer()
	#user_file = get_user_file_from_session(session, user, file_identifier)
	
	#if user_file:
		#file = PreloadedUserFile(user_file)
		#if file:
			#viewer.show(file)
	
	#return render_to_response('viewer-identifier-tab.template', {'viewer': viewer,})


#def structure_tab(request, file_identifier):
	#session = request.session
	#user = request.user
	
	#user_file = get_user_file_from_session(session, user, file_identifier)
	
	#viewer = Viewer()
	
	##user_file.base_name = user_file.name.split('.')[0]
	#if user_file:
		#viewer.show(user_file)
	
	#return render_to_response('viewer-structure-tab.template', {'viewer': viewer})


#def view_structure(request, file_identifier, record_identifier):
	#session = request.session
	#file_id = int(file_identifier)
	#record_id = int(record_identifier)
	#viewer = Viewer()
	#if session['user_file_list'][file_id]:
		#file = session['user_file_list'][file_id]
		#user_structure = file.structures.filter(record=record_id).get()
		#if user_structure:
			#viewer.load_user_structure(user_structure)
	
	#return render_to_response('viewer-structure.template', {'viewer': viewer, 'user_structure': user_structure,})


def file_list(request):
	session = request.session
	user = request.user
	#string = 'uploaded %s %s %s' % (session_object.items(), session_object['file'], dir(session_object['file'][0]))
	return render_to_response('list.template', {'files': session['user_file_dict'][user]})


def upload(request):
	session = request.session
	user = request.user
	session.set_test_cookie()
	if request.method == 'POST':
		form = ChemicalFileUpload(request.POST, request.FILES)
		if form.is_valid():
			
			session.set_expiry(60*60*24*7)
			session_key = session.session_key
			if not session.has_key('user_file_dict'):
				session['user_file_dict'] = {}
				
			if not request.user.is_anonymous():
				date_invalid = None
				session['user_file_dict'][user] = list(UserFile.objects.filter(user=user))
			else:
				date_invalid = session.get_expiry_date()
				if not session['user_file_dict'].has_key(user):
					session['user_file_dict'][user] = []
			
			key = request.POST['upload_key']
			
			original_filename, display_name, server_filename = prepare_upload_file(request, form.cleaned_data['string'])
			
			upload = UserFileProcessor(
				user = user,
				key = key,
				date_invalid = date_invalid,
				original_filename = original_filename,
				display_name = display_name,
				server_filename = server_filename
			)
			
			upload.create_user_file()
			upload.resolve()
			
			event_string = 'Upload of file "%s"' % (original_filename,) 
			upload.attach_event(string=event_string)
			
			upload.load_into_database()
			upload.attach_to_session(session)
			
		else:
			raise UserFileProcessorError('form not valid') 
	else:
		raise UserFileProcessorError('upload failed') 
	to_url = 'latest'
	return HttpResponse()
	#return render_to_response('upload.template', {'form': form, 'session': session, 'upload_key': uploaded_key})
	

def upload_progress(request):
	"""
	Return JSON object with information about the progress of an upload.
	"""
	progress_id = ''
	if 'X-Progress-ID' in request.GET:
		progress_id = request.GET['X-Progress-ID']
	elif 'X-Progress-ID' in request.META:
		progress_id = request.META['X-Progress-ID']
	if progress_id:
		cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
		cache_data = cache.get(cache_key)
		data = {}
		if cache_data:
			progress = float(cache_data['uploaded']) / float(cache_data['length'])
			data['progress'] = progress
			#data['progress'] = cache_data
		else:
			data['progress'] = None
		return HttpResponse(simplejson.dumps(data))
 	else:
		return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')


def processing_status(request, string):
	from django.utils import simplejson
	
	session = request.session
	user_file = UserFileKey.objects.filter(upload=string)[0].user_file
	
	data = {}
	data['records'] = user_file.records
	data['processed'] = user_file.structures.count()
	data['file_name'] = user_file.name
	return HttpResponse(simplejson.dumps(data))

def download(request, file_identifier):
	session = request.session
	user = request.user
	user_file = get_user_file_from_session(session, user, file_identifier)
	format = request.GET.get('format', 'sdf')
	get3d = request.GET.get('get3d', 0)
	download = UserFileProcessor(user_file=user_file, download_format=format)
	file = download.create_from_database().download_file
	if file:
		response = HttpResponse(file, mimetype='text/plain')
		response['Content-Disposition'] = 'attachment; filename=' + file.download_name
	else:
		raise Http500
	return response


### the REST stuff

def post(request):
	
	session = request.session
	session.set_test_cookie()
	
	date_invalid = datetime.datetime.now()+datetime.timedelta(days=30)

	#s = "%s\n----------\n%s\n----------\n%s" % (request, request.FILES, request.raw_post_data)
	#return HttpResponse(s)

	if request.method == 'POST':
		session.set_expiry(date_invalid)
		upload_key = FileKey().get()
		original_name, display_name, server_filename = prepare_upload_file(request, upload_key)
		processor = UserFileProcessor(
			key = upload_key,
			date_invalid = date_invalid,
			server_filename = server_filename,
			original_filename = original_name,
			do_identifier_lookup = False,
			do_database_lookup = False,
		)
		processor.create_user_file()
		processor.resolve()
		processor.load_into_database()
		user_file = processor.user_file
		
		private_key = user_file.key.private

		format = request.POST.get('format', None)
		if not format:
			format = request.POST.get('download', None)
		if format:
			return get(
				request = request,
				key = private_key,
				format = format
			)
		else:
			response = {'private_key': private_key}
			#return HttpResponse(simplejson.dumps(response))
			return HttpResponse(response['private_key'] + '\n')
		

def get(request, key, format=None, records=None, get3d=None):
	if not format:
		format = request.GET.get('format', None)
	if not format:
		format = request.GET.get('download', None)	
	if not records:
		records = request.GET.get('records', None)
	if not get3d:
		get3d = request.GET.get('get3d', 0)
	user_file = UserFile.objects.get(key__private=key)
	p = UserFileProcessor(
		user_file = user_file,
		download_format = format,
	)
	download_file = p.create_from_database(
		only_records=str(records),
		calculate_3d=str(get3d),
	).download_file
	return HttpResponse(download_file, mimetype='text/plain')


def fields(request, key):
	user_file = UserFile.objects.get(key__private=key)
	fields = '\n'.join([f['original_name'] for f in UserFile.objects.filter(key__private = key).get().fields.all().values()])
	return HttpResponse(fields, mimetype='text/plain')




# ------------ below this we need a clean up ---------------------


		
