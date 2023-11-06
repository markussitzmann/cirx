from django.core.management.base import BaseCommand
from django.db.models import QuerySet, Q

# from structure.models import Structure
from etl.models import StructureFile, StructureFileTag
from etl.tasks import *

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'calcinchi'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--tag', type=str, default=None)
        parser.add_argument('-l', '--limit', type=int, default=0)

    def handle(self, *args, **options):
        logger.info("calcinchi")
        _calcinchi(options)


def _calculate_inchis(structure_file_id: int):
    task_list = (
        fetch_structure_file_for_calcinchi_task.s(structure_file_id) |
        calcinchi_chunk_mapper.s(calculate_inchi_task.s())
    )
    logger.info("submitting %s tasks", len(task_list))
    return task_list.delay()


def _calcinchi(options):
    tag = options['tag']
    limit = options['limit']
    files: QuerySet = StructureFile.objects.filter(
        Q(calcinchi_status__isnull=True)
        | Q(calcinchi_status__progress__lte=0.98)
    ).exclude(tags__tag=tag, tags__process='calcinchi').all()

    n = 0
    file: StructureFile
    for file in files:
        if file.structure_file_records.count() < file.count:
            continue
        if limit and n >= limit:
            continue
        if tag:
            StructureFileTag.objects.get_or_create(structure_file=file, tag=tag, process='calcinchi')
        logger.info("calcinchi for structure file %s" % file.id)
        _calculate_inchis(file.id)
        n += 1




