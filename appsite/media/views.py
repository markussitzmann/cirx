import datetime
import time

from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
#from django.core.paginator import Paginator
from django.shortcuts import render_to_response
from django.conf import settings 
from django.http import *

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout as openid_logout

from django.template import RequestContext
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder

from csdb.base import *
from csdb.schema import *

from csdb.media.creator import StructureMediaCreator
from csdb.tool.base import *

from chemical.structure.resolver import ChemicalString

from chemical.response import *


def media(request):
	string_list = (dict(request.GET.lists()).get('string', None))
	config_hash_list = (dict(request.GET.lists()).get('config', None))
	media_request = dict([(i,i) for i in config_hash_list])
	response = Response()
	#response.resolve_string_list(string_list).load_structure_objects().load_media(media_request).load_database_records()
	response.resolve_string_list(string_list).load_structure_objects().load_media(media_request)
	data = dict([
		(group.query, dict([(item.query_type, [dict([(config, getattr(response, config)[structure['hash']]) for config in config_hash_list]) for structure in item.structure_list]) for item in group.item_list])) for group in response.group_list
	])
	return HttpResponse(simplejson.dumps(data), content_type='application/javascript, charset=utf8')


def db_media(request):
	media_request={
		'image': '07c6c4160b0ff903bdc0de9c18036a25',
		'test': '20f6ad910b6ffbc247bf1bdc5f565f5a',
	}
	string_list = (dict(request.GET.lists()).get('string', None))
	config_hash_list = (dict(request.GET.lists()).get('config', None))
	if config_hash_list:
		media_request.update(dict([(i,i) for i in config_hash_list]))
	response = Response()
	response.resolve_string_list(string_list).load_structure_objects().load_media(media_request).load_dataset_records()

	data = dict([
		(
			group.query, 
			dict([
				(item.query_type, {
					'media': [
						dict([
							(media_key, getattr(response, media_key)[structure['hash']]) for media_key in media_request.keys()
						]) for structure in item.structure_list
					],
					'compound': response.structure_compound_list[structure['id']].id,
					'dataset_record_count': response.short_database_record_count.get(response.structure_compound_list[structure['id']].id, None),
					'test': 'test'
				})
				for item in group.item_list
			])
		)
		for group in response.group_list
	])

	return HttpResponse(simplejson.dumps(data, cls=DjangoJSONEncoder), content_type='application/javascript, charset=utf8')


def media_config(request):
	config_list = csdb_session.query(MediaConfig).all()
	response = simplejson.dumps(dict([(config.hash, {'type': config.type.string, 'string': config.string}) for config in config_list]))
	return HttpResponse(response, content_type='application/javascript, charset=utf8')







