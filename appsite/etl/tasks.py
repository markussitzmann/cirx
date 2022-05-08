import logging

from celery import shared_task
from etl.registration import FileRegistry, StructureRegistry

logger = logging.getLogger('cirx')


@shared_task
def count_and_save_file_task(file_id: int):
    return FileRegistry.count_and_save_structure_file(file_id)


@shared_task
def register_file_record_chunk_mapper(file_id: int, callback):
    logger.info("args %s %s" % (file_id, callback))
    return FileRegistry.register_structure_file_record_chunk_mapper(file_id, callback)


@shared_task
def register_file_record_chunk_task(file_id: int, chunk_number: int, chunk_size: int):
    return FileRegistry.register_structure_file_record_chunk(file_id, chunk_number, chunk_size)


@shared_task
def normalize_structure_task(structure_ids: list):
    return StructureRegistry.normalize_structures(structure_ids)

