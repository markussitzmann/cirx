import logging
from pathlib import Path
from typing import List

import shortuuid

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
        parser.add_argument('-s', '--preprocessors', type=int, nargs='+')

    def handle(self, *args, **options):
        logger.info("addfiles")
        logger.info(options)
        if bool(options['release']) != bool(options['preprocessors']):
            logger.error("REFUSED: if a release is set, specification of a preprocessor is required, or vice versa")
        _addfiles(options)


def _addfile(key: str, pattern: str, file: str, check: bool, release: int, preprocessors: List[int]):
    task = add_file_task.delay(key, pattern, file, check, release, preprocessors)
    return task


def _addfiles(options):
    logger.info("pattern %s" % options['pattern'])
    pattern = options['pattern']
    check = options['check']
    release = options['release']
    preprocessors = options['preprocessors']

    instore_path = settings.CIR_INSTORE_ROOT
    files = sorted(Path(instore_path).glob(pattern))
    if not files:
        logger.warning("no files are matching the pattern")
    key = shortuuid.uuid()[:8]
    for file in files:
        logger.info("submitting file %s %s", file, key)
        _addfile(key, pattern, str(file), check, release, preprocessors)

    logger.info("done")




















