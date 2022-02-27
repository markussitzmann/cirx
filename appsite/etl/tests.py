import glob
import logging
import os

from pycactvs import Molfile
from unittest import skip

from django.test import SimpleTestCase, TestCase
from django.conf import settings

from etl.models import FileCollection

logger = logging.getLogger('cirx')

fpath = os.path.join(settings.CIR_FILESTORE_ROOT, 'nci', 'NCI_DTP.sdf')


class MolfileTests(TestCase):
    fixtures = ["etl.json"]

    def setUp(self):
        self.molfile = Molfile.Open(fpath)

    @skip
    def test_loop(self):
        logger.info(self.molfile)

        def loopfunction(ens):
            ficus = ens.get('E_HASHISY')
            smiles = ens.get('E_MINIMOL')
            logger.info("%s %s" % (ficus, smiles))
        Molfile.Loop(fpath, function=loopfunction, maxloop=1000)

    def test_file_pattern(self):
        collections = FileCollection.objects.all()
        for collection in collections:
            logger.info(collection.file_location_pattern_string)
            file_list = glob.glob(
                os.path.join(settings.CIR_FILESTORE_ROOT, collection.file_location_pattern_string),
                recursive=True
            )
            logger.info(file_list)


