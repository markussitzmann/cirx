#from django.conf.urls.defaults import *
from django.conf.urls import *
from django.contrib import admin
from django.urls import path, re_path
from django.views.decorators.cache import cache_page

import structure.views
#import file.views
#import media.views
#import network.views

#import database.csls.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
from . import views

urlpatterns = [
    re_path('^structure/(?P<string>.+)/(?P<representation>.+)/(?P<format>xml)', views.identifier),
    re_path('^structure/(?P<string>.+)/(?P<representation>.+)$', views.identifier),
    re_path('^structure/(?P<string>.+)$', views.structure),
    re_path('^structure$', views.structure),
    re_path('^image/(?P<string>.+)$', views.image),
    re_path('^image$', views.image),
]

# urlpatterns = patterns('',
# 	url(r'^apps/', include('chemical.apps.urls')),
# 	url(r'^activity/', include('chemical.activity.urls')),
# 	url(r'^identifier/', include('chemical.identifier.urls')),
# 	#(r'^database/', include('chemical.database.urls')),
# 	url(r'^database/', include('chemical.database.urls')),
# 	#(r'^database/pdb', include('chemical.database.ligand.urls')),
# 	#(r'^structure/openid/', include('django_openid_auth.urls')),
# 	#(r'^dbmedia', media.views.db_media),
# 	#(r'^media_config', media.views.media_config),
# 	url(r'^media', media.views.media),
# 	#(r'^network', network.views.network),
# 	#(r'^file/test', file.views.test),
# 	#(r'^file/list', file.views.file_list),
# 	#(r'^file/upload_progress', file.views.upload_progress),
# 	#(r'^file/upload', file.views.upload),
# 	#(r'^file/preload', file.views.preload),
# 	#(r'^file/(?P<key>.{32})/fields', file.views.fields),
# 	#(r'^file/(?P<key>.{32})', file.views.get),
# 	#(r'^file', file.views.post),
# 	#(r'^file/(?P<file_identifier>.+)/database_tab', file.views.database_tab),
# 	#(r'^file/(?P<file_identifier>.+)/identifier_tab', file.views.identifier_tab),
# 	#(r'^file/(?P<file_identifier>.+)/structure_tab', file.views.structure_tab),
# 	#(r'^file/(?P<file_identifier>.+)/delete', file.views.delete),
# 	#(r'^file/(?P<file_identifier>.+)/download', file.views.download),
# 	#(r'^file/(?P<file_identifier>.+)/add/(?P<chemical_string>.+)', file.views.add),
# 	#(r'^file/(?P<file_identifier>.+)/preload', file.views.preload),
# 	#(r'^file/processing_status/(?P<string>.{32})$', file.views.processing_status),
# 	#(r'^file/(?P<file_identifier>.+)/(?P<record_identifier>.+)', file.views.view_structure),
# 	#(r'^file/(?P<file_identifier>.+)', file.views.view),
# 	#(r'^file', file.views.view),
# 	#url(r'^structure_opsin_resolver/(?P<name>.+)$', cache_page(structure.views.opsin_resolver, 60 * 60 * 24)),
# 	url(r'^structure_opsin_resolver/(?P<name>.+)$', cache_page(60*60*24)(structure.views.opsin_resolver)),
# 	#(r'^structure/name/(?P<string>.+)', structure.views.name),
# 	#(r'^structure/test$', structure.views.test),
# 	#(r'^structure/name$', structure.views.name),
# 	#(r'^structure/documentation$', structure.views.structure_documentation),
# 	#(r'^structure/statistic/seconds$', cache_page(structure.views.statistic_seconds, 10)),
# 	#(r'^structure/statistics$', cache_page( structure.views.statistics, 60 * 60 * 24 * 10)),
# 	#(r'^structure/editor$', structure.views.editor),
# 	#(r'^structure/test/(?P<string>.+)', structure.views.test),
# 	#(r'^structure/(?P<string>.+)/twirl_cached/(?P<dom_id>.+)$', structure.views.twirl_cache),
# 	url(r'^structure_documentation$', structure.views.structure_documentation),
# 	#url(r'^structure/(?P<string>.+)/twirl_cached/(?P<dom_id>.+)$', cache_page(structure.views.twirl_cache, 60 * 60 * 240)),
# 	url(r'^structure/(?P<string>.+)/twirl_cached/(?P<dom_id>.+)$', cache_page(60*60*240)(structure.views.twirl_cache)),
# 	url(r'^structure/(?P<string>.+)/chemdoodle_cached/(?P<dom_id>.+)$', structure.views.chemdoodle_cache),
# 	#url(r'^structure/(?P<string>.+)/(?P<representation>.+)/(?P<format>xml)', cache_page(structure.views.identifier, 60 * 60 * 24)),
# 	url(r'^structure/(?P<string>.+)/(?P<representation>.+)/(?P<format>xml)', cache_page(60*60*24)(structure.views.identifier)),
# 	#url(r'^structure/(?P<string>.+)/(?P<representation>.+)$', cache_page(structure.views.identifier, 60 * 60 * 24)),
# 	url(r'^structure/(?P<string>.+)/(?P<representation>.+)$', cache_page(60*60*24)(structure.views.identifier)),
# 	url(r'^structure/(?P<string>.+)$', structure.views.structure),
# 	url(r'^structure$', structure.views.structure),
#
#     # Uncomment the next line to enable admin documentation:
#     # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
#
#     # Uncomment the next line to enable the admin:
#     # (r'^admin/(.*)', admin.site.root),
# )
