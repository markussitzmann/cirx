import logging

from django.test import TestCase, SimpleTestCase

from pycactvs import Ens

from custom.cactvs import CactvsHash, CactvsMinimol
from structure.models import Structure2, InChI
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

    def test_minimol(self):
        ens1 = Ens("CCO")
        minimol = CactvsMinimol(ens1).minimol()
        ens2 = Ens(minimol)
        self.assertEqual(CactvsHash(ens1), CactvsHash(ens2))
        self.assertEqual(CactvsMinimol(ens1), CactvsMinimol(ens2))

    def test_structure_db_fetch(self):
        ens = Ens("CCO")
        structure_obj = Structure2.objects.get_or_create_from_ens(ens)
        structure_obj.save()

        hashisy = CactvsHash(ens)
        structure = Structure2.objects.get(hashisy=hashisy)

        logger.info(">>> %s %s" % (structure, structure.to_ens().get("E_SMILES")))
        fetched = structure.to_ens()
        self.assertEqual(ens.get('E_HASHISY'), fetched.get('E_HASHISY'))


    def test_inchi_model(self):
        ens = Ens("CCO")
        inchi_key = ens.get("E_INCHIKEY")
        inchi_string = ens.get("E_INCHI")

        inchi_key_obj = InChI.create(key=inchi_key)
        inchi_string_obj = InChI.create(string=inchi_string)

        inchi_key_obj.save()

        i, created = InChI.objects.get_or_create(inchi_string_obj)
        i.string = inchi_string
        i.save()


        test_inchi = InChI.objects.get(id=i.id)
        logger.info("x>>> %s | %s" % (test_inchi, test_inchi.string))

        self.assertEqual(inchi_string, test_inchi.string)

    def test_inchi_model(self):
        ens = Ens("CCO")
        inchi_key = ens.get("E_INCHIKEY")
        inchi_string = ens.get("E_INCHI")
        inchi_string_obj = InChI.create(key=inchi_key, string=inchi_string)
        logger.info("x>>> %s | %s" % (inchi_string_obj, inchi_string_obj))
        logger.info("k>>> %s" % (inchi_string_obj.__dict__,))
        z = InChI.create(**inchi_string_obj.__dict__.pop('_state'))

        logger.info("z>>> %s" % (z,))


    def test_inchi_model2(self):
        ens = Ens("CCO")
        inchi = InChI.objects.get_or_create_from_ens(ens)
        logger.info("i >>> %s", inchi)

