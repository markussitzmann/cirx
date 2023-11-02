import logging
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from etl.tasks import add_file_task
from etl.models import StructureFileCollection

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'add structure to the file store'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--pattern', type=str)
        parser.add_argument('-c', '--check', type=bool, default=False)
        parser.add_argument('-r', '--release', type=int, default=0)

        #parser.add_argument('-r', '--release', type=int, default=None)

    def handle(self, *args, **options):
        logger.info("addfiles")
        _addfiles(options)


def _addfile(file, check, release):
    task = add_file_task.delay(file, check, release)
    return task


def _addfiles(options):
    logger.info("pattern %s" % options['pattern'])
    pattern = options['pattern']
    check = options['check']
    release = options['release']

    instore_path = settings.CIR_INSTORE_ROOT
    files = sorted(Path(instore_path).glob(pattern))
    for file in files:
        logger.info("submitting file %s", file)
        _addfile(str(file), check, release)

    logger.info("done")




















