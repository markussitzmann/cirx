from django.core.management.base import BaseCommand
from django.db.models import QuerySet, Q

# from structure.models import Structure
from etl.models import StructureFileRecord, StructureFile
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

    #task = calculate_inchi_task
    #chunks = structure_id_chunks(structure_ids)
    #tasks = [task.delay(chunk) for chunk in chunks]
    #return tasks


def _calcinchi():
    files: QuerySet = StructureFile.objects.filter(
        Q(inchi_status__isnull=True) | Q(inchi_status__progress__lte=0.95)
    ).all()
    for file in files:
        logger.info("calc inchi for structure file %s" % file.id)
        _calculate_inchis(file.id)



# def _calcinchi():
#     records: QuerySet = StructureFileRecord.objects \
#         .select_related('structure') \
#         .values('structure__id') \
#         .filter(
#         # structure_file_id=structure_file_id,
#         structure__compound__isnull=False,
#         structure__blocked__isnull=True,
#         structure__inchis__isnull=True,
#     )
#
#     structure_ids = [r['structure__id'] for r in records]
#     tasks = _calculate_inchis(structure_ids)
#
#     logger.info("normalize: submitting %s structure IDs in %s task(s)" % (len(structure_ids), len(tasks)))
