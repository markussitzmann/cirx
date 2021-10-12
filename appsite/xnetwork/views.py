# import datetime
# import time
#
# from django.core.exceptions import ObjectDoesNotExist
# from django.core import serializers
# #from django.core.paginator import Paginator
# from django.shortcuts import render_to_response
# from django.conf import settings
# from django.http import *
#
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
# from django.contrib.auth import logout as openid_logout
#
# from django.template import RequestContext
# from django.utils import simplejson
# from django.core.serializers.json import DjangoJSONEncoder
#
# from csdb.base import *
# from csdb.schema import *
#
# from csdb.network.db.schema import *
#
# #from csdb.media.creator import StructureMediaCreator
# #from csdb.tool.base import *
#
# #from chemical.structure.resolver import ChemicalString
#
# #from chemical.apps.response import *
#
#
# def network(request):
# 	#string_list = (dict(request.GET.lists()).get('string', None))
# 	#config_hash_list = (dict(request.GET.lists()).get('config', None))
# 	#media_request = dict([(i,i) for i in config_hash_list])
# 	#response = Response()
# 	##response.resolve_string_list(string_list).load_structure_objects().load_media(media_request).load_database_records()
# 	#response.resolve_string_list(string_list).load_structure_objects().load_media(media_request)
# 	#data = dict([
# 		#(group.query, dict([(item.query_type, [dict([(config, getattr(response, config)[structure['hash']]) for config in config_hash_list]) for structure in item.structure_list]) for item in group.item_list])) for group in response.group_list
# 	#])
#
# 	n = csdb_session.query(Network).filter(Network.string=="C1=C(C=CC(=C1)C)C(C(C2=CC=CC=C2)=O)O").one()
#
# 	vertices = [ {'name': v.hash, 'group': 1} for v in n.vertices ]
# 	connections = [ {'source': c.vertex_label_1 - 1, 'target': c.vertex_label_2 - 1, 'value': 1} for c in n.connections ]
#
# 	data = {'nodes': vertices, 'links': connections}
#
# 	return HttpResponse(simplejson.dumps(data), content_type='application/javascript, charset=utf8')
#
#
#
#
#
