import glob
import logging
import os
from typing import List, Tuple, Dict

from django.conf import settings
from django.db import transaction, DatabaseError

from custom.cactvs import CactvsHash, CactvsMinimol
from etl.models import FileCollection, StructureFile, StructureFileFields, StructureFileRecord

from pycactvs import Molfile

from structure.models import Structure2

logger = logging.getLogger('cirx')


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
            [structure_file['file'] for fname in self._file_name_list if (structure_file := self.register_file(fname))['created']]
        return self._file_list

    def register_file(self, fname) -> Dict:
        structure_file, created = StructureFile.objects.get_or_create(
            collection=self.file_collection,
            file=fname
        )
        if created:
            logger.info("counting file %s", fname)
            molfile_handle = Molfile.Open(fname)
            structure_file.count = molfile_handle.count()
            structure_file.save()
            logger.info("registered file '%s' with %s records" % (fname, structure_file.count))
            return {'file': structure_file, 'created': True}
        logger.info("file '%s' had already been registered previously (%s records)" % (fname, structure_file.count))
        return {'file': structure_file, 'created': False}

    def register_file_records(self, structure_file: StructureFile, max_records=None):
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
                structure = Structure2(
                    hashisy=CactvsHash(ens),
                    minimol=CactvsMinimol(ens)
                )
                structures.append(structure)
            except Exception as e:
                logger.error("error while registering file record '%s': %s" % (fname, e))
                break
            record = StructureFileRecord(
                structure_file=structure_file,
                record=index
            )
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
                StructureFileRecord.objects.bulk_create(records, batch_size=1000)
                Structure2.objects.bulk_create(structures, batch_size=1000, ignore_conflicts=True)
                logger.error("registering file fields for '%s'" % (fname,))
                for field in list(fields):
                    logger.info("registering file field '%s'" % (field,))
                    sff, created = StructureFileFields.objects.get_or_create(name=field)
                    sff.structure_files.add(structure_file)
                    sff.save()
        except DatabaseError:
            logger.error("file record registration failed for '%s'" % (fname,))
        logger.info("data registration data finished for file '%s'" % (fname, ))


