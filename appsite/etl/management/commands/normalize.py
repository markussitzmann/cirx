import uuid
from typing import List

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import QuerySet

from custom.cactvs import SpecialCactvsHash
from etl.models import StructureFileRecord
from etl.tasks import *
from etl.registration import structure_id_chunks
from resolver.models import Structure, Compound

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'normalize structures (FICTS, FICuS, uuuuu)'

    def handle(self, *args, **options):
        logger.info("normalize")
        _normalize()


def _normalize_structures(structure_ids: List[uuid.UUID]):
    task = normalize_structure_task
    chunks = structure_id_chunks(structure_ids)
    tasks = [task.delay(chunk) for chunk in chunks]
    return tasks


def _normalize():
    records: QuerySet = StructureFileRecord.objects\
        .select_related('structure')\
        .values('structure__id')\
        .filter(
            #structure_file_id=structure_file_id,
            structure__compound__isnull=True,
            structure__blocked__isnull=True,
            structure__ficts_parent__isnull=True,
            structure__ficus_parent__isnull=True,
            structure__uuuuu_parent__isnull=True,
        ).exclude(
            structure__hashisy_key=SpecialCactvsHash.ZERO.hashisy
        ).exclude(
            structure__hashisy_key=SpecialCactvsHash.MAGIC.hashisy
        )

    structure_ids = [r['structure__id'] for r in records]
    tasks = _normalize_structures(structure_ids)

    logger.info("normalize: submitting %s structure IDs in %s task(s)" % (len(structure_ids), len(tasks)))
















