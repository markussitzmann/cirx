import logging

from django.test import SimpleTestCase
from pycactvs import Ens, Dataset, Molfile

logger = logging.getLogger('cirx')

class CactvsTests(SimpleTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        logger.info("ens list >>> %s", Dataset(Ens.List()).get("E_HASHISY"))

    def test_write3d(self):
        e1 = Ens("CCO")
        e2 = Ens("CCN")
        dataset = Dataset([e1, e2])
        b: bytes = Molfile.String(dataset, {'writeflags': ["write3d",]})
        s: str = b.decode("UTF-8")
        self.assertTrue("-0.0392    1.1971   -0.8900" in s)

    def test_dataset(self):
        e1 = Ens("CCO")
        e2 = Ens("CCN")
        d = Dataset([e1])
        d = Dataset([e2])
        logger.info("datasets: %s" % Dataset.List())
        self.assertTrue(len(Dataset.List()) == 1)

