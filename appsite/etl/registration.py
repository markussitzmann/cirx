import glob
import logging
import os
from collections import namedtuple
from typing import List, Tuple, Dict

from django.conf import settings
from django.db import transaction, DatabaseError, IntegrityError

from custom.cactvs import CactvsHash, CactvsMinimol
from etl.models import FileCollection, StructureFile, StructureFileField, StructureFileRecord

from pycactvs import Molfile

from structure.models import Structure2

logger = logging.getLogger('cirx')
Status = namedtuple('Status', 'file created')


class FileRegistry(object):

    def __init__(self, file_collection: FileCollection):
        self.file_collection = file_collection
        self._file_name_list = glob.glob(
            os.path.join(settings.CIR_FILESTORE_ROOT, file_collection.file_location_pattern_string),
            recursive=True
        )
        self._file_list = list()

    def register_files(self) -> List[StructureFile]:
        # def structure_file_creator(fname):
        #     structure_file, created = StructureFile.objects.get_or_create(
        #         collection=self.file_collection,
        #         file=fname
        #     )
        #     if created:
        #         logger.info("counting file %s", fname)
        #         molfile_handle = Molfile.Open(fname)
        #         structure_file.count = molfile_handle.count()
        #         structure_file.save()
        #         return structure_file
        #     return None
        self._file_list = \
            [status.file for fname in self._file_name_list if (status := self.register_file(fname)).created]
        #   [structure_file['file'] for fname in self._file_name_list if (structure_file := self.register_file(fname))['created']]
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
    def count_and_save_file(structure_file_id: int):
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
    def register_file_records(structure_file_id: int, max_records=None):
        logger.info("accepted task for registering file with id: %s", structure_file_id)
        structure_file = StructureFile.objects.get(id=structure_file_id)
        logger.info("registering file records for file %s (file id %s)", (structure_file.file.name, structure_file_id))
        index: int = 1
        fname: str = structure_file.file.name
        molfile: Molfile = Molfile.Open(fname)
        fields: set = set()
        structures: list = list()
        records: list = list()
        count: int
        if not structure_file.count:
            count = Molfile.count()
        else:
            count = structure_file.count
        while index <= count:
            if not index % 10000:
                logger.info(">>> %s", index)
            try:
                ens = molfile.read()
                hashisy = CactvsHash(ens)
                structure = Structure2(
                     hashisy=hashisy,
                     minimol=CactvsMinimol(ens)
                )
                structures.append(structure)
            except Exception as e:
                logger.error("error while registering file record '%s': %s" % (fname, e))
                break
            record = {
                'hashisy': hashisy,
                'index': index,
            }
            records.append(record)
            molfile_fields = [str(f) for f in molfile.fields]
            fields.update(molfile_fields)
            if max_records and index >= max_records:
                break
            index += 1
        molfile.close()
        logger.info("adding registration data to database for file '%s'" % (fname, ))
        try:
            with transaction.atomic():
                Structure2.objects.bulk_create(structures, batch_size=1000, ignore_conflicts=True)
                page_size = 1000
                records = [records[i:i + page_size] for i in range(0, len(records), page_size)]
                for page in records:
                    hashisy_list = [record['hashisy'] for record in page]
                    structures = Structure2.objects.in_bulk(hashisy_list, field_name='hashisy')
                    record_objects = list()
                    for record in page:
                        structure = structures[record['hashisy']]
                        record_objects.append(StructureFileRecord(
                            structure_file=structure_file,
                            structure=structure,
                            record=record['index']
                        ))
                    StructureFileRecord.objects.bulk_create(record_objects, batch_size=1000)
                logger.error("registering file fields for '%s'" % (fname,))
                for field in list(fields):
                    logger.info("registering file field '%s'" % (field,))
                    sff, created = StructureFileField.objects.get_or_create(name=field)
                    sff.structure_files.add(structure_file)
                    sff.save()
        except DatabaseError:
            logger.error("file record registration failed for '%s'" % (fname,))
        except Exception as e:
            logger.error("file record registration failed for '%s': %s" % (fname, e))

        logger.info("data registration data finished for file '%s'" % (fname, ))
        return structure_file_id


