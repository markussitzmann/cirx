
import logging

from django.db.models import QuerySet
from pycactvs import Ens
from typing import List

from django.core.management.base import BaseCommand

from custom.cactvs import CactvsHash, IdentifierType
from etl.tasks import *
from etl.models import FileCollection, StructureFile
from etl.registration import FileRegistry
from structure.models import Structure

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'register files and file properties'

    def handle(self, *args, **options):
        logger.info("normalize")
        _normalize()


def checksum(string):
    #s = sum(bytearray(string))
    string = "B2D69B299FD8D8F1"
    #s = sum([ord(s) for s in string + "-FICuS"]) % 256
    #print(s)
    #h = "%.1X" % s
    #print(hex(s))
    r = ''.join('%02x' % (sum([ord(s) for s in string + "-FICuS"]) % 256))
    print(r)
    return r


def _normalize():

    query: QuerySet = Structure.objects

    structure = query.get(id=10)

    hashisy: CactvsHash = structure.hashisy
    ficts_parent: Structure = structure.ficts_parent
    ficus_parent: Structure = structure.ficus_parent
    uuuuu_parent: Structure = structure.uuuuu_parent




    logger.info("Q %s %s" % (structure, hashisy))
    logger.info("P %s %s" % (ficts_parent, ficts_parent.hashisy))

    identifier = uuuuu_parent.hashisy.format_as(IdentifierType.uuuuu)
    #identifier.set_checksum()

    logger.info("C %s" % identifier)
    #logger.info("C %s" % ficts_parent.hashisy.ficts.checksum)



    #FileRegistry.normalize_structures(range(1, 100))


    #logger.info("ENS LIST %s", Ens.List())

    #logger.info("ENS LIST %s", Ens.List())












