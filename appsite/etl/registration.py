import datetime
import glob
import gzip
import hashlib
import logging
import math
import os
import shutil
import time
from collections import namedtuple, defaultdict
from dataclasses import dataclass, field
from pathlib import PurePath, Path
from typing import List, Optional, Dict

from mmap import mmap, ACCESS_READ
from hashlib import md5
from uuid import UUID

import pytz
import ujson as json
from celery import subtask, group
from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import transaction, DatabaseError, IntegrityError
from django.db.models import QuerySet, F, Q
from pycactvs import Molfile, Ens, Prop

from core.common import NCICADD_TYPES, InChIAndSaveOpt, INCHI_TYPES
from core.cactvs import CactvsHash, CactvsMinimol, SpecialCactvsHash
from etl.models import StructureFileCollection, StructureFile, StructureFileField, StructureFileRecord, \
    ReleaseNameField, StructureFileCollectionPreprocessor, StructureFileNormalizationStatus, \
    StructureFileCalcInChIStatus, \
    StructureFileRecordNameAssociation, StructureFileSource, StructureFileLinkNameStatus
from resolver.models import InChI, Structure, Compound, StructureInChIAssociation, InChIType, Dataset, Publisher, \
    Release, NameType, Name, Record, StructureHashisy, StructureParentStructure, StructureNameAssociation, \
    NameAffinityClass
from structure.inchi.identifier import InChIString, InChIKey

logger = logging.getLogger('celery.task')

from pycactvs import cactvs

CACTVS_SETTINGS = cactvs
CACTVS_SETTINGS['python_object_autodelete'] = True
CACTVS_SETTINGS['lookup_hosts'] = []

DEFAULT_CHUNK_SIZE = 10000
DEFAULT_DATABASE_ROW_BATCH_SIZE = 50000
DEFAULT_LOGGER_BLOCK = 100
DEFAULT_MAX_CHUNK_NUMBER = 1000

Status = namedtuple('Status', 'file created')

StructureRelationships = namedtuple('StructureRelationships', 'structure relationships')
StructureFileRecordReleaseTuple = namedtuple('StructureFileRecordRelease', 'record releases')

PubChemDatasource = namedtuple('PubChemDatasource', 'name url')


@dataclass(frozen=True)
class NameData:
    name: str = None
    hash: str = None
    name_type: str = None
    parent: str = None

    def __hash__(self):
        return hash(self.hash)


@dataclass
class RecordData:
    structure_file: StructureFile
    hash: CactvsHash
    index: int
    preprocessors: defaultdict = field(default_factory=lambda: defaultdict(dict))
    release_name: str = None
    release_object: Release = None
    record_object: Record = None
    structure_file_record_object: StructureFileRecord = None
    regid: str = None
    regid_hash: str = None
    version: int = 1
    names: List[NameData] = field(default_factory=lambda: [])

    def __str__(self):
        return "RecordData[index=%s, release=%s, regid=%s, regid_hash=%s]" % (
            self.index, self.release_object, self.regid, self.regid_hash)

    def __hash__(self) -> int:
        return hash(repr(self.structure_file.id) + ":" + repr(self.index))


class FileRegistry(object):
    CHUNK_SIZE = DEFAULT_CHUNK_SIZE
    MAX_CHUNKS = DEFAULT_MAX_CHUNK_NUMBER
    DATABASE_ROW_BATCH_SIZE = DEFAULT_DATABASE_ROW_BATCH_SIZE

    def __init__(self, file_collection: StructureFileCollection):
        self.file_collection = file_collection
        self._file_name_list = glob.glob(
            os.path.join(settings.CIR_FILESTORE_ROOT, file_collection.file_location_pattern_string),
            recursive=True
        )
        self._file_list = list()

    @staticmethod
    def hash_file(file_path: str):
        with open(file_path, 'rb') as file, mmap(file.fileno(), 0, access=ACCESS_READ) as file:
            return md5(file).hexdigest()

    @staticmethod
    def add_file(key: str, pattern: str, file_path: str, check: bool = False, release: int = 0,
                 preprocessors: List[int] = None):
        file: PurePath = PurePath(file_path)
        if release and preprocessors:
            check = True
        outfile_path = FileRegistry._create_filestore_name(key, file, 0)[1].parent
        logger.info("out file path: %s", outfile_path)

        filestore_pattern = FileRegistry._create_filestore_pattern(key, file)
        logger.info("pattern: %s", filestore_pattern)

        try:
            Path(outfile_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.critical("SKIPPED - something went wrong creating the target directory %s %s" % (outfile_path, e))
            return
        molfile: Molfile = Molfile.Open(str(file))
        if check:
            molfile_count = molfile.count()
            logger.info("file count %s" % molfile_count)
        else:
            molfile_count = -1
        i = 0
        finished = False
        chunk_sum_count = 0
        while i < FileRegistry.MAX_CHUNKS:
            i += 1
            outfile_name_and_path = FileRegistry._create_filestore_name(key, file, i)
            outfile_name = outfile_name_and_path[0]
            temp_outfile_name = outfile_name + ".tmp"
            with open(temp_outfile_name, 'wb') as outfile:
                try:
                    logger.info("creating chunk %s" % outfile_name)
                    molfile.copy(outfile=outfile, count=FileRegistry.CHUNK_SIZE)
                except RuntimeError:
                    finished = True
            with open(temp_outfile_name, 'rb') as chunk_file:
                with gzip.open(outfile_name, 'wb') as zipped_chunk_file:
                    shutil.copyfileobj(chunk_file, zipped_chunk_file)
                os.remove(temp_outfile_name)
                if check:
                    chunk_molfile: Molfile = Molfile.Open(outfile_name)
                    chunk_molfile_count = chunk_molfile.count()
                    chunk_sum_count += chunk_molfile_count
                    chunk_molfile.close()
                    logger.info("chunk file count %s sum %s" % (chunk_molfile_count, chunk_sum_count))
            if finished:
                if check:
                    try:
                        assert chunk_sum_count == molfile_count
                        logger.info("check passed")
                    except:
                        logger.critical("check failed")
                if release and preprocessors:
                    logger.info("linking dataset release")
                    description = ""
                    if pattern:
                        description = "addfile using file pattern %s with key %s" % (pattern, key)
                    structure_file_collection, created = StructureFileCollection.objects.get_or_create(
                        release_id=release,
                        file_location_pattern_string=filestore_pattern
                    )
                    structure_file_collection.preprocessors.add(*preprocessors)
                    structure_file_collection.description = description
                    structure_file_collection.save()
                molfile.close()
                break

    def register_files(self, force=False) -> List[StructureFile]:
        self._file_list = \
            [status.file for fname in self._file_name_list if (status := self.register_file(fname, force)).created]
        return self._file_list

    def register_file(self, fname, force=False) -> Status:
        structure_file, created = StructureFile.objects.get_or_create(
            collection=self.file_collection,
            file=fname
        )
        if created:
            try:
                file_hash = FileRegistry.hash_file(fname)
                structure_file.hash = file_hash
                structure_file.save()
            except Exception as e:
                logging.warning("calculation of file hash failed for %s %s" % (fname, e))
            return Status(file=structure_file, created=True)
        if not force:
            logger.info("file '%s' had already been registered previously (%s records)" % (fname, structure_file.count))
            return Status(file=structure_file, created=False)
        else:
            logger.info("file '%s' had already been registered previously (%s records) but registration was enforced"
                        % (fname, structure_file.count))
            return Status(file=structure_file, created=True)

    @staticmethod
    def count_and_save_structure_file(structure_file_id: int) -> int:
        structure_file = StructureFile.objects.get(id=structure_file_id)
        logger.info("structure file %s", structure_file)
        if structure_file:
            fname = structure_file.file.name
            logger.info("counting file '%s'", fname)
            molfile_handle = Molfile.Open(fname)
            try:
                with transaction.atomic():
                    structure_file.count = molfile_handle.count()
                    structure_file.save()
            except (IntegrityError, DatabaseError) as e:
                logging.error("counting of %s failed: %s" % (fname, e))
                raise Exception("counting of %s failed", fname)
        logger.info("structure file has been counted successfully: %s", structure_file)
        return structure_file_id

    @staticmethod
    def register_structure_file_record_chunk_mapper(structure_file_id: int, callback):
        try:
            logger.info("register structure file record chunk mapper for structure file id %s" % structure_file_id)
            structure_file = StructureFile.objects.get(id=structure_file_id)
            count = structure_file.count
        except Exception as e:
            logger.error("structure file and count not available for file id %s" % structure_file_id)
            raise Exception(e)
        chunk_size = FileRegistry.CHUNK_SIZE
        chunk_number = math.ceil(count / chunk_size)
        chunks = range(0, chunk_number)
        callback = subtask(callback)
        return group(callback.clone([structure_file_id, chunk, chunk_size]) for chunk in chunks)()

    @staticmethod
    def register_structure_file_record_chunk(
            structure_file_id: int,
            chunk_number: int,
            chunk_size: int,
            max_records=None,
    ) -> int:
        logger.info("---------- STARTED with file %s chunk %s size %s" % (structure_file_id, chunk_number, chunk_size))
        logger.info("accepted task for registering file with id: %s chunk %s" % (structure_file_id, chunk_number))
        structure_file: StructureFile = StructureFile.objects.get(id=structure_file_id)

        chunk_time0 = time.perf_counter()
        count: int
        if not structure_file.count:
            count = Molfile.Count(structure_file.file.name)
            logger.warning("no count provided, counted now %s", count)
        else:
            count = structure_file.count
        file_records = range(1, count + 1)
        chunks = [file_records[i:i + min(chunk_size, count)] for i in range(0, count, chunk_size)]
        try:
            chunk_records = chunks[chunk_number]
        except IndexError as e:
            logging.info("chunks %s index %s" % (len(chunks), chunk_number))
            logging.warning("chunk index exceeded - skipped")
            return structure_file_id
        record: int = chunk_records[0]
        last_record: int = chunk_records[-1]

        logger.info("registering file records for file %s (file id %s | chunk %s | first record %s | last record %s )" %
                    (structure_file.file.name, structure_file_id, chunk_number, record, last_record))

        fname: str = structure_file.file.name
        preprocessors: List[StructureFileCollectionPreprocessor] = [
            p for p in structure_file.collection.preprocessors.all()
        ]

        molfile: Molfile = Molfile.Open(fname)
        molfile.set('record', record)

        structures: list = list()
        record_data_list: List[RecordData] = list()
        release = structure_file.collection.release

        record -= 1
        while record < last_record:
            record += 1
            if not record % DEFAULT_LOGGER_BLOCK:
                logger.info("processed record %s of %s", record, fname)
            try:
                molfile.set('record', record)
                ens: Ens = molfile.read()
                hash = CactvsHash(ens)
                structure = Structure(
                    hash=hash,
                    minimol=CactvsMinimol(ens)
                )
                structures.append(structure)

            except Exception as e:
                logger.error("error while registering file record '%s': %s" % (fname, e))
                break

            for preprocessor in preprocessors:
                record_data = RecordData(structure_file=structure_file, hash=hash, index=record)
                record_data_list.append(record_data)
                preprocessor_callable = getattr(Preprocessors, preprocessor.name, None)
                if callable(preprocessor_callable):
                    preprocessor_callable(release, structure_file, preprocessor, ens, record_data)
                else:
                    logger.warning("preprocessor '%s' was not callable", preprocessor_callable)
            if max_records and record >= max_records:
                break
        molfile.close()
        logger.info("finished reading records")

        structures = sorted(structures, key=lambda s: s.hash.int)

        logger.info("adding registration data to database for file '%s'" % (fname,))
        g0 = time.perf_counter()
        try:
            with transaction.atomic():
                for preprocessor in preprocessors:
                    preprocessor_transaction = getattr(Preprocessors, preprocessor.name + "_transaction", None)
                    if callable(preprocessor_transaction):
                        logger.info("starting preprocessor transaction %s" % preprocessor.name)
                        preprocessor_transaction(structure_file, record_data_list)
                        logger.info("finished preprocessor %s transaction" % preprocessor.name)

                time0 = time.perf_counter()
                structure_objects = Structure.objects.bulk_create(
                    structures,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
                StructureFileSource.objects.bulk_create_from_structures(
                    structures=structure_objects,
                    structure_file=structure_file,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE
                )
                time1 = time.perf_counter()
                logging.info("STRUCTURE BULK Time: %ss Count: %s" % ((time1 - time0), len(structures)))

                time0 = time.perf_counter()
                structure_hashkey_dict = StructureHashisy.objects.bulk_create_from_hash_list(
                    [record_data.hash for record_data in record_data_list],
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    skip_hashisy_creation=True
                )
                time1 = time.perf_counter()
                logging.info(
                    "STRUCTURE HASHISY BULK Time: %s Count: %s" % ((time1 - time0), len(structure_hashkey_dict)))

                logger.info("registering structure file records for '%s'" % (fname,))
                sorted_record_data_structure_list = sorted(
                    [
                        (record_data.index, record_data, structure_hashkey_dict[record_data.hash])
                        for record_data in record_data_list
                    ],
                    key=lambda u: u[0]
                )
                structure_file_record_object_dict = {}
                for data in sorted_record_data_structure_list:
                    index, record_data, structure = data
                    if index not in structure_file_record_object_dict:
                        structure_file_record_object = StructureFileRecord(
                            structure_file=structure_file,
                            structure=structure,
                            number=index,
                        )
                        structure_file_record_object_dict[index] = structure_file_record_object
                    record_data.structure_file_record_object = structure_file_record_object_dict[index]

                time0 = time.perf_counter()
                structure_file_records = StructureFileRecord.objects.bulk_create(
                    structure_file_record_object_dict.values(),
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                )
                time1 = time.perf_counter()
                logging.info("STRUCTURE RECORD BULK T: %ss C: %s" % ((time1 - time0), len(structure_file_records)))

                name_set, name_type_set = set(), set()
                for record_data in record_data_list:
                    for name_data in record_data.names:
                        name_set.add(name_data)
                        name_type_set.add((name_data.name_type, name_data.parent))

                NameType.objects.bulk_create(
                    [NameType(title=item[1]) for item in name_type_set],
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
                name_type_dict = {name_type.title: name_type for name_type in NameType.objects.all()}

                name_type_list = []
                for item in name_type_set:
                    name_type_list.append(NameType(title=item[0], parent=name_type_dict[item[1]]))
                NameType.objects.bulk_create(
                    name_type_list,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
                name_type_dict = {name_type.title: name_type for name_type in NameType.objects.all()}

                time0 = time.perf_counter()
                name_list = [Name(
                    hash=UUID(data.hash),
                    name=data.name
                ) for data in name_set]
                Name.objects.bulk_create(
                    name_list,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
                names = Name.objects.in_bulk([UUID(n.hash) for n in name_set], field_name='hash')
                time1 = time.perf_counter()
                logging.info("NAME BULK Time: %ss Count: %s" % ((time1 - time0), len(names)))

                structure_file_record_dict = {
                    str(r.structure_file.id) + ":" + str(r.number): r for r in structure_file_records
                }

                record_list = list()
                for record_data in record_data_list:
                    key = str(record_data.structure_file.id) + ":" + str(record_data.index)
                    sfr = structure_file_record_dict[key]
                    record_object = Record(
                        name=names[UUID(record_data.regid_hash)],
                        regid=record_data.regid,
                        version=record_data.version,
                        release=record_data.release_object,
                        dataset=record_data.release_object.dataset,
                        structure_file_record=sfr
                    )
                    record_list.append(record_object)
                    record_data.record_object = record_object

                time0 = time.perf_counter()
                Record.objects.bulk_create(
                    record_list,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                )
                time1 = time.perf_counter()
                logging.info("RECORD BULK Time: %ss" % (time1 - time0))

                structure_file_record_name_objects = []
                for record_data in record_data_list:
                    for name in record_data.names:
                        sfr_name_association = StructureFileRecordNameAssociation(
                            name=names[UUID(name.hash)],
                            structure_file_record=record_data.structure_file_record_object,
                            name_type=name_type_dict[name.name_type]
                        )
                        structure_file_record_name_objects.append(sfr_name_association)

                StructureFileRecordNameAssociation.objects.bulk_create(
                    structure_file_record_name_objects,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )

        except DatabaseError as e:
            logger.error("file record registration failed for '%s': %s" % (fname, e))
            raise (DatabaseError(e))
        except Exception as e:
            logger.error("file record registration failed for '%s': %s" % (fname, e))
            raise Exception(e)

        g1 = time.perf_counter()
        chunk_time1 = time.perf_counter()

        logging.info("TRANSACTION BULK T: %ss" % (g1 - g0))
        t = ((chunk_time1 - chunk_time0) * 1000) / chunk_size
        logging.info("TIME PER RECORD: %.1fms" % t)

        return structure_file_id

    @staticmethod
    def _create_filestore_name(key: str, file_path: PurePath, index):
        parent = file_path.parent
        stem = file_path.stem
        suffixes = file_path.suffixes
        if suffixes[-1] != ".gz":
            suffixes.append(".gz")
        splitted_stem = stem.split(".", 1)

        name_elements = [splitted_stem[0], "." + str(index)]
        name_elements.extend(suffixes)
        new_name = "".join(name_elements)

        filestore_name = os.path.join(
            str(settings.CIR_FILESTORE_ROOT),
            *[str(p) for p in parent.parts[2:]],
            key,
            str(new_name)
        )
        return filestore_name, Path(filestore_name)

    @staticmethod
    def _create_filestore_pattern(key: str, file_path: PurePath):
        parent = file_path.parent
        # stem = file_path.stem
        suffixes = file_path.suffixes
        if suffixes[-1] != ".gz":
            suffixes.append(".gz")

        # splitted_stem = stem.split(".", 1)
        file_pattern = os.path.join(
            *[str(p) for p in parent.parts[2:]],
            key,
            "*" + "".join(suffixes)
        )
        logger.info(file_pattern)
        return file_pattern


class StructureRegistry(object):
    CHUNK_SIZE = 1000

    @staticmethod
    def fetch_structure_file_for_normalization(structure_file_id: int) -> Optional[int]:
        try:
            structure_file = StructureFile.objects.get(id=structure_file_id)
        except StructureFile.DoesNotExist:
            return None
        logger.info("normalize structure file %s", structure_file)
        if hasattr(structure_file, 'normalization_status'):
            status = structure_file.normalization_status
        else:
            status = StructureFileNormalizationStatus(structure_file=structure_file)
            status.save()
        if status.progress > 0.95:
            return None
        return structure_file_id

    @staticmethod
    def normalize_chunk_mapper(structure_file_id: int, chunk_task):
        try:
            logger.info("normalize chunk mapper for structure file id %s" % structure_file_id)
            structure_file = StructureFile.objects.get(id=structure_file_id)
            records: QuerySet = StructureFileRecord.objects \
                .select_related('structure', 'structure__parents') \
                .values('structure__id') \
                .filter(
                    structure_file=structure_file,
                    structure__parents__isnull=True,
                    structure__blocked__isnull=True,
                ).exclude(
                    structure__hash=SpecialCactvsHash.ZERO.hashisy
                ).exclude(
                    structure__hash=SpecialCactvsHash.MAGIC.hashisy
                )
        except Exception as e:
            logger.error("structure file and count not available")
            raise Exception(e)
        return StructureRegistry.structure_records_to_chunk_callbacks(records, structure_file_id, chunk_task)

    @staticmethod
    def normalize_structures(structure_id_arg_tuples):
        logger.info("ens %s dataset %s" % (cactvs['ens_count'], cactvs['dataset_count']))

        structure_file_id, structure_ids = structure_id_arg_tuples

        structure_file = StructureFile.objects.get(id=structure_file_id)
        # NOTE: the order matters, it has to go from broader to more specific identifier!!
        identifiers = NCICADD_TYPES

        source_structures: Dict[int, Structure] = Structure.objects.in_bulk(structure_ids, field_name='id')
        parent_structure_relationships = []
        source_structure_relationships = []

        local_index: int = 0
        for structure_id, structure in source_structures.items():
            local_index += 1
            if structure.blocked:
                logger.info("structure %s is blocked and has been skipped" % (structure_id,))
                continue
            try:
                related_hashes = {}
                t0 = time.perf_counter()
                for identifier in identifiers:
                    relationships = {}
                    ens = structure.to_ens
                    parent_ens = ens.get(identifier.parent_structure)
                    cactvs_hash: CactvsHash = CactvsHash(parent_ens)
                    related_hashes[identifier.attr] = cactvs_hash
                    parent_structure: Structure = Structure(
                        hash=cactvs_hash,
                        minimol=CactvsMinimol(parent_ens)
                    )
                    parent_structure_relationships \
                        .append(StructureRelationships(parent_structure, related_hashes.copy()))
                    relationships[identifier.attr] = cactvs_hash
                    source_structure_relationships.append(StructureRelationships(structure, relationships))
                t1 = time.perf_counter()
                if not local_index % DEFAULT_LOGGER_BLOCK:
                    ens0 = structure.to_ens
                    natoms = len([a.get('A_SYMBOL') for a in ens0.atoms() if a.get('A_SYMBOL') != 'H'])
                    complexity = ens0.get('E_COMPLEXITY')
                    Ens.Delete(ens0)
                    logger.info("finished normalizing structure %s (%s atoms, %s) after %.2f "
                                "(structure_file_id %s structure_id %s) "
                                "ens %s dataset %s" %
                                (
                                    local_index,
                                    natoms,
                                    complexity,
                                    (t1 - t0),
                                    structure_file_id,
                                    structure_id,
                                    cactvs['ens_count'],
                                    cactvs['dataset_count']
                                )
                    )
            except Exception as e:
                structure.blocked = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
                structure.save()
                logger.error("normalizing structure %s failed : %s" % (structure_id, e))

        parent_structure_hash_list = list(set([p.structure.hash for p in parent_structure_relationships]))
        try:
            with transaction.atomic():
                # create parent structures in bulk
                structures = sorted(
                    [p.structure for p in parent_structure_relationships], key=lambda s: s.hash.int
                )
                Structure.objects.bulk_create(
                    structures,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )

                # fetch hashisy / parent structures in bulk (by that they have an id)
                parent_structures = Structure.objects.in_bulk(parent_structure_hash_list, field_name='hash')
                StructureHashisy.objects.bulk_create_from_hash_list(parent_structures.keys())
                StructureFileSource.objects.bulk_create_from_structures(
                    parent_structures.values(),
                    structure_file,
                    FileRegistry.DATABASE_ROW_BATCH_SIZE
                )

                # create compounds in bulk
                compound_structures = sorted(parent_structures.values(), key=lambda s: s.hash.int)
                Compound.objects.bulk_create(
                    [Compound(structure=compound_structure) for compound_structure in compound_structures],
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )

                source_structure_dict = {
                    id: StructureParentStructure(structure=source_structures[id]) for id in source_structures
                }
                for relationship in source_structure_relationships:
                    parent = source_structure_dict[relationship.structure.id]
                    for attr, parent_hash in relationship.relationships.items():
                        setattr(parent, attr, parent_structures[parent_hash])
                sorted_source_structures = sorted(source_structure_dict.values(), key=lambda p: p.structure_id)
                StructureParentStructure.objects.bulk_create(
                    sorted_source_structures,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )

                parent_structure_dict = {
                    id: StructureParentStructure(structure=parent_structures[id]) for id in parent_structures
                }
                for relationship in parent_structure_relationships:
                    parent = parent_structure_dict[relationship.structure.hash]
                    for attr, parent_hash in relationship.relationships.items():
                        setattr(parent, attr, parent_structures[parent_hash])
                sorted_parent_structure = sorted(parent_structure_dict.values(), key=lambda p: p.structure_id)
                StructureParentStructure.objects.bulk_create(
                    sorted_parent_structure,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )

        except DatabaseError as e:
            logger.error(e)
            raise (DatabaseError(e))
        except Exception as e:
            logger.error(e)
            raise Exception(e)
        StructureRegistry.update_normalization_status(structure_file_id)
        StructureRegistry.update_calcinchi_progress(structure_file_id, silent=True)
        return True

    @staticmethod
    def update_normalization_status(file_id):
        structure_file = StructureFile.objects.get(id=file_id)
        records: QuerySet = StructureFileRecord.objects \
            .select_related('structure', 'structure__parents') \
            .values('structure__id') \
            .filter(
            structure_file=structure_file,
            structure__parents__isnull=False,
        )
        structure_file_count = structure_file.count
        records_count = records.count()
        logger.info("structure normalization progress for file %s: %s (%s : %s)" % (
            structure_file.id,
            structure_file_count == records_count,
            structure_file_count,
            records_count
        ))
        status, created = StructureFileNormalizationStatus.objects.get_or_create(structure_file=structure_file)
        status.progress = records_count / structure_file_count
        status.save()

    @staticmethod
    def fetch_structure_file_for_calcinchi(structure_file_id: int) -> Optional[int]:
        try:
            structure_file = StructureFile.objects.get(id=structure_file_id)
        except StructureFile.DoesNotExist:
            return None
        logger.info("calc inchi structure file %s", structure_file)
        if hasattr(structure_file, 'calcinchi_status'):
            status = structure_file.calcinchi_status
        else:
            status = StructureFileCalcInChIStatus(structure_file=structure_file)
            status.save()
        if status.progress > 0.98:
            return None
        return structure_file_id

    @staticmethod
    def calcinchi_chunk_mapper(structure_file_id: int, chunk_task):
        try:
            logger.info("calcinchi chunk mapper for structure file id %s" % structure_file_id)
            structure_file = StructureFile.objects.get(id=structure_file_id)
            structure_id_list: QuerySet = StructureFileSource.objects \
                .select_related('structure') \
                .values('structure__id') \
                .filter(
                structure_file=structure_file,
                structure__blocked__isnull=True,
                structure__inchis__isnull=True,
            )
        except Exception as e:
            logger.error("selecting structure records for InChI calculation failed")
            raise Exception(e)

        return StructureRegistry.structure_records_to_chunk_callbacks(structure_id_list, structure_file_id, chunk_task)

    @staticmethod
    def calculate_inchi(structure_id_arg_tuples):
        structure_file_id, structure_ids = structure_id_arg_tuples
        logger.info("---------- STARTED with file %s size %s" % (structure_file_id, len(structure_ids)))

        source_structures: Dict[int, Structure] = Structure.objects.in_bulk(structure_ids, field_name='id')

        logger.info("source_structures %s", len(source_structures.keys()))

        for inchi_type in INCHI_TYPES:
            options = Prop(inchi_type.property).getparam("options")
            options += " SaveOpt"
            Prop(inchi_type.property).setparam("options", options)

        structure_to_inchi_relationships = []
        local_index: int = 0
        for structure_id, structure in source_structures.items():
            local_index += 1
            if structure.blocked:
                logger.info("structure %s is blocked and has been skipped" % (structure_id,))
                continue
            try:
                inchi_relationships = {}
                t0 = time.perf_counter()
                for inchi_type in INCHI_TYPES:
                    inchi_property = Prop.Ref(inchi_type.property)
                    inchi_property.setparam("options", inchi_type.options)
                    ens = structure.to_ens
                    split_string = ens.get(inchi_type.property).split('\\')
                    split_length = len(split_string)
                    if split_length:
                        inchi_string = split_string[0]
                    else:
                        logging.warning("no InChI string available")
                        continue
                    inchi_saveopt: Optional[str] = None
                    if split_length >= 2:
                        inchi_saveopt = split_string[1]
                    key = InChIKey(ens.get(inchi_type.key))
                    inchi_string = InChIString(
                        key=key,
                        string=inchi_string,
                        validate_key=False
                    )
                    inchi: InChI = InChI(**inchi_string.model_dict)
                    inchi_relationships[inchi_type] = InChIAndSaveOpt(inchi, inchi_saveopt)
                structure_to_inchi_relationships.append(StructureRelationships(structure_id, inchi_relationships))
                t1 = time.perf_counter()

                if not local_index % DEFAULT_LOGGER_BLOCK:
                    logger.info("finished calculating inchi %s after %.2f "
                                "(structure_file_id %s structure_id %s) "
                                "ens %s dataset %s" %
                                (
                                    local_index,
                                    (t1 - t0),
                                    structure_file_id,
                                    structure_id,
                                    cactvs['ens_count'],
                                    cactvs['dataset_count']
                                )
                    )
            except Exception as e:
                structure.blocked = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
                structure.save()
                logger.error("calculating inchi for structure %s failed : %s" % (structure_id, e))

        inchi_dict = {
            inchi_data.inchi.key: inchi_data.inchi
            for structure_to_inchi in structure_to_inchi_relationships
            for inchi_data in structure_to_inchi.relationships.values()
        }

        sorted_inchi_list = sorted(inchi_dict.values(), key=lambda inchi: inchi.key)

        try:
            with transaction.atomic():
                InChI.objects.bulk_create(
                    sorted_inchi_list,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
                inchi_objects = InChI.objects.bulk_get_from_objects(inchi_dict.values())
                inchi_objects_by_key = {i.key: i for i in inchi_objects}

                structure_id_list = [s.structure for s in structure_to_inchi_relationships]
                structure_objects = Structure.objects.in_bulk(structure_id_list, field_name='id')

                inchi_type_objects = InChIType.objects.in_bulk(
                    [t.id for t in INCHI_TYPES],
                    field_name='title'
                )

                structure_inchi_associations = []
                for structure_to_inchi in structure_to_inchi_relationships:
                    sid = structure_to_inchi.structure
                    for inchi_type, inchi_data in structure_to_inchi.relationships.items():
                        if inchi_data.inchi.key in inchi_objects_by_key:
                            inchi = inchi_objects_by_key[inchi_data.inchi.key]
                        else:
                            logger.warning("associated inchi does not exists %s" % (inchi_data.inchi.key,))
                            continue

                        structure_inchi_association = StructureInChIAssociation(
                            structure=structure_objects[sid],
                            inchi=inchi,
                            inchi_type=inchi_type_objects[inchi_type.id],
                            save_opt=inchi_data.saveopt if inchi_data.saveopt else "",
                            software_version=inchi_type.softwareversion
                        )
                        structure_inchi_associations.append(structure_inchi_association)
                sorted_structure_inchi_associations = sorted(structure_inchi_associations,
                                                             key=lambda item: (item.inchi_id, item.structure_id))
                StructureInChIAssociation.objects.bulk_create(
                    sorted_structure_inchi_associations,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
        except DatabaseError as e:
            logger.error(e)
            raise (DatabaseError(e))
        except Exception as e:
            logger.error(e)
            raise Exception(e)
        StructureRegistry.update_calcinchi_progress(structure_file_id)
        return True

    @staticmethod
    def update_calcinchi_progress(file_id, silent=False):
        structure_file = StructureFile.objects.get(id=file_id)
        structure_count: int = StructureFileSource.objects \
            .filter(
            structure_file=structure_file,
        ).distinct().count()
        structure_count_with_inchi: int = StructureFileSource.objects \
            .filter(
            structure_file=structure_file,
            structure__inchis__isnull=False
        ).distinct().count()
        if not silent:
            logger.info("inchi calculation progress file %s: %s (%s : %s)" % (
                structure_file.id,
                structure_count == structure_count_with_inchi,
                structure_count_with_inchi,
                structure_count
            ))
            logger.info("PROGRESS %s/%s %s" % (
                structure_count_with_inchi,
                structure_count,
                structure_count_with_inchi / structure_count)
                        )
        status, created = StructureFileCalcInChIStatus.objects.get_or_create(structure_file=structure_file)
        status.progress = structure_count_with_inchi / structure_count
        status.save()

    @staticmethod
    def structure_records_to_chunk_callbacks(records: QuerySet, structure_file_id: int, chunk_task):
        count = len(records)
        chunk_size = StructureRegistry.CHUNK_SIZE
        chunks = [records[i:i + min(chunk_size, count)] for i in range(0, count, chunk_size)]
        chunk_subtask = subtask(chunk_task)
        chunk_task_args = [[r['structure__id'] for r in chunk] for chunk in chunks]
        chunk_tasks = [chunk_subtask.clone(((structure_file_id, args,),), ) for args in chunk_task_args]
        return group(chunk_tasks)()

    #########

    @staticmethod
    def fetch_structure_file_for_linkname(structure_file_id: int) -> Optional[int]:
        try:
            structure_file = StructureFile.objects.get(id=structure_file_id)
        except StructureFile.DoesNotExist:
            return None
        logger.info("link name structure file %s", structure_file)
        if hasattr(structure_file, 'linkname_status'):
            status = structure_file.linkname_status
        else:
            status = StructureFileLinkNameStatus(structure_file=structure_file)
            status.save()
        if status.progress > 0.98:
            return None
        return structure_file_id

    @staticmethod
    def linkname_chunk_mapper(structure_file_id: int, chunk_task):
        try:
            logger.info("linkname chunk mapper for structure file id %s" % structure_file_id)
            structure_file = StructureFile.objects.get(id=structure_file_id)
            structure_id_list: QuerySet = StructureFileSource.objects \
                .select_related('structure') \
                .values('structure__id') \
                .filter(
                structure_file=structure_file,
                structure__blocked__isnull=True,
                #structure__names__isnull=True,
            )
        except Exception as e:
            logger.error("selecting structures for name linking failed")
            raise Exception(e)

        return StructureRegistry.structure_records_to_chunk_callbacks(structure_id_list, structure_file_id, chunk_task)

    @staticmethod
    def link_structure_names(arg_tuple):
        structure_file_id, structure_ids = arg_tuple

        sorted_structure_ids = sorted(structure_ids)
        logger.info("IN %s %s [%s, %s]" % (
            structure_file_id,
            len(structure_ids), sorted_structure_ids[0],
            sorted_structure_ids[-1])
                    )

        query = Structure.objects \
            .select_related('parents', 'structure_file_source') \
            .filter(structure_file_source__structure_id__in=structure_ids) \
            .annotate(
            record_names=ArrayAgg('structure_file_records__structure_file_record_name_associations'),
            ficts=F('parents__ficts_parent'),
            ficus=F('parents__ficus_parent'),
            uuuuu=F('parents__uuuuu_parent'),
        )
        structures = query \
            .values('id', 'record_names', 'ficts', 'ficus', 'uuuuu') \
            .all()

        structure_association_list = []
        for structure in structures:
            record_names = structure['record_names']
            structure_association_list.extend(record_names)

        file_record_associations = StructureFileRecordNameAssociation.objects \
            .in_bulk(structure_association_list, field_name='id')

        name_association_types = {c.title: c for c in NameAffinityClass.objects.all()}

        structure_association_list = []
        for structure in structures:
            record_name_ids = structure['record_names']
            for record_name_id in record_name_ids:
                if not record_name_id:
                    continue
                record_name_association = file_record_associations[record_name_id]
                if structure['ficts']:
                    structure_association_list.append(StructureNameAssociation(
                        name_id=record_name_association.name_id,
                        structure_id=structure['ficts'],
                        name_type_id=record_name_association.name_type_id,
                        affinity_class=name_association_types['exact'],
                        confidence=100
                    ))
                if structure['ficus'] and not structure['ficus'] == structure['ficts']:
                    structure_association_list.append(StructureNameAssociation(
                        name_id=record_name_association.name_id,
                        structure_id=structure['ficus'],
                        name_type_id=record_name_association.name_type_id,
                        affinity_class=name_association_types['narrow'],
                        confidence=100
                    ))
                if structure['uuuuu'] and not structure['uuuuu'] == structure['ficus'] and not structure['uuuuu'] == \
                                                                                               structure['ficts']:
                    structure_association_list.append(StructureNameAssociation(
                        name_id=record_name_association.name_id,
                        structure_id=structure['uuuuu'],
                        name_type_id=record_name_association.name_type_id,
                        affinity_class=name_association_types['broad'],
                        confidence=100
                    ))
        try:
            with transaction.atomic():
                StructureNameAssociation.objects.bulk_create(
                    structure_association_list,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
        except DatabaseError as e:
            logger.error(e)
            raise (DatabaseError(e))
        except Exception as e:
            logger.error(e)
            raise Exception(e)
        StructureRegistry.update_linkname_progress(structure_file_id)
        return True

    @staticmethod
    def update_linkname_progress(file_id):
        structure_file = StructureFile.objects.get(id=file_id)

        structure_count: int = StructureParentStructure.objects \
            .select_related('structure__structure_file_source') \
            .filter(structure__structure_file_source__structure_file=structure_file) \
            .filter(
            Q(structure_id=F('ficts_parent_id'))
            | Q(structure_id=F('ficus_parent_id'))
            | Q(structure_id=F('uuuuu_parent_id'))
        ).count()

        structure_count_with_name: int = StructureFileSource.objects \
            .filter(
            structure_file=structure_file,
            structure__names__isnull=False,
        ).distinct().count()

        logger.info("link name progress file %s: %s (%s : %s)" % (
            structure_file.id,
            structure_count == structure_count_with_name,
            structure_count_with_name,
            structure_count
        ))
        status, created = StructureFileLinkNameStatus.objects.get_or_create(structure_file=structure_file)
        status.progress = structure_count_with_name / structure_count
        status.save()


def structure_id_chunks(structure_ids):
    chunk_size = StructureRegistry.CHUNK_SIZE
    return [structure_ids[x:x + chunk_size] for x in range(0, len(structure_ids), chunk_size)]


class Preprocessors:

    def __init__(self):
        pass

    @staticmethod
    def generic(
            release: Release,
            structure_file: StructureFile,
            preprocessor: StructureFileCollectionPreprocessor,
            ens: Ens,
            record_data: RecordData
    ):
        logger.debug("generic preprocessor")
        params = json.loads(preprocessor.params)
        regid_field_name = params['regid']['field']
        regid_field_type = params['regid']['type']
        try:
            regid = ens.dget(regid_field_name, None)
            record_data.regid = regid
            record_data.regid_hash = hashlib.md5(str(regid).encode("UTF-8")).hexdigest()
            # release_object = structure_file.collection.release
            record_data.release_name = release.name
            record_data.release_object = release
            record_data.names.append(NameData(
                regid,
                hashlib.md5(str(regid).encode("UTF-8")).hexdigest(),
                regid_field_type,
                "REGID"
            ))
        except Exception as e:
            logger.warning("getting regid failed: %s", e)
        name_field_names = [n for n in params['names']]
        props = ens.props()
        for name_field_name in name_field_names:
            prop = name_field_name['field']
            check = True in [prop in p for p in props]
            if not check:
                continue
            try:
                name = ens.get(prop)
            except Exception as e:
                name = None
            if name:
                if type(name) is tuple:
                    add_names = name[0].replace("\n", "\t").split("\t")
                else:
                    add_names = name.replace("\n", "\t").split("\t")
                name_type = name_field_name['type']
                for n in add_names:
                    record_data.names.append(NameData(
                        n,
                        hashlib.md5(str(n).encode("UTF-8")).hexdigest(),
                        name_type,
                        "NAME"
                    ))

    @staticmethod
    def pubchem_ext_datasource(
            release: Release,
            structure_file: StructureFile,
            preprocessor: StructureFileCollectionPreprocessor,
            ens: Ens,
            record_data: RecordData
    ):
        logger.debug("preprocessor pubchem_ext_datasource")
        datasource_name = ens.dget('E_PUBCHEM_EXT_DATASOURCE_NAME', None)
        datasource_regid = ens.dget('E_PUBCHEM_EXT_DATASOURCE_REGID', None)
        record_data.version = ens.dget('PUBCHEM_SUBSTANCE_VERSION', None)
        record_data.release_name = datasource_name
        try:
            datasource_name_url = ens.dget('E_PUBCHEM_EXT_DATASOURCE_URL', None)
        except Exception as e:
            logger.error("getting URL failed: %s", e)
            datasource_name_url = None
        record_data.preprocessors['pubchem_ext_datasource'] = PubChemDatasource(datasource_name, datasource_name_url)
        record_data.names = [NameData(
            datasource_regid,
            hashlib.md5(str(datasource_regid).encode("UTF-8")).hexdigest(),
            "E_PUBCHEM_EXT_DATASOURCE_REGID",
            "REGID")
        ]
        record_data.regid = datasource_regid
        record_data.regid_hash = hashlib.md5(str(datasource_regid).encode("UTF-8")).hexdigest()

    @staticmethod
    def generic_transaction(structure_file: StructureFile, record_data_list: List):
        pass

    @staticmethod
    def pubchem_ext_datasource_transaction(structure_file: StructureFile, record_data_list: List):
        logger.debug("preprocessor transaction pubchem_ext_datasource")

        datasource_names = []
        for record_data in record_data_list:
            if 'pubchem_ext_datasource' in record_data.preprocessors:
                datasource_names.append(record_data.preprocessors['pubchem_ext_datasource'])
        datasource_names = list(set(datasource_names))

        pubchem_release = structure_file.collection.release
        pubchem_publisher = pubchem_release.publisher
        pubchem_release_status = pubchem_release.status
        pubchem_release_classification = pubchem_release.classification
        pubchem_release_version = pubchem_release.version
        pubchem_release_downloaded = pubchem_release.downloaded
        pubchem_release_released = pubchem_release.released
        release_objects = {}

        for data in datasource_names:
            dataset_publisher_name = data.name
            dataset_publisher, created = Publisher.objects.get_or_create(
                name=dataset_publisher_name,
                category='generic',
                href=None,
                orcid=None
            )
            if created:
                dataset_publisher.parent = pubchem_publisher
                dataset_publisher.description = "generic from Pubchem"
                dataset_publisher.save()
            dataset, created = Dataset.objects.get_or_create(
                name=data.name,
                publisher=dataset_publisher
            )
            if created:
                dataset.description = "generic from PubChem"
                dataset.publisher = dataset_publisher
                dataset.href = data.url
                dataset.save()

            dataset_release_name = data.name
            release, created = Release.objects.get_or_create(
                dataset=dataset,
                publisher=dataset_publisher,
                name=dataset_release_name,
                version=pubchem_release_version,
                downloaded=pubchem_release_downloaded,
                released=pubchem_release_released
            )
            if created:
                regid_id_field, created = StructureFileField.objects \
                    .get_or_create(field_name="E_PUBCHEM_EXT_DATASOURCE_REGID")
                name_type, created = NameType.objects.get_or_create(title="REGID")
                release.parent = pubchem_release
                release.description = "generic from PubChem"
                release.status = pubchem_release_status
                release.classification = pubchem_release_classification
                release.save()
                release_name_field, created = ReleaseNameField.objects.get_or_create(
                    release=release,
                    structure_file_field=regid_id_field,
                    name_type=name_type
                )
                if created:
                    release_name_field.is_regid = True
                    release_name_field.save()
            release_objects[data.name] = release
        for record_data in record_data_list:
            if not record_data.release_object and record_data.release_name:
                record_data.release_object = release_objects[record_data.release_name]
