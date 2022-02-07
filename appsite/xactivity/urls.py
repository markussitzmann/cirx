#from django.conf.urls.defaults import *
from django.conf.urls import *
from django.views.decorators.cache import cache_page
#import structure.views
#import file.views
#import media.views
#import network.views
#import database.csls.views

import chemical.activity.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^endpoint/(?P<category>.+)/(?P<model>.+)/(?P<endpoint>.+)$', chemical.activity.views.endpoint),
	url(r'^endpoint/(?P<category>.+)/(?P<model>.+)$', chemical.activity.views.endpoint),
	url(r'^endpoint/(?P<category>.+)', chemical.activity.views.endpoint),
	url(r'^endpoint$', chemical.activity.views.endpoint),

	#(r'^(endpoint|endpoints)/(?P<category>.+)/(?P<model>.+)/(?P<sign>.+)/(?P<query>.+)$', chemical.activity.views.predict),
	url(r'^predictor/(?P<query>.+)/(?P<category>.+)/(?P<model>.+)/(?P<endpoint>.+)', chemical.activity.views.predictor),
	url(r'^predictor/(?P<query>.+)/(?P<category>.+)/(?P<model>.+)', chemical.activity.views.predictor),
    # Uncomment the next line to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
)
