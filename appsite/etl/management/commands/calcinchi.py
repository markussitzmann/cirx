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


def _calculate_inchis(structure_ids: List[uuid.UUID]):
    task = calculate_inchi_task
    chunks = structure_id_chunks(structure_ids)
    tasks = [task.delay(chunk) for chunk in chunks]
    return tasks


def _calcinchi():
    # TODO: is set locally
    #settings.INIT_SYSTEM = True
    #if settings.INIT_SYSTEM:
    #    logger.info("--- deleting InChI ---")
    #    for i in InChI.objects.all():
    #        logger.info("deleting %s", i)
    #        i.delete()
    #    logger.info("--- deleting Structure InChI ---")
    #    # for r in StructureInChIs.objects.all():
    #    #     logger.info("deleting %s", r)
    #    #     r.delete()
    #    logger.info("--- deleting blocked ---")
    #    for s in Structure.objects.filter(blocked__isnull=False).all():
    #        s.blocked = None
    #        s.save()

    #logger.info("--- deleting done ---")

    # TODO: remove!
    structure_file_id = 1
    # TODO: remove slicing!
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

    #for task in tasks:
    #  for k, v in task.collect(intermediate=False):
    #      logger.info("%s : %s" % (k.successful(), v))

    #########

    # structure_ids = [r['structure__id'] for r in records]
    # print("--->%s" % len(structure_ids))
    #
    # StructureRegistry.calculate_inchi(structure_ids)


    #print(len(records))













