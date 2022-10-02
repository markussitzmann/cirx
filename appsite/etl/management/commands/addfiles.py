import logging
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from etl.tasks import add_file_task

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'add structure to the file store'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--pattern', type=str)
        parser.add_argument('-c', '--check', type=bool, default=False)
        #parser.add_argument('-r', '--release', type=int, default=None)

    def handle(self, *args, **options):
        logger.info("addfiles")
        _addfiles(options)


def _addfile(file, check):
    task = add_file_task.delay(file, check)
    return task


def _addfiles(options):
    logger.info("pattern %s" % options['pattern'])
    pattern = options['pattern']
    check = options['check']

    instore_path = settings.CIR_INSTORE_ROOT
    files = sorted(Path(instore_path).glob(pattern))
    for file in files:
        logger.info("submitting file %s", file)
        _addfile(str(file), check)
    logger.info("done")


# def _add_file(file_path, check):
#     file = PurePath(file_path)
#     outfile_path = _create_filestore_name(file, 0)[1].parent
#     try:
#         Path(outfile_path).mkdir(parents=True, exist_ok=False)
#     except FileExistsError:
#         logger.critical("target destination '%s' already exists - skipped" % outfile_path)
#         return
#     molfile: Molfile = Molfile.Open(str(file))
#     if check:
#         molfile_count = molfile.count()
#         logger.info("file count %s" % molfile_count)
#     i = 0
#     finished = False
#     chunk_sum_count = 0
#     while i < MAX_CHUNKS:
#         i += 1
#         outfile_name_and_path = _create_filestore_name(file, i)
#         outfile_name = outfile_name_and_path[0]
#         temp_outfile_name = outfile_name + ".tmp"
#         with open(temp_outfile_name, 'wb') as outfile:
#             try:
#                 logger.info("creating chunk %s" % outfile_name)
#                 molfile.copy(outfile=outfile, count=FILE_CHUNK_SIZE)
#             except RuntimeError:
#                 finished = True
#         with open(temp_outfile_name, 'rb') as chunk_file:
#             with gzip.open(outfile_name, 'wb') as zipped_chunk_file:
#                 shutil.copyfileobj(chunk_file, zipped_chunk_file)
#             os.remove(temp_outfile_name)
#             if check:
#                 chunk_molfile: Molfile = Molfile.Open(outfile_name)
#                 chunk_molfile_count = chunk_molfile.count()
#                 chunk_sum_count += chunk_molfile_count
#                 chunk_molfile.close()
#                 logger.info("chunk file count %s sum %s" % (chunk_molfile_count, chunk_sum_count))
#         if finished:
#             if check:
#                 try:
#                     assert chunk_sum_count == molfile_count
#                     logger.info("check passed")
#                 except:
#                     logger.critical("check failed")
#             molfile.close()
#             break


# def _create_filestore_name(file_path, index):
#     parent = file_path.parent
#     stem = file_path.stem
#     suffixes = file_path.suffixes
#     splitted_stem = stem.split(".", 1)
#
#     name_elements = [splitted_stem[0], "." + str(index)]
#     name_elements.extend(suffixes)
#     new_name = "".join(name_elements)
#     dir_name = name_elements[0]
#
#     filestore_name = os.path.join(
#         str(settings.CIR_FILESTORE_ROOT),
#         str(os.path.split(parent)[1:][0]),
#         str(dir_name),
#         str(new_name)
#     )
#
#     return filestore_name, Path(filestore_name)

















