import logging
from pycactvs import Ens, Molfile

from django.test import TestCase

from etl.models import StructureFileCollection, StructureFile, StructureFileRecord
from registration import Preprocessors, FileRegistry

logger = logging.getLogger('cirx')


class FileRegistryTests(TestCase):

    fixtures = ['etl.json', 'resolver.json']

    def setUp(self):

        StructureFile.objects.all().delete()

        self.structure_file_collection: StructureFileCollection = StructureFileCollection.objects.get(id=4)
        self.file_registry: FileRegistry = FileRegistry(self.structure_file_collection)

        logger.info("R %s", self.file_registry)
        self.file_registry.register_files()

        self.structure_file: StructureFile = StructureFile.objects.first()
        logger.info("F %s %s", self.structure_file, self.structure_file.id)

        FileRegistry.count_and_save_structure_file(self.structure_file.id)
        FileRegistry.register_structure_file_record_chunk(self.structure_file.id, 1, 3)

        fname: str = self.structure_file.file.name
        molfile: Molfile = Molfile.Open(fname)
        molfile.set('record', 4)

        self.ens = molfile.read()

    def tearDown(self):
        for record in StructureFileRecord.objects.all():
            logger.info("R %s %s" % (record, record.structure.to_ens.get("E_SMILES")))

    def test_file_registry(self):
        logger.info("----- file registry start ----")
        release = self.structure_file.collection.release.dataset
        logger.info("R %s", release)
        logger.info("E %s", self.ens)










