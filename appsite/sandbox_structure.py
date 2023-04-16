import logging
import os

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Prefetch
from django.db.models.functions import Coalesce

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsite.settings")

from django.conf import settings
import django
django.setup()

from django.db import connection, reset_queries
from resolver.models import *

settings.DEBUG = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cirx")

reset_queries()

compounds = [200, 203, 400, 333]

structures = Structure.with_related_objects.by_compound(
  compounds=compounds
).all()

for structure in structures:
    logger.info("SID %s : CID %s : FICTS %s FICUS %s UUUUU %s" % (
        structure.id,
        structure.compound.id,
        structure.parents.ficts_parent,
        structure.parents.ficus_parent,
        structure.parents.uuuuu_parent
    ))
    logger.info("XXX %s" % structure.parents.ficts_parent.compound.id)

logger.info("-----------")
logger.info("COUNT %s", len(connection.queries))
logger.info("-----------")


