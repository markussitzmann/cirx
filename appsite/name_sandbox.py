import logging
import os

from django.db.models import Prefetch

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

#prefetch = Prefetch()
#prefetch = Prefetch('parents__ficts_parent', queryset=Structure.objects.all(), to_attr='ficts_parent_structure')

query = Structure.objects.match_names(['narrow',]).filter(id=313113, annotated_name="NSC271626")

# NSC56362 51390-22-8 NSC280834"

structures = query.all()[0:1000]

logger.info("A COUNT %s", len(structures))
logger.info("B COUNT %s", len(connection.queries))


response = structures

logger.info("COUNT %s", len(connection.queries))


logger.info("%s" % structures)
logging.info("connection count: %s" % (len(connection.queries)))

for item in response:
    logger.info("ID %s | %s %s" % (item.id, item.hashisy, item.annotated_name))

logger.info("-----------")
logger.info("COUNT %s", len(connection.queries))
logger.info("-----------")


for query in connection.queries:
    logger.info("%s" % query)
