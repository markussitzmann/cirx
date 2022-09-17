import logging
import uuid
from typing import List

from celery import shared_task
from celery.utils.log import get_task_logger

from etl.registration import FileRegistry, StructureRegistry

logger = logging.getLogger('celery.task')
#logger = get_task_logger('celery.tasks')


@shared_task(name="register count")
def count_and_save_file_task(file_id: int):
    return FileRegistry.count_and_save_structure_file(file_id)


@shared_task(name="register mapper")
def register_file_record_chunk_mapper(file_id: int, callback):
    logger.info("args %s %s" % (file_id, callback))
    return FileRegistry.register_structure_file_record_chunk_mapper(file_id, callback)


@shared_task(name="register")
def register_file_record_chunk_task(file_id: int, chunk_number: int, chunk_size: int):
    return FileRegistry.register_structure_file_record_chunk(file_id, chunk_number, chunk_size)


@shared_task(name="normalize")
def normalize_structure_task(structure_ids: List[uuid.UUID]):
    return StructureRegistry.normalize_structures(structure_ids)


@shared_task(name="calcinchi")
def calculate_inchi_task(structure_ids: List[uuid.UUID]):
    return StructureRegistry.calculate_inchi(structure_ids)
