import logging

from pycactvs import Ens

from celery import shared_task

logger = logging.getLogger('cirx')

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
