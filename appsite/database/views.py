import os
import time
import datetime
import base64
#import codecs

from csdb.file.db.schema import *


#from django.utils import simplejson

#from django.core.files.uploadedfile import UploadedFile
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


import json



### the REST stuff

def csdb_files(request):
	files = [{
		'id': str(f.id), 
		'url': str(settings.DATABASE_BASE_URL + '/csdb/file/' + str(f.id) ),
		'name': str(f.name),
		'added': str(f.added),
		'blocked': str(f.blocked),
		'directory': str(f.directory.id)
	} for f in csdb_session.query(File).all()]
	r = {'aaData': files}
	return HttpResponse(json.dumps(r))


#def csdb_file(request):
#	file = [{
#		'id': str(f.id), 
#		'name': str(f.name),
#		'added': str(f.added),
#		'blocked': str(f.blocked),
#		'directory': str(f.directory.id)
#	} for f in csdb_session.query(File).all()]


def csdb_file_record(request, id):
	file_record = csdb_session.query(FileRecord).filter(FileRecord.id==id).one()
	return HttpResponse(file_record)


def csdb_database(request, id):
	database = csdb_session.query(Database).filter(Database.id==id).one()
	return HttpResponse(database)


def csdb_release(request, id):
	pass
