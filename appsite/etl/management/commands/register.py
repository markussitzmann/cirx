
import logging
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
        _register()


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


def _register():

    for f in StructureFile.objects.all():
        logger.info("deleting %s", f)
        f.delete()

    file_collections = FileCollection.objects.all()
    #file_collections = FileCollection.objects.filter(id=4)
    for file_collection in file_collections:
        processor = FileRegistry(file_collection)
        file_list: List[StructureFile] = processor.register_files()

        for file in file_list:
            register_file_records(file.id)





