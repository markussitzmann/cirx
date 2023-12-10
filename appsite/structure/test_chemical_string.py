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

TestData = namedtuple("TestData", "identifier representations")
TestResponse = namedtuple("TestResponse", "resolver expectations exception")


class ChemicalStringTests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        logger.info("cactvs version: %s", cactvs['version'])

    def tearDown(self):
        logger.info("------------- Tear Down -------------")
        logger.info("dataset list {} {} ens list {} {}".format(len(Dataset.List()), Dataset.List(), len(Ens.List()),
                                                               Ens.List()))

    @parameterized.expand([
        ["cas", TestData(
            identifier="50-00-0",
            representations=[
                TestResponse(resolver="cas_number", expectations={'E174572A915E4471'}, exception=None),
                TestResponse(resolver="smiles", expectations=None, exception=ValueError()),
                TestResponse(resolver="stdinchikey", expectations=None, exception=ValueError()),
                TestResponse(resolver="stdinchi", expectations=None, exception=ValueError()),
                TestResponse(resolver="structure_representation", expectations=None, exception=ValueError()),
            ]
        )],
        # ["smiles1", TestData(
        #     identifier="CCO",
        #     representations=[
        #         TestResponse(resolver="smiles", expectations={'E174572A915E4471'}, exception=None),
        #         TestResponse(resolver="stdinchikey", expectations=None, exception=ValueError()),
        #         TestResponse(resolver="stdinchi", expectations=None, exception=ValueError()),
        #         TestResponse(resolver="structure_representation", expectations=None, exception=ValueError()),
        #     ]
        # )],
        # ["smiles1", TestData(
        #     identifier="CCO",
        #     representations=[
        #         TestResponse(resolver="structure_representation", expectations={'E174572A915E4471'}, exception=None)
        #     ]
        # )],
        # ["name1", TestData(
        #     identifier="ethanol",
        #     representations=[
        #         TestResponse(resolver="name", expectations={'E174572A915E4471'}, exception=None),
        #         TestResponse(resolver="stdinchikey", expectations=None, exception=ValueError()),
        #         TestResponse(resolver="stdinchi", expectations=None, exception=ValueError()),
        #         TestResponse(resolver="structure_representation", expectations=None, exception=ValueError()),
        #     ]
        # )],
        # ["ficts1", TestData(
        #     identifier="E174572A915E4471-FICTS-01-1A",
        #     representations=[
        #         TestResponse(resolver="ncicadd_identifier", expectations={'E174572A915E4471'}, exception=None),
        #         TestResponse(resolver="smiles", expectations=None, exception=ValueError()),
        #         TestResponse(resolver="structure_representation", expectations=None, exception=ValueError()),
        #     ]
        # )],
        # ["inchi-key-full", TestData(
        #     identifier="LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
        #     representations=[
        #         TestResponse(resolver="stdinchikey", expectations={'E174572A915E4471'}, exception=None)
        #     ],
        # )],
        # ["inchi-key-prefixed-full", TestData(
        #     identifier="InChIKey=LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
        #     representations=[
        #         TestResponse(resolver="stdinchikey", expectations={'E174572A915E4471'}, exception=None)
        #     ],
        # )],
        # ["inchi-partial", TestData(
        #     identifier="LFQSCWFLJHTTHZ-UHFFFAOYSA",
        #     representations=[
        #         TestResponse(resolver="stdinchikey", expectations={'E174572A915E4471'}, exception=None)
        #     ],
        # )],
        # ["inchi-short", TestData(
        #     identifier="LFQSCWFLJHTTHZ",
        #     representations=[
        #         TestResponse(resolver="stdinchikey", expectations={'E174572A915E4471'}, exception=None)
        #     ],
        # )],
        # ["inchi-short-multiple-structure", TestData(
        #     identifier="DDPJWUQJQMKQIF",
        #     representations=[
        #         TestResponse(resolver="stdinchikey", expectations={'893627AD7BDD6B4F', '3FC9522042E03718'}, exception=None)
        #     ],
        # )],
        # ["hashisy1", TestData(
        #     identifier="1AD375920BE60DAD",
        #     representations=[
        #         TestResponse(resolver="hashisy", expectations={'1AD375920BE60DAD'}, exception=None)
        #     ],
        # )],
        # ["rid1", TestData(
        #     identifier="NCICADD:RID=1",
        #     representations=[
        #         TestResponse(resolver="ncicadd_rid", expectations={'E174572A915E4471'}, exception=None),
        #         TestResponse(resolver="stdinchikey", expectations=None, exception=ValueError()),
        #         TestResponse(resolver="stdinchi", expectations=None, exception=ValueError()),
        #         TestResponse(resolver="structure_representation", expectations=None, exception=ValueError()),
        #     ],
        # )],
        # ["cid1", TestData(
        #     identifier="NCICADD:CID=1",
        #     representations=[
        #         TestResponse(resolver="ncicadd_cid", expectations={'1AD375920BE60DAD'}, exception=None),
        #         TestResponse(resolver="stdinchikey", expectations=None, exception=ValueError()),
        #         TestResponse(resolver="stdinchi", expectations=None, exception=ValueError()),
        #         TestResponse(resolver="structure_representation", expectations=None, exception=ValueError()),
        #     ],
        # )],
        # ["tautomers", TestData(
        #     identifier="tautomers:Warfarin",
        #     representations=[
        #         TestResponse(
        #             resolver="name",
        #             expectations={'20A701AA27DA3574', '551515A8181F0DDC', '73CEC1A3C72EEA00', 'D76B88C0354759F1',
        #                           '8868B850DAEF2039', '571F55B366B95577', '6151CAE0B3730D90', 'DE5C78BB2B58C15A',
        #                           '93B460E97954E4E8'},
        #             exception=None
        #         )
        #     ],
        # )],
        # ["stdinchi", TestData(
        #     identifier="InChI=1S/C19H16O4/"
        #                "c1-12(20)11-15(13-7-3-2-4-8-13)17-18(21)14-9-5-6-10-16(14)23-19(17)22/h2-10,15,22H,11H2,1H3",
        #     representations=[
        #         TestResponse(resolver="stdinchi", expectations={'20A701AA27DA3574'}, exception=None),
        #         TestResponse(resolver="stdinchikey", expectations=None, exception=ValueError())
        #     ],
        # )]
    ])
    def test(self, name, resolver_test: TestData):

        resolver_list = [test.resolver for test in resolver_test.representations]

        chemical_string = ChemicalString(string=resolver_test.identifier, resolver_list=resolver_list)
        actual_data = chemical_string.resolver_data

        for expected_data in resolver_test.representations:
            resolver, expectations = expected_data.resolver, expected_data.expectations
            logger.info("-- REQUEST {} RESOLVER {}".format(resolver_test.identifier, resolver))
            if expected_data.exception:
                exception = actual_data[resolver][0].exception
                logger.info("exception {}".format(expected_data.exception))
                logger.info("received {}".format(exception))
                self.assertIsInstance(exception, type(expected_data.exception))
            else:
                resolved = set([structure.hashisy for item in actual_data[resolver] for structure in item.resolved])
                logger.info("expected {}".format(expectations)),
                logger.info("received {}".format(resolved))
                self.assertEqual(resolved, expectations)
