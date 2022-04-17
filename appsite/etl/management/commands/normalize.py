
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
        logger.info("register")
        _normalize()


# def _register():
#     #file_collections = FileCollection.objects.all()
#     file_collections = FileCollection.objects.filter(id=4)
#     for file_collection in file_collections:
#         processor = FileRegistry(file_collection)
#         file_list: List[StructureFile] = processor.register_files()
#         file: StructureFile
#         for file in file_list:
#             logger.info("found file : %s" % file)
#             processor.register_file_records(file)


def _normalize():

    FileRegistry.normalize_structures(range(10, 15))


    logger.info("ENS LIST %s", Ens.List())

    logger.info("ENS LIST %s", Ens.List())










