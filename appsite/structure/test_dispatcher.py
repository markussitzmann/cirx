import logging
from typing import List
from unittest import skip

from django.conf import settings
from django.test import TestCase, RequestFactory
from parameterized import parameterized
from pycactvs import Ens, Dataset, cactvs, Molfile

from dispatcher import Dispatcher, DispatcherData
from structure.string_resolver import ChemicalString

logger = logging.getLogger('cirx')

FIXTURES = ['sandbox.json']
RESOLVER_LIST = ["name", "smiles"]


class DispatcherTests(TestCase):
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
        # ["CCO", RESOLVER_LIST, (1, True)],
        # ["CCN", RESOLVER_LIST, (1, True)],
        # ["CCS", RESOLVER_LIST, (1, True)],
        # ["CCOCC", RESOLVER_LIST, (1, True)],
        # ["CCNCC", RESOLVER_LIST, (1, True)],
        # ["tautomers:guanine", RESOLVER_LIST, (26, True)],
    ])
    @skip
    def test_dispatcher_create_dataset(self, string, resolver_list, expectations):
        logger.info("------------- Test Dispatcher (%s) -------------" % string)
        expected_dataset_count, expected_status = expectations

        resolver_data = ChemicalString(string=string, resolver_list=resolver_list).resolver_data
        dataset: Dataset = Dispatcher._create_dataset(resolver_data=resolver_data, simple=True)

        for e in dataset.ens():
            logger.info("%s %s" % (e.get('E_SMILES'), e.get('E_FICUS_ID')))

        self.assertEqual(dataset.count(), expected_dataset_count)
        self.assertTrue(expected_status)

    @parameterized.expand([
        ["warfarin", RESOLVER_LIST, (9, True)],
        ["tautomers:warfarin", RESOLVER_LIST, (9, True)],
        #["CCO", RESOLVER_LIST, (1, True)],
        # ["CCN", RESOLVER_LIST, (1, True)],
        # ["CCS", RESOLVER_LIST, (1, True)],
        # ["CCOCC", RESOLVER_LIST, (1, True)],
        # ["CCNCC", RESOLVER_LIST, (1, True)],
        # ["tautomers:guanine", RESOLVER_LIST, (26, True)],
    ])
    def test(self, string, resolver_list, expectations):
        logger.info("------------- Test Dispatcher (%s) -------------" % string)
        expected, expected_status = expectations

        dispatcher: Dispatcher = Dispatcher("ncicadd_cid", request=None, representation_param=None, output_format="plain")
        data: DispatcherData = dispatcher.parse(string)

        logger.info("DISPATCHER %s", data)


    # @parameterized.expand([
    #     ["tautomers:guanine", RESOLVER_LIST, (2, 3, 2), (6, True)],
    #     ["tautomers:guanine", RESOLVER_LIST, (2, 3, 5), (2, True)],
    #     ["tautomers:guanine", RESOLVER_LIST, (2, 3, 20), (0, True)],
    #     ["tautomers:guanine", RESOLVER_LIST, (2, 0, 20), (0, True)],
    #     ["tautomers:guanine", RESOLVER_LIST, (0, 3, 20), (0, True)],
    # ])
    # #@skip
    # def test_dispatcher_page(self, string, resolver_list, paging, expectations):
    #     logger.info("------------- Test Dispatcher Page (%s) -------------" % string)
    #     expected_dataset_count, expected_status = expectations
    #
    #     dataset: Dataset = Dispatcher._create_dataset_from_resolver_string(
    #         string=string,
    #         resolver_list=resolver_list,
    #         simple=True
    #     )
    #
    #     rows, columns, page = paging
    #     page_dataset: Dataset = Dispatcher._create_dataset_page(dataset, rows, columns, page)
    #
    #     self.assertEqual(page_dataset.count(), expected_dataset_count)
    #     self.assertTrue(expected_status)

    # @parameterized.expand([
    #     ["tautomers:warfarin", None, (9, True)],
    #     ["tautomers:warfarin", "/file?structure_index=1", (1, True)],
    #     ["tautomers:tylenol", None, (10, True)],
    #     ["CCO", None, (1, True)],
    #     ["CCN", None, (1, True)],
    #     ["CCS", None, (1, True)],
    #     ["CCOCC", None, (1, True)],
    #     ["CCNCC", None, (1, True)],
    #     ["tautomers:guanine", None, (26, True)],
    #     ["tautomers:guanine", "/file?structure_index=25", (1, True)],
    # ])
    # def test_dispatcher_molfile_request(self, string, dummy_request_string, expectations):
    #     logger.info("------------- Test Dispatcher Molfile (%s) -------------" % string)
    #     expected_molfile_count, expected_status = expectations
    #
    #     if dummy_request_string:
    #         request = self.factory.get(dummy_request_string)
    #     else:
    #         request = self.factory.request()
    #     dispatcher: Dispatcher = Dispatcher("file", request)
    #
    #     molfile_string = dispatcher.molfilestring(string)
    #     molfile = Molfile.Open(molfile_string, mode="s")
    #
    #     logger.info(">>> %s %s" % (dispatcher.response_list, molfile.count()))
    #
    #     self.assertEqual(molfile.count(), expected_molfile_count)
    #     self.assertTrue(expected_status)
