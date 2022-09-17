import datetime
import time

import pytz
import glob
import logging
import os
from collections import namedtuple, defaultdict
from typing import List, Dict

from celery import subtask, group
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db import transaction, DatabaseError, IntegrityError
from pycactvs import Molfile, Ens, Prop

from custom.cactvs import CactvsHash, CactvsMinimol
from etl.models import StructureFileCollection, StructureFile, StructureFileField, StructureFileRecord, \
    StructureFileRecordRelease, ReleaseNameField, StructureFileCollectionPreprocessor
from structure.inchi.identifier import InChIString, InChIKey
from resolver.models import InChI, Structure, Compound, StructureInChIAssociation, InChIType, Dataset, Publisher, \
    Release, NameType

logger = logging.getLogger('celery.task')
#logger = get_task_logger('celery.tasks')


Status = namedtuple('Status', 'file created')

Identifier = namedtuple('Identifier', 'property parent_structure attr')
StructureRelationships = namedtuple('StructureRelationships', 'structure relationships')
InChIAndSaveOpt = namedtuple('InChIAndSaveOpt', 'inchi saveopt')
InChITypeTuple = namedtuple('InChITypes', 'id property key softwareversion software options')
StructureFileRecordReleaseTuple = namedtuple('StructureFileRecordRelease', 'record releases')

PubChemDatasource = namedtuple('PubChemDatasource', 'name url')


class FileRegistry(object):

    CHUNK_SIZE = 100000
    DATABASE_ROW_BATCH_SIZE = 10000

    def __init__(self, file_collection: StructureFileCollection):
        self.file_collection = file_collection
        self._file_name_list = glob.glob(
            os.path.join(settings.CIR_FILESTORE_ROOT, file_collection.file_location_pattern_string),
            recursive=True
        )
        self._file_list = list()

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
        chunk_number = int(count / chunk_size) + 1
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
        i0 = time.perf_counter()
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
        record_data_list: list[[Dict]] = list()

        g0 = time.perf_counter()
        record -= 1
        while record < last_record:
            record += 1
            if not record % FileRegistry.CHUNK_SIZE:
                logger.info("processed record %s of %s", record, fname)
            try:
                # TODO: registering structures needs improvement - hadd might do harm here
                molfile.set('record', record)
                ens: Ens = molfile.read()
                ens.hadd()
                hashisy_key = CactvsHash(ens)
                structure = Structure(
                    hashisy_key=hashisy_key,
                    hashisy=hashisy_key.padded,
                    minimol=CactvsMinimol(ens)
                )
                structures.append(structure)
            except Exception as e:
                logger.error("error while registering file record '%s': %s" % (fname, e))
                break

            for preprocessor in preprocessors:
                record_data = {
                    'hashisy_key': hashisy_key,
                    'index': record,
                    'preprocessors': defaultdict(dict),
                    'release_names': [],
                    'release_objects': []
                }
                record_data_list.append(record_data)
                preprocessor_callable = getattr(Preprocessors, preprocessor.name, None)
                if callable(preprocessor_callable):
                    preprocessor_callable(structure_file, preprocessor, ens, record_data)
                else:
                    logger.warning("preprocessor '%s' was not callable", preprocessor_callable)
            if max_records and record >= max_records:
                break
        molfile.close()

        structures = sorted(structures, key=lambda s: s.hashisy_key.int)

        logger.info("adding registration data to database for file '%s'" % (fname, ))
        try:
            with transaction.atomic():
                time0 = time.perf_counter()
                for preprocessor in preprocessors:
                    preprocessor_transaction = getattr(Preprocessors, preprocessor.name + "_transaction", None)
                    if callable(preprocessor_transaction):
                        preprocessor_transaction(structure_file, record_data_list)

                Structure.objects.bulk_create(
                    structures,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
                time1 = time.perf_counter()

                hashisy_list = [r['hashisy_key'] for r in record_data_list]
                structures = Structure.objects.in_bulk(hashisy_list, field_name='hashisy_key')

                logger.info("registering structure file records for '%s'" % (fname,))
                structure_file_record_objects = list()
                unique_record_data_list = \
                    sorted(
                        list(set([(structures[r['hashisy_key']], r['index']) for r in record_data_list])),
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
                StructureFileRecord.objects.bulk_create(
                    structure_file_record_objects,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                )
                time2 = time.perf_counter()

                time3 = time.perf_counter()
                logger.info("TIMING 1 %s 2 %s 3 %s T %s" % ((time1-time0), (time2-time1), (time3-time2), (time3-time0)))

        except DatabaseError as e:
            logger.error("file record registration failed for '%s': %s" % (fname, e))
            raise(DatabaseError(e))
        except Exception as e:
            logger.error("file record registration failed for '%s': %s" % (fname, e))
            raise Exception(e)
        g1 = time.perf_counter()
        logger.info("INIT %s GLOBAL %s" % ((g0 - i0), (g1 - g0)))
        logger.info("data registration data finished for file '%s'" % (fname, ))
        logger.info("---------- FINISHED file %s chunk %s size %s" % (structure_file_id, chunk_number, chunk_size))
        return structure_file_id


class StructureRegistry(object):

    #CHUNK_SIZE = 100

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
    def normalize_structures(structure_ids: list):
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
                        hashisy=hashisy_key.padded,
                        minimol=CactvsMinimol(parent_ens)
                    )
                    parent_structure_relationships\
                        .append(StructureRelationships(parent_structure, related_hashes.copy()))
                    relationships[identifier.attr] = hashisy_key
                    source_structure_relationships.append(StructureRelationships(structure, relationships))
                logger.info("finished normalizing structure %s" % structure_id)
            except Exception as e:
                structure.blocked = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
                structure.save()
                logger.error("normalizing structure %s failed : %s" % (structure_id, e))

        parent_structure_hash_list = list(set([p.structure.hashisy_key for p in parent_structure_relationships]))
        try:
            with transaction.atomic():
                # create parent structures in bulk
                structures = sorted([p.structure for p in parent_structure_relationships], key=lambda s: s.hashisy_key.int)
                Structure.objects.bulk_create(
                    structures,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE, ignore_conflicts=True
                )

                # fetch hashisy / parent structures in bulk (by that they have an id)
                parent_structures = Structure.objects.in_bulk(parent_structure_hash_list, field_name='hashisy_key')

                # create compounds in bulk
                structures = sorted(parent_structures.values(), key=lambda s: s.hashisy_key.int)
                Compound.objects.bulk_create(
                    [Compound(structure=parent_structure) for parent_structure in structures],
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )

                # update normalized structure with parent structure relationships in bulk
                for relationship in source_structure_relationships:
                    for attr, parent_hash in relationship.relationships.items():
                        setattr(source_structures[relationship.structure.id], attr, parent_structures[parent_hash])
                structures = sorted(source_structures.values(), key=lambda s: s.hashisy_key.int)
                Structure.objects.bulk_update(
                    structures,
                    [identifier.attr for identifier in identifiers]
                )

                # update parent structure relationships in bulk
                for relationship in parent_structure_relationships:
                    for attr, parent_hash in relationship.relationships.items():
                        setattr(parent_structures[relationship.structure.hashisy_key], attr, parent_structures[parent_hash])
                structures = sorted(parent_structures.values(), key=lambda s: s.hashisy_key.int)
                Structure.objects.bulk_update(
                    structures,
                    [identifier.attr for identifier in identifiers]
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
            record_data: Dict
    ):
        logger.debug("generic preprocessor")
        datasource_name = ens.dget('E_PUBCHEM_EXT_DATASOURCE_NAME', None)
        record_data['release_names'].append(datasource_name)
        try:
            datasource_name_url = ens.dget('E_PUBCHEM_EXT_DATASOURCE_URL', None)
        except Exception as e:
            logger.error("getting URL failed: %s", e)
            datasource_name_url = None
        record_data['preprocessors']['pubchem_ext_datasource'] = PubChemDatasource(datasource_name, datasource_name_url)

    @staticmethod
    def pubchem_ext_datasource(
            structure_file: StructureFile,
            preprocessor: StructureFileCollectionPreprocessor,
            ens: Ens,
            record_data: Dict
    ):
        logger.debug("preprocessr pubchem_ext_datasource")
        # datasource_name = ens.dget('E_PUBCHEM_EXT_DATASOURCE_NAME', None)
        # record_data['release_names'].append(datasource_name)
        # try:
        #     datasource_name_url = ens.dget('E_PUBCHEM_EXT_DATASOURCE_URL', None)
        # except Exception as e:
        #     logger.error("getting URL failed: %s", e)
        #     datasource_name_url = None
        # record_data['preprocessors']['pubchem_ext_datasource'] = PubChemDatasource(datasource_name, datasource_name_url)

    @staticmethod
    def generic_transaction(structure_file: StructureFile, record_data_list: List):
        logger.info("GENERIC TRANSACTION")

    @staticmethod
    def pubchem_ext_datasource_transaction(structure_file: StructureFile, record_data_list: List):
        logger.debug("preprocessor transaction pubchem_ext_datasource")

        datasource_names = []
        for record_data in record_data_list:
            if 'pubchem_ext_datasource' in record_data['preprocessors']:
                datasource_names.append(record_data['preprocessors']['pubchem_ext_datasource'])
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
                publisher=pubchem_publisher,
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
        for record in record_data_list:
            for name in record['release_names']:
                record['release_objects'].append(release_objects[name])
