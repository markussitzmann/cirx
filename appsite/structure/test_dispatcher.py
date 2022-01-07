import logging
import gc
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
RESOLVER_LIST = ["name", "smiles"]


class DispatcherComponentTests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.factory = RequestFactory()
        logger.info("cactvs version: %s", cactvs['version'])
        logger.info("cactvs settings: %s", settings.CACTVS_SETTINGS['python_object_autodelete'])

    def tearDown(self):
        logger.info("------------- Tear Down -------------")
        logger.info("dataset list 1 >>> %s", Dataset.List())
        logger.info("ens list >>> %s : %s" % (len(Ens.List()), Ens.List()))
        logger.info("dataset list 2 >>> %s", Dataset.List())


    @parameterized.expand([
        ["tautomers:warfarin", RESOLVER_LIST, (9, True)],
        ["tautomers:tylenol", RESOLVER_LIST, (10, True)],
        ["CCO", RESOLVER_LIST, (1, True)],
        ["CCN", RESOLVER_LIST, (1, True)],
        ["CCS", RESOLVER_LIST, (1, True)],
        ["CCOCC", RESOLVER_LIST, (1, True)],
        ["CCNCC", RESOLVER_LIST, (1, True)],
        ["tautomers:guanine", RESOLVER_LIST, (26, True)],
    ])
    def test_dispatcher(self, string, resolver_list, expectations):
        logger.info("------------- Test Dispatcher (%s) -------------" % string)
        expected_dataset_count, expected_status = expectations

        interpretations: List[ChemicalString.Interpretation] = ChemicalString(
            string=string,
            resolver_list=resolver_list
        ).interpretations
        dataset: Dataset = Dispatcher._create_dataset(interpretations=interpretations, simple=True)

        for e in dataset.ens():
            logger.info("%s %s" % (e.get('E_SMILES'), e.get('E_FICUS_ID')))

        self.assertEqual(dataset.count(), expected_dataset_count)
        self.assertTrue(expected_status)

    @parameterized.expand([
        ["tautomers:guanine", RESOLVER_LIST, (2, 3, 2), (6, True)],
        ["tautomers:guanine", RESOLVER_LIST, (2, 3, 5), (2, True)],
        ["tautomers:guanine", RESOLVER_LIST, (2, 3, 20), (0, True)],
        ["tautomers:guanine", RESOLVER_LIST, (2, 0, 20), (0, True)],
        ["tautomers:guanine", RESOLVER_LIST, (0, 3, 20), (0, True)],
    ])
    def test_dispatcher_page(self, string, resolver_list, paging, expectations):
        logger.info("------------- Test Dispatcher Page (%s) -------------" % string)
        expected_dataset_count, expected_status = expectations

        dataset: Dataset = Dispatcher._create_dataset_from_resolver_string(
            string=string,
            resolver_list=resolver_list,
            simple=True
        )

        rows, columns, page = paging
        page_dataset: Dataset = Dispatcher._create_dataset_page(dataset, rows, columns, page)

        self.assertEqual(page_dataset.count(), expected_dataset_count)
        self.assertTrue(expected_status)
