import logging

from django.test import TestCase

from etl.models import StructureFileCollection, StructureFile, StructureFileRecord
from resolver.models import Structure
from registration import Preprocessors, FileRegistry

logger = logging.getLogger('cirx')


class FileRegistryTests(TestCase):

    fixtures = ['init.json']

    def setUp(self):
        logger.info("----- file registry set up ----")
        self.structure_file_collection = StructureFileCollection.objects.get(id=2)


    def tearDown(self):
        logger.info("----- file registry tear down ----")

        structure_count = Structure.objects.count()
        logger.info("STRUCTURE %s", structure_count)

        structure_file_record_count = StructureFileRecord.objects.count()
        logger.info("RECORD %s", structure_file_record_count)

    def test_file_registry(self):
        logger.info("----- file registry test ----")

        registry = FileRegistry(self.structure_file_collection)
        registry.register_files()

        for file in self.structure_file_collection.files.all():
            logger.info("----- %s ----", file)
            FileRegistry.count_and_save_structure_file(file.id)
            FileRegistry.register_structure_file_record_chunk(file.id, 0, 100)









