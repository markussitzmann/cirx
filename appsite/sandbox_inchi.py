import logging
import os
import sys

# Pycactvs needs that
sys.setdlopenflags(os.RTLD_GLOBAL|os.RTLD_NOW)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsite.settings")

from django.conf import settings
import django
django.setup()

from django.db import connection, reset_queries
from resolver.models import *

settings.DEBUG = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cirx")

from inchi.identifier import InChIKey


reset_queries()

compounds = [200, 203]
inchikeys = ["IQNVSUXISHTAPK-UHFFFAOYSA-N", "ZYSBALASVLAQKM-UHFFFAOYNA-N"]
partial_inchikeys = ["IQNVSUXISHTAPK-UHFFFAOYSA", "IQNVSUXISHTAPK", "ORRDQCCQFUMUHZ-UHFFFAOYSA"]

standard = InChIType.objects.filter(title="standard").first()

inchi_associations = StructureInChIAssociation.with_related_objects.by_compound(
  compounds=compounds,
  inchi_types=[standard, ]
).all()

for a in inchi_associations.all():
    logger.info("COMPOUND %s %s -> %s : %s" % (
        a.inchi,
        a.inchi_type,
        a.structure,
        a.structure.compound.id
    ))


inchi_associations = StructureInChIAssociation.with_related_objects.by_inchikey(
  inchikeys=inchikeys,
  inchi_types=[standard, ]
).all()

for a in inchi_associations.all():
    logger.info("INCHIKEY %s %s -> %s : %s" % (
        a.inchi,
        a.inchi_type,
        a.structure,
        a.structure.compound.id
    ))

inchi_associations = StructureInChIAssociation.with_related_objects.by_partial_inchikey(
  inchikeys=partial_inchikeys
).all()

for a in inchi_associations.all():
    logger.info("PARTIAL %s %s -> %s : %s" % (
        a.inchi,
        a.inchi_type,
        a.structure,
        a.structure.compound.id
    ))


for k in partial_inchikeys:
    io = InChIKey(key="InChIKey" + k)
    logger.info(">>> %s", io)

logger.info("-----------")
logger.info("COUNT %s", len(connection.queries))
logger.info("-----------")


