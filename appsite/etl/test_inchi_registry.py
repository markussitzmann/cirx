import logging
from typing import List

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
        structure_files: List[StructureFile] = StructureFile.objects.all()
        f: StructureFile
        for f in structure_files:
            logger.info("%s : %s" % (f.id, f.file.name))

    def tearDown(self):
        logger.info("----- inchi registry tear down ----")
        for inchi in InChI.objects.all():
            logger.info("InChI : %s", inchi)
        logger.info("InChI : %s", InChI.objects.count())

    def test_inchi_registry(self):
        logger.info("----- inchi registry test ----")

        structure_file = StructureFile.objects.get(id=8)
        structure_ids = [record.structure.id for record in structure_file.structure_file_records.all()]

        StructureRegistry.calculate_inchi((structure_file.id, structure_ids))





