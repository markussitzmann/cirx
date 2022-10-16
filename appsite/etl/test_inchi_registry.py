import logging
from pycactvs import Ens

from django.test import TestCase

from etl.models import StructureFileCollection, StructureFileRecord, StructureFile
from registration import FileRegistry, StructureRegistry
from resolver.models import Structure, Dataset, Release, NameType, Name, InChI

logger = logging.getLogger('cirx')


class InChIRegistryTests(TestCase):

    fixtures = ['register.json']

    def setUp(self):
        logger.info("----- inchi registry set up ----")

    def tearDown(self):
        logger.info("----- inchi registry tear down ----")
        for inchi in InChI.objects.all():
            logger.info("InChI : %s", inchi)
        logger.info("InChI : %s", InChI.objects.count())

    def test_file_registry(self):
        logger.info("----- inchi registry test ----")

        structure_file = StructureFile.objects.get(id=2)
        structure_ids = [record.structure.id for record in structure_file.structure_file_records.all()]

        #for s in structures:
        #    logger.info(">> %s" % s)

        StructureRegistry.calculate_inchi((structure_file.id, structure_ids))





