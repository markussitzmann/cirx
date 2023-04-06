from django.core.management.base import BaseCommand
from django.db.models import QuerySet, Q

# from structure.models import Structure
from etl.models import StructureFile
from etl.tasks import *

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'calcinchi'

    def handle(self, *args, **options):
        logger.info("calcinchi")
        _calcinchi()


def _calculate_inchis(structure_file_id: int):
    task_list = (
        fetch_structure_file_for_calcinchi_task.s(structure_file_id) |
        calcinchi_chunk_mapper.s(calculate_inchi_task.s())
    )
    logger.info("submitting %s tasks", len(task_list))
    return task_list.delay()


def _calcinchi():
    files: QuerySet = StructureFile.objects.filter(
        Q(calcinchi_status__isnull=True) | Q(calcinchi_status__progress__lte=0.98)
    ).all()
    for file in files:
        logger.info("calc inchi for structure file %s" % file.id)
        _calculate_inchis(file.id)




