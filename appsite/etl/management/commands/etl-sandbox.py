import logging
from typing import List

from django.contrib.postgres.aggregates import ArrayAgg
from django.core.management.base import BaseCommand
from django.db.models import F, Q

from etl.models import StructureFileCollection, StructureFile, StructureFileSource
from etl.tasks import FileRegistry, count_and_save_file_task, register_file_record_chunk_mapper, \
    register_file_record_chunk_task
from resolver.models import StructureNameAssociation, StructureParentStructure

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'sandbox'

    # def add_arguments(self, parser):
    #     parser.add_argument('-c', '--file_collection_id', type=int)
    #     parser.add_argument('-f', '--force', type=bool, default=False)

    def handle(self, *args, **options):
        logger.info("sandbox")
        _sandbox(options)

def _sandbox(options):

    structure_file = StructureFile.objects.get(id=8)

    # structure_count: int = StructureFileSource.objects\
    #     .filter(
    #         structure_file=structure_file,)\
    #     .distinct().count()
    # logger.info("COUNT %s", structure_count)
    #
    # structure_count_with_name: int = StructureFileSource.objects \
    #     .filter(
    #         structure_file=structure_file,
    #         structure__names__isnull=False,
    #         structure__parents__isnull=False)\
    #     .distinct().count()
    # logger.info("COUNT WITH NAME %s", structure_count_with_name)
    #
    # sfs = StructureFileSource.objects.prefetch_related('structure__names')\
    #     .filter(structure_file=structure_file).annotate(name_array=ArrayAgg('structure__names'))
    #
    # logger.info("COUNT WITH NAME %s", structure_count_with_name)
    #
    # # x = {n for n in nn if n.name_array and n.name_array[0]}
    #
    # a = StructureNameAssociation.objects\
    #     .select_related('structure__structure_source')\
    #     .filter(structure__structure_file_source__structure_file=structure_file)\
    #     .distinct('structure_id').count()
    #
    # logger.info("A %s", a)

    # structure_count: int = StructureNameAssociation.objects \
    #     .select_related('structure__structure_source') \
    #     .filter(structure__structure_file_source__structure_file_id=structure_file.id) \
    #     .distinct('structure_id').count()

    structure_count: int = StructureParentStructure.objects \
        .select_related('structure__structure_file_source') \
        .filter(structure__structure_file_source__structure_file=structure_file) \
        .filter(Q(structure_id=F('ficts_parent_id')) | Q(structure_id=F('ficus_parent_id')) | Q(structure_id=F('uuuuu_parent_id')) ) \
        .count()


    structure_count_with_name: int = StructureFileSource.objects \
        .filter(
        structure_file=structure_file,
        structure__names__isnull=False,
    ).distinct().count()

    logger.info("C %s", structure_count)
    logger.info("N %s", structure_count_with_name)





