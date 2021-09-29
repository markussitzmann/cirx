import os
import time
import datetime
import math

from django.core.files import File
from django.views.decorators.vary import vary_on_headers
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.template import Template, Context
from django.conf import settings 
from django.http import *
from django.utils import simplejson

from django.core.urlresolvers import reverse

from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

#from django.contrib.auth.decorators import login_required
#from django.contrib.auth.models import User
#from django.contrib.auth import logout

from chemical.response import Response, ResponseGroup, ResponseItem, DataViews, DataView


from csdb.base import *

from csdb.activity.db.schema import *
from csdb.activity.creator import GusarDataCreator
from csdb.activity.views import ActivityGusarViews, ActivityView
from csdb.media.db.schema import *


def endpoint_url_urn_uri(category, model, endpoint):
	host = settings.HOSTNAME
	url = 'http://%s%s' % (host, reverse('chemical.activity.views.endpoint'))
	urn = '%s/%s/%s' % (category, model, endpoint,)
	uri = '%s/%s' % (url, urn)
	return {'url': url, 'urn': urn, 'uri': uri}


def endpoint(request, category=None, model=None, endpoint=None):
	try:
		view = ActivityGusarViews().endpoints
		if category:
			view = DataView(view.group_by('category_sign')[category])
			data = view.as_list
			if model:
				view = DataView(view.group_by('model_sign')[model])
				data = view.as_list
				if endpoint:
					view = DataView(view.group_by('sign')[endpoint])
					data = view.as_list
		else:
			data = view.as_list
		if len(data)==0:
			raise Http404
		json_view = [
			{
				'name': d['name'],
				'uri': endpoint_url_urn_uri(d['category_object'].sign, d['model_object'].sign, d['sign'],)['uri'],
				'urn': endpoint_url_urn_uri(d['category_object'].sign, d['model_object'].sign, d['sign'],)['urn'],
				'unit': d['unit'],
				'type': d['type'],
			}
			for d in data
		]
		return HttpResponse(simplejson.dumps(json_view, cls=DjangoJSONEncoder), content_type='application/javascript, charset=utf8')
	except:
		return HttpResponse(status=400)


def predictor(request, query, category=None, model=None, endpoint=None):
	try:
		if not endpoint:
			model_endpoint_view = ActivityGusarViews().endpoints.group_by('model_sign')[model]
			model_endpoint_hash_list = [e['hash'] for e in model_endpoint_view]
		else:
			model_endpoint_view = ActivityGusarViews().endpoints.group_by('model_sign')[model]
			model_endpoint_hash_list = [dict([(e['sign'],e['hash']) for e in model_endpoint_view])[endpoint],]
		endpoint_hash_list = model_endpoint_hash_list
		data_view = DataViews()
		data_view.parse_query_data([query,])
		data_view_response = data_view.create_response(media_request_list=['hashisy', 'stdinchikey'], activity_endpoint_list=model_endpoint_hash_list)
		activity_data = dict([
			(
				item,[dict([
					(k,v) for k,v in DataView([{'hash': a['endpoint_object'].hash, 'data': {
						'endpoint': {
							'urn': endpoint_url_urn_uri(a['category_object'].sign, a['model_object'].sign, a['sign'])['urn'],
							'uri': endpoint_url_urn_uri(a['category_object'].sign, a['model_object'].sign, a['sign'])['uri'],
						},
						'in_AD': a['in_AD'],
						'type': a['type'],
						'unit': a['unit'],
						'float': a['float'],
						'string': a['string'],
					}} for a in item.activity_data]).group_by('hash')[H][0]['data'].items()
				]) for H in endpoint_hash_list]
			)
			for item in data_view_response.response.item_list
		])
		grouped = DataView([{'group': item.group, 'item': item, 'activity_data': activity_data_list} for item, activity_data_list in activity_data.items()]).group_by('group')
		if len(grouped.items())==0:
			raise Http404
		json_data = [{
				'query': k.query, 
				'data': [{
					'resolver': vv['item'].resolver_data['chemical_string_type'],
					'notation': vv['item'].resolver_data['chemical_string_notation'],
					'smiles': vv['item'].resolver_data['structure_smiles'],
					'activity_data': vv['activity_data']
				} for vv in v],
			} for k,v in grouped.items()]
		return HttpResponse(simplejson.dumps(json_data), content_type='application/javascript, charset=utf8')
	except:
		return HttpResponse(status=400)



