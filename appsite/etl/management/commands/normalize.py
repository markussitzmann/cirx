from django.core.management.base import BaseCommand
from django.db.models import QuerySet, Q

from etl.models import StructureFile, StructureFileTag
from etl.tasks import *

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'normalize structures (FICTS, FICuS, uuuuu)'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--tag', type=str, default=None)
        parser.add_argument('-l', '--limit', type=int, default=0)

    def handle(self, *args, **options):
        logger.info("normalize")
        _normalize(options)


def _normalize_structures(structure_file_id: int):
    task_list = (
            fetch_structure_file_for_normalization_task.s(structure_file_id) |
            normalize_chunk_mapper.s(normalize_structure_task.s())
    )
    logger.info("submitting %s tasks", len(task_list))
    return task_list.delay()


def _normalize(options):
    tag = options['tag']
    limit = options['limit']
    files: QuerySet = StructureFile.objects.filter(
        Q(normalization_status__isnull=True)
        | Q(normalization_status__progress__lte=0.98)
    ).exclude(tags__tag=tag, tags__process='normalize').all()

    n = 0
    file: StructureFile
    for file in files:
        if file.structure_file_records.count() < file.count:
            continue
        if limit and n >= limit:
            continue
        if tag:
            StructureFileTag.objects.get_or_create(structure_file=file, tag=tag, process='normalize')
        logger.info("normalize structure file %s" % file.id)
        _normalize_structures(file.id)
        n += 1

