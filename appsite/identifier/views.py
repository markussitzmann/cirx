import os
import time
import datetime

from django.core.files import File
from django.views.decorators.vary import vary_on_headers
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.template import Template, Context
from django.conf import settings 
from django.http import *
from django.utils import simplejson

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout

#from models import *
#from forms import *


#from dispatcher import URLmethod

#import resolver
#import ncicadd.identifier
#import formula
#import smiles
#import usage


def inchi(request):
	#from cactvs.cactvs import *
	#c = Cactvs()
	#e = Ens(c, "CCO")
	#s = e.get('molfilestring', parameters={'get3d': True})
	#s = c.cmd('set cactvs(version)')
	if request.method=="GET":
		s = request
	if request.method=="POST":
		s = request.raw_post_data
	return HttpResponse(s, mimetype = 'text/plain')




