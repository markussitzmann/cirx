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

affinity_classes = ['exact', 'narrow']

#query = Structure.objects.match_names(['exact', 'narrow']).filter(annotated_name__in=["Warfarin",])

query = Structure.objects.select_related('parents', 'hashisy', 'parents__ficts_parent') \
            .filter(names__affinity_class__in=affinity_classes) \
            .annotate(
                annotated_name=F('names__name__name'),
                annotated_affinity_class=F('names__affinity_class')
            )


# NSC56362 51390-22-8 NSC280834"

# structure = Structure.objects.prefetch_related('names', 'names__name').get(id=690600)
# names = structure.names.all()
# for name in names:
#     print(name.name)

structures = query\
    .filter(annotated_name__in=["NSC123", "NSC-123", "123", "10-Methylphenothiazine 5-oxide", "2234-09-5", "Phenothiazine, 5-oxide"])\
    .all()

logger.info("1 COUNT %s", len(connection.queries))
items = structures.values("id", "annotated_name", "annotated_affinity_class", "minimol")

logger.info("2 COUNT %s", len(connection.queries))
logger.info("--> COUNT %s", len(structures))

logger.info("3 COUNT %s", len(connection.queries))
for item in items:
    logger.info("I %s %s ", item, item['minimol'].ens.get("E_SMILES"))

#response = structures

logger.info("3 COUNT %s", len(connection.queries))


logger.info("%s" % structures)
logging.info("connection count: %s" % (len(connection.queries)))

#for item in structures:
#    logger.info("ID %s | %s %s %s" % (item.id, item.hashisy, item.annotated_name, item.smiles))

logger.info("-----------")
logger.info("COUNT %s", len(connection.queries))
logger.info("-----------")


for query in connection.queries:
    logger.info("%s" % query)

