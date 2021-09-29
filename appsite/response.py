import random
import json
import datetime

from operator import itemgetter

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from chemical.structure.resolver import ChemicalString
from chemical.loader import *


from csdb.base import *
from csdb.schema import *
from csdb.tool.base import *

from csdb.media.creator import StructureMediaCreator
from csdb.activity.creator import GusarDataCreator
from csdb.media.views import *
from csdb.activity.views import *

from csdb.views import *

from csdb.structure.db.schema import Structure, structure_table
from csdb.compound.db.schema import Compound, compound_table

class DataView(ViewsBase):
	def __init__(self, rows):
		#self.session = session
		self.rows = rows
		super(DataView, self).__init__()
		
	@property
	def as_list(self):
		return self.rows

	@property
	def row_keys(self):
		return self.rows[0].keys()

	#def insert_group_splitter(self, key):
		#for row in self.rows:
			#if


class DataViews(object):
#jds 2017-11-27	def __init__(self, rows):
	def __init__(self):
		self.data = {}
		self.query_string_list = []
		self.query_string_hash_list	= []
		self.query_data = []

	def _unique_query_list(self, L, key=None):
		if key is None:
			def key(x):
				return x
		seen = set()
		n = iter(xrange(len(L) - 1, -2, -1))
		for x in xrange(len(L) - 1, -1, -1):
			item = L[x]
			k = key(item)
			if k not in seen:
				seen.add(k)
				L[next(n)] = item
		L[:next(n) + 1] = []

	def parse_query_data(self, query_data):
		data = self.data
		timestamp = datetime.datetime.now()
		self.query_string_list = query_data
		self._unique_query_list(self.query_string_list)
		i = iter(range(1, len(self.query_string_list) + 1))
		self.query_data.extend([
			{'index': i.next(), 'hash': md5string(query_string), 'query': query_string, 'timestamp': timestamp} 
			for query_string in self.query_string_list
		])
		self.query_data_grouped = DataView(self.query_data).group_by('query')
		self.query_string_hash_list = list(set([md5string(s) for s in self.query_string_list]))
		return cmp(data, self.data)

	def create_response(self, items_per_page=25, media_request_list=['hashisy'], activity_model_list=[], activity_endpoint_list=[]):
		self.response = ResponseCreator(
			self.query_string_list,
			media_request_list=media_request_list,
			activity_model_list=activity_model_list,
			activity_endpoint_list=activity_endpoint_list
		).response
		self.response_query_item_keys = dict([
			(k, [vv['item_key'] for vv in v]) 
			for k,v in AppView([
				{'query': i.group.query, 'item_key': i.random_key} 
				for i in self.response.item_list]
				).group_by('query').items()]
			)
		self.response_group_item_keys = dict([
			(k, [vv['item_key'] for vv in v]) 
			for k,v in AppView([
				{'group_key': i.group.random_key, 'item_key': i.random_key} 
				for i in self.response.item_list]
				).group_by('group_key').items()]
			)
		self.presorted_item_list = [i['o'] for i in DataView([{
			'i': str(i.group.index), 
			't': str(i.group.query_type), 
			'q': str(i.group.query), 
			'n': str(i.resolver_data['chemical_string_notation']),
			'o': i
			} for i in self.response.item_list]).multikey_natural_sorted_by(['i', 'n']).as_list]

		if items_per_page:
			self.pages = Paginator(self.response.item_list, items_per_page)	
		return self

	def response_for_item(self, item_key):
		# CLEAN UP !!!!!
		self.response_with_timestamp = DataView([
			{
				'query_index': self.query_data_grouped[item.group.query][0]['index'],
				'timestamp': self.query_data_grouped[item.group.query][0]['timestamp'], 
				'query': item.group.query,
				'group': item.group,
				'item': item
			}
			for item in self.response.item_list
			if item.random_key==item_key
		])
		self.response_grouped_by_timestamp = self.response_with_timestamp.group_by('timestamp')
		self.response_query_item_notations = dict(
			[
				(item.random_key, item.resolver_data['chemical_string_notation'])
				if item.resolver_data['chemical_string_notation']!=item.group.query else
				(item.random_key, item.resolver_data['chemical_string_type'])
				for item in self.response.item_list
				if item_key in self.response_group_item_keys[item.group.random_key]
			]
		)
		self.response_item = [item for item in self.response.item_list if item.random_key==item_key][0]
		return self

	def response_page(self, number):
		if self.pages:
			try:
				page = self.pages.page(number)
			except PageNotAnInteger:
				page = self.pages.page(1)
			except EmptyPage:
				page = self.pages.page(self.pages.num_pages)
			def page_item_index():
				for i in range(len(page.object_list)):
					yield i + 1
			g = page_item_index()
			self.response_with_timestamp = DataView([
				{
					'query_index': self.query_data_grouped[item.group.query][0]['index'],
					'timestamp': self.query_data_grouped[item.group.query][0]['timestamp'], 
					'query': item.group.query,
					'group': item.group,
					'item': item,
					'item_page_index': g.next(),
				} 
				for item in page.object_list
			])

			# CLEAN UP !!!!!
			self.response_grouped_by_timestamp = self.response_with_timestamp.group_by('timestamp')
			#self.response_page_data_by_timestamp = [
			#	{
			#		'timestamp': k, 
			#		'page_groups':DataView(v).group_by('group')
			#	}
			#	for k, v in self.response_grouped_by_timestamp.items()
			#]
			self.response_grouped_by_query_index = self.response_with_timestamp.group_by('query_index')
			self.response_page_data_by_query_index = [
				{
					'query_index': k, 
					#'page_groups': DataView(v).group_by('group')
					'page_groups': DataView(v).group_by('group')
				}
				for k, v in self.response_grouped_by_query_index.items()
			]
		else:
			self.page_groups_and_items = []
			self.grouped_response_page = DataView()
			self.response_with_timestamp = DataView()
			self.response_grouped_by_timestamp = {}
			#self.response_page_data_by_timestamp = []
			self.response_grouped_by_query_index = {}
			self.response_page_data_by_query_index = []
		return self

	@property
	def page_list(self):
		if self.pages:
			return range(1,self.pages.num_pages+1)
		else:
			return []

	@property
	def page_num(self):
		return len(self.page_list)


class AppView(ViewsBase):
	def __init__(self, rows):
		#self.session = session
		self.rows = rows
		super(AppView, self).__init__()
		
	@property
	def as_list(self):
		return self.rows

	@property
	def row_keys(self):
		return self.rows[0].keys()


class AppViews(DataViews):
	def __init__(self):
		super(AppViews, self).__init__()

	def parse_body(self, body):
		timestamp = datetime.datetime.now()
		self.data = json.loads(body)
		#self.query_string_list = self.data['user_data']['term_array']
		self.current_app = self.data['app']
		self.model_switch_list = [int(z[2]) for z in [[s for s in e.split('-')] for e in self.data['user_data']['switch_array']] if len(z)>0 and z[0]=='model']
		return self.parse_query_data(self.data['user_data']['term_array'])

	def create_app_response(self, items_per_page=25):
		return self.create_response(
			items_per_page=items_per_page,
			media_request_list=['sdf', 'sdf_hspecial', 'hashisy'],
			activity_model_list=self.model_switch_list
		)


class ResolverViews(ViewsBase):
	def __init__(self, query_string_list = []):
		#self.session = session
		self.query_string_list = query_string_list
		super(ResolverViews, self).__init__()
		self._structures_and_compounds = None
		self._preload_objects = True
		self._resolved_strings = None

	@property
	def resolved_strings(self, deduplicate_by_hashisy=True):
		if not self._resolved_strings:
			chemical_strings = [(md5string(string.strip()), string.strip(), ChemicalString(string=string)) for string in self.query_string_list]
			string_length = sum([len(s) for s in chemical_strings])
			#i = iter(range(1,string_length+2))
			rows = []			
			[[rows.extend([dict((
				#('index', i.next()),
				('query_hash_key', string_hash),
				('query_string', string),
				('structure_id', structure.object.id),
				('structure_smiles', structure.ens.get('smiles')),
				('structure_smiles_hash', md5string(structure.ens.get('smiles'))),
				('media_request', structure.ens.get('smiles')),
				('media_hash_key', md5string(structure.ens.get('smiles'))),
				('structure_hashisy', structure.ens.get('hashisy')),
				('chemical_string_type', structure.metadata['query_type']),
				('chemical_string_notation', structure.metadata['description'])
			))
			for structure in interpretation.structures])
			for interpretation in chemical_string.interpretations]
			for string_hash, string, chemical_string in chemical_strings]
			view = ResolverView(rows)
			
			if deduplicate_by_hashisy:
				# if a query creates identical structures from different modules take only the first one
				# first group by query, then by hashisy, create new view:
				V=[]
				[[V.extend([vv[0],]) for kk, vv in ResolverView(v).group_by('structure_hashisy').items()] for k,v in view.group_by('query_hash_key').items()]
				view = ResolverView(V)
			#view.multikey_natural_sorted_by(['chemical_string_notation'])
			#view.natural_sorted_by('index')
			#view.natural_sorted_by('chemical_string_notation')
			self._resolved_strings = view
		if self._preload_objects:
			pass
		return self._resolved_strings

	@property
	def structures_and_compounds(self):
		if not self._structures_and_compounds:
			t1, t2 = structure_table, compound_table
			from_obj = t1.join(t2)
			filter_criterion=or_(*[structure_table.c.id==row['structure_id'] for row in self.rows])
			q = select([
				t1.c.id.label('structure_id'),
				t2.c.id.label('compound_id'),
			], from_obj=from_obj).where(filter_criterion).order_by('structure_id')
			rows = q.execute().fetchall()
			view = ResolverView([dict(row.items()) for row in rows])
			self._structures_and_compounds = view
		if self._preload_objects:
			self._structures_and_compounds.preload_objects([
				('structure_object', Structure, structure_table.c.id, 'structure_id'),
				('compound_object', Compound, compound_table.c.id, 'compound_id'),
			])
		return self._structures_and_compounds

	@property
	def media_requests(self):
		return self.resolved_strings.group_by('media_request').keys()

	@property
	def query_media_hash_keys(self):
		keys = dict([(k, [(vv['chemical_string_type'], vv['media_hash_key']) for vv in v]) for k, v in self.resolved_strings.group_by('query_string').items()])
		grouped_keys = {}
		for k,v in keys.items():
			d = defaultdict(list)
			[d[vv[0]].append(vv[1]) for vv in v]
			grouped_keys[k] = dict(d)
		return grouped_keys

	def __getstate__(self):
		odict = self.__dict__.copy()
		#del odict['session']  
		return odict

	def __setstate__(self, state):
		self.__dict__.update(state)


class ResolverView(ViewsBase):
	def __init__(self, rows):
		#self.session = session
		self.rows = rows
		super(ResolverView, self).__init__()
		
	@property
	def as_list(self):
		return self.rows

	@property
	def row_keys(self):
		return self.rows[0].keys()


class ResponseCreator(object):
	def __init__(self, query_list, media_request_list=[], activity_endpoint_list=[], activity_model_list=[]):
		self._resolver = ResolverViews(query_list)
		if media_request_list:
			self._media_hash_list = MediaViews().media_name_to_hash_list(media_request_list)
			self._media_creator = StructureMediaCreator(self._resolver.media_requests, self._media_hash_list)
			self._media_view = MediaViews(self._resolver.media_requests, self._media_hash_list)
			self._media_data = self._media_view.media.group_by('media_hash_key')
		if activity_endpoint_list or activity_model_list:
			if activity_endpoint_list:
				self._activity_hash_list = ActivityGusarViews().endpoints_to_hash_list(activity_endpoint_list)
			if activity_model_list:
				self._activity_hash_list = ActivityGusarViews().models_to_hash_list(activity_model_list)
			#print self._activity_hash_list
			self._activity_creator = GusarDataCreator(self._resolver.media_requests, self._activity_hash_list)
			self._activity_view = ActivityGusarViews(self._resolver.media_requests, self._activity_hash_list)
			self._activity_data = self._activity_view.data.group_by('media_hash_key')
		else:
			self._activity_creator = None
			self._activity_hash_list = []
			self._activity_view = None
			self._activity_data = None
	
		self.response = Response()

		resolver_data = self._resolver.resolved_strings.group_by('query_string')

		qindex, iindex = 0, 0
		for query, query_type_and_media_key in self._resolver.query_media_hash_keys.items():
			response_group = ResponseGroup(self.response)
			iindex0 = 1
			for q in query_type_and_media_key.items():
				#response_group = ResponseGroup(self.response)
				qindex += 1
				qtype, media_hash_keys = q
				response_group.query_type = qtype
				response_group.index = qindex
				response_group.query = query
				for k in media_hash_keys:
					iindex += 1
					response_item = ResponseItem(response_group)
					response_item.index = iindex
					response_item.index0 = iindex0
					iindex0 = 0
					response_item.resolver_data = ResolverView(resolver_data[query]).group_by('media_hash_key')[k][0]
					# media 
					response_item.media_data = self._media_data.get(k, {})
					media_types = ResolverView(response_item.media_data).group_by('media_type')
					response_item.media = dict([(t, m[0]['media_string']) for t, m in media_types.items()])
					# activity
					if self._activity_data:
						response_item.activity_data = self._activity_data.get(k, {})
						response_item.activity_by_model = ActivityView(response_item.activity_data).group_by('model_object')
					

class Response(object):
	def __init__(self, compound_list=[]):
		self.group_list = []
		self.item_list = []


class ResponseGroup(Response):
	def __init__(self, response_object):
		self.item_list = []
		self.response = response_object
		super(ResponseGroup, self).__init__()
		self.response.group_list.append(self)
		self.random_key = '%032x' % random.getrandbits(128)


class ResponseItem(Response):
	def __init__(self, group_object):
		self.group = group_object
		self.response = self.group.response
		super(ResponseItem, self).__init__()
		self.group.item_list.append(self)
		self.response.item_list.append(self)
		self.random_key = '%032x' % random.getrandbits(128)
		
	
