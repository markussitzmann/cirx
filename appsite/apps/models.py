from django.db import models

# Create your models here.

from chemical.file.models import *

schema='chemical_apps`.`'

class GusarIn(models.Model):
	id = models.AutoField(primary_key=True)
	user = models.ForeignKey(User, blank=True, null=True)
	user_file = models.ForeignKey(UserFile, blank=True, null=True)
	molfile = models.TextField(max_length=4096)
	uploaded = models.DateTimeField(null=False)
	processed = models.BooleanField(null=False, default=0)
	results = models.TextField(max_length=4096)
	
	class Meta:
		db_table = schema + 'gusar_in'


class GusarResult(models.Model):
	id = models.AutoField(primary_key=True)
	user = models.ForeignKey(User, blank=True, null=True)
	user_file = models.ForeignKey(UserFile, blank=True, null=True)
	molfile = models.TextField(max_length=4096)
	result = models.TextField(max_length=4096)
	
	class Meta:
		db_table = schema + 'gusar_result'
