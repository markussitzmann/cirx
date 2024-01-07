import logging
from collections import namedtuple

from django.test import TestCase
from parameterized import parameterized
from pycactvs import Ens, Dataset, cactvs

from smiles import SMILES, SmilesError
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

TestData = namedtuple("TestData", "smiles params expectations")
TestParams = namedtuple("TestParams", "strict_testing")
TestExpectations = namedtuple("TestExpectations", "is_smiles exception")
ActualData = namedtuple("ActualData", "is_smiles exception")

class SMILESTests(TestCase):
    #fixtures = FIXTURES

    def setUp(self):
        logger.info("cactvs version: %s", cactvs['version'])

    def tearDown(self):
        logger.info("------------- Tear Down -------------")
        # logger.info("dataset list {} {} ens list {} {}".format(len(Dataset.List()), Dataset.List(), len(Ens.List()),
        #                                                        Ens.List()))

    @parameterized.expand([
        ["smiles1", TestData(
            smiles="C",
            params=TestParams(strict_testing=True),
            expectations=[
                TestExpectations(is_smiles=True, exception=None),
            ])
        ],
        ["smiles2", TestData(
            smiles="CCO",
            params=TestParams(strict_testing=True),
            expectations=[
                TestExpectations(is_smiles=True, exception=None),
            ])
        ],
        ["smiles3", TestData(
            smiles="C#O",
            params=TestParams(strict_testing=True),
            expectations=[
                TestExpectations(is_smiles=True, exception=None),
            ])
        ],
        ["smiles3", TestData(
            smiles="C##O",
            params=TestParams(strict_testing=True),
            expectations=[
                TestExpectations(is_smiles=True, exception=None),
            ])
         ],
        ["cas", TestData(
            smiles="50-00-0",
            params=TestParams(strict_testing=True),
            expectations=[
                TestExpectations(is_smiles=False, exception=SmilesError("no valid SMILES string")),
            ])
        ],
        ["dummy", TestData(
            smiles="BLA",
            params=TestParams(strict_testing=True),
            expectations=[
                TestExpectations(is_smiles=False, exception=SmilesError("no valid SMILES string")),
            ])
         ]
    ])
    def test(self, name, test: TestData):

        actual: ActualData
        try:
            _ = SMILES(test.smiles, test.params.strict_testing)
            actual = ActualData(is_smiles=True, exception=None)
        except Exception as exception:
            actual = ActualData(is_smiles=False, exception=exception)

        for expected in test.expectations:
            logger.info("-- {} SMILES {} PARAMS {}".format(name, test.smiles, test.params))
            if expected.exception:
                logger.info("expected {}".format(expected.exception))
                logger.info("actual {}".format(actual.exception))
                self.assertIsInstance(actual.exception, type(expected.exception))
            else:
                # resolved = set([structure.hashisy for item in actual_data[resolver] for structure in item.resolved])
                logger.info("expected {}".format(expected.is_smiles)),
                logger.info("actual {}".format(actual.is_smiles))
                self.assertEqual(expected.is_smiles, actual.is_smiles)
