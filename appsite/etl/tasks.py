import logging
from typing import List

from celery import shared_task, Task

from etl.registration import FileRegistry, StructureRegistry

logger = logging.getLogger('celery.task')
#logger = get_task_logger('celery.tasks')


@shared_task(name="add file")
def add_file_task(file_path: str, check: bool):
    return FileRegistry.add_file(file_path, check)


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


### Normalize

@shared_task(bind=True, name="normalize fetch")
def fetch_structure_file_for_normalization_task(self, file_id: int):
    file_id = StructureRegistry.fetch_structure_file_for_normalization(file_id)
    if file_id:
        logger.info("structure file %s fetched for normalization" % (file_id, ))
        return file_id
    return None


@shared_task(name="normalize mapper")
def normalize_chunk_mapper(file_id: int, callback):
    logger.info("args %s %s" % (file_id, callback))
    return StructureRegistry.normalize_chunk_mapper(file_id, callback)


@shared_task(name="normalize")
def normalize_structure_task(structure_ids: List[int]):
    return StructureRegistry.normalize_structures(structure_ids)


### InChI

@shared_task(bind=True, name="calcinchi fetch")
def fetch_structure_file_for_calcinchi_task(self, file_id: int):
    file_id = StructureRegistry.fetch_structure_file_for_calcinchi(file_id)
    if file_id:
        logger.info("structure file %s fetched for InChI calculation" % (file_id, ))
        return file_id
    return None


@shared_task(name="calcinchi mapper")
def calcinchi_chunk_mapper(file_id: int, callback):
    logger.info("args %s %s" % (file_id, callback))
    return StructureRegistry.calcinchi_chunk_mapper(file_id, callback)


@shared_task(name="calcinchi")
def calculate_inchi_task(structure_ids: List[int]):
    return StructureRegistry.calculate_inchi(structure_ids)
