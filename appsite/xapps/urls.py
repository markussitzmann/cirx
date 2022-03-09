#from django.conf.urls.defaults import *
from django.conf.urls import *
from django.views.decorators.cache import cache_page
import chemical.apps.views
#import chemical.file.views
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
	url(r'openid/', include('django_openid_auth.urls')),
	#url(r'login', chemical.apps.views.login),
	url(r'logout', chemical.apps.views.logout),
	#url(r'gusar/summary', chemical.apps.views.gusar_summary),
	#url(r'info', chemical.apps.views.info),
	#url(r'search/term', chemical.apps.views.qterm),
	url(r'^(input|edit|add|view)/(?P<page>(structure|structures|structure_list|list|info))$', chemical.apps.views.edit_structures),
	#url(r'search/list', chemical.apps.views.qlist),
	#url(r'editor/(?P<editor>.+)', chemical.apps.views.editor),	
	url(r'^editor$', chemical.apps.views.editor),	
	#url(r'summary', chemical.apps.views.summary),
	#url(r'result/(?P<string>.+)', chemical.apps.views.result),
	url(r'^response/(?P<string>.+)$', chemical.apps.views.response),
	url(r'^response$', chemical.apps.views.response),
	url(r'^browse/(?P<page>\d+)$', chemical.apps.views.browse),
	url(r'^(?P<subpage>(details|jsmol))/(?P<string>.+)$', chemical.apps.views.details),
	url(r'info', chemical.apps.views.info),
	#url(r'(cap|chemical_activity_predictor)/category/(?P<name>.+)', chemical.apps.views.cap_category),
	#url(r'(cap|chemical_activity_predictor)/endpoint/(?P<name>.+)', chemical.apps.views.cap_endpoint),
	url(r'^csls/(?P<page>(databases|releases))$', chemical.apps.views.csls_manual),
	url(r'^csls/(?P<page>(database|release))/(?P<name>.+)$', chemical.apps.views.csls_manual),
	url(r'^cap/(?P<page>(categories|models|endpoints|config))$', chemical.apps.views.cap_manual),
	url(r'^cap/(?P<page>(category|model|endpoint))/(?P<name>.+)$', chemical.apps.views.cap_manual),
	#url(r'^cap/models', chemical.apps.views.cap_models),
	url(r'^(?P<app>(cap|csls|cir|apps))$', chemical.apps.views.splash),
	#url(r'patent', chemical.apps.views.patent),
	#url(r'cir', chemical.apps.views.cir),
	#url(r'tautomer/network', chemical.apps.views.tautomer_network),
	#url(r'tautomer', chemical.apps.views.tautomer),
	#url(r'cfr', chemical.apps.views.cfr),
	#url(r'csls/(?P<string>.+)', chemical.apps.views.csls),
	#url(r'media', chemical.apps.views.media),
	#url(r'lookup', chemical.apps.views.lookup),
	#url(r'csls/summary', chemical.apps.views.csls_summary),
	#url(r'csls', chemical.apps.views.csls),
	#url(r'csdb/database', chemical.apps.views.csdb_database),
	#url(r'csdb/database_counts', chemical.apps.views.csdb_database_counts),
	#url(r'csdb/database/(?P<database_id>.+)', chemical.apps.views.csdb_database),
	#url(r'csdb/databases', chemical.apps.views.csdb_databases),
	#url(r'csdb/releases', chemical.apps.views.csdb_releases),
	#url(r'csdb/release/(?P<release_id>.+)', chemical.apps.views.csdb_release),
	#url(r'csdb/compound/(?P<compound_id>.+)', chemical.apps.views.csdb_compound),
	#url(r'csdb/structure/(?P<structure_id>.+)', chemical.apps.views.csdb_structure),
	#url(r'csdb/file/(?P<file_id>.+)', chemical.apps.views.csdb_file),
	#url(r'csdb/files', chemical.apps.views.csdb_files),
	#url(r'csdb/file_record/(?P<file_record_id>.+)', chemical.apps.views.csdb_file_record),
	#url(r'csdb/record/(?P<record_id>.+)', chemical.apps.views.csdb_record),
	#url(r'csdb', chemical.apps.views.csdb),
	#url(r'test', chemical.apps.views.test),
	url(r'^$', chemical.apps.views.home),
)