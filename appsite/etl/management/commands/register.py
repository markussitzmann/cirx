
import logging

from django.core.management.base import BaseCommand, CommandError

from etl.models import FileCollection
from etl.registration import FileRegistry

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'register files and file properties'

    def handle(self, *args, **options):
        logger.info("register")
        _register()


def _register():
    file_collections = FileCollection.objects.all()
    for file_collection in file_collections:
        processor = FileRegistry(file_collection)
        file_list = processor.register_files()
        for file in file_list:
            logger.info("found file : %s" % file)
            processor.register_file_records(file)






