import logging

from django.test import TestCase

from etl.models import StructureFileCollection, StructureFileRecord
from registration import FileRegistry
from resolver.models import Structure, Dataset, Release

logger = logging.getLogger('cirx')


class FileRegistryTests(TestCase):

    fixtures = ['init.json']

    def setUp(self):
        logger.info("----- file registry set up ----")
        self.structure_file_collection = StructureFileCollection.objects.get(id=2)
        logger.info("COLLECTION %s", self.structure_file_collection)
        for f in self.structure_file_collection.files.all():
            logger.info("FILE %s", f)

    def tearDown(self):
        logger.info("----- file registry tear down ----")


    def test_file_registry(self):
        logger.info("----- file registry test ----")

        registry = FileRegistry(self.structure_file_collection)
        registry.register_files()

        for file in self.structure_file_collection.files.all():
            logger.info("----- %s ----", file)
            FileRegistry.count_and_save_structure_file(file.id)
            FileRegistry.register_structure_file_record_chunk(file.id, 0, 100)

        structure_count = Structure.objects.count()
        logger.info("STRUCTURE %s", structure_count)
        self.assertEqual(structure_count, 195)

        structure_file_record_count = StructureFileRecord.objects.count()
        logger.info("RECORD %s", structure_file_record_count)
        self.assertEqual(structure_file_record_count, 201)

        dataset_count = Dataset.objects.count()
        logger.info("DATASETS %s", dataset_count)

        release_count = Release.objects.count()
        logger.info("RELEASES %s", release_count)


        #self.assertEqual(release_count, 201)



    # @skip
    # def test_json_field(self):
    #     for p in StructureFileCollectionPreprocessor.objects.all():
    #         logger.info("PREPROCESSOR %s %s" % (p, p.params))
    #         d = json.loads(p.params)
    #         logger.info("D %s" % d["test"])





