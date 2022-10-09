import datetime
import glob
import gzip
import math
import shutil
from dataclasses import dataclass, field
from pathlib import PurePath, Path

import ujson as json
import logging
import os
import time
from collections import namedtuple, defaultdict
from typing import List, Optional

import pytz
from celery import subtask, group
from django.conf import settings
from django.db import transaction, DatabaseError, IntegrityError
from django.db.models import QuerySet
from pycactvs import Molfile, Ens, Prop

from custom.cactvs import CactvsHash, CactvsMinimol, SpecialCactvsHash
from etl.models import StructureFileCollection, StructureFile, StructureFileField, StructureFileRecord, \
    ReleaseNameField, StructureFileCollectionPreprocessor, StructureFileStatus
from resolver.models import InChI, Structure, Compound, StructureInChIAssociation, InChIType, Dataset, Publisher, \
    Release, NameType, Name, Record, StructureHashisy, StructureParentStructure
from structure.inchi.identifier import InChIString, InChIKey

logger = logging.getLogger('celery.task')
#logger = get_task_logger('celery.tasks')


DEFAULT_CHUNK_SIZE = 10000
DEFAULT_DATABASE_ROW_BATCH_SIZE = 1000
DEFAULT_LOGGER_BLOCK = 10
DEFAULT_MAX_CHUNK_NUMBER = 1000

Status = namedtuple('Status', 'file created')

Identifier = namedtuple('Identifier', 'property parent_structure attr')
StructureRelationships = namedtuple('StructureRelationships', 'structure relationships')
InChIAndSaveOpt = namedtuple('InChIAndSaveOpt', 'inchi saveopt')
InChITypeTuple = namedtuple('InChITypes', 'id property key softwareversion software options')
StructureFileRecordReleaseTuple = namedtuple('StructureFileRecordRelease', 'record releases')

PubChemDatasource = namedtuple('PubChemDatasource', 'name url')


@dataclass(frozen=True)
class NameTriple:
    name: str = None
    name_type: str = None
    parent: str = None


@dataclass
class RecordData:
    structure_file: StructureFile
    hashisy_key: CactvsHash
    index: int
    preprocessors: defaultdict = field(default_factory=lambda: defaultdict(dict))
    release_name: str = None
    release_object: Release = None
    regid: str = None
    names: List[NameTriple] = field(default_factory=lambda: [])

    def __str__(self):
        return "RecordData[%s, %s]" % (self.index, self.release_object)


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
    def add_file(file_path: str, check: bool):
        file = PurePath(file_path)
        outfile_path = FileRegistry._create_filestore_name(file, 0)[1].parent
        try:
            Path(outfile_path).mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            logger.critical("target destination '%s' already exists - skipped" % outfile_path)
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
            outfile_name_and_path = FileRegistry._create_filestore_name(file, i)
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
            structure_file = StructureFile.objects.get(id=structure_file_id)
            count = structure_file.count
        except Exception as e:
            logger.error("structure file and count not available")
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

        count: int
        if not structure_file.count:
            count = Molfile.count()
        else:
            count = structure_file.count
        file_records = range(1, count+1)
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

        record -= 1
        while record < last_record:
            record += 1
            if not record % DEFAULT_LOGGER_BLOCK:
                logger.info("processed record %s of %s", record, fname)
            try:
                # TODO: registering structures needs improvement - hadd might do harm here
                molfile.set('record', record)
                ens: Ens = molfile.read()
                ens.hadd()
                hashisy_key = CactvsHash(ens)
                structure = Structure(
                    hashisy_key=hashisy_key,
                    #hashisy=hashisy_key.padded,
                    minimol=CactvsMinimol(ens)
                )
                structures.append(structure)

            except Exception as e:
                logger.error("error while registering file record '%s': %s" % (fname, e))
                break

            for preprocessor in preprocessors:
                record_data = RecordData(structure_file=structure_file, hashisy_key=hashisy_key, index=record)
                record_data_list.append(record_data)
                preprocessor_callable = getattr(Preprocessors, preprocessor.name, None)
                if callable(preprocessor_callable):
                    preprocessor_callable(structure_file, preprocessor, ens, record_data)
                else:
                    logger.warning("preprocessor '%s' was not callable", preprocessor_callable)
            if max_records and record >= max_records:
                break
        molfile.close()
        logger.info("finished reading records")

        structures = sorted(structures, key=lambda s: s.hashisy_key.int)

        logger.info("adding registration data to database for file '%s'" % (fname, ))
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
                Structure.objects.bulk_create(
                    structures,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
                time1 = time.perf_counter()
                logging.info("STRUCTURE BULK T: %s C: %s" % ((time1 - time0), len(structures)))

                hashisy_key_list = [record_data.hashisy_key for record_data in record_data_list]
                structures = Structure.objects.in_bulk(hashisy_key_list, field_name='hashisy_key')

                structure_hashisy_list = [StructureHashisy(structure=structures[key], hashisy=key.padded) for key in hashisy_key_list]
                StructureHashisy.objects.bulk_create(
                    structure_hashisy_list,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )


                logger.info("registering structure file records for '%s'" % (fname,))
                structure_file_record_objects = list()
                unique_record_data_list = \
                    sorted(
                        list(set([(structures[record_data.hashisy_key], record_data.index) for record_data in record_data_list])),
                        key=lambda u: u[1]
                    )
                for t in unique_record_data_list:
                    structure, index = t
                    structure_file_record_objects.append(
                        StructureFileRecord(
                            structure_file=structure_file,
                            structure=structure,
                            number=index,
                        )
                    )

                time0 = time.perf_counter()
                structure_file_records = StructureFileRecord.objects.bulk_create(
                    structure_file_record_objects,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                )
                time1 = time.perf_counter()
                logging.info("STRUCTURE RECORD BULK T: %s C: %s" % ((time1 - time0), len(structure_file_records)))

                name_set, name_type_set = set(), set()
                for record_data in record_data_list:
                    for triplet in record_data.names:
                        name_set.add(triplet.name)
                        name_type_set.add((triplet.name_type, triplet.parent))

                parent_name_types = {name_type.id: name_type for name_type in NameType.objects.bulk_create(
                    [NameType(id=item[1]) for item in name_type_set],
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )}

                name_type_list = [NameType(id=item[0], parent=parent_name_types[item[1]]) for item in name_type_set]
                NameType.objects.bulk_create(
                    name_type_list,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
                name_types = NameType.objects.in_bulk(name_set, field_name='id')

                time0 = time.perf_counter()
                name_list = [Name(name=name) for name in name_set]
                Name.objects.bulk_create(
                    name_list,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
                names = Name.objects.in_bulk(name_set, field_name='name')
                time1 = time.perf_counter()
                logging.info("NAME BULK T: %s C: %s" % ((time1 - time0), len(names)))

                structure_file_record_dict = {
                    str(r.structure_file.id) + ":" + str(r.number): r for r in structure_file_records
                }

                record_list = list()
                for record_data in record_data_list:
                    key = str(record_data.structure_file.id) + ":" + str(record_data.index)
                    sfr = structure_file_record_dict[key]
                    record_list.append(
                        Record(
                            regid=names[str(record_data.regid)],
                            version=1,
                            release=record_data.release_object,
                            dataset=record_data.release_object.dataset,
                            structure_file_record=sfr
                        )
                    )

                time0 = time.perf_counter()
                record_object_list = Record.objects.bulk_create(
                    record_list,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                )
                time1 = time.perf_counter()
                logging.info("RECORD BULK T: %s C: %s" % ((time1 - time0), len(record_object_list)))

        except DatabaseError as e:
            logger.error("file record registration failed for '%s': %s" % (fname, e))
            raise(DatabaseError(e))
        except Exception as e:
            logger.error("file record registration failed for '%s': %s" % (fname, e))
            raise Exception(e)

        g1 = time.perf_counter()
        logging.info("TRANSACTION BULK T: %s" % (g1 - g0))

        return structure_file_id

    @staticmethod
    def _create_filestore_name(file_path, index):
        parent = file_path.parent
        stem = file_path.stem
        suffixes = file_path.suffixes
        if suffixes[-1] != ".gz":
            suffixes.append(".gz")
        splitted_stem = stem.split(".", 1)

        name_elements = [splitted_stem[0], "." + str(index)]
        name_elements.extend(suffixes)
        new_name = "".join(name_elements)
        dir_name = name_elements[0]

        filestore_name = os.path.join(
            str(settings.CIR_FILESTORE_ROOT),
            *[str(p) for p in parent.parts[2:]],
            str(dir_name),
            str(new_name)
        )

        return filestore_name, Path(filestore_name)


class StructureRegistry(object):

    CHUNK_SIZE = DEFAULT_DATABASE_ROW_BATCH_SIZE

    NCICADD_TYPES = [
        Identifier('E_UUUUU_ID', 'E_UUUUU_STRUCTURE', 'uuuuu_parent'),
        Identifier('E_FICUS_ID', 'E_FICUS_STRUCTURE', 'ficus_parent'),
        Identifier('E_FICTS_ID', 'E_FICTS_STRUCTURE', 'ficts_parent'),
    ]

    INCHI_TYPES = [
        InChITypeTuple(
            'standard',
            'E_STDINCHI',
            'E_STDINCHIKEY',
            Prop.Ref('E_STDINCHI').softwareversion,
            Prop.Ref('E_STDINCHI').software,
            ""
        ),
        InChITypeTuple(
            'original',
            'E_INCHI',
            'E_INCHIKEY',
            Prop.Ref('E_INCHI').softwareversion,
            Prop.Ref('E_INCHI').software,
            "SAVEOPT  RECMET NOWARNINGS FIXEDH"
        ),
        InChITypeTuple(
            'xtauto',
            'E_INCHI',
            'E_INCHIKEY',
            Prop.Ref('E_INCHI').softwareversion,
            Prop.Ref('E_INCHI').software,
            "SAVEOPT  RECMET NOWARNINGS KET 15T"
        ),
        InChITypeTuple(
            'xtautox',
            'E_TAUTO_INCHI',
            'E_TAUTO_INCHIKEY',
            Prop.Ref('E_TAUTO_INCHI').softwareversion,
            Prop.Ref('E_TAUTO_INCHI').software,
            "SAVEOPT DONOTADDH RECMET NOWARNINGS KET 15T PT_22_00 PT_16_00 PT_06_00 PT_39_00 PT_13_00 PT_18_00"
        ),
    ]

    @staticmethod
    def fetch_structure_file_for_normalization(structure_file_id: int) -> Optional[int]:
        try:
            structure_file = StructureFile.objects.get(id=structure_file_id)
        except StructureFile.DoesNotExist:
            return None
        logger.info("normalize structure file %s", structure_file)
        if hasattr(structure_file, 'file_status'):
            status = structure_file.file_status
        else:
            status = StructureFileStatus(structure_file=structure_file)
            status.save()
        if status.normalization_finished:
            return None
        return structure_file_id

    @staticmethod
    def normalize_chunk_mapper(structure_file_id: int, callback):
        try:
            structure_file = StructureFile.objects.get(id=structure_file_id)
            records: QuerySet = StructureFileRecord.objects \
                .select_related('structure') \
                .values('structure__id') \
                .filter(
                    structure_file=structure_file,
                    structure__compound__isnull=True,
                    structure__blocked__isnull=True,
                ).exclude(
                    structure__hashisy_key=SpecialCactvsHash.ZERO.hashisy
                ).exclude(
                    structure__hashisy_key=SpecialCactvsHash.MAGIC.hashisy
                )
        except Exception as e:
            logger.error("structure file and count not available")
            raise Exception(e)
        count = len(records)
        chunk_size = StructureRegistry.CHUNK_SIZE
        chunk_number = math.ceil(count / chunk_size)
        #chunks = range(0, chunk_number)

        chunks = [records[i:i + min(chunk_size, count)] for i in range(0, count, chunk_size)]
        logger.info("-----> %s" % chunks)
        #[r['structure__id'] for r in chunk]

        callback = subtask(callback)
        return group(callback.clone([[r['structure__id'] for r in chunk]]) for chunk in chunks)()

    @staticmethod
    def normalize_structures(structure_ids: list):

        logger.info("!-----> %s" % structure_ids)


        # NOTE: the order matters, it has to go from broader to more specific identifier!!
        identifiers = StructureRegistry.NCICADD_TYPES

        source_structures = Structure.objects.in_bulk(structure_ids, field_name='id')
        parent_structure_relationships = []
        source_structure_relationships = []

        for structure_id, structure in source_structures.items():
            if structure.blocked:
                logger.info("structure %s is blocked and has been skipped" % (structure_id, ))
                continue
            try:
                related_hashes = {}
                for identifier in identifiers:
                    relationships = {}
                    ens = structure.to_ens
                    parent_ens = ens.get(identifier.parent_structure)
                    hashisy_key: CactvsHash = CactvsHash(parent_ens)
                    related_hashes[identifier.attr] = hashisy_key
                    parent_structure: Structure = Structure(
                        hashisy_key=hashisy_key,
                        minimol=CactvsMinimol(parent_ens)
                    )
                    parent_structure_relationships\
                        .append(StructureRelationships(parent_structure, related_hashes.copy()))
                    relationships[identifier.attr] = hashisy_key
                    source_structure_relationships.append(StructureRelationships(structure, relationships))
                if not structure_id % DEFAULT_LOGGER_BLOCK:
                    logger.info("finished normalizing structure %s" % structure_id)
            except Exception as e:
                structure.blocked = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
                structure.save()
                logger.error("normalizing structure %s failed : %s" % (structure_id, e))

        parent_structure_hash_list = list(set([p.structure.hashisy_key for p in parent_structure_relationships]))
        try:
            with transaction.atomic():
                # create parent structures in bulk
                structures = sorted(
                    [p.structure for p in parent_structure_relationships], key=lambda s: s.hashisy_key.int
                )
                Structure.objects.bulk_create(
                    structures,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )

                # fetch hashisy / parent structures in bulk (by that they have an id)
                parent_structures = Structure.objects.in_bulk(parent_structure_hash_list, field_name='hashisy_key')

                # create compounds in bulk
                compound_structures = sorted(parent_structures.values(), key=lambda s: s.hashisy_key.int)
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
                StructureParentStructure.objects.bulk_create(
                    sorted(source_structure_dict.values(), key=lambda p: p.structure_id),
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )

                parent_structure_dict = {
                    id: StructureParentStructure(structure=parent_structures[id]) for id in parent_structures
                }
                for relationship in parent_structure_relationships:
                    parent = parent_structure_dict[relationship.structure.hashisy_key]
                    for attr, parent_hash in relationship.relationships.items():
                        setattr(parent, attr, parent_structures[parent_hash])
                StructureParentStructure.objects.bulk_create(
                    sorted(parent_structure_dict.values(), key=lambda p: p.structure_id),
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
        except DatabaseError as e:
            logger.error(e)
            raise(DatabaseError(e))
        except Exception as e:
            logger.error(e)
            raise Exception(e)

        return structure_ids

    @staticmethod
    def calculate_inchi(structure_ids: list):
        source_structures = Structure.objects.in_bulk(structure_ids, field_name='id')

        for inchi_type in StructureRegistry.INCHI_TYPES:
            options = Prop(inchi_type.property).getparam("options")
            options += " SaveOpt"
            Prop(inchi_type.property).setparam("options", options)

        structure_to_inchi_list = []

        for structure_id, structure in source_structures.items():
            if structure.blocked:
                logger.info("structure %s is blocked and has been skipped" % (structure_id, ))
                continue
            try:
                inchi_relationships = {}
                for inchi_type in StructureRegistry.INCHI_TYPES:
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
                    inchi_saveopt: str = None
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
                structure_to_inchi_list.append(StructureRelationships(structure_id, inchi_relationships))
            except Exception as e:
                structure.blocked = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
                structure.save()
                logger.error("calculating inchi for structure %s failed : %s" % (structure_id, e))

        try:
            with transaction.atomic():
                inchi_list = [
                    inchi_data.inchi for structure_to_inchi in structure_to_inchi_list
                    for inchi_data in structure_to_inchi.relationships.values()
                ]
                InChI.objects.bulk_create(
                    inchi_list,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )

                # fetch uuid / inchi structures in bulk (by that they have an id)
                inchi_id_list = [i.id for i in inchi_list]
                structure_id_list = [s.structure for s in structure_to_inchi_list]

                inchi_objects = InChI.objects.in_bulk(inchi_id_list, field_name='id')
                inchi_objects_by_key = {i.key: i for i in inchi_objects.values()}

                structure_objects = Structure.objects.in_bulk(structure_id_list, field_name='id')

                inchi_type_objects = InChIType.objects.in_bulk(
                    [t.id for t in StructureRegistry.INCHI_TYPES],
                    field_name='id'
                )

                structure_inchi_associations = []
                for structure_to_inchi in structure_to_inchi_list:
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
                            inchitype=inchi_type_objects[inchi_type.id],
                            save_opt=inchi_data.saveopt,
                            software_version=inchi_type.softwareversion
                        )
                        structure_inchi_associations.append(structure_inchi_association)
                StructureInChIAssociation.objects.bulk_create(
                    structure_inchi_associations,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
        except DatabaseError as e:
            logger.error(e)
            raise(DatabaseError(e))
        except Exception as e:
            logger.error(e)
            raise Exception(e)
        return structure_ids


def structure_id_chunks(structure_ids):
    chunk_size = StructureRegistry.CHUNK_SIZE
    return [structure_ids[x:x + chunk_size] for x in range(0, len(structure_ids), chunk_size)]


class Preprocessors:

    def __init__(self):
        pass

    @staticmethod
    def generic(
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
            release_object = structure_file.collection.release
            record_data.release_name = release_object.name
            record_data.release_object = release_object
            record_data.names.append(NameTriple(regid, regid_field_type, "REGID"))
        except Exception as e:
            logger.error("getting regid failed: %s", e)
        name_field_names = [n for n in params['names']]
        for name_field_name in name_field_names:
            try:
                name = ens.dget(name_field_name['field'], None)
                if name:
                    add_names = name.replace("\n", "\t").split("\t")
                    name_type = name_field_name['type']
                    for n in add_names:
                        record_data.names.append(NameTriple(n, name_type, "NAME"))
            except Exception as e:
                #logger.warning("getting name failed: %s", e)
                pass

    @staticmethod
    def pubchem_ext_datasource(
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
        record_data.names = [NameTriple(datasource_regid, "E_PUBCHEM_EXT_DATASOURCE_REGID", "REGID"), ]
        record_data.regid = datasource_regid

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
                regid_id_field, created = StructureFileField.objects\
                    .get_or_create(field_name="E_PUBCHEM_EXT_DATASOURCE_REGID")
                name_type, created = NameType.objects.get_or_create(id="REGID")
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
