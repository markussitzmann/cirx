#from django.conf.urls.defaults import *
from django.conf.urls import *
from django.views.decorators.cache import cache_page
import chemical.database.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	#(r'csdb/files', chemical.database.views.csdb_files),
	url(r'csdb/files', chemical.database.views.csdb_files),
	#(r'csdb/record/(?P<id>.+)', chemical.database.views.csdb_file_record),
	url(r'csdb/record/(?P<id>.+)', chemical.database.views.csdb_file_record),
	#(r'csdb/database/(?P<id>.+)', chemical.database.views.csdb_database),
	url(r'csdb/database/(?P<id>.+)', chemical.database.views.csdb_database),
	#(r'csls/(?P<string>.+)', chemical.apps.views.csls),
	#(r'csls', chemical.apps.views.csls),
	#(r'test', chemical.apps.views.test),
)
