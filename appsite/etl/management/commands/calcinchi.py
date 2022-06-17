from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import QuerySet

from custom.cactvs import SpecialCactvsHash
from structure.models import Structure
from resolver.models import InChI
from etl.models import StructureFileRecord
from etl.tasks import *


logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'calcinchi'

    def handle(self, *args, **options):
        logger.info("calcinchi")
        _calculate_inchi()


# def normalize_structures(structure_ids: List[int]):
#     logger.info("--- bla ---")
#     task = normalize_structure_task
#
#     chunk_size = StructureRegistry.CHUNK_SIZE
#     chunks = [structure_ids[x:x + chunk_size] for x in range(0, len(structure_ids), chunk_size)]
#     tasks = [task.delay(chunk) for chunk in chunks]
#
#     return tasks


def _calculate_inchi():
    # TODO: is set locally
    settings.INIT_SYSTEM = True
    if settings.INIT_SYSTEM:
        logger.info("--- deleting InChI ---")
        for i in InChI.objects.all():
            logger.info("deleting %s", i)
            i.delete()
        logger.info("--- deleting Structure InChI ---")
        # for r in StructureInChIs.objects.all():
        #     logger.info("deleting %s", r)
        #     r.delete()
        logger.info("--- deleting blocked ---")
        for s in Structure.objects.filter(blocked__isnull=False).all():
            s.blocked = None
            s.save()

    logger.info("--- deleting done ---")

    # TODO: remove!
    structure_file_id = 1
    # TODO: remove slicing!
    records: QuerySet = StructureFileRecord.objects\
        .select_related('structure')\
        .values('structure__id')\
        .filter(
             structure_file_id=structure_file_id,
             structure__compound__isnull=False,
             structure__blocked__isnull=True
        )[10:1000]

    structure_ids = [r['structure__id'] for r in records]
    print("--->%s" % len(structure_ids))

    StructureRegistry.calculate_inchi(structure_ids)


    # tasks = normalize_structures(structure_ids)
    #
    # for task in tasks:
    #    for k, v in task.collect(intermediate=False):
    #        logger.info("%s : %s" % (k.successful(), v))

    #for r in records:
    #    print(r)

    print(len(records))













