import os
import sys

os.environ['PYTHON_EGG_CACHE'] = '/var/cache/pythoneggs'
os.environ['DJANGO_SETTINGS_MODULE'] = 'chemical.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

path = '/www/django'
if not path in sys.path:
	sys.path.append(path)
