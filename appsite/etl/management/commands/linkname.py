from django.core.management.base import BaseCommand
from django.db.models import QuerySet, Q

from etl.models import StructureFile
from etl.tasks import *

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'link structure names'

    def handle(self, *args, **options):
        logger.info("linkname")
        _linkname()


def _link_structure_names(structure_file_id: int):
    task_list = (
        fetch_structure_file_for_normalization_task.s(structure_file_id) |
        normalize_chunk_mapper.s(normalize_structure_task.s())
    )
    logger.info("submitting %s tasks", len(task_list))
    return task_list.delay()


def _linkname():
    files: QuerySet = StructureFile.objects.filter(
        Q(normalization_status__isnull=True) | Q(normalization_status__progress__lte=0.98)
    ).all()
    for file in files:
        logger.info("normalize structure %s" % file.id)
        _link_structure_names(file.id)
















