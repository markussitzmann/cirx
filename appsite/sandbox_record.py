import logging
import os

from django.core.files import File
from django.db.models import Prefetch, OuterRef, Subquery
from django.db.models.functions import JSONObject

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

# record: Record = Record.objects.filter(structure_file_record=213541).first()
# logger.info("R {}".format(record))
#
# structure: Structure = record.structure_file_record.structure
# ens: Ens = structure.to_ens
# #
# # molfile: str = record.structure_file_record.source.decode('UTF-8')
# file: StructureFile = record.structure_file_record.structure_file
# number = record.structure_file_record.number
# #
# #
# logger.info("E0 {}".format(ens.get("E_SMILES")))
# # #logger.info("M {}".format(molfile))
# # logger.info("F {} :: {}".format(file, number))
#
# m = Molfile.Open("/home/app/error.1.sdf")
# #m.set('record', number)
# e = m.read()
#
# #logger.info("E {}".format(e.get("E_SMILES")))
#
#
# #minimol = e.get("E_MINIMOL")
# #e2 = Ens(minimol)
# minimol = CactvsMinimol(e)
# e2 = minimol.ens
# parent = e2.get("E_FICTS_STRUCTURE")
#
#
# logger.info("E {}".format(e.get("E_SMILES")))
# logger.info("E2 {}".format(e2.get("E_SMILES")))
# logger.info("P {}".format(parent.get("E_SMILES")))

m = Molfile.Open("/home/app/error.2.sdf")
ens = m.read()

hashisy = CactvsHash(ens)
structure = Structure(
    hash=hashisy,
    minimol=CactvsMinimol(ens)
)

structures = Structure.objects.filter(hashisy_key=hashisy_key).all()

logger.info("// {}".format(structures))

structure = structures[0]

ficts_parent = structure.parents.ficts_parent.to_ens

e = structure.to_ens

#e = minimol.ens

logger.info("E2.0 https://cirx.chemicalcreatures.com/chemical/structure/{}/image".format(e.get("E_SMILES")))

e.hadd()

logger.info("E2.1 https://cirx.chemicalcreatures.com/chemical/structure/{}/image".format(e.get("E_SMILES")))

logger.info("E2.1 https://cirx.chemicalcreatures.com/chemical/structure/{}/image".format(ficts_parent.get("E_SMILES")))


#structure_object, created = Structure.objects.get_or_create(structure)

#logger.info("--> {}", structure_object)

# minimol = CactvsMinimol(e)
# e2 = minimol.ens
#
# logger.info("E2.0 https://cirx.chemicalcreatures.com/chemical/structure/{}/image".format(e2.get("E_SMILES")))
#
# e2.hadd()
#
# logger.info("E2.1 https://cirx.chemicalcreatures.com/chemical/structure/{}/image".format(e2.get("E_SMILES")))











