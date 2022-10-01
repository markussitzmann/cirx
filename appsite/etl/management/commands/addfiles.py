import glob, os
import gzip
import logging
import shutil
from pathlib import PurePath, Path

from django.conf import settings
from pycactvs import Molfile

from django.core.management.base import BaseCommand


logger = logging.getLogger('cirx')

FILE_CHUNK_SIZE=10000

class Command(BaseCommand):
    help = 'add structure to the file store'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--pattern', type=str)
        parser.add_argument('-r', '--release', type=int, default=None)

    def handle(self, *args, **options):
        logger.info("addfiles")
        _addfiles(options)


def _addfiles(options):
    logger.info("pattern %s" % options['pattern'])
    pattern = options['pattern']

    instore_path = settings.CIR_INSTORE_ROOT
    files = sorted(Path(instore_path).glob(pattern))
    for file in files:
        outfile_path = _create_filestore_name(file, 0)[1].parent
        Path(outfile_path).mkdir(parents=True, exist_ok=False)
        molfile: Molfile = Molfile.Open(str(file))
        i = 0
        finished = False
        while i < 1000:
            i += 1
            outfile_name_and_path = _create_filestore_name(file, i)
            with open(outfile_name_and_path[0], 'wb') as outfile:
                try:
                    logger.info(outfile_name_and_path)
                    molfile.copy(outfile=outfile, count=FILE_CHUNK_SIZE)
                except RuntimeError:
                    finished = True
            with open(outfile_name_and_path[0], 'rb') as f_in:
                with gzip.open(outfile_name_and_path[0] + 'z', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            if finished:
                break
    logger.info("done")


def _create_filestore_name(file_path, index):
    parent = file_path.parent
    stem = file_path.stem
    suffixes = file_path.suffixes
    splitted_stem = stem.split(".", 1)

    #name_elements = [splitted_stem[0], "." + str(index)]
    name_elements = [splitted_stem[0], "." + str(index)]
    name_elements.extend(suffixes)
    new_name = "".join(name_elements)
    dir_name = name_elements[0]

    filestore_name = os.path.join(
        str(settings.CIR_FILESTORE_ROOT),
        str(os.path.split(parent)[1:][0]),
        str(dir_name),
        str(new_name)
    )

    return filestore_name, Path(filestore_name)




    #logger.info("SPLIT NAME %s", dname)
    #logger.info("F NAME %s", fname)


# def _normalize_structures(structure_ids: List[int]):
#     task = normalize_structure_task
#     chunks = structure_id_chunks(structure_ids)
#     tasks = [task.delay(chunk) for chunk in chunks]
#     return tasks
#
#
# def _normalize():
#     records: QuerySet = StructureFileRecord.objects\
#         .select_related('structure')\
#         .values('structure__id')\
#         .filter(
#             #structure_file_id=structure_file_id,
#             structure__compound__isnull=True,
#             structure__blocked__isnull=True,
#             structure__ficts_parent__isnull=True,
#             structure__ficus_parent__isnull=True,
#             structure__uuuuu_parent__isnull=True,
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
















