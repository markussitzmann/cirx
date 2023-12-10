import logging
from collections import namedtuple

from django.test import TestCase
from parameterized import parameterized
from pycactvs import Ens, Dataset, cactvs

from structure.string_resolver import ChemicalString

CACTVS_SETTINGS = cactvs

propertypath = list(CACTVS_SETTINGS['propertypath'])
propertypath.insert(1, '/home/app/cactvsenv/prop')

CACTVS_SETTINGS['python_object_autodelete'] = True
CACTVS_SETTINGS['lookup_hosts'] = []
CACTVS_SETTINGS['propertypath'] = tuple(propertypath)

logger = logging.getLogger('cirx')

FIXTURES = ['sandbox.json']
RESOLVER_LIST = ["name", "smiles", "hashisy"]

ResolverTest = namedtuple("ResolverTest", "identifier representations")
ResolverResponse = namedtuple("ResolverResponse", "resolver expectations exception")


# class ChemicalStructureTests(TestCase):
#     fixtures = FIXTURES
#
#     def setUp(self):
#         logger.info("cactvs version: %s", cactvs['version'])
#
#     def tearDown(self):
#         logger.info("------------- Tear Down -------------")
#         logger.info("dataset list {} {} ens list {} {}"
#                     .format(len(Dataset.List()), Dataset.List(), len(Ens.List()), Ens.List()))
#         logger.info("dataset list {} {} ens list {} {}"
#                     .format(len(Dataset.List()), Dataset.List(), len(Ens.List()), Ens.List()))
#
#     @parameterized.expand([
#         [{'ens': Ens("CCO")}, None],
#         [{'structure': Structure.objects.get(id=8)}, None],
#         [{'structure': Structure.objects.get(id=8), 'ens': Ens("CCO")}, None],
#         #[{'structure': Structure.objects.get(id=7), 'ens': Ens("CCO")}, None],
#         #[{'structure': Structure.objects.get(id=7), 'ens': Ens("CCOCC")}, None],
#     ])
#     def test(self, kwargs, expectation):
#         cs = ChemicalStructure(**kwargs)
#         logger.info("structure {} ens {} identifier {} x {}".format(cs.structure, cs.ens, cs.identifier, cs.metadata))


# class DispatcherTest(TestCase):
#     fixtures = FIXTURES
#
#     def setUp(self):
#         logger.info("cactvs version: %s", cactvs['version'])
#
#     def tearDown(self):
#         logger.info("------------- Tear Down -------------")
#         logger.info("dataset list {} {} ens list {} {}".format(len(Dataset.List()), Dataset.List(), len(Ens.List()), Ens.List()))
#
#     @parameterized.expand([
#     ])
#     def test(self, resolver_test: ResolverTest):
#         dispatcher: Dispatcher


class ChemicalStringTests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        logger.info("cactvs version: %s", cactvs['version'])

    def tearDown(self):
        logger.info("------------- Tear Down -------------")
        logger.info("dataset list {} {} ens list {} {}".format(len(Dataset.List()), Dataset.List(), len(Ens.List()),
                                                               Ens.List()))

    @parameterized.expand([
        [ResolverTest(
            identifier="CCO",
            representations=[
                ResolverResponse(resolver="smiles", expectations={'E174572A915E4471'}, exception=None),
                ResolverResponse(resolver="stdinchikey", expectations=None, exception=ValueError()),
                ResolverResponse(resolver="stdinchi", expectations=None, exception=ValueError()),
                ResolverResponse(resolver="structure_representation", expectations=None, exception=ValueError()),
            ]
        )],
        [ResolverTest(
            identifier="CCO",
            representations=[
                ResolverResponse(resolver="structure_representation", expectations={'E174572A915E4471'}, exception=None)
            ]
        )],
        [ResolverTest(
            identifier="ethanol",
            representations=[
                ResolverResponse(resolver="name", expectations={'E174572A915E4471'}, exception=None),
                ResolverResponse(resolver="stdinchikey", expectations=None, exception=ValueError()),
                ResolverResponse(resolver="stdinchi", expectations=None, exception=ValueError()),
                ResolverResponse(resolver="structure_representation", expectations=None, exception=ValueError()),
            ]
        )],
        [ResolverTest(
            identifier="E174572A915E4471-FICTS-01-1A",
            representations=[
                ResolverResponse(resolver="ncicadd_identifier", expectations={'E174572A915E4471'}, exception=None),
                ResolverResponse(resolver="smiles", expectations=None, exception=ValueError()),
                ResolverResponse(resolver="structure_representation", expectations=None, exception=ValueError()),
            ]
        )],
        [ResolverTest(
            identifier="LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
            representations=[
                ResolverResponse(resolver="stdinchikey", expectations={'E174572A915E4471'}, exception=None)
            ],
        )],
        [ResolverTest(
            identifier="LFQSCWFLJHTTHZ-UHFFFAOYSA",
            representations=[
                ResolverResponse(resolver="stdinchikey", expectations={'E174572A915E4471'}, exception=None)
            ],
        )],
        [ResolverTest(
            identifier="LFQSCWFLJHTTHZ",
            representations=[
                ResolverResponse(resolver="stdinchikey", expectations={'E174572A915E4471'}, exception=None)
            ],
        )],
        [ResolverTest(
            identifier="DDPJWUQJQMKQIF",
            representations=[
                ResolverResponse(resolver="stdinchikey", expectations={'893627AD7BDD6B4F', '3FC9522042E03718'}, exception=None)
            ],
        )],
        #######################################################
        # [ResolverTest(
        #     request="1AD375920BE60DAD",
        #     responses=[
        #         ResolverResponse(resolver="hashisy", expectations={'1AD375920BE60DAD'}, exception=None)
        #     ],
        # )],
        # [ResolverTest(
        #     request="NCICADD:RID=102",
        #     responses=[
        #         ResolverResponse(resolver="ncicadd_cid", expectations={'3DB0124A3ECF5ECE'}, exception=None)
        #     ],
        # )],
        # [ResolverTest(
        #     request="NCICADD:RID=104",
        #     responses=[
        #         ResolverResponse(resolver="ncicadd_rid", expectations={'1AD375920BE60DAD'}, exception=None)
        #     ],
        # )],
        # [ResolverTest(
        #     request="NCICADD:CID=5",
        #     responses=[
        #         ResolverResponse(resolver="ncicadd_cid", expectations={'59B33067D13A00C2'}, exception=None),
        #         ResolverResponse(resolver="smiles", expectations=None, exception=ValueError()),
        #         ResolverResponse(resolver="stdinchikey", expectations=None, exception=ValueError())
        #     ],
        # )],

        # [ResolverTest(
        #     request="tautomers:Warfarin",
        #     responses=[
        #         ResolverResponse(
        #             resolver="name",
        #             expectations={'20A701AA27DA3574', '551515A8181F0DDC', '73CEC1A3C72EEA00', 'D76B88C0354759F1',
        #                           '8868B850DAEF2039', '571F55B366B95577', '6151CAE0B3730D90', 'DE5C78BB2B58C15A',
        #                           '93B460E97954E4E8'},
        #             exception=None
        #         )
        #     ],
        # )],
        # [ResolverTest(
        #    request="CCO",
        #    responses=[
        #        ResolverResponse(resolver="smiles", expectations={'E174572A915E4471'}, exception=None),
        #        ResolverResponse(resolver="stdinchikey", expectations=None, exception=ValueError()),
        #    ]
        # )],
    ])
    def test(self, resolver_test: ResolverTest):

        resolver_list = [test.resolver for test in resolver_test.representations]

        chemical_string = ChemicalString(string=resolver_test.identifier, resolver_list=resolver_list)
        actual_data = chemical_string.resolver_data

        for expected_data in resolver_test.representations:
            resolver, expectations = expected_data.resolver, expected_data.expectations
            logger.info("REQUEST {} RESOLVER {}".format(resolver_test.identifier, resolver))
            if expected_data.exception:
                exception = actual_data[resolver][0].exception
                logger.info("exception {} received {}".format(expected_data.exception, exception))
                self.assertIsInstance(exception, type(expected_data.exception))
            else:
                #resolved = set([structure.hashisy for structure in actual_data[resolver].resolved])
                resolved = set([structure.hashisy for item in actual_data[resolver] for structure in item.resolved])
                logger.info("expected {} received {}".format(expectations, resolved))
                self.assertEqual(resolved, expectations)
