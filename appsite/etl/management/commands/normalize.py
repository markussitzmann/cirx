from django.core.management.base import BaseCommand
from django.db.models import QuerySet, Q

from custom.cactvs import SpecialCactvsHash
from etl.models import StructureFileRecord, StructureFile
from etl.registration import structure_id_chunks
from etl.tasks import *

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'normalize structures (FICTS, FICuS, uuuuu)'

    def handle(self, *args, **options):
        logger.info("normalize")
        _normalize()


def _normalize_structures(structure_file_id: int):
    task_list = (
        fetch_structure_file_for_normalization_task.s(structure_file_id)
        | normalize_chunk_mapper.s(normalize_structure_task.s())
    )
    logger.info("submitting %s tasks", len(task_list))
    return task_list.delay()




#def _normalize_structures(structure_ids: List[int]):
#    task = normalize_structure_task
#    chunks = structure_id_chunks(structure_ids)
#    tasks = [task.delay(chunk) for chunk in chunks]
#    return tasks

def _normalize():
    files: QuerySet = StructureFile.objects.filter(
        Q(normalization_status__isnull=True) | Q(normalization_status__finished=False)
    ).all()
    for file in files:
        _normalize_structures(file.id)


# def _normalize():
#     records: QuerySet = StructureFileRecord.objects\
#         .select_related('structure')\
#         .values('structure__id')\
#         .filter(
#             #structure_file_id=structure_file_id,
#             structure__compound__isnull=True,
#             structure__blocked__isnull=True,
#             #structure__ficts_parent__isnull=True,
#             #structure__ficus_parent__isnull=True,
#             #structure__uuuuu_parent__isnull=True,
#         ).exclude(
#             structure__hashisy_key=SpecialCactvsHash.ZERO.hashisy
#         ).exclude(
#             structure__hashisy_key=SpecialCactvsHash.MAGIC.hashisy
#         )
#
#     structure_ids = [r['structure__id'] for r in records]
#     tasks = _normalize_structures(structure_ids)
#
#     logger.info("normalize: submitting %s structure IDs in %s task(s)" % (len(structure_ids), len(tasks)))
















