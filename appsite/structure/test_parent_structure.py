import logging
from unittest import skip

from django.test import SimpleTestCase, TestCase
from pycactvs import Ens, Dataset, Molfile

from resolver.models import Name, StructureNameAssociation, Structure, Compound, StructureParentStructure
from string_resolver import ChemicalStructure

logger = logging.getLogger('cirx')

FIXTURES = ['sandbox.json']


class ParentStructureTests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        pass

    # def tearDown(self):
    #     logger.info("------------- Tear Down -------------")
    #     logger.info("ens list >>> %s : %s" % (len(Ens.List()), Ens.List()))
    #     logger.info("dataset list >>> %s", Dataset.List())
    #     logger.info("ens list >>> %s : %s" % (len(Ens.List()), Ens.List()))

    def test_parent_structure(self):
        logger.info("------------- Test Tautomer -------------")



        for association in StructureNameAssociation.with_related_objects.by_name(names=['warfarin']).all():
            logger.info("--------")
            structure: Structure = association.structure
            compound: Compound = structure.compound
            parents: StructureParentStructure = structure.parents

            logger.info(parents)

            chemical_structure: ChemicalStructure = ChemicalStructure(structure=structure)

            logger.info(chemical_structure)
            logger.info(chemical_structure.ficts_parent(only_lookup=False).hashisy)
            logger.info(chemical_structure.ficus_parent(only_lookup=False).hashisy)
            logger.info(chemical_structure.uuuuu_parent(only_lookup=False).hashisy)






