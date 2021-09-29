from csdb.base import *
from csdb.schema import *


class CompoundRecordLoader(object):

	def __init__(self, compound_list):
		
		self.database_object_list = []
		self.compound_list = []
		self.record_list = []
		self.query = None
		self.normalized_cid_lookup = {}

		if not compound_list:
			return
		
		for c in compound_list:
			if isinstance(c, Compound):
				self.compound_list.append(c.id)
			else:
				self.compound_list.append(c)
		self.record_list = self._load()
	
	def group_concat(self, tuple_list):
		r = {}
		for k, v in tuple_list:
			if r.has_key(k):
				r[k].append(v)
			else:
				r[k] = [v,]

		r = dict([(k,sorted(v)) for k,v in r.items()])
		#groupby(sorted(database_list[association])
		return r

	def _load(self):
		record = record_table.alias()
		q=[]
		normalized_cid = self._normalized_compound_query(self.compound_list)

		if not len([k for k,v in normalized_cid.items() if len(v)]):
			return
		
		for identifier in ncicadd_identifiers.keys():
			column=getattr(record.c, '%s_compound_id' % (identifier))
			q.append(
				select(
					[
						column,
						record.c.id, 
						record.c.database_id,
						record.c.release_id,
						record.c.file_record_id,
						record.c.database_regid_id,
						record.c.date_released,
						record.c.date_deprecated,
						func.concat(identifier),
					],
					or_(*[column==norm_cid for cid, norm_cid in normalized_cid[identifier]])
				)
			)
		self.query = union(*q)
		#self.normalized_cid_lookup = [k,dict(v) for k,v in normalized_cid.items()]
		self.normalized_cid_lookup = dict([(k,dict(v)) for k,v in normalized_cid.items()])
		search_result = self.query.execute().fetchall()
		field_label = [
			'compound_id',
			'record_id',
			'database_id',
			'release_id',
			'file_record_id',
			'database_regid_id',
			'date_released',
			'date_deprecated',
			'identifier'
		]
		records = [dict(r) for r in [[r for r in zip(field_label,record)] for record in search_result]]
		self.record_list = records
		return self.record_list

	def _normalized_compound_query(self, compound_list):
		from_obj=compound_table
		normalized_compound_table = {}
		nquery = []
		for identifier in ncicadd_identifiers.keys():
			normalized_compound_table[identifier] = compound_table.alias()
			from_obj = from_obj.join(
				structure_identifier_table[identifier],
				compound_table.c.hashisy_int==structure_identifier_table[identifier].c.hashisy_int
			).join(
				normalized_compound_table[identifier],
				normalized_compound_table[identifier].c.hashisy_int==getattr(structure_identifier_table[identifier].c, '%s_int' % identifier)
			)
			nquery.append(select(
				[func.concat(identifier), compound_table.c.id, getattr(normalized_compound_table[identifier].c, 'id')],
				from_obj=from_obj
			).where(or_(*[compound_table.c.id==cid for cid in compound_list])))
		q = union(*nquery)
		r = self.group_concat([(identifier,(compound_id, normalized_compound_id)) for identifier, compound_id, normalized_compound_id in q.execute().fetchall()])
		#print dict([(k,dict(v)) for k,v in r.items()])
		return r

	@property
	def by_identifier(self):
		r = {}
		for identifier in ncicadd_identifiers.keys():
			r[identifier] = [record for record in self.record_list if record['identifier']==identifier]
		return r
		
	@property
	def by_identifier_database(self):
		r = {}
		for identifier in ncicadd_identifiers.keys():
			r[identifier] = self.group_concat([
				(record['query_compound_id'], record['database_id'])
				for record in self.by_identifier[identifier]
			])
		return r
	
	@property
	def by_identifier_compound(self):
		r = {}
		for compound in self.compound_list:
			if self.record_list:
				r[compound] = self.group_concat([
					(record['identifier'], record) for record in self.record_list 
					if self.normalized_cid_lookup[record['identifier']].has_key(compound)
					and record['compound_id']==self.normalized_cid_lookup[record['identifier']][compound]
				])
		return r

	@property
	def by_identifier_compound_database(self):
		record_dict = self.by_identifier_compound
		dd = {}
		for compound, by_identifier in record_dict.items():
			dd[compound] = {}
			for identifier, record_list in by_identifier.items():
				dd[compound][identifier] = self.group_concat(
					[(record['database_id'], record) for record in record_dict[compound][identifier]]
				)
		return dd

	@property
	def database_record_count(self):
		record_dict = self.by_identifier_compound
		dd = {}
		for compound, by_identifier in record_dict.items():
			dd[compound] = {}
			for identifier, record_list in by_identifier.items():
				database_records = self.group_concat(
					[(record['database_id'], record) for record in record_dict[compound][identifier]]
				)
				dd[compound][identifier]={
					'database_count': len(database_records.keys()),
					'record_count': sum([len(r) for d,r in database_records.items()]),
					'databases': [self.database_objects[did] for did in database_records.keys()]
				}
		return dd

	@property
	def short_database_record_count(self):
		record_dict = self.by_identifier_compound
		dd = {}
		for compound, by_identifier in record_dict.items():
			dd[compound] = {}
			for identifier, record_list in by_identifier.items():
				database_records = self.group_concat(
					[(record['database_id'], record) for record in record_dict[compound][identifier]]
				)
				dd[compound][identifier]={
					'database_count': len(database_records.keys()),
					'record_count': sum([len(r) for d,r in database_records.items()]),
					'databases': dict([(self.database_objects[did].id, self.database_objects[did].name) for did in database_records.keys()])
				}
		return dd

	@property
	def database_objects(self):
		if self.database_object_list:
			return self.database_object_list
		database_id_list = [
			record['database_id'] for record in self.record_list
		]
		filter_criterion = or_(*[Database.id==database_id for database_id in list(set(database_id_list))])
		self.database_object_list = dict([(database.id, database) for database in csdb_session.query(Database).filter(filter_criterion).all()])
		return self.database_object_list

	@property
	def release_object_list(self):
		release_id_list = [
			release_id for compound_id, record_id, database_id, release_id, association in self.record_list
		]
		f = or_(*[Release.id==release_id for release_id in sorted(list(set(release_id_list)))])
		return csdb_session.query(Release).filter(f).all()

	@property	
	def record_object_list(self):
		record_id_list = [
			record_id for compound_id, record_id, database_id, release_id, association in self.record_list
		]
		f = or_(*[Record.id==record_id for record_id in sorted(list(set(record_id_list)))])
		return csdb_session.query(Record).filter(f).all()




class RelatedRecordLoader(object):

	def __init__(self, record):
		self.record=record
		self.record_relations = None
		record_id = self.record.id
		file_record_q = csdb_session.query(Record, literal_column("'file_record_id'").label('from_rel1')).filter(
			and_(
				Record.file_record_id==record.file_record_id,
				not_(Record.id==record_id)
			)
		)
		ficts_q = csdb_session.query(Record, literal_column("'ficts_compound_id'").label('from_rel2')).filter(
			and_(
				Record.ficts_compound_id==record.ficts_compound_id,
				not_(Record.id==record_id),
				not_(Record.ficts_compound_id==1),
			)
		)
		ficus_q = csdb_session.query(Record, literal_column("'ficus_compound_id'").label('from_rel3')).filter(
			and_(
				Record.ficus_compound_id==record.ficus_compound_id,
				not_(Record.id==record_id),
				not_(Record.ficus_compound_id==1),
			)
		)
		uuuuu_q = csdb_session.query(Record, literal_column("'uuuuu_compound_id'").label('from_rel4')).filter(
			and_(
				Record.uuuuu_compound_id==record.uuuuu_compound_id,
				not_(Record.id==record_id),
				not_(Record.uuuuu_compound_id==1),
			)
		)
		self.related_records = file_record_q.union(ficts_q).union(ficus_q).union(uuuuu_q).all()

	def merge_record_relations(self):
		if self.record_relations:
			return self.record_relations
		record_relations = {}
		for record, from_rel in self.related_records:
			rel_object = getattr(record, from_rel)
			if record_relations.has_key(record):
				record_relations[record].append(rel_object)
			else:
				record_relations[record] = [rel_object,]
		self.record_relations = record_relations
		return record_relations


class ReleaseSampleFileRecordLoader(object):

	def __init__(self, release_list):
		self.release_list = release_list
		query = csdb_session.query(FileRecord, DatabaseRecord, FileRecordDatabaseReleaseRecord).join(FileRecordDatabaseReleaseRecord).join(DatabaseRecord)
		file_record_list = []
		for release in release_list:
			file_record_list.extend(query.filter(FileRecordDatabaseReleaseRecord.release==release).limit(5).all())
		self.file_record_list = file_record_list

