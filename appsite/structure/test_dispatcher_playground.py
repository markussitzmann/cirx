import logging
from typing import List
from unittest import skip

from django.test import TestCase, RequestFactory
from parameterized import parameterized
from pycactvs import Ens, Dataset, cactvs

from dispatcher import Dispatcher
from django.conf import settings

from structure.models import Structure2
from resolver import ChemicalString, ChemicalStructure

logger = logging.getLogger('cirx')

FIXTURES = ['structure.json', 'database.json']


class DispatcherComponentTests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.factory = RequestFactory()
        logger.info("cactvs version: %s", cactvs['version'])
        logger.info("cactvs settings: %s", settings.CACTVS_SETTINGS['python_object_autodelete'])

    def tearDown(self):
        logger.info("------------- Tear Down -------------")
        #logger.info("ens list >>> %s", Dataset(Dataset(Ens.List()).unique()).get("E_HASHISY"))
        logger.info("ens list >>> %s", Ens.List())
        logger.info("dataset list >>> %s", Dataset.List())
        #logger.info("ens delete >>> %s", Ens.Delete("all"))
        #logger.info("ens list after delete >>> %s", Ens.List())
        #for ens in Ens.List():
        #    logger.info("ens >>> %s %s" % (ens, ens.get("E_HASHISY")))
        #    logger.info("del >>> %s", Ens.Delete(ens))
        #logger.info("ens list >>> %s", Ens.List())


        for s in Structure2.objects.all():
            logger.info("SSS %s", s)


    @parameterized.expand([
        ["tautomers:warfarin", "hashisy", True],
        ["tautomers:guanine", "hashisy", True],
        ["tautomers:tylenol", "hashisy", True],
        ["CCO", "hashisy", True],
        ["CCN", "hashisy", True],
    ])
    @skip
    def test_dispatcher(self, string, representation, expected):
        logger.info("------------- Test Dispatcher (%s, %s) -------------" % (string, representation))
        #url: str = "/chemical/structure/" + string + "/" + representation
        #request = self.factory.get(url)

        dataset1: Dataset = Dispatcher._create_dataset(string=string, resolver_list=["name", "smiles"], simple=True)
        #dataset2: Dataset = Dispatcher._create_dataset(string=string, resolver_list=["smiles", "name"], simple=False)

        dataset1 = None
        #dataset2 = None

        self.assertTrue(True)

    @skip
    def test_ens(self):
        logger.info("------------- Test Ens -------------")
        e = Ens("warfarin")
        logger.info("ens list: %s", Ens.List())

        tautomers = e.get("E_RESOLVER_TAUTOMERS")

        for structure in tautomers:
            logger.info(">>> %s", structure.get("E_SMILES"))
            chemical_structure = ChemicalStructure(ens=structure)
            logger.info(">>> %s", chemical_structure)

        logger.info("ens list: %s", Ens.List())
        logger.info("dataset ens list: %s %s", tautomers, tautomers.ens())
        logger.info("ens list: %s", Ens.List())

    @skip
    def test_operator(self):
        logger.info("------------- Test Operator -------------")
        string = "warfarin"
        ens = Ens(string)
        logger.info("ens list: %s", Ens.List())

        chemical_string = ChemicalString(string=string)

        interpretation = chemical_string.Interpretation()
        interpretation.structures = [ChemicalStructure(ens=ens),]

        chemical_string._operator_tautomers(interpretation)

        logger.info("ens list: %s", Ens.List())



    def test_chemical_structure(self):
        logger.info("------------- Test Chemical Structure -------------")

        string = "tautomers:warfarin"

        resolver_list = ["name"]
        simple = True

        logger.info("0: ens list: %s", Ens.List())

        interpretations = ChemicalString(string=string, resolver_list=resolver_list).interpretations

        logger.info("1: ens list: %s", Ens.List())

        structure_lists: List[List[ChemicalStructure]] = [
           interpretation.structures for interpretation in ([interpretations[0]] if simple else interpretations)
        ]

        #logger.info("2: ens list: %s", Ens.List())

        ens_list: List[Ens] = [
           structure.ens for structure_list in structure_lists for structure in structure_list
        ]

        #logger.info("3 : ens list: %s", Ens.List())

        #dataset: Dataset = Dataset(ens_list)

        logger.info("ens list: %s", Ens.List())
        #logger.info("dataset ens list: %s %s", dataset, dataset.ens())
        #logger.info("ens list: %s", Ens.List())
