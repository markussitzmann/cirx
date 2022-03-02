import glob
import logging
import os
from typing import List

from django.conf import settings

from custom.cactvs import CactvsHash, CactvsMinimol
from etl.models import FileCollection, StructureFile

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
        def structure_file_creator(fname):
            structure_file, created = StructureFile.objects.get_or_create(
                collection=self.file_collection,
                name=fname
            )
            if created:
                logger.info("counting file %s", fname)
                molfile_handle = Molfile.Open(fname)
                structure_file.count = molfile_handle.count()
                structure_file.save()
                return structure_file
            return None
        self._file_list = \
            [structure_file for fname in self._file_name_list if (structure_file := structure_file_creator(fname)) is not None]
        return self._file_list

    def register_file_records(self, structure_file: StructureFile, maxloop=None):
        index = 0
        molfile = Molfile.Open(structure_file.name.name)
        fields = set()
        structures = list()
        while True:
            try:
                ens = molfile.read()
                structure = Structure2(
                    hashisy=CactvsHash(ens),
                    minimol=CactvsMinimol(ens)
                )
                structures.append(structure)
            except Exception as e:
                break
            fields.add(molfile.fields)
            if maxloop and index >= maxloop:
                print("BREAK")
                break
            index += 1
            print(index)
        Structure2.objects.bulk_create(structures, batch_size=1000, ignore_conflicts=True)