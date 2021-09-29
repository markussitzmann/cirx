from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User

from chemical.structure.models import *
from chemical.database.models import *
from chemical.structure.ncicadd.identifier import *
from chemical.structure.inchi.identifier import *

schema='chemical_file`.`'

class UserFile(models.Model):
	id = models.AutoField(primary_key=True)
	user = models.ForeignKey(User, blank=True, null=True)
	records = models.IntegerField(unique=False)
	name = models.CharField(max_length=255, blank=True, null=True)
	display_name = models.CharField(max_length=255, blank=True, null=True)
	comment = models.TextField(max_length=4096)
	date_added = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)
	date_invalid = models.DateTimeField(null=True)
	created_from_search_result = models.BooleanField(default=False)
	
	class Meta:
		db_table = schema + 'user_file'
		
	def get_field_values(self): 
		fields = UserFileField.objects.filter(user_file=self.user_file)
		field_values = self.user_field_values.all().values_list()
		field_value_dict = dict([(fields.filter(id=field_id).get().original_name, value) for structure_id, field_id, value in field_values])
		return field_value_dict

	def __repr__(self):
		return "< %s : %s %s >" % (self.id, self.name, self.records)
	
	def __str__(self):
		return "< %s : %s %s >" % (self.id, self.name, self.records)


class UserFileKey(models.Model):
	user_file = models.OneToOneField(UserFile, primary_key=True, null=False, related_name='key')
	upload = models.CharField(max_length=32, blank=True)
	public = models.CharField(max_length=32, blank=True)
	private = models.CharField(max_length=32, blank=True)
	
	class Meta:
		db_table = schema + 'user_file_key'
		

class UserFileStatus(models.Model):
	user_file = models.OneToOneField(UserFile, primary_key=True, null=False, related_name='status')
	#progress = models.IntegerField()
	string = models.CharField(max_length=768, blank=True, null=True)
	date_blocked = models.DateTimeField(null=True)
	
	class Meta:
		db_table = schema + 'user_file_status'


class UserFileEvent(models.Model):
	id = models.AutoField(primary_key=True)
	user_file = models.ForeignKey(UserFile, null=False, related_name='events')
	string = models.CharField(max_length=768)
	date_added = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = schema + 'user_file_event'

	def __str__(self):
		return "%s %s %s" % (self.id, self.user_file, self.string,)


class UserStructureImage(models.Model):
	id = models.AutoField(primary_key=True)
	hashisy = models.BigIntegerField(unique=False, null=False)
	small = models.TextField(max_length=65535)
	medium = models.TextField(max_length=65535)
	large = models.TextField(max_length=65535)
	
	class Meta:
		db_table = schema + 'user_structure_image'


class UserStructure(models.Model):
	id = models.AutoField(primary_key=True)
	user_file = models.ForeignKey(UserFile, null=False, related_name='structures')
	event = models.ForeignKey(UserFileEvent, null=True, related_name='structures')
	image = models.ForeignKey(UserStructureImage, null=True, related_name='structures')
	record = models.IntegerField(unique=False)
	structure = models.ForeignKey(Structure, null=True)
	hashisy = models.BigIntegerField(unique=False, null=False)
	packstring = models.TextField(max_length=1500)
	date_added = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)
	error = models.BooleanField(default=False)
	blocked = models.BooleanField(default=False)

	class Meta:
		db_table = schema + 'user_structure'
		unique_together = (('user_file', 'record'),)
		
	def get_field_values(self): 
		fields = UserFileField.objects.filter(user_file=self.user_file)
		field_values = self.user_field_values.all().values_list()
		field_value_dict = dict([(fields.filter(id=field_id).get().original_name, value) for structure_id, field_id, value in field_values])
		return field_value_dict


class UserStructureDataSource(models.Model):
	user_structure = models.OneToOneField(UserStructure, null=False, primary_key=True, related_name='data_source')
	string = models.CharField(max_length=768)
	
	class Meta:
		db_table = schema + 'user_structure_data_source'


class UploadUserStructure(models.Model):
	id = models.AutoField(primary_key=True)
	user_file = models.ForeignKey(UserFile, null=False, related_name='upload_structures')
	record = models.IntegerField(unique=False)
	structure = models.ForeignKey(Structure, null=True)
	hashisy = models.BigIntegerField(unique=False, null=False)
	packstring = models.TextField(max_length=1500)
	date_added = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)
	blocked = models.BooleanField(default=False)

	class Meta:
		db_table = schema + 'upload_user_structure'
		unique_together = (('user_file', 'record'),)
		
	def get_field_values(self): 
		fields = UserFileField.objects.filter(user_file=self.user_file)
		field_values = self.user_field_values.all().values_list()
		field_value_dict = dict([(fields.filter(id=field_id).get().original_name, value) for structure_id, field_id, value in field_values])
		return field_value_dict


class UserStructureIdentifier(models.Model):
	user_structure = models.OneToOneField(UserStructure, null=False, primary_key=True, related_name='ncicadd_identifier')
	ficts_hashcode = models.CharField(max_length=16)
	ficus_hashcode = models.CharField(max_length=16)
	uuuuu_hashcode = models.CharField(max_length=16)
	valid = models.BooleanField(default=False)
	blocked = models.BooleanField(default=False)
	
	class Meta:
		db_table = schema + 'user_structure_identifier'

	def get_ficts(self):
		identifier=Identifier(hashcode=self.ficts_hashcode, type='FICTS')
		return identifier
	
	def get_ficus(self):
		identifier=Identifier(hashcode=self.ficus_hashcode, type='FICuS')
		return identifier
	
	def get_uuuuu(self):
		identifier=Identifier(hashcode=self.uuuuu_hashcode, type='uuuuu')
		return identifier


class UserStructureInchi(models.Model):
	user_structure = models.OneToOneField(UserStructure, null=False, primary_key=True, related_name='inchi')
	inchikey = models.CharField(max_length=27)
	inchi = models.TextField(max_length=65535)
	valid = models.BooleanField()
	blocked = models.BooleanField()

	class Meta:
		db_table = schema + 'user_structure_inchi'


class UserStructureDatabase(models.Model):
	user_structure = models.ForeignKey(UserStructure, null=False, primary_key=True, related_name='databases')
	user_file = models.ForeignKey(UserFile, null=False, related_name='databases')
	database = models.ForeignKey(Database, null=False)
	association_type = models.ForeignKey(AssociationType, null=False)

	class Meta:
		db_table = schema + 'user_structure_database'
		unique_together = (('user_structure', 'user_file', 'database', 'association_type'),)
		
		
class UserStructureRecord(models.Model):
	user_structure = models.ForeignKey(UserStructure, null=False, primary_key=True, related_name='database_records')
	record = models.ForeignKey(Record, null=False)
	release = models.ForeignKey(Release, null=False)
	database = models.ForeignKey(Database, null=False)
	association_type = models.ForeignKey(AssociationType, null=False)

	class Meta:
		db_table = schema + 'user_structure_record'
		unique_together = (('user_structure', 'record', 'association_type'),)



		

#class UploadUserStructureImage(models.Model):
#	user_structure = models.OneToOneField(UserStructure, null=False, primary_key=True, related_name='upload_images')
#	small = models.TextField(max_length=65535)
#	medium = models.TextField(max_length=65535)
#	large = models.TextField(max_length=65535)
#	
#	class Meta:
#		db_table = schema + 'upload_user_structure_image'


class UserFileField(models.Model):
	id = models.AutoField(primary_key=True)
	user_file = models.ForeignKey(UserFile, null=False, related_name='fields')
	original_name = models.CharField(max_length=64, blank=True)
	display_name = models.CharField(max_length=64, blank=True)
	
	class Meta:
		db_table = schema + 'user_file_field'
		unique_together = (('user_file', 'original_name'),)


class UserStuctureFieldValue(models.Model):
	user_structure = models.ForeignKey(UserStructure, primary_key=True, null=False, related_name='field_values')
	field = models.ForeignKey(UserFileField, null=False)
	value = models.TextField(max_length=65535)	

	class Meta:
		db_table = schema + 'user_structure_field_value'
		unique_together = (('user_structure', 'field'),)
		

class UploadUserStuctureFieldValue(models.Model):
	user_structure = models.ForeignKey(UserStructure, primary_key=True, null=False, related_name='upload_user_field_values')
	field = models.ForeignKey(UserFileField, null=False)
	value = models.TextField(max_length=65535)	

	class Meta:
		db_table = schema + 'upload_user_structure_field_value'
		unique_together = (('user_structure', 'field'),)
		
	
	
