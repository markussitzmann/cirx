
import logging
from typing import List

from django.conf import settings
from django.core.management.base import BaseCommand

from etl.tasks import *
from etl.models import StructureFileCollection, StructureFile
from etl.registration import FileRegistry

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'register files and file properties'

    def add_arguments(self, parser):
        parser.add_argument('-c', '--file_collection_id', type=int)
        parser.add_argument('-f', '--force', type=bool, default=False)

    def handle(self, *args, **options):
        logger.info("register")
        _register(options)


def register_file_records(structure_file_id: int):
    task_list = \
        (count_and_save_file_task.s(structure_file_id) |
         register_file_record_chunk_mapper.s(register_file_record_chunk_task.s()))
    return task_list.delay()


def _register(options):
    # if settings.INIT_SYSTEM:
    #     for f in StructureFile.objects.all():
    #         logger.info("INITIALIZING SYSTEM: deleting %s", f)
    #         f.delete()

    file_collections = StructureFileCollection.objects.all()
    if 'file_collection_id' in options:
        file_collections = file_collections.filter(id=options['file_collection_id'])

    tasks = []
    for file_collection in file_collections:
        processor = FileRegistry(file_collection)
        file_list: List[StructureFile] = processor.register_files(force=options['force'])

        for file in file_list:
            task = register_file_records(file.id)
            tasks.append(task)








