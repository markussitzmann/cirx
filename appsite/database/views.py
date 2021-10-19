# #import codecs
#
# import json
#
# #from csdb.file.db.schema import *
# # from django.core.files.uploadedfile import UploadedFile
# from django.conf import settings
# from django.http import *
#
#
# # from django.utils import simplejson
#
#
# ### the REST stuff
#
# def csdb_files(request):
# 	files = [{
# 		'id': str(f.id),
# 		'url': str(settings.DATABASE_BASE_URL + '/csdb/file/' + str(f.id) ),
# 		'name': str(f.name),
# 		'added': str(f.added),
# 		'blocked': str(f.blocked),
# 		'directory': str(f.directory.id)
# 	} for f in csdb_session.query(File).all()]
# 	r = {'aaData': files}
# 	return HttpResponse(json.dumps(r))
#
#
# #def csdb_file(request):
# #	file = [{
# #		'id': str(f.id),
# #		'name': str(f.name),
# #		'added': str(f.added),
# #		'blocked': str(f.blocked),
# #		'directory': str(f.directory.id)
# #	} for f in csdb_session.query(File).all()]
#
#
# def csdb_file_record(request, id):
# 	file_record = csdb_session.query(FileRecord).filter(FileRecord.id==id).one()
# 	return HttpResponse(file_record)
#
#
# def csdb_database(request, id):
# 	database = csdb_session.query(Database).filter(Database.id==id).one()
# 	return HttpResponse(database)
#
#
# def csdb_release(request, id):
# 	pass
