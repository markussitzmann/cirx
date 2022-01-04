import logging
from unittest import skip

from django.test import SimpleTestCase
from pycactvs import Ens, Dataset, Molfile

logger = logging.getLogger('cirx')


class CactvsTests(SimpleTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        logger.info("------------- Tear Down -------------")
        logger.info("ens list >>> %s : %s" % (len(Ens.List()), Ens.List()))
        logger.info("dataset list >>> %s", Dataset.List())
        logger.info("ens list >>> %s : %s" % (len(Ens.List()), Ens.List()))



    @skip
    def test_write3d(self):
        e1 = Ens("CCO")
        e2 = Ens("CCN")
        dataset = Dataset([e1, e2])
        b: bytes = Molfile.String(dataset, {'writeflags': ["write3d",]})
        s: str = b.decode("UTF-8")
        self.assertTrue("-0.0392    1.1971   -0.8900" in s)

    @skip
    def test_dataset(self):
        e1 = Ens("CCO")
        e2 = Ens("CCN")
        d = Dataset([e1])
        d = Dataset([e2])
        logger.info("datasets: %s" % Dataset.List())
        self.assertTrue(len(Dataset.List()) == 1)

    def test_tautomer(self):
        logger.info("------------- Test Tautomer -------------")
        e = Ens("CC(=O)CC(C1=CC=CC=C1)C2=C(C3=CC=CC=C3OC2=O)O")
        logger.info("ens list: %s", Ens.List())


        #tautomers = e.get("E_CIR_TAUTOMERS")
        tautomers = e.get("E_RESOLVER_TAUTOMERS")


        logger.info("Python tautomers: %s %s | %s" % (tautomers, tautomers.ens(), Dataset.List()))

        # for structure in tautomers:
        #     logger.info(">>> %s", structure.get("E_SMILES"))
        #     chemical_structure = ChemicalStructure(ens=structure)
        #     logger.info(">>> %s", chemical_structure)
        #
        # logger.info("ens list: %s", Ens.List())
        # logger.info("dataset ens list: %s %s", tautomers, tautomers.ens())
        # logger.info("ens list: %s", Ens.List())