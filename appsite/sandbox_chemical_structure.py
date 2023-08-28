import logging
import os
import sys
import gc
from time import sleep

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsite.settings")

from django.conf import settings
import django

# Pycactvs needs that
sys.setdlopenflags(os.RTLD_GLOBAL|os.RTLD_NOW)

django.setup()

from django.db import connection, reset_queries
from pycactvs import Dataset, Ens

from dispatcher import Dispatcher
from structure.string_resolver import ChemicalStructure, ChemicalString

#from resolver.models import *

settings.DEBUG = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cirx")

reset_queries()

#ens = Ens("CC(=O)CC(C1=CC=CC=C1)C2=C(C3=CC=CC=C3OC2=O)O")



def resolver():

    chemical_string = ChemicalString("tautomers:warfarin")
    logger.info("---> {}".format(chemical_string))

    #del(chemical_string)

def dispatcher():
    dispatcher = Dispatcher(request=None, representation_type='image')
    response = dispatcher.parse("tautomers:warfarin")
    logger.info("LOG {}".format(response._asdict()))

def sandbox():

    ens = Ens("CCO")
    chemical_structure = ChemicalStructure(ens=ens)

    structure = chemical_structure.structure
    ficts_parent = chemical_structure.ficts_parent()
    ficus_parent = chemical_structure.ficus_parent()

    logger.info("STRUCTURE {}".format(structure.id))
    logger.info("FICTS {} {} {}".format(ficts_parent.structure.id, ficts_parent.ens, ficts_parent.hashisy))
    if ficus_parent:
        logger.info("FICUS {} {} {}".format(ficus_parent.structure.id, ficus_parent.ens, ficus_parent.hashisy))
    else:
        logger.info("NO FICUS")

    chemical_structure2 = ChemicalStructure(structure=structure)

    structure2 = chemical_structure2.structure
    ficts_parent2 = chemical_structure2.ficts_parent()
    ficus_parent2 = chemical_structure2.ficus_parent()

    logger.info("STRUCTURE {}".format(structure2.id))
    logger.info("FICTS {} {} {}".format(ficts_parent2.structure.id, ficts_parent2.ens, ficts_parent2.hashisy))
    if ficus_parent:
        logger.info("FICUS {} {} {}".format(ficus_parent.structure.id, ficus_parent.ens, ficus_parent.hashisy))
    else:
        logger.info("NO FICUS")

#sandbox()

for i in range(1000):
    #gc.collect()
    #sleep(1)
    dispatcher()
    logger.info("-----------")
    logger.info("COUNT QUERIES {}".format(len(connection.queries)))
    logger.info("-----------")
    logger.info("{} COUNT ENS {} DATASET {}".format(i, len(Ens.List()), len(Dataset.List())))


