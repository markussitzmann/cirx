import glob
import os
from typing import List

from django.conf import settings

from etl.models import FileCollection, StructureFile

from pycactvs import Molfile


class FileRegistry(object):

    def __init__(self, file_collection: FileCollection):
        self.file_collection = file_collection
        self._file_name_list = glob.glob(
            os.path.join(settings.CIR_FILESTORE_ROOT, file_collection.file_location_pattern_string),
            recursive=True
        )
        self._file_list = list()

    def register(self) -> List[StructureFile]:
        def structure_file_creator(fname):
            structure_file, created = StructureFile.objects.get_or_create(
                collection=self.file_collection,
                name=fname
            )
            if created:
                molfile_handle = Molfile.Open(fname)
                structure_file.count = molfile_handle.count()
                structure_file.save()
                return structure_file
            return None
        self._file_list = \
            [structure_file for fname in self._file_name_list if (structure_file := structure_file_creator(fname)) is not None]
        return self._file_list

    #def scan_fields(self, structure_file: StructureFile):
