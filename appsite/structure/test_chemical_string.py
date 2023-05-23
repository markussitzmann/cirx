import logging
from collections import namedtuple
from typing import List

from django.test import TestCase
from parameterized import parameterized

from resolver.models import Structure
from structure.smiles import SmilesError
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

ResolverTest = namedtuple("ResolverTest", "resolver expectations exception")

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
        #["CCO", ['smiles', 'stdinchikey'], [8, ValueError()]],
        # ["CCO", ['stdinchikey', ], [ValueError(), ]],
        # ["1AD375920BE60DAD", ['hashisy', ], [1, ]],
        # ["Warfarin", ['name', ], [2, ]],
        # ["NCICADD:CID=3", ['ncicadd_cid', ], [3, ]],
        # ["E174572A915E4471-FICTS-01-1A", ['ncicadd_identifier', 'smiles', ], [8, ValueError()]],
        # ["LFQSCWFLJHTTHZ-UHFFFAOYSA-N", ['stdinchikey', ], [8, ]],
        # ["LFQSCWFLJHTTHZ-UHFFFAOYSA", ['stdinchikey', ], [8, ]],
        # ["LFQSCWFLJHTTHZ", ['stdinchikey', ], [8, ]],
        # ["NCICADD:RID=4", ['ncicadd_rid', 'smiles', 'compound_cid', ], [1, ValueError(), ValueError(), ]],
        # ["NCICADD:CID=5", ['ncicadd_cid', 'ncicadd_rid', 'smiles', ], [4, ValueError(), ValueError(), ]],
        #["tautomers:Warfarin", ['name', ], [['20A701AA27DA3574', '551515A8181F0DDC', '73CEC1A3C72EEA00', 'D76B88C0354759F1', '8868B850DAEF2039', '571F55B366B95577', '6151CAE0B3730D90', 'DE5C78BB2B58C15A', '93B460E97954E4E8'], ]],
        ["CCO", [
            ResolverTest(resolver="smiles", expectations={'E174572A915E4471'}, exception=None),
            ResolverTest(resolver="stdinchikey", expectations=None, exception=ValueError()),
        ]],
        ["1AD375920BE60DAD", [
            ResolverTest(resolver="hashisy", expectations={'1AD375920BE60DAD'}, exception=None),
        ]],
        ["NCICADD:CID=3", [
            ResolverTest(resolver="ncicadd_cid", expectations={'3DB0124A3ECF5ECE'}, exception=None),
        ]],
        ["LFQSCWFLJHTTHZ-UHFFFAOYSA-N", [
            ResolverTest(resolver="stdinchikey", expectations={'E174572A915E4471'}, exception=None),
        ]],
        ["LFQSCWFLJHTTHZ-UHFFFAOYSA", [
            ResolverTest(resolver="stdinchikey", expectations={'E174572A915E4471'}, exception=None),
        ]],
        ["LFQSCWFLJHTTHZ", [
            ResolverTest(resolver="stdinchikey", expectations={'E174572A915E4471'}, exception=None),
        ]],
        ["tautomers:Warfarin", [
            ResolverTest(
                resolver="name",
                expectations={'20A701AA27DA3574', '551515A8181F0DDC', '73CEC1A3C72EEA00', 'D76B88C0354759F1', '8868B850DAEF2039', '571F55B366B95577', '6151CAE0B3730D90', 'DE5C78BB2B58C15A', '93B460E97954E4E8'},
                exception=None
            ),
        ]]
    ])
    def test(self, string: str, resolver_tests: List[ResolverTest]):

        resolver_list = [test.resolver for test in resolver_tests]

        chemical_string = ChemicalString(string=string, resolver_list=resolver_list)
        resolver_data = chemical_string.resolver_data

        for test in resolver_tests:
            resolver = test.resolver
            if test.exception:
                self.assertIsInstance(resolver_data[resolver].exception, type(test.exception))
            else:
                resolved = resolver_data[resolver].resolved
                resolver_response = set([structure.hashisy for structure in resolved])
                self.assertEqual(test.expectations, resolver_response)



