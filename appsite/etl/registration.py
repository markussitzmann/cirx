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
from pycactvs import Molfile, Ens

from custom.cactvs import CactvsHash, CactvsMinimol
from etl.models import FileCollection, StructureFile, StructureFileField, StructureFileRecord
from structure.inchi.identifier import InChIString
from structure.models import Structure, Compound
from resolver.models import InChI

logger = logging.getLogger('cirx')
Status = namedtuple('Status', 'file created')

Identifier = namedtuple('Identifier', 'property parent_structure attr')
StructureRelationships = namedtuple('StructureRelationships', 'structure relationships')


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
                hashisy = CactvsHash(ens)
                structure = Structure(
                     hashisy=hashisy,
                     minimol=CactvsMinimol(ens)
                )
                structures.append(structure)
            except Exception as e:
                logger.error("error while registering file record '%s': %s" % (fname, e))
                break
            record_data = {
                'hashisy': hashisy,
                'index': record,
            }
            records.append(record_data)
            molfile_fields = [str(f) for f in molfile.fields]
            fields.update(molfile_fields)
            if max_records and record >= max_records:
                break
            record += 1
        molfile.close()

        structures = sorted(structures, key=lambda s: s.hashisy.int)

        logger.info("adding registration data to database for file '%s'" % (fname, ))
        try:
            with transaction.atomic():
                Structure.objects.bulk_create(
                    structures,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )
                hashisy_list = [record['hashisy'] for record in records]
                structures = Structure.objects.in_bulk(hashisy_list, field_name='hashisy')
                record_objects = list()
                for record_data in records:
                    structure = structures[record_data['hashisy']]
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
            logger.error("file record registration failed for '%s'" % (fname,))
            raise(DatabaseError(e))
        except Exception as e:
            logger.error("file record registration failed for '%s': %s" % (fname, e))
            raise Exception(e)
        logger.info("data registration data finished for file '%s'" % (fname, ))
        return structure_file_id


class StructureRegistry(object):

    CHUNK_SIZE = 100

    @staticmethod
    def normalize_structures(structure_ids: list):
        # NOTE: the order matters, it has to go from broader to more specific identifier
        identifiers = [
            Identifier('E_UUUUU_ID', 'E_UUUUU_STRUCTURE', 'uuuuu_parent'),
            Identifier('E_FICUS_ID', 'E_FICUS_STRUCTURE', 'ficus_parent'),
            Identifier('E_FICTS_ID', 'E_FICTS_STRUCTURE', 'ficts_parent'),
        ]

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
                    hashisy: CactvsHash = CactvsHash(parent_ens)
                    related_hashes[identifier.attr] = hashisy
                    parent_structure: Structure = Structure(
                        hashisy=hashisy,
                        minimol=CactvsMinimol(parent_ens)
                    )
                    parent_structure_relationships\
                        .append(StructureRelationships(parent_structure, related_hashes.copy()))
                    relationships[identifier.attr] = hashisy
                    source_structure_relationships.append(StructureRelationships(structure, relationships))
                logger.info("finished normalizing structure %s" % structure_id)
            except Exception as e:
                structure.blocked = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
                structure.save()
                logger.error("normalizing structure %s failed : %s" % (structure_id, e))

        parent_structure_hash_list = list(set([p.structure.hashisy for p in parent_structure_relationships]))
        try:
            with transaction.atomic():
                # create parent structures in bulk
                structures = sorted([p.structure for p in parent_structure_relationships], key=lambda s: s.hashisy.int)
                Structure.objects.bulk_create(
                    structures,
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE, ignore_conflicts=True
                )

                # fetch hashisy / parent structures in bulk (by that they have an id)
                parent_structures = Structure.objects.in_bulk(parent_structure_hash_list, field_name='hashisy')

                # create compounds in bulk
                structures = sorted(parent_structures.values(), key=lambda s: s.hashisy.int)
                Compound.objects.bulk_create(
                    [Compound(structure=parent_structure) for parent_structure in structures],
                    batch_size=FileRegistry.DATABASE_ROW_BATCH_SIZE,
                    ignore_conflicts=True
                )

                # update normalized structure with parent structure relationships in bulk
                for relationship in source_structure_relationships:
                    for attr, parent_hash in relationship.relationships.items():
                        setattr(source_structures[relationship.structure.id], attr, parent_structures[parent_hash])
                structures = sorted(source_structures.values(), key=lambda s: s.hashisy.int)
                Structure.objects.bulk_update(
                    structures,
                    [identifier.attr for identifier in identifiers]
                )

                # update parent structure relationships in bulk
                for relationship in parent_structure_relationships:
                    for attr, parent_hash in relationship.relationships.items():
                        setattr(parent_structures[relationship.structure.hashisy], attr, parent_structures[parent_hash])
                structures = sorted(parent_structures.values(), key=lambda s: s.hashisy.int)
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
        for structure_id, structure in source_structures.items():
            if structure.blocked:
                logger.info("structure %s is blocked and has been skipped" % (structure_id, ))
                continue
            try:
                print("----")
                print(structure.id)
                print(structure.compound.id)
                ens = structure.to_ens
                inchi_string = ens.get("E_STDINCHI")
                print(inchi_string)
                print(ens.get('E_SMILES'))
                d = InChIString(string=inchi_string).model_dict
                inchi: InChI = InChI(**d)
                inchi.version_string = "1.06"
            except Exception as e:
                print(ens.get('E_SMILES'))
                #structure.blocked = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
                #structure.save()
                logger.error("normalizing structure %s failed : %s" % (structure_id, e))
