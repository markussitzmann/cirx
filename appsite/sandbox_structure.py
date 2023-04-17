import logging
import os
from collections import defaultdict

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
hashisy_list1 = ['42DD33293B742322', '4BCD5CEFEB609C11', 0x42DD33293B742322, 0x4BCD5CEFEB609C11]
hashisy_list2 = [0x42DD33293B742322, 0x4BCD5CEFEB609C11]
hashisy_list3 = [4818063428540441378, 5462124108586195985]


structures = Structure.with_related_objects.by_compound(
  compounds=compounds
).all()

for structure in structures:
    logger.info("SID %s : CID %s : int %s : FICTS %s FICUS %s UUUUU %s" % (
        structure.id,
        structure.compound.id,
        structure.hashisy_key.int,
        structure.parents.ficts_parent,
        structure.parents.ficus_parent,
        structure.parents.uuuuu_parent
    ))
    #logger.info("XXX %s %s" % (
    #    structure.parents.ficts_parent.compound.id,
    #    structure.inchis.all()
    #))


compounds = [s.compound for s in structures]
inchis = StructureInChIAssociation.with_related_objects.by_compound(compounds=compounds)
d = defaultdict(list)
logger.info([d[inchi.structure.compound].append(inchi.inchi) for inchi in inchis])
logger.info(d)

structures = Structure.with_related_objects.by_hashisy(
  hashisy_list=hashisy_list1
).all()

for structure in structures:
    logger.info("HASH1 SID %s : CID %s : FICTS %s FICUS %s UUUUU %s" % (
        structure.id,
        structure.compound.id,
        structure.parents.ficts_parent,
        structure.parents.ficus_parent,
        structure.parents.uuuuu_parent
    ))

structures = Structure.with_related_objects.by_hashisy(
  hashisy_list=hashisy_list2
).all()

for structure in structures:
    logger.info("HASH2 SID %s : CID %s : FICTS %s FICUS %s UUUUU %s" % (
        structure.id,
        structure.compound.id,
        structure.parents.ficts_parent,
        structure.parents.ficus_parent,
        structure.parents.uuuuu_parent
    ))

structures = Structure.with_related_objects.by_hashisy(
  hashisy_list=hashisy_list3
).all()

for structure in structures:
    logger.info("HASH3 SID %s : CID %s : FICTS %s FICUS %s UUUUU %s" % (
        structure.id,
        structure.compound.id,
        structure.parents.ficts_parent,
        structure.parents.ficus_parent,
        structure.parents.uuuuu_parent
    ))

logger.info("-----------")
logger.info("COUNT %s", len(connection.queries))
logger.info("-----------")


