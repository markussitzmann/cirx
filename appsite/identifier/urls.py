#from django.conf.urls.defaults import *
from django.conf.urls import *
from django.views.decorators.cache import cache_page
#import structure.views
#import file.views
#import media.views
#import database.csls.views

import chemical.identifier.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^inchi', chemical.identifier.views.inchi),
)
