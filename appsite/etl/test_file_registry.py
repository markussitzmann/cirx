import logging
from pathlib import Path
from unittest import skip

from django.conf import settings
from pycactvs import Ens

from django.test import TestCase

from etl.models import StructureFileCollection, StructureFileRecord, StructureFileRecordNameAssociation
from registration import FileRegistry
from resolver.models import Structure, Dataset, Release, NameType, Name

logger = logging.getLogger('cirx')


class FileRegistryTests(TestCase):

    fixtures = ['sandbox.json']

    def setUp(self):
        logger.info("----- file registry set up ----")

    def tearDown(self):
        logger.info("----- file registry tear down ----")


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



