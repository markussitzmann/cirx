import logging
from collections import namedtuple
from unittest import skip

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
TestResponse = namedtuple("TestResponse", "module expectations exception")


class ChemicalStringTests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        logger.info("cactvs version: %s", cactvs['version'])

    def tearDown(self):
        logger.info("------------- Tear Down -------------")
        logger.info("dataset list {} {} ens list {} {}".format(len(Dataset.List()), Dataset.List(), len(Ens.List()),
                                                               Ens.List()))

    @parameterized.expand([
        ["name warfarin", TestData(
            identifier="warfarin",
            representations=[
                TestResponse(module="name", expectations={'20A701AA27DA3574'}, exception=None),
            ],
        )],
        ["ficts warfarin", TestData(
            identifier="ficts:warfarin",
            representations=[
                TestResponse(module="name", expectations={'20A701AA27DA3574'}, exception=None),
            ],
        )],
        ["ficus warfarin", TestData(
            identifier="ficus:warfarin",
            representations=[
                TestResponse(module="name", expectations={'D76B88C0354759F1'}, exception=None),
            ],
        )],
        ["cas", TestData(
            identifier="64-17-5",
            representations=[
                TestResponse(module="cas_number", expectations={'E174572A915E4471'}, exception=None),
                TestResponse(module="smiles", expectations=None, exception=ValueError()),
                TestResponse(module="stdinchikey", expectations=None, exception=ValueError()),
                TestResponse(module="stdinchi", expectations=None, exception=ValueError()),
                TestResponse(module="structure_representation", expectations=None, exception=ValueError()),
            ]
        )],
        ["smiles1", TestData(
            identifier="CCO",
            representations=[
                TestResponse(module="smiles", expectations={'E174572A915E4471'}, exception=None),
                TestResponse(module="stdinchikey", expectations=None, exception=ValueError()),
                TestResponse(module="stdinchi", expectations=None, exception=ValueError()),
                TestResponse(module="structure_representation", expectations=None, exception=ValueError()),
            ]
        )],
        ["smiles1", TestData(
            identifier="CCO",
            representations=[
                TestResponse(module="structure_representation", expectations={'E174572A915E4471'}, exception=None)
            ]
        )],
        ["name1", TestData(
            identifier="ethanol",
            representations=[
                TestResponse(module="name", expectations={'E174572A915E4471'}, exception=None),
                TestResponse(module="stdinchikey", expectations=None, exception=ValueError()),
                TestResponse(module="stdinchi", expectations=None, exception=ValueError()),
                TestResponse(module="structure_representation", expectations=None, exception=ValueError()),
            ]
        )],
        ["ficts1", TestData(
            identifier="E174572A915E4471-FICTS-01-1A",
            representations=[
                TestResponse(module="ncicadd_identifier", expectations={'E174572A915E4471'}, exception=None),
                TestResponse(module="smiles", expectations=None, exception=ValueError()),
                TestResponse(module="structure_representation", expectations=None, exception=ValueError()),
            ]
        )],
        ["inchi-key-full", TestData(
            identifier="LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
            representations=[
                TestResponse(module="stdinchikey", expectations={'E174572A915E4471'}, exception=None)
            ],
        )],
        ["inchi-key-prefixed-full", TestData(
            identifier="InChIKey=LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
            representations=[
                TestResponse(module="stdinchikey", expectations={'E174572A915E4471'}, exception=None)
            ],
        )],
        ["inchi-partial", TestData(
            identifier="LFQSCWFLJHTTHZ-UHFFFAOYSA",
            representations=[
                TestResponse(module="stdinchikey", expectations={'E174572A915E4471'}, exception=None)
            ],
        )],
        ["inchi-short", TestData(
            identifier="LFQSCWFLJHTTHZ",
            representations=[
                TestResponse(module="stdinchikey", expectations={'E174572A915E4471'}, exception=None)
            ],
        )],
        ["inchi-short-multiple-structure", TestData(
            identifier="DDPJWUQJQMKQIF",
            representations=[
                TestResponse(module="stdinchikey", expectations={'893627AD7BDD6B4F', '3FC9522042E03718'}, exception=None)
            ],
        )],
        ["hashisy1", TestData(
            identifier="1AD375920BE60DAD",
            representations=[
                TestResponse(module="hashisy", expectations={'1AD375920BE60DAD'}, exception=None)
            ],
        )],
        ["rid1", TestData(
            identifier="NCICADD:RID=1",
            representations=[
                TestResponse(module="ncicadd_rid", expectations={'E174572A915E4471'}, exception=None),
                TestResponse(module="stdinchikey", expectations=None, exception=ValueError()),
                TestResponse(module="stdinchi", expectations=None, exception=ValueError()),
                TestResponse(module="structure_representation", expectations=None, exception=ValueError()),
            ],
        )],
        ["cid1", TestData(
            identifier="NCICADD:CID=1",
            representations=[
                TestResponse(module="ncicadd_cid", expectations={'1AD375920BE60DAD'}, exception=None),
                TestResponse(module="stdinchikey", expectations=None, exception=ValueError()),
                TestResponse(module="stdinchi", expectations=None, exception=ValueError()),
                TestResponse(module="structure_representation", expectations=None, exception=ValueError()),
            ],
        )],
        ["sid1", TestData(
            identifier="NCICADD:SID=2",
            representations=[
                TestResponse(module="ncicadd_sid", expectations={'20A701AA27DA3574'}, exception=None),
                TestResponse(module="stdinchikey", expectations=None, exception=ValueError()),
                TestResponse(module="stdinchi", expectations=None, exception=ValueError()),
                TestResponse(module="structure_representation", expectations=None, exception=ValueError()),
            ],
        )],
        ["tautomers", TestData(
            identifier="tautomers:warfarin",
            representations=[
                TestResponse(
                    module="name",
                    expectations={'20A701AA27DA3574', '551515A8181F0DDC', '73CEC1A3C72EEA00', 'D76B88C0354759F1',
                                  '8868B850DAEF2039', '571F55B366B95577', '6151CAE0B3730D90', 'DE5C78BB2B58C15A',
                                  '93B460E97954E4E8'},
                    exception=None
                )
            ],
        )],
        ["stereoisomers", TestData(
            identifier="stereoisomers:F[C@H](Cl)Br",
            representations=[
                TestResponse(
                    module="smiles",
                    expectations={'66DAC3DEE25DE645', '88967B9483C4898C', 'A7C644ED537F940E'},
                    exception=None
                )
            ],
        )],
        ["no stereo", TestData(
            identifier="no_stereo:F[C@H](Cl)Br",
            representations=[
                TestResponse(
                    module="smiles",
                    expectations={'88967B9483C4898C'},
                    exception=None
                )
            ],
        )],
        ["add hydrogens", TestData(
            identifier="add_hydrogens:[C][C]",
            representations=[
                TestResponse(
                    module="smiles",
                    expectations={'48F6C98BB4B46628'},
                    exception=None
                )
            ],
        )],
        ["remove hydrogens", TestData(
            identifier="remove_hydrogens:CCO",
            representations=[
                TestResponse(
                    module="smiles",
                    expectations={'145B9F9381F3C5E0'},
                    exception=None
                )
            ],
        )],
        ["warfarin", TestData(
            identifier="warfarin",
            representations=[
                TestResponse(
                    module="name",
                    expectations={'20A701AA27DA3574'},
                    exception=None
                )
            ],
        )],
        ["Warfarin", TestData(
            identifier="Warfarin",
            representations=[
                TestResponse(
                    module="name",
                    expectations={'20A701AA27DA3574'},
                    exception=None
                )
            ],
        )],
        ["stdinchi", TestData(
            identifier="InChI=1S/C19H16O4/"
                       "c1-12(20)11-15(13-7-3-2-4-8-13)17-18(21)14-9-5-6-10-16(14)23-19(17)22/h2-10,15,22H,11H2,1H3",
            representations=[
                TestResponse(module="stdinchi", expectations={'20A701AA27DA3574'}, exception=None),
                TestResponse(module="stdinchikey", expectations=None, exception=ValueError())
            ],
        )]
    ])
    def test(self, name, data: TestData):

        resolver_list = [test.module for test in data.representations]

        chemical_string = ChemicalString(string=data.identifier, resolver_list=resolver_list)
        actual_data = chemical_string.resolver_data

        for expected_data in data.representations:
            resolver, expectations = expected_data.module, expected_data.expectations
            logger.info("-- REQUEST {} RESOLVER {}".format(data.identifier, resolver))
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

    @parameterized.expand([
        ["is hashisy", TestData(
            identifier="20A701AA27DA3574",
            representations=[
                TestResponse(module="hashisy", expectations=True, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_identifier", expectations=False, exception=None),
            ],
        )],
        ["is inchi", TestData(
            identifier="LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
            representations=[
                TestResponse(module="stdinchikey", expectations=True, exception=None),
                TestResponse(module="hashisy", expectations=False, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_identifier", expectations=False, exception=None),
            ],
        )],
        ["is name", TestData(
            identifier="ethanol",
            representations=[
                TestResponse(module="hashisy", expectations=False, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_identifier", expectations=False, exception=None),
                TestResponse(module="stdinchikey", expectations=False, exception=None),
            ],
        )],
        ["is NCICADD RID", TestData(
            identifier="NCICADD:RID=1",
            representations=[
                TestResponse(module="ncicadd_rid", expectations=True, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_identifier", expectations=False, exception=None),
                TestResponse(module="stdinchikey", expectations=False, exception=None),
            ],
        )],
        ["is NCICADD CID", TestData(
            identifier="NCICADD:CID=1",
            representations=[
                TestResponse(module="ncicadd_cid", expectations=True, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="ncicadd_identifier", expectations=False, exception=None),
                TestResponse(module="stdinchikey", expectations=False, exception=None),
            ],
        )],
        ["is NCICADD SID", TestData(
            identifier="NCICADD:SID=2",
            representations=[
                TestResponse(module="ncicadd_sid", expectations=True, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="ncicadd_identifier", expectations=False, exception=None),
                TestResponse(module="stdinchikey", expectations=False, exception=None),
            ],
        )],
        ["is NCICADD identifier 1", TestData(
            identifier="E174572A915E4471-FICTS-01-1A",
            representations=[
                TestResponse(module="ncicadd_identifier", expectations=True, exception=None),
                TestResponse(module="ncicadd_sid", expectations=False, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="stdinchikey", expectations=False, exception=None),
            ],
        )],
        ["is NCICADD identifier 2", TestData(
            identifier="E174572A915E4471-FICTS-01",
            representations=[
                TestResponse(module="ncicadd_identifier", expectations=True, exception=None),
                TestResponse(module="ncicadd_sid", expectations=False, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="stdinchikey", expectations=False, exception=None),
            ],
        )],
        ["is SMILES1", TestData(
            identifier="CCO",
            representations=[
                TestResponse(module="smiles", expectations=True, exception=None),
                TestResponse(module="ncicadd_sid", expectations=False, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="stdinchikey", expectations=False, exception=None),
            ],
        )],
        ["is INCHI", TestData(
            identifier="InChI=1S/C19H16O4/"
                       "c1-12(20)11-15(13-7-3-2-4-8-13)17-18(21)14-9-5-6-10-16(14)23-19(17)22/h2-10,15,22H,11H2,1H3",
            representations=[
                TestResponse(module="stdinchi", expectations=True, exception=None),
                TestResponse(module="smiles", expectations=False, exception=None),
                TestResponse(module="ncicadd_sid", expectations=False, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="stdinchikey", expectations=False, exception=None),
            ],
        )],
        ["is InChIKey 2", TestData(
            identifier="LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
            representations=[
                TestResponse(module="stdinchikey", expectations=True, exception=None),
                TestResponse(module="hashisy", expectations=False, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_identifier", expectations=False, exception=None),
                TestResponse(module="stdinchi", expectations=False, exception=None),
            ],
        )],
        ["is InChIKey 3 partial", TestData(
            identifier="LFQSCWFLJHTTHZ-UHFFFAOYSA",
            representations=[
                TestResponse(module="stdinchikey", expectations=True, exception=None),
                TestResponse(module="hashisy", expectations=False, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_identifier", expectations=False, exception=None),
                TestResponse(module="stdinchi", expectations=False, exception=None),
            ],
        )],
        ["is InChIKey 4 parital ", TestData(
            identifier="LFQSCWFLJHTTHZ",
            representations=[
                TestResponse(module="stdinchikey", expectations=True, exception=None),
                TestResponse(module="hashisy", expectations=False, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_identifier", expectations=False, exception=None),
            ],
        )],
        ["is CAS number ", TestData(
            identifier="50-00-0",
            representations=[
                TestResponse(module="cas_number", expectations=True, exception=None),
                TestResponse(module="stdinchikey", expectations=False, exception=None),
                TestResponse(module="hashisy", expectations=False, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_identifier", expectations=False, exception=None),
            ],
        )],
        ["is name ", TestData(
            identifier="50-00-0",
            representations=[
                TestResponse(module="name", expectations=True, exception=None),
                TestResponse(module="cas_number", expectations=True, exception=None),
                TestResponse(module="stdinchikey", expectations=False, exception=None),
                TestResponse(module="hashisy", expectations=False, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_identifier", expectations=False, exception=None),
            ],
        )],
        ["is integer", TestData(
            identifier="123",
            representations=[
                TestResponse(module="hashisy", expectations=False, exception=None),
                TestResponse(module="ncicadd_rid", expectations=False, exception=None),
                TestResponse(module="ncicadd_cid", expectations=False, exception=None),
                TestResponse(module="ncicadd_identifier", expectations=False, exception=None),
                TestResponse(module="stdinchikey", expectations=False, exception=None),
                TestResponse(module="stdinchi", expectations=False, exception=None),
            ],
        )],
    ])
    def test_is_module(self, name, data: TestData):

        resolver_list = [test.module for test in data.representations]

        chemical_string = ChemicalString(string=data.identifier, resolver_list=resolver_list)

        for expected_data in data.representations:
            function_name = "_is_" + expected_data.module
            logger.info("-- REQUEST {} FUNCTION {}".format(data.identifier, function_name))
            # if expected_data.exception:
            #     try:
            #         _ = (getattr(chemical_string, function_name)())
            #     except Exception as e:
            #         logger.info("exception {}".format(expected_data.exception))
            #         logger.info("received {}".format(type(e)))
            #         self.assertIsInstance(e, expected_data.exception)
            #         return
            #     self.fail()
            # else:
            test_data = (getattr(chemical_string, function_name)())
            resolved = test_data is not None
            logger.info("expected {}".format(expected_data.expectations)),
            logger.info("received {}".format(resolved))
            self.assertEqual(resolved, expected_data.expectations)