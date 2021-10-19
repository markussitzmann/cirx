import logging

from django.test import TestCase, SimpleTestCase
from pycactvs import Ens
from resolver import ChemicalStructure

logger = logging.getLogger('cirx')


class ChemicalStructureTests(TestCase):

    def test_chemical_structure(self):
        ens = Ens('CCO')
        structure = ChemicalStructure(ens=ens)
        logger.info(structure.hashisy)
        self.assertTrue(True)
