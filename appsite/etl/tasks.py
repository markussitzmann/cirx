import logging

from celery import shared_task

from etl.registration import FileRegistry
from etl.sandbox import count_box, chunk_box

logger = logging.getLogger('cirx')


@shared_task
def count_and_save_file(file_id):
    return FileRegistry.count_and_save_file(file_id)


@shared_task
def register_file_records(file_id):
    return FileRegistry.register_file_records(file_id)


@shared_task
def count_box_task(fid):
    return count_box(fid)


@shared_task
def chunk_box_task(fid, count, chunk_number, chunk_size):
    return chunk_box(fid, count, chunk_number, chunk_size)


# file_collections = FileCollection.objects.all()
#     file_collections = FileCollection.objects.filter(id=4)
#     for file_collection in file_collections:
#         processor = FileRegistry(file_collection)
#         file_list = processor.register_files()
#         for file in file_list:
#             logger.info("found file : %s" % file)
#             processor.register_file_records(file)


#
# @shared_task
# def register_file():
#     file_collections = FileCollection.objects.all()
#     file_collections = FileCollection.objects.filter(id=4)
#     for file_collection in file_collections:
#     processor = FileRegistry(file_collection)
#         file_list = processor.register_files()
#         for file in file_list:
#             logger.info("found file : %s" % file)
#     processor.register_file_records(file)
#
#
# def ficus(structure):
#     logger.info("running at worker with %s" % structure)
#     return Ens(structure).get('E_FICUS_ID')
#
#
# @shared_task
# def add(x, y):
#     return x + y
#
#
# @shared_task
# def mul(x, y):
#     return x * y
#
#
# @shared_task
# def xsum(numbers):
#     return sum(numbers)
