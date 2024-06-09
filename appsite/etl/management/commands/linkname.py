from django.core.management.base import BaseCommand
from django.db.models import QuerySet, Q

from etl.models import StructureFile, StructureFileTag
from etl.tasks import *

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'link structure names'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--tag', type=str, default=None)
        parser.add_argument('-l', '--limit', type=int, default=0)

    def handle(self, *args, **options):
        logger.info("linkname")
        _linkname(options)


def _link_structure_names(structure_file_id: int):
    task_list = (
        fetch_structure_file_for_linkname_task.s(structure_file_id) |
        linkname_chunk_mapper.s(link_structure_names_task.s())
    )
    logger.info("submitting %s tasks", len(task_list))
    return task_list.delay()


def _linkname(options):
    tag = options['tag']
    limit = options['limit']
    files: QuerySet = StructureFile.objects.filter(
        Q(linkname_status__isnull=True)
        | Q(linkname_status__progress__lte=0.999)
    ).exclude(tags__tag=tag, tags__process='linkname').all()

    n = 0
    file: StructureFile
    for file in files:
        if file.structure_file_records.count() < file.count:
            continue
        if limit and n >= limit:
            continue
        if tag:
            StructureFileTag.objects.get_or_create(structure_file=file, tag=tag, process='linkname')
        logger.info("link names for structure file %s" % file.id)
        _link_structure_names(file.id)
        n += 1

















