import logging

from django.test import TestCase, SimpleTestCase

from pycactvs import Ens

from custom.cactvs import CactvsHash, CactvsMinimol
from structure.models import StructureCactvsHash, Structure2
from resolver import ChemicalStructure

logger = logging.getLogger('cirx')


class StructureTests(TestCase):

    def tearDown(self):
        logger.info("ens list >>> %s", Ens.List())

    def test_chemical_structure(self):
        smiles = 'CCO'
        ens = Ens(smiles)
        hashisy = ens.get('E_HASHISY')

        structure = ChemicalStructure(ens=ens)
        self.assertEqual(CactvsHash(structure.hashisy).padded(), hashisy)

    def test_cactvs_hash(self):
        hashisy = CactvsHash('FF')
        name = "FF"

        structure_cactvs_hash = StructureCactvsHash(hashisy=hashisy, name=name)
        structure_cactvs_hash.save()

        from_db = StructureCactvsHash.objects.get(hashisy=hashisy)
        self.assertEqual(from_db.name, name)

    def test_minimol(self):
        ens1 = Ens("CCO")
        minimol = CactvsMinimol(ens1).minimol()
        ens2 = Ens(minimol)
        self.assertEqual(CactvsHash(ens1), CactvsHash(ens2))
        self.assertEqual(CactvsMinimol(ens1), CactvsMinimol(ens2))

    def test_structure_db_fetch(self):
        ens = Ens("CCO")
        Structure2.objects.createFromEns(ens)

        hashisy = CactvsHash(ens)
        structure = Structure2.objects.get(hashisy=hashisy)

        logger.info(">>> %s %s", structure, structure.to_ens().get("E_SMILES"))

