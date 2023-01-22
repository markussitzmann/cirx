import logging
from typing import List

from django.test import TestCase

from etl.models import StructureFile, StructureFileLinkNameStatus
from registration import StructureRegistry

logger = logging.getLogger('cirx')


class LinkNameRegistryTests(TestCase):

    fixtures = ['normalize.json']

    def setUp(self):
        logger.info("----- link name registry set up ----")
        structure_files: List[StructureFile] = StructureFile.objects.all()
        f: StructureFile
        for f in structure_files:
            logger.info("%s : %s" % (f.id, f.file.name))

    def tearDown(self):
        logger.info("----- link name registry tear down ----")
        for status in StructureFileLinkNameStatus.objects.all():
            logger.info("Link name status : %s", status)
        logger.info("InChI : %s", StructureFileLinkNameStatus.objects.count())

    def test_inchi_registry(self):
        logger.info("----- link name registry test ----")

        structure_file = StructureFile.objects.get(id=8)
        structure_ids = [record.structure.id for record in structure_file.structure_file_records.all()]

        StructureRegistry.link_structure_names((structure_file.id, structure_ids))





