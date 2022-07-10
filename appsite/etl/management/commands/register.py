
import logging
from typing import List

from django.conf import settings
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


def register_file_records(structure_file_id: int):
    task_list = \
        (count_and_save_file_task.s(structure_file_id) |
         register_file_record_chunk_mapper.s(register_file_record_chunk_task.s()))
    return task_list.delay()


def _register():
    if settings.INIT_SYSTEM:
        for f in StructureFile.objects.all():
            logger.info("INITIALIZING SYSTEM: deleting %s", f)
            f.delete()

    #file_collections = FileCollection.objects.all()
    file_collections = FileCollection.objects.filter(id=4)

    tasks = []
    for file_collection in file_collections:
        processor = FileRegistry(file_collection)
        file_list: List[StructureFile] = processor.register_files()

        for file in file_list:
            task = register_file_records(file.id)
            tasks.append(task)

    for task in tasks:
        for k, v in task.collect(intermediate=False):
            logger.info("%s : %s" % (k.successful(), v))






