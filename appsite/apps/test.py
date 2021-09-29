import datetime
import time

from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
#from django.core.paginator import Paginator
from django.shortcuts import render_to_response
from django.conf import settings 
from django.http import *

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout as openid_logout

from django.template import RequestContext

from django.utils import simplejson

import chemical.apps.forms

from chemical.apps.viewer import Viewer
from chemical.apps.models import GusarIn, GusarResult
from chemical.apps.response import Response, ResponseGroup, ResponseItem

from chemical.apps.loader import *

from csdb.base import *
from csdb.schema import *

from csdb.media.creator import StructureMediaCreator
from csdb.database.ibm.db.schema import *
from csdb.tool.gusar import Gusar

from chemical.structure.resolver import ChemicalString


string_list = ['CCO', 'CCN', 'Aspirin']

r = Response()
r.resolve_string_list(string_list).load_structure_compound_objects().load_media().load_database_records()
#s = r.database_record_count[88843443]['ficts']['databases']

