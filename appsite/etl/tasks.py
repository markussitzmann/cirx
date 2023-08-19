import logging
from typing import List, Tuple

from celery import shared_task, Task

from etl.registration import FileRegistry, StructureRegistry

logger = logging.getLogger('celery.task')
#logger = get_task_logger('celery.tasks')


@shared_task(name="add file", queue='register')
def add_file_task(file_path: str, check: bool):
    return FileRegistry.add_file(file_path, check)


@shared_task(name="register count", queue='register')
def count_and_save_file_task(file_id: int):
    return FileRegistry.count_and_save_structure_file(file_id)


@shared_task(name="register mapper", queue='register')
def register_file_record_chunk_mapper(file_id: int, callback):
    logger.info("args %s %s" % (file_id, callback))
    return FileRegistry.register_structure_file_record_chunk_mapper(file_id, callback)


@shared_task(name="register", queue='register')
def register_file_record_chunk_task(file_id: int, chunk_number: int, chunk_size: int):
    return FileRegistry.register_structure_file_record_chunk(file_id, chunk_number, chunk_size)


### Normalize

@shared_task(name="normalize fetch", queue='normalize')
def fetch_structure_file_for_normalization_task(file_id: int):
    file_id = StructureRegistry.fetch_structure_file_for_normalization(file_id)
    if file_id:
        logger.info("structure file %s fetched for normalization" % (file_id, ))
        return file_id
    return None


@shared_task(name="normalize mapper", queue='normalize')
def normalize_chunk_mapper(file_id: int, callback):
    logger.info("args %s %s" % (file_id, callback))
    return StructureRegistry.normalize_chunk_mapper(file_id, callback)


@shared_task(name="normalize", queue='normalize')
def normalize_structure_task(structure_id_arg_tuples: Tuple[int, List[int]]):
    return StructureRegistry.normalize_structures(structure_id_arg_tuples)


### InChI

@shared_task(bind=True, name="calcinchi fetch", queue='calcinchi')
def fetch_structure_file_for_calcinchi_task(self, file_id: int):
    file_id = StructureRegistry.fetch_structure_file_for_calcinchi(file_id)
    if file_id:
        logger.info("structure file %s fetched for InChI calculation" % (file_id, ))
        return file_id
    return None


@shared_task(name="calcinchi mapper", queue='calcinchi')
def calcinchi_chunk_mapper(file_id: int, callback):
    logger.info("args %s %s" % (file_id, callback))
    return StructureRegistry.calcinchi_chunk_mapper(file_id, callback)


@shared_task(name="calcinchi", queue='calcinchi')
def calculate_inchi_task(structure_id_arg_tuples: Tuple[int, List[int]]):
    return StructureRegistry.calculate_inchi(structure_id_arg_tuples)


### Link Names

@shared_task(name="linkname fetch", queue='linkname')
def fetch_structure_file_for_linkname_task(file_id: int):
    file_id = StructureRegistry.fetch_structure_file_for_linkname(file_id)
    if file_id:
        logger.info("structure file %s fetched for linking structure names" % (file_id, ))
        return file_id
    return None


@shared_task(name="linkname mapper", queue='linkname')
def linkname_chunk_mapper(file_id: int, callback):
    logger.info("args %s %s" % (file_id, callback))
    return StructureRegistry.linkname_chunk_mapper(file_id, callback)


@shared_task(name="linkname", queue='linkname')
def link_structure_names_task(structure_id_arg_tuples: Tuple[int, List[int]]):
    return StructureRegistry.link_structure_names(structure_id_arg_tuples)
