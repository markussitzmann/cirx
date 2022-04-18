
import logging
from pycactvs import Ens
from typing import List

from django.core.management.base import BaseCommand

from etl.tasks import *
from etl.models import FileCollection, StructureFile
from etl.registration import FileRegistry

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'register files and file properties'

    def handle(self, *args, **options):
        logger.info("normalize")
        _normalize()



def _normalize():

    FileRegistry.normalize_structures(range(1, 100))


    logger.info("ENS LIST %s", Ens.List())

    logger.info("ENS LIST %s", Ens.List())










