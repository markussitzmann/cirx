from typing import List

from django.core.management.base import BaseCommand
from django.db.models import QuerySet

from custom.cactvs import IdentifierType, SpecialCactvsHash
from etl.tasks import *
from etl.models import StructureFileRecord
from structure.models import Structure

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'register files and file properties'

    def handle(self, *args, **options):
        logger.info("normalize")
        _normalize()





def _normalize():

    records: QuerySet = StructureFileRecord.objects\
        .select_related('structure')\
        .filter(
            structure_file_id=38,
            structure__compound__isnull=True,
            structure__blocked__isnull=True,
            structure__ficts_parent__isnull=True,
            structure__ficus_parent__isnull=True,
            structure__uuuuu_parent__isnull=True,
        ).exclude(
            structure__hashisy=SpecialCactvsHash.ZERO.value
        ).exclude(
            structure__hashisy=SpecialCactvsHash.MAGIC.value
        )


    logger.info("R --> %s" % sorted([(r.id, r.structure.id) for r in records.all()]))

    query: QuerySet = Structure.objects
    logger.info("--> %s" % query.count())

    filtered = query.filter(
        compound__isnull=True,
        blocked__isnull=True,
#        ficts_parent__isnull=True,
#        ficus_parent__isnull=True,
#        uuuuu_parent__isnull=True,
    )

    logger.info("--> %s", filtered.count())
    logger.info("--> %s", [s.structure_file_records.all() for s in filtered.order_by('id').all()])


    #logger.info("--> %s", structure.hashisy.format_as(IdentifierType.FICuS))
    #logger.info("--> %s", structure.ficus_parent.hashisy.format_as(IdentifierType.FICuS))
    #logger.info("--> %s", structure.ficus_parent.has_compound())


    #logger.info("--> %s", structure.ficus_parent)


    #FileRegistry.normalize_structures(range(1, 100))
    #logger.info("ENS LIST %s", Ens.List())













