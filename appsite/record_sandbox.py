import logging
import os

from django.db.models import Prefetch
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsite.settings")

from django.conf import settings
import django
django.setup()

from django.db import connection, reset_queries
from resolver.models import *
from etl.models import *


settings.DEBUG = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cirx")

reset_queries()

records = Record.objects\
    .select_related('structure_file_record', 'structure_file_record__structure', 'structure_file_record__structure__parents')\
    .annotate(
        annotated_structure=F('structure_file_record__structure'),
        annotated_ficts_parent=F('structure_file_record__structure__parents__ficts_parent'),
        annotated_ficus_parent=F('structure_file_record__structure__parents__ficus_parent')
    )\
    .filter(annotated_structure=9731)

#sfr = StructureFileRecord.objects.select_related('structure')
#print(sfr)

r = records.first()
logger.info(r)
logger.info("FICTS %s" % r.annotated_ficts_parent)
logger.info("FICUS %s" % r.annotated_ficus_parent)


logger.info(connection.queries)
logger.info(len(connection.queries))

