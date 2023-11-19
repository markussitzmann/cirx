import logging
from pathlib import Path
from unittest import skip

from django.conf import settings
from pycactvs import Ens

from django.test import TestCase

from etl.models import StructureFileCollection, StructureFileRecord, StructureFileRecordNameAssociation, StructureFile
from registration import FileRegistry
from resolver.models import Structure, Dataset, Release, NameType, Name

logger = logging.getLogger('cirx')


class FileRegistryTests(TestCase):

    fixtures = ['init.json']

    def setUp(self):
        logger.info("----- file registry set up ----")

    def tearDown(self):
        logger.info("----- file registry tear down ----")

    def test_register_file(self):

        structure_file_collection = StructureFileCollection.objects.get(id=4)

        registry = FileRegistry(structure_file_collection)
        registry.register_files()

        structure_file = StructureFile.objects.first()
        logger.info("FILE: %s" % structure_file)

        FileRegistry.register_structure_file_record_chunk(
            structure_file_id=structure_file.id,
            chunk_number=0,
            chunk_size=100,
            max_records=100
        )




    @skip
    def test_add_file(self):
        logger.info("----- add file test ----")

        pattern = "nci/NCI_DTP.sdf"
        check = True
        release = 1

        instore_path = settings.CIR_INSTORE_ROOT
        files = sorted(Path(instore_path).glob(pattern))
        for file in files:
            logger.info("submitting file %s", file)
            FileRegistry.add_file(str(file), check, release)

        collection: StructureFileCollection
        for collection in StructureFileCollection.objects.all():
            logger.info("Collection: ID %s RELEASE ID %s : %s : %s" % (
                collection.id,
                collection.release_id,
                collection.file_location_pattern_string,
                collection
            ))

        logger.info("done")



