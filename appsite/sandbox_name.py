import logging
import os

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

compounds = [200, 203]
names = ["NSC810703", "NSC810731", ]

exact = NameAffinityClass.objects.filter(title="exact").first()
pubchem_substance_synonym = NameType.objects.filter(title="PUBCHEM_SUBSTANCE_SYNONYM").first()

affinity_classes = [exact, ]

name_associations = StructureNameAssociation.with_related_objects.by_compound(
  compounds=compounds,
  affinity_classes=affinity_classes
).all()

for a in name_associations.all():
    logger.info("COMPOUND %s %s %s -> %s : %s" % (
        a.name,
        a.affinity_class,
        a.name_type,
        a.structure,
        a.structure.compound.id
    ))


compound_associations = StructureNameAssociation.with_related_objects.by_name(
   names=names,
   name_types=[pubchem_substance_synonym, ],
   affinity_classes=affinity_classes
)

for a in compound_associations.all():
    logger.info("NAME %s %s %s -> %s : %s" % (a.name, a.affinity_class, a.name_type, a.structure, a.structure.compound.id))


logger.info("-----------")
logger.info("COUNT %s", len(connection.queries))
logger.info("-----------")

