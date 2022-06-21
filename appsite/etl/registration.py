import datetime
import pytz
import glob
import logging
import os
from collections import namedtuple
from typing import List

from celery import subtask, group
from django.conf import settings
from django.db import transaction, DatabaseError, IntegrityError
from pycactvs import Molfile, Ens, Prop

from custom.cactvs import CactvsHash, CactvsMinimol
from etl.models import FileCollection, StructureFile, StructureFileField, StructureFileRecord
from structure.inchi.identifier import InChIString, InChIKey
#from structure.models import
from resolver.models import InChI, Structure, Compound

logger = logging.getLogger('cirx')
Status = namedtuple('Status', 'file created')

Identifier = namedtuple('Identifier', 'property parent_structure attr')
StructureRelationships = namedtuple('StructureRelationships', 'structure relationships')
InChIAndSaveOpt = namedtuple('InChIAndSaveOpt', 'inchi saveopts')
InChIType = namedtuple('InChIType', 'id property key softwareversion software options')

class FileRegistry(object):

    CHUNK_SIZE = 10000
    DATABASE_ROW_BATCH_SIZE = 1000

    def __init__(self, file_collection: FileCollection):
        self.file_collection = file_collection
        self._file_name_list = glob.glob(
            os.path.join(settings.CIR_FILESTORE_ROOT, file_collection.file_location_pattern_string),
            recursive=True
        )
        self._file_list = list()

    def register_files(self) -> List[StructureFile]:
        self._file_list = \
            [status.file for fname in self._file_name_list if (status := self.register_file(fname)).created]
        return self._file_list

    def register_file(self, fname) -> Status:
        structure_file, created = StructureFile.objects.get_or_create(
            collection=self.file_collection,
            file=fname
        )
        if created:
            return Status(file=structure_file, created=True)
        logger.info("file '%s' had already been registered previously (%s records)" % (fname, structure_file.count))
        return Status(file=structure_file, created=False)

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
    def register_structure_file_record_chunk(structure_file_id: int, chunk_number: int, chunk_size: int, max_records=None) -> int:
        logger.info("accepted task for registering file with id: %s chunk %s" % (structure_file_id, chunk_number))
        structure_file: StructureFile = StructureFile.objects.get(id=structure_file_id)

        count: int
        if not structure_file.count:
            count = Molfile.count()
        else:
            count = structure_file.count
        file_records = range(1, count+1)
        chunk_records = [file_records[i:i + min(chunk_size, count)] for i in range(0, count, chunk_size)][chunk_number]
        record: int = chunk_records[0]
        last_record: int = chunk_records[-1]

        logger.info("registering file records for file %s (file id %s | chunk %s | first record %s | last record %s )" %
                    (structure_file.file.name, structure_file_id, chunk_number, record, last_record))

        fname: str = structure_file.file.name
        molfile: Molfile = Molfile.Open(fname)
        molfile.set('record', record)
        fields: set = set()
        structures: list = list()
        records: list = list()

        while record <= last_record:
            if not record % FileRegistry.CHUNK_SIZE:
                logger.info("processed record %s of %s", record, fname)
            try:
                # TODO: registering structures needs improvement - hadd might do harm here
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
            record_data = {
                'hashisy_key': hashisy_key,
                'index': record,
            }
            records.append(record_data)
            molfile_fields = [str(f) for f in molfile.fields]
            fields.update(molfile_fields)
            if max_records and record >= max_records:
                break
            record += 1
        molfile.close()

        structures = sorted(structures, key=lambda s: s.hashisy_key.int)

        logger.info("adding registration data to database for file '%s'" % (fname, ))
        try:
            with transaction.atomic():
                Structure.objects.bulk_create(
                    structures,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
                hashisy_list = [record['hashisy_key'] for record in records]
                structures = Structure.objects.in_bulk(hashisy_list, field_name='hashisy_key')
                record_objects = list()
                for record_data in records:
                    structure = structures[record_data['hashisy_key']]
                    record_objects.append(StructureFileRecord(
                        structure_file=structure_file,
                        structure=structure,
                        number=record_data['index']
                    ))
                StructureFileRecord.objects.bulk_create(record_objects, batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE)
                logger.info("registering file fields for '%s'" % (fname,))
                for field in list(fields):
                    logger.info("registering file field '%s'" % (field,))
                    sff, created = StructureFileField.objects.get_or_create(name=field)
                    sff.structure_files.add(structure_file)
                    sff.save()
        except DatabaseError as e:
            logger.error("file record registration failed for '%s': %s" % (fname, e))
            raise(DatabaseError(e))
        except Exception as e:
            logger.error("file record registration failed for '%s': %s" % (fname, e))
            raise Exception(e)
        logger.info("data registration data finished for file '%s'" % (fname, ))
        return structure_file_id


class StructureRegistry(object):

    CHUNK_SIZE = 100

    NCICADD_TYPES = [
        Identifier('E_UUUUU_ID', 'E_UUUUU_STRUCTURE', 'uuuuu_parent'),
        Identifier('E_FICUS_ID', 'E_FICUS_STRUCTURE', 'ficus_parent'),
        Identifier('E_FICTS_ID', 'E_FICTS_STRUCTURE', 'ficts_parent'),
    ]

    INCHI_TYPES = [
        InChIType(
            'standard',
            'E_STDINCHI',
            'E_STDINCHIKEY',
            Prop.Ref('E_STDINCHI').softwareversion,
            Prop.Ref('E_STDINCHI').software,
            ""
        ),
        InChIType(
            'original',
            'E_INCHI',
            'E_INCHIKEY',
            Prop.Ref('E_INCHI').softwareversion,
            Prop.Ref('E_INCHI').software,
            "DONOTADDH RECMET NOWARNINGS FIXEDH"
        ),
        InChIType(
            'xtauto',
            'E_INCHI',
            'E_INCHIKEY',
            Prop.Ref('E_INCHI').softwareversion,
            Prop.Ref('E_INCHI').software,
            "DONOTADDH RECMET NOWARNINGS KET 15T"
        ),
        InChIType(
            'xtautox',
            'E_TAUTO_INCHI',
            'E_TAUTO_INCHIKEY',
            Prop.Ref('E_TAUTO_INCHI').softwareversion,
            Prop.Ref('E_TAUTO_INCHI').software,
            "DONOTADDH RECMET NOWARNINGS KET 15T PT_22_00 PT_16_00 PT_06_00 PT_39_00 PT_13_00 PT_18_00"
        ),
    ]

    @staticmethod
    def normalize_structures(structure_ids: list):
        # NOTE: the order matters, it has to go from broader to more specific identifier
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
        logger.info("A")
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
                    inchi_software_version = inchi_type.softwareversion
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
                        #save_options=inchi_saveopt,
                        #software_version_string=inchi_software_version,
                        validate_key=False
                    )
                    d = inchi_string.model_dict
                    inchi: InChI = InChI(**d)
                    inchi_relationships[inchi_type] = InChIAndSaveOpt(inchi, inchi_saveopt)
                structure_to_inchi_list\
                    .append(StructureRelationships(structure_id, inchi_relationships))
            except Exception as e:
                structure.blocked = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
                structure.save()
                logger.error("calculating inchi for structure %s failed : %s" % (structure_id, e))

        for s in structure_to_inchi_list:
            logger.info("x %s" % (s,))

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

                structure_inchis_list = []
                for structure_to_inchi in structure_to_inchi_list:
                    sid = structure_to_inchi.structure
                    for inchi_type, inchi_data in structure_to_inchi.relationships.items():
                        logger.info("%s ---> %s | %s : %s" % (sid, inchi_data.inchi.id, inchi_type, inchi_data))
                        if inchi_data.inchi.key in inchi_objects_by_key:
                            inchi = inchi_objects_by_key[inchi_data.inchi.key]
                            logger.info("I %s" % (inchi,))
                            structure_objects[sid].inchis.add(inchi)
                        else:
                            logger.info("I %s" % (inchi,))
                            logger.info("DOES NOT EXISTS %s" % (inchi_data.inchi.key,))

                        # structure_inchi = StructureInChIs(
                        #     structure=structure_objects[sid],
                        #     inchi=inchi_objects[inchi_data.inchi.id],
                        #     software_version_string=inchi_type.version,
                        #     save_options=inchi_data.saveopts
                        # )
                        # structure_inchis_list.append(structure_inchi)
                # StructureInChIs.objects.bulk_create(
                #     structure_inchis_list,
                #     batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                #     ignore_conflicts=True
                # )

        except DatabaseError as e:
            logger.error(e)
            raise(DatabaseError(e))
        except Exception as e:
            logger.error(e)
            raise Exception(e)

        logger.info("B")
        return structure_ids

