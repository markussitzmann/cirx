import logging

from django.test import TestCase
from parameterized import parameterized

from resolver.models import Structure
from structure.string_resolver import ChemicalString, ChemicalStructure

from pycactvs import Ens, Dataset, cactvs
CACTVS_SETTINGS = cactvs

propertypath = list(CACTVS_SETTINGS['propertypath'])
propertypath.insert(1, '/home/app/cactvsenv/prop')

CACTVS_SETTINGS['python_object_autodelete'] = True
CACTVS_SETTINGS['lookup_hosts'] = []
CACTVS_SETTINGS['propertypath'] = tuple(propertypath)


logger = logging.getLogger('cirx')

FIXTURES = ['sandbox.json']
RESOLVER_LIST = ["name", "smiles", "hashisy"]


class ChemicalStructureTests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        logger.info("cactvs version: %s", cactvs['version'])

    def tearDown(self):
        logger.info("------------- Tear Down -------------")
        logger.info("dataset list {} {} ens list {} {}"
                    .format(len(Dataset.List()), Dataset.List(), len(Ens.List()), Ens.List()))
        logger.info("dataset list {} {} ens list {} {}"
                    .format(len(Dataset.List()), Dataset.List(), len(Ens.List()), Ens.List()))

    @parameterized.expand([
        [{'ens': Ens("CCO")}, None],
        [{'structure': Structure.objects.get(id=8)}, None],
        [{'structure': Structure.objects.get(id=8), 'ens': Ens("CCO")}, None],
        #[{'structure': Structure.objects.get(id=7), 'ens': Ens("CCO")}, None],
        #[{'structure': Structure.objects.get(id=7), 'ens': Ens("CCOCC")}, None],
    ])
    def test(self, kwargs, expectation):
        cs = ChemicalStructure(**kwargs)
        logger.info("structure {} ens {} identifier {} x {}".format(cs.structure, cs.ens, cs.identifier, cs.metadata))


class ChemicalStringTests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        #self.factory = RequestFactory()
        logger.info("cactvs version: %s", cactvs['version'])
        #logger.info("cactvs settings: %s", settings.CACTVS_SETTINGS['python_object_autodelete'])

    def tearDown(self):
        logger.info("------------- Tear Down -------------")
        logger.info("dataset list {} {} ens list {} {}".format(len(Dataset.List()), Dataset.List(), len(Ens.List()), Ens.List()))

    @parameterized.expand([
        ["CCO", ['smiles'], None],
        ["1AD375920BE60DAD", ['hashisy'], None],
        ["Warfarin", ['name'], None],
        ["NCICADD:CID=3", ['ncicadd_cid'], None]
    ])
    def test(self, string, resolver_list, expectations):
        logger.info("START string '{}' resolver {} expectations {}".format(string, resolver_list, expectations))
        chemical_string = ChemicalString(string=string, resolver_list=resolver_list)
        data = chemical_string.structure_data
        self.assertTrue(len(data))
        item: ChemicalStructure
        for item in data:
            logger.info("representation {}".format(item))
            #logger.info("hashisy {}".format(item))
            logger.info(item.metadata)

            #self.assertTrue(representation.structures and len(representation.structures) >= 1)


