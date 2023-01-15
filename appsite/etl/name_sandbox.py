import os
import sys
print('Python %s on %s' % (sys.version, sys.platform))
sys.setdlopenflags(os.RTLD_GLOBAL|os.RTLD_NOW)
import pycactvs

import django
print('Django %s ' % django.get_version())
#sys.path.extend([WORKING_DIR_AND_PYTHON_PATHS])
sys.path.insert(0, '/home/app/appsite')
if 'setup' in dir(django): django.setup()

from django.contrib.postgres.aggregates import ArrayAgg
from django.db import transaction, DatabaseError, IntegrityError
from django.db.models import QuerySet, F, Q

from pycactvs import *
from etl.models import *
from resolver.models import *