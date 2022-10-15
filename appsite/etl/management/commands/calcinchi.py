import uuid
from typing import List

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import QuerySet

from custom.cactvs import SpecialCactvsHash
#from structure.models import Structure
from resolver.models import InChI, Structure
from etl.models import StructureFileRecord
from etl.tasks import *
from etl.registration import structure_id_chunks


logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'calcinchi'

    def handle(self, *args, **options):
        logger.info("calcinchi")
        _calcinchi()


def _calculate_inchis(structure_ids: List[int]):
    task = calculate_inchi_task
    chunks = structure_id_chunks(structure_ids)
    tasks = [task.delay(chunk) for chunk in chunks]
    return tasks


def _calcinchi():

    records: QuerySet = StructureFileRecord.objects\
        .select_related('structure')\
        .values('structure__id')\
        .filter(
            #structure_file_id=structure_file_id,
            structure__compound__isnull=False,
            structure__blocked__isnull=True,
            structure__inchis__isnull=True,
        )

    structure_ids = [r['structure__id'] for r in records]
    tasks = _calculate_inchis(structure_ids)

    logger.info("normalize: submitting %s structure IDs in %s task(s)" % (len(structure_ids), len(tasks)))















