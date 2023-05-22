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

TestData = namedtuple("TestData", "resolver expectations exception")

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
        [
            "tautomers:Warfarin", [
                TestData(
                    resolver="name",
                    expectations={'20A701AA27DA3574', '551515A8181F0DDC', '73CEC1A3C72EEA00', 'D76B88C0354759F1', '8868B850DAEF2039', '571F55B366B95577', '6151CAE0B3730D90', 'DE5C78BB2B58C15A', '93B460E97954E4E8'},
                    exception=None
                ),
            ]
        ]
    ])
    def test(self, string: str, test_data: List[TestData]):
        #expected_structure_id = expectations[0]

        resolver_list = [data.resolver for data in test_data]
        #expectation_list = [data.expectation for data in test_data]
        #logger.info("START string '{}' resolver {} expectations {}".format(string, resolver_list, expectation_list))

        chemical_string = ChemicalString(string=string, resolver_list=resolver_list)
        resolver_data = chemical_string.resolver_data
        #chemical_structure: ChemicalStructure


        for test in test_data:
            resolver = test.resolver
            if test.exception:
                self.assertIsInstance(resolver_data[resolver], type(test.exception))
            else:
                structure: ChemicalStructure
                h = resolver_data[resolver][0]
                print(h)
                resolver_response = set([s.hashisy for s in resolver_data[resolver].resolved])
                self.assertEqual(test.expectations, resolver_response)

            # for expectation in expectations:
            #     id, _, resolved_list, exception = resolver_data[resolver]
            #     if isinstance(expectation, Exception):
            #         self.assertIsInstance(expectation, type(exception))
            #     else:
            #         resolved: ChemicalStructure
            #         print([h.ens.get('E_HASHISY') for h in resolved_list])
            #         logger.info("id {} : resolver {} : resolved {}".format(id, resolver, resolved))
            #         logger.info("METADATA  {}".format(resolved.metadata))
            #         logger.info("STRUCTURE {}".format(resolved.structure.id))
            #         self.assertEqual(resolved.ens, expectation)


        # for resolver, expectation in zip(resolver_list, expectation_list):
        #     id, _, resolved_list, exception = resolver_data[resolver]
        #     for resolved, expectation in zip(resolved_list, expectation_list):
        #         if isinstance(expectation, Exception):
        #             self.assertIsInstance(expectation, type(exception))
        #         else:
        #             resolved: ChemicalStructure
        #             print([h.ens.get('E_HASHISY') for h in resolved_list])
        #             logger.info("id {} : resolver {} : resolved {}".format(id, resolver, resolved))
        #             logger.info("METADATA  {}".format(resolved.metadata))
        #             logger.info("STRUCTURE {}".format(resolved.structure.id))
        #             self.assertEqual(resolved.ens, expectation)

