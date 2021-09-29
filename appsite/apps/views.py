import os
import datetime
import time

from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

#from django.core.paginator import Paginator
from django.shortcuts import render_to_response
from django.conf import settings 
from django.http import *
from django.http import HttpResponse 

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout as openid_logout

from django.template import RequestContext
from django.template.defaultfilters import striptags

#from django.utils import simplejson
import json

import chemical.apps.forms

from chemical.response import Response, ResponseGroup, ResponseItem, ResponseCreator, AppViews
from chemical.loader import *

from csdb.base import *
from csdb.schema import *

from csdb.media.creator import StructureMediaCreator
from csdb.activity.views import ActivityGusarViews
from csdb.database.views import DatabaseViews

from chemical.structure.resolver import ChemicalString

# temporary here 

class ContextBuilder(object):
	
	def __init__(self, request, context_name, app_name):
		context = {
			'apps': {
				'app_name': app_name,
				'add_structure_form': chemical.apps.forms.AppsAddStructureForm,
				'base_url': settings.BASE_URL,
				'apps_base_url': settings.APPS_BASE_URL,
				'structure_base_url': settings.STRUCTURE_BASE_URL,
				'database_base_url': settings.DATABASE_BASE_URL,
				'forward_url': settings.APPS_BASE_URL,
				'app_url': settings.APPS_BASE_URL,
				'user_string_parameter': dict(request.GET.lists()).get('string', None)
			},
			'csdb': {
				'app_name': app_name,
				'base_url': settings.BASE_URL,
				'apps_base_url': settings.APPS_BASE_URL,
				'structure_base_url': settings.STRUCTURE_BASE_URL,
				'database_base_url': settings.DATABASE_BASE_URL,
				'forward_url': settings.APPS_BASE_URL + '/csdb',
				'app_url': settings.APPS_BASE_URL + '/csdb',
			},
			'cir': {
				'app_name': app_name,
				'app_string': 'Chemical Identifier Resolver',
				'app_theme': 'j',
				'form': chemical.apps.forms.CIRForm,
				'base_url': settings.BASE_URL,
				'apps_base_url': settings.APPS_BASE_URL,
				'structure_base_url': settings.STRUCTURE_BASE_URL,
				'file_base_url': settings.FILE_BASE_URL,
				'forward_url': settings.APPS_BASE_URL + '/cir',
				'app_url': settings.APPS_BASE_URL + '/cir',
			},
			'csls': {
				'app_name': app_name,
				'app_string': 'Chemical Structure Lookup Service',
				'app_theme': 'i',
				'form': chemical.apps.forms.CSLSForm,
				'base_url': settings.BASE_URL,
				'apps_base_url': settings.APPS_BASE_URL,
				'structure_base_url': settings.STRUCTURE_BASE_URL,
				'file_base_url': settings.FILE_BASE_URL,
				'media_base_url': settings.MEDIA_BASE_URL,
				'forward_url': settings.APPS_BASE_URL + '/csls',
				'app_url': settings.APPS_BASE_URL + '/csls',
				'user_string_parameter': dict(request.GET.lists()).get('string', None)
			},
			'cap': {
				'app_name': app_name,
				'app_string': 'Chemical Activity Predictor - GUSAR',
				'app_theme': 'k',
				'add_structure_form': chemical.apps.forms.AppsAddStructureForm,
				'cap_config_form': chemical.apps.forms.CAPForm,
				'base_url': settings.BASE_URL,
				'apps_base_url': settings.APPS_BASE_URL,
				'structure_base_url': settings.STRUCTURE_BASE_URL,
				'file_base_url': settings.FILE_BASE_URL,
				'media_base_url': settings.MEDIA_BASE_URL,
				'forward_url': settings.APPS_BASE_URL + '/cap',
				'app_url': settings.APPS_BASE_URL + '/cap',
				'user_string_parameter': dict(request.GET.lists()).get('string', None)
			},
			'csnc': {
				'app_name': app_name,
				'app_string': 'Chemical Structure Network Creator',
				'app_theme': 'i',
				#'form': chemical.apps.forms.CSLSForm,
				'base_url': settings.BASE_URL,
				'apps_base_url': settings.APPS_BASE_URL,
				#'structure_base_url': settings.STRUCTURE_BASE_URL,
				#'file_base_url': settings.FILE_BASE_URL,
				#'media_base_url': settings.MEDIA_BASE_URL,
				'forward_url': settings.APPS_BASE_URL + '/csnc',
				'app_url': settings.APPS_BASE_URL + '/csnc',
				'user_string_parameter': dict(request.GET.lists()).get('string', None)
			},
			'patent': {
				'app_name': 'patent',
				'form': chemical.apps.forms.PatentForm,
				'add_structure_form': chemical.apps.forms.AppsAddStructureForm,
				'base_url': settings.BASE_URL,
				'apps_base_url': settings.APPS_BASE_URL,
				'structure_base_url': settings.STRUCTURE_BASE_URL,
				#'file_base_url': settings.FILE_BASE_URL,
				#'structure_base_url': settings.STRUCTURE_BASE_URL,
				'forward_url': settings.APPS_BASE_URL + '/patent',
				'app_url': settings.APPS_BASE_URL + '/patent',
			},
			'cfr': {
				'app_name': 'cfr',
				'base_url': settings.BASE_URL,
				'apps_base_url': settings.APPS_BASE_URL,
				'file_base_url': settings.FILE_BASE_URL,
				'forward_url': settings.APPS_BASE_URL + '/cfr',
				'app_url': settings.APPS_BASE_URL + '/cfr',
			},
		}
		for key, value in context[context_name].items():
			setattr(self, key, value)
		self.instance = RequestContext(request, context[context_name])


# Create your views here.

@login_required
def login(request):
	#next_page = request.GET.get('next', None)
	string = "%s %s %s %s :: %s" % (request.user.first_name, request.user.last_name, request.user.email, request.user.last_login, request.session.session_key)
	if next_page:
		#return HttpResponseRedirect(next_page)
		pass
	else:
		return HttpResponse(string, mimetype = 'text/plain')

def logout(request):
	next_page = request.GET.get('next', None)
	string = "Logout %s %s %s %s %s :: %s" % ((next_page), request.user.first_name, request.user.last_name, request.user.email, request.user.last_login, request.session.session_key)
	openid_logout(request)
	if next_page:
		return HttpResponseRedirect(next_page)
	else:
		return HttpResponse(string, mimetype = 'text/plain')


def home(request):
	context = ContextBuilder(request, 'apps', request.session.get('app', 'apps'))
	return render_to_response('home.template', context_instance=context.instance)


def splash(request, app):
	session = request.session
	session['app'] = app
	context = ContextBuilder(request, app, app)
	return render_to_response('splash.template', context_instance=context.instance)


def edit_structures(request, page):
	context = ContextBuilder(request, request.session.get('app', 'apps'), request.session.get('app', 'apps'))
	form = context.add_structure_form(request.POST)
	if page=='structures' or page=='structure_list':
		page='list'
	return render_to_response('edit_structure.template', {
		'form': form,
		'page': page,
	}, 
	context_instance=context.instance)


def editor(request, editor='chemwriter'):
	context = ContextBuilder(request, request.session.get('app', 'apps'), request.session['app'])
	#form = context.form(request.POST)
	#editor_template = 'editor.template' % (editor,)
	return render_to_response('editor.template', {'editor': editor}, context_instance=context.instance)


def info(request):
	context = ContextBuilder(request, 'apps', request.session.get('app', 'apps'))
	#form = context.form(request.POST)
	return render_to_response('info.template', {'form': None}, context_instance=context.instance)


def csls(request):
	context = ContextBuilder(request, 'csls', request.session['app'])
	form = context.form(request.POST)
	return render_to_response('csls/splash.template', {'form': form}, context_instance=context.instance)


def cap(request):
	context = ContextBuilder(request, 'cap', request.session.get('app', 'cap'))
	return render_to_response('cap/splash.template', context_instance=context.instance)


def cap_manual(request, page, name=None):
	context = ContextBuilder(request, 'cap', request.session.get('app', 'cap'))
	#form = context.form(request.POST)
	views = ActivityGusarViews()
	if name:
		view = getattr(views, page)(name)
		if not view:
			raise Http404
	else:
		view = getattr(views, page)
		# ugly:
		if page != 'config':
			view.minor = views.minor(page)

	# ugly, too:
	if page=='endpoint':
		view['description_template_short'] = 'endpoint/%s_short.template' % view['sign']
		view['description_template_long'] = 'endpoint/%s_long.template' % view['sign']
	return render_to_response('cap/manual.template', {
		'views': views,
		'view': view,
		'page': page,
		'name': name,
		'context': context,
	}, context_instance=context.instance)


def csls_manual(request, page, name=None):
	context = ContextBuilder(request, 'csls', request.session['app'])
	views = DatabaseViews()
	if name:
		view = getattr(views, page)(name)
	else:
		view = getattr(views, page)
		# ugly:
		if page != 'config':
			view.minor = views.minor(page)
	return render_to_response('csls/manual.template', {
		'views': views,
		'view': view,
		'page': page,
		'name': name,
		'context': context,
	}, context_instance=context.instance)


def details(request, subpage, string):
	session = request.session
	context = ContextBuilder(request, request.session.get('app', 'apps'), request.session.get('app', 'apps'))
	if session.has_key('app_views'):
		app_views = session['app_views']
	else:
		return HttpResponse('no such view')
	app_views.response_for_item(string)
	return render_to_response('details.template', {
		'response': app_views,
		'item': app_views.response_item,
		'page': string,
		'subpage': subpage,
	}, context_instance=context.instance)


def browse(request, page):
	session = request.session
	context = ContextBuilder(request, request.session.get('app', 'apps'), request.session.get('app', 'apps'))
	if session.has_key('app_views'):
		app_views = session['app_views']
		app_views.response_page(page)
	else:
		page = 'empty'
		app_views = None
		#return HttpResponse('no such view')
	return render_to_response('browse.template', {
		'response': app_views,
		'page': int(page),
		'page_object': app_views.pages.page(page),
		'context': context,
	}, context_instance=context.instance)


def response(request, string=None):
	session = request.session
	page = request.GET.get('page', 1)
	app_views = AppViews()
#	app_views.parse_raw_post_data(request.body)
	app_views.parse_body(request.body)
	app_views.create_app_response(items_per_page=10)
	session['app_views'] = app_views
#1	status = simplejson.dumps(app_views.__dict__['query_string_list'], cls=DjangoJSONEncoder)
	status = json.dumps(app_views.__dict__['query_string_list'], cls=DjangoJSONEncoder)
#	result_json = json.dumps(app_views.__dict__['query_string_list'], cls=DjangoJSONEncoder)
#1	result_json = simplejson.dumps(app_views.__dict__['query_string_list'], cls=DjangoJSONEncoder)
#2	result_json = json.dumps(app_views.__dict__['query_string_list'], cls=DjangoJSONEncoder)
#	status = status.rstrip('\r')
#	return HttpResponse(status)
#	try:
#		http_response = HttpResponse(result_json, status=200)
	http_response = HttpResponse(status, status=200)

#		return http_response
#		return HttpResponse(result_json)
#		response = HttpResponse(result_json)
#	response = HttpResponse(status)
#	response = HttpResponse(status, content_type='text/html', charset='utf-8')
	response = HttpResponse(status, content_type='text/html')
#	response = response.replace('\r', '')
#	response = response.rstrip('\r')
#		return HttpResponse("aspirin")
#		return HttpResponse(result_json,response)
#		return HttpResponse(result_json)
	return HttpResponse(status)
#	return HttpResponse("aspirin")
#		return HttpResponse(result_json,content_type="text/html")
#		return HttpResponse(result_json,'application/json')
#		return HttpResponse(result_json,content_type="application/xhtml+xml")
