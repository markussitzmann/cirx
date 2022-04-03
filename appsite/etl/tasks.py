import logging

from celery import shared_task

from etl.registration import FileRegistry
from etl.sandbox import count_box, chunk_box, chunk_creator

logger = logging.getLogger('cirx')


def register_file_records(structure_file_id: int):
    task_list = \
        (count_and_save_file_task.s(structure_file_id) |
         register_file_record_chunk_mapper.s(register_file_record_chunk_task.s()))
    return task_list.delay()


@shared_task
def count_and_save_file_task(file_id: int):
    return FileRegistry.count_and_save_file(file_id)


@shared_task
def register_file_record_chunk_mapper(file_id: int, callback):
    logger.info("args %s %s" % (file_id, callback))
    return FileRegistry.register_file_record_chunk_mapper(file_id, callback)


@shared_task
def register_file_record_chunk_task(file_id: int, chunk_number: int, chunk_size: int):
    return FileRegistry.register_file_record_chunk(file_id, chunk_number, chunk_size)


@shared_task
def count_box_task(fid):
    return count_box(fid)


@shared_task
def chunk_creator_task(count_result, callback):
    return chunk_creator(count_result, callback)


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
