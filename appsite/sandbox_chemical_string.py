import logging
import os
import time

from django.db.models import Prefetch
from django.db.models.functions import Coalesce

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsite.settings")

from django.conf import settings
import django

django.setup()

from django.db import connection, reset_queries

from structure.string_resolver import ChemicalStructure
from resolver.models import *

settings.DEBUG = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cirx")

reset_queries()

warfarin_smiles = [
    'C1=CC=CC2=C1C(=O)C(=C(O2)O)C(C3=CC=CC=C3)C=C(O)C',
    'C1=CC=CC3=C1C(=C(C(C2=CC=CC=C2)CC(=O)C)C(O3)=O)O',
    'C1=CC=CC3=C1C(=O)C(C(C2=CC=CC=C2)CC(O)=C)C(O3)=O',
    'C1=CC=CC2=C1C(=O)C(=C(O2)O)C(C3=CC=CC=C3)CC(=O)C',
    'C1=CC=CC3=C1C(=C(C(C2=CC=CC=C2)C=C(O)C)C(O3)=O)O',
    'C1=CC=CC3=C1C(=C(C(C2=CC=CC=C2)CC(O)=C)C(O3)=O)O',
    'C1=CC=CC3=C1C(=O)C(C(C2=CC=CC=C2)C=C(O)C)C(O3)=O',
    'C1=CC=CC3=C1C(=O)C(C(C2=CC=CC=C2)CC(=O)C)C(O3)=O',
    'C1=CC=CC2=C1C(=O)C(=C(O2)O)C(C3=CC=CC=C3)CC(O)=C'
]

for smiles in warfarin_smiles:
    structure = ChemicalStructure(ens=Ens(smiles))
    ficts_parent = structure._parent('ficts')
    t0 = time.perf_counter()
    ficus_parent = structure._parent('ficus')
    t1 = time.perf_counter()
    ficus = ficus_parent.ens.get('E_FICUS_ID')
    t2 = time.perf_counter()

    logger.info("FICTS {} FICuS {} : {} T {}".format( ficts_parent.hashisy if ficts_parent else "---", ficus_parent.hashisy if ficus_parent else "---", ficus, t1 - t0, t2 - t1))




logger.info("-----------")
logger.info("COUNT %s", len(connection.queries))
logger.info("-----------")

