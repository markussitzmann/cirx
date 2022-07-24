import os
import time
import datetime
import base64
import codecs

from csdb.tool.cactvs_script import *

from django.conf import settings
from django.core.files import File

from chemical.structure.resolver import *
from chemical.file.models import *

from chemical.file.filekey import FileKey


class PreloadedUserFile():
	
	def __init__(self, user_file):	
		try:
			user_file = UserFile.objects.select_related().order_by('records').get(id=user_file.id)
			self.object = user_file
		except:
			self.object = None
			self.structures = None

		if user_file:
			fields = dict([(field_id,name) for field_id, dummy, name, dummy2 in UserFileField.objects.filter(user_file=user_file).values_list()])
			structures = user_file.structures.all()
			self.structures = structures.values()
			
			databases = dict([(database['id'], database) for database in Database.objects.all().values()])
			
			joined_databases = {}
			for object, item in zip(structures, self.structures):
			
				item['object'] = object
				try:
					compound = object.structure.compound
					item['compound'] = compound
				#	item['records'] = compound.get_records()
				except:
					item['compound'] = None
					
				
				item['fields'] = dict([(fields[field_id], value ) for user_structure_id, field_id, value in object.user_field_values.values_list()])
				try:
					item['image'] = object.image
				except:
					pass
				try:
					item['data_source'] = object.data_source.string
				except:
					item['data_source'] = None

				database_associations = object.databases
						
				
				try:
					item['ficts_databases'] = [databases[association['database_id']] for association in database_associations.filter(association_type=1).values()]
					item['ficts_database_count'] = len(item['ficts_databases'])
				except:
					item['ficts_databases'] = None
					item['ficts_database_count'] = 0
				try:
					item['ficus_databases'] = [databases[association['database_id']] for association in database_associations.filter(association_type=2).values()]
					item['ficus_database_count'] = len(item['ficus_databases'])
				except:
					item['ficus_databases'] = None
					item['ficus_database_count'] = 0
				try:
					item['uuuuu_databases'] = [databases[association['database_id']] for association in database_associations.filter(association_type=8).values()]
					item['uuuuu_database_count'] = len(item['uuuuu_databases'])
				except:
					item['uuuuu_databases'] = None
					item['uuuuu_database_count'] = 0
				try:
					item['databases'] = dict([(association['database_id'], databases[association['database_id']]) for association in database_associations.values()])
					item['database_list'] = item['databases'].values()
					item['database_count'] = len(item['databases'])
					#joined_databases.update(database_association.all().values())
					#dummy
				except:
					item['databases'] = None
					item['database_list'] = None
					item['database_count'] = 0
				try:
					ncicadd = object.ncicadd_identifier
					item['ncicadd_identifier'] = {
						'ficts': Identifier(hashcode=ncicadd.ficts_hashcode, type='FICTS'),
						'ficus': Identifier(hashcode=ncicadd.ficus_hashcode, type='FICuS'),
						'uuuuu': Identifier(hashcode=ncicadd.uuuuu_hashcode, type='uuuuu')
					}
				except:
					item['ncicadd_identifier'] = None
				
				try:
					inchi = object.inchi
					item['inchi'] = {
						'string': String(inchi.inchi),
						'key': Key(inchi.inchikey)
					}
				except:
					item['inchi'] = None
				
			self.joined_databases = joined_databases
			
				
	def records(self):
		if self.structures:
			return dict([(s['record'],s) for s in self.structures])
		else:
			return None
		
	def events_with_structures(self):
		events = self.object.events.all().order_by('date_added')
		self.events = events.values()
		structure_dict = dict([(s['id'],s) for s in self.structures])
		if self.events:
			for object, item in zip(events, self.events):
				item['structure_list'] = [structure_dict[structure['id']] for structure in object.structures.all().order_by('record').values('id')]
				#pass
			return self.events
		else:
			return None


class UserFileProcessor(CactvsScript):
	
	resolver_list = [
		'smiles',
		'stdinchikey',
		'stdinchi',
		'ncicadd_identifier',
		'hashisy',
		'chemspider_id',
		'chemnavigator_sid',
		'pubchem_sid',
		'emolecules_vid',
		'ncicadd_rid',
		'ncicadd_cid',
		'ncicadd_sid',
		'cas_number',
		'nsc_number',
		'zinc_code',
		'opsin',
		'name',
		'SDFile',
		'minimol',
		'packstring',
	]
	
	def __init__(self, user=None, key=None, event=None, date_invalid=None, user_file=None, original_filename=None, server_filename=None, result_file=False, display_name=None, structure_data_list=[], download_format='sdf', parameters={}, max_records=1000, do_identifier_lookup=True, do_database_lookup=True):
		self.user = user
		self.key = key
		self.event = event
		self.date_invalid = date_invalid
		self.user_file = user_file
		self.original_filename = original_filename
		self.server_filename = server_filename
		self.structure_data_list = structure_data_list
		self.max_records = max_records
		self.download_format = download_format
		#self.only_records = only_records
		self.parameters = parameters
		self.result_file = result_file
		self.display_name = display_name
		self.do_database_lookup = do_database_lookup
		self.do_identifier_lookup = do_identifier_lookup
		self.download_file = None
		self.from_resolver = False
		
		script_env = CactvsScriptEnv()
		script_env.dataset = {
			'name': settings.DATABASE_NAME,
			'user': settings.DATABASE_USER,
			'password': settings.DATABASE_PASSWORD,
			'host': settings.DATABASE_HOST,
		}
		
		#script_env.CSSCRIPT_DIR = settings.FILE_CACTVS_SCRIPT_DIR
		#script_env.CSCLIENT_INST_DIR = settings.PYCACTVS_SITE_PACKAGE_DIR
			
		self.script_env = script_env
		self.exec_env = CactvsExecEnv(cactvs_path = settings.CACTVS_INST_DIR, user_lib_paths=[settings.FILE_CACTVS_SCRIPT_DIR,])

	def block(self, string=None, progress=None):
		status = self.user_file.status 
		if status.date_blocked:
			raise UserFileProcessorError('writing to a blocked file')
		status.string='test'
		status.date_blocked = datetime.datetime.now()
		status.save()
		self.user_file.status = status
		return self
		
	def unblock(self):
		status = self.user_file.status 
		status.string=None
		status.date_blocked=None
		status.save()
		#self.user_file.status = status
		return self
	
	def create_user_file(self):
		if not self.key:
			self.key = FileKey().get()	
		try:
			if self.user.is_anonymous():
				user = None
			else:	
				user = self.user
		except:
			user = None
		if self.original_filename and not self.display_name:
			self.display_filename = os.path.splitext(self.original_filename)[0]
		user_file = UserFile(
			user=user, 
			name=self.original_filename,
			display_name=self.display_name,
			records=0, 
			date_invalid=self.date_invalid,
			created_from_search_result=self.result_file
		)
		user_file.save()
		user_file_key = UserFileKey(
			user_file = user_file, 
			upload = self.key, 
			public = FileKey().get(),
			private = FileKey().get(),
		)
		user_file_key.save()
		user_file_status = UserFileStatus(
			user_file = user_file, 
			string = 'created',
			date_blocked = None
		)
		user_file_status.save()
		user_file.key = user_file_key
		user_file.status = user_file_status
		user_file.save()
		self.user_file = user_file
		return self
			
	def attach_to_session(self, session):
		user_file_dict = session['user_file_dict']
		user_file_dict[self.user].append(self.user_file)
		session['user_file_dict'] = user_file_dict
		return self
	
	def attach_event(self, string):
		self.event = UserFileEvent(user_file=self.user_file, string=string)
		return self

	def resolve(self):
		"""
			if the upload is a simple list of chemical strings CIR can
			be used to convert it into structure representations. These
			can be pushed into the database by method "load_into_database" like
			a regular file.
		"""
		if self.server_filename:
			try:
				file = codecs.open(self.server_filename, 'r', 'utf-8')
				string = file.read()
			except:
				file = codecs.open(self.server_filename, 'r')
				string = file.read()
			file.close()
		else:
			string = self.structure_data_list[0]
	
		structure_data_list = []
		failed_attempts = 0
		self.from_resolver = True
		item_count = 1
		
		for item in string.split('\n'):
			chemical_string = ChemicalString(
				item, 
				resolver_list=UserFileProcessor.resolver_list
			)
			success = len(chemical_string._interpretations)
			if not success:
				chemical_string = ChemicalString(
					item, 
					resolver_list=['name_pattern',]
				)
				success = len(chemical_string._interpretations)
				if not success:
					failed_attempts += 1
			if item_count > 3 and float(failed_attempts) / float(item_count) >= 0.3:
				self.from_resolver = False
				break
			retrieved_cid_list = []
			for interpretation in chemical_string._interpretations:
				for structure in interpretation.structures:
					ncicadd_cid = structure.object.compound.id
					if ncicadd_cid in retrieved_cid_list:
						continue
					else:
						retrieved_cid_list.append(ncicadd_cid)
					minimol = structure.object.minimol
					structure_data_list.append(minimol)
					metadata = "resolved as %s matching \"%s\"" % (
						structure._metadata['query_search_string'],
						structure._metadata['description']
					)
					structure_data_list.append(base64.b64encode(metadata.encode('utf-8')))
				# this break is because we care only for the first interpretation
				break
			item_count += 1

		if self.from_resolver:
			self.structure_data_list = structure_data_list
			self.server_filename = None
		return self
	
	def create_from_database(self, calculate_3d=0, only_records=None):
		key = self.user_file.key.upload
		media_path = settings.MEDIA_ROOT
		fname = os.path.splitext(self.user_file.name)[0]
	
		abs_download_file_name = '%s/tmp/%s-%s.%s' % (media_path, key, fname, self.download_format)
		rel_download_file_name = 'tmp/%s-%s.%s' % (key, fname, self.download_format)
		download_file_name = '%s-%s.%s' % (key, os.path.split(fname)[-1], self.download_format)
			
		self.script_env.calculate_3d = calculate_3d
		self.script_env.only_records = str(only_records)

		script = CactvsScript(
			script = os.path.join(settings.FILE_CACTVS_SCRIPT_DIR, 'download.tcl'), 
			script_env = self.script_env, 
			exec_env = self.exec_env,
			#tracefile='/tmp/trace.log',
			#logfile='/tmp/log.log'
		)
		result = script.run(args=[
			str(self.user_file.id),
			str(abs_download_file_name),
			str(self.download_format),
		])
		file = open(abs_download_file_name)
		download_file = File(file)
		download_file.name = rel_download_file_name
		download_file.download_name = download_file_name
		download_file.format = self.download_format
		self.download_file = download_file
		return self

	def load_into_database(self):
		"""
			loads the file uploaded to the server into the databases
			for this, it calls an external CACTVS script
		"""
		if not self.structure_data_list:
			self.structure_data_list = None
		else:
			self.structure_data_list = ' '.join(self.structure_data_list)
			self.structure_data_list = base64.b64encode(self.structure_data_list)
		if self.event:
			self.event.save()
			event_id = self.event.id
		else:
			event_id = None
		script = CactvsScript(
			script = os.path.join(settings.FILE_CACTVS_SCRIPT_DIR, 'upload.tcl'), 
			script_env = self.script_env, 
			exec_env = self.exec_env,
			tracefile='/tmp/trace.log',
			#logfile='/home/sitzmann/log.log'
		)
		#print script.script
		result = script.run(args=[
			str(self.user_file.id), 
			str(event_id),
			str(self.server_filename),
			str(self.structure_data_list),
			str(self.max_records),
			self._bool_to_int(self.do_identifier_lookup),
			self._bool_to_int(self.do_database_lookup),
		])
		return self
		
	def normalize(self):
		"""
			normalize missing structures
		"""
		script = CactvsScript(
			script = os.path.join(settings.FILE_CACTVS_SCRIPT_DIR, 'normalize.tcl'), 
			script_env = self.script_env, 
			exec_env = self.exec_env,
			#tracefile='/home/sitzmann/trace.log',
			#logfile='/home/sitzmann/log.log'
		)
		result = script.run(args=[
			str(self.user_file.id),
			self._bool_to_int(self.do_identifier_lookup),
			self._bool_to_int(self.do_database_lookup),
		])
		return self
		
	def preload(self):
		return PreloadedUserFile(self.user_file)

	def _bool_to_int(self, boolean):
		if boolean:
			return str(1)
		else:
			return str(0)