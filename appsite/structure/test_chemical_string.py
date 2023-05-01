import logging
from typing import List

from django.conf import settings
from django.test import TestCase, RequestFactory
from parameterized import parameterized
from pycactvs import Ens, Dataset, cactvs, Molfile

from dispatcher import Dispatcher
from structure.string_resolver import ChemicalString

logger = logging.getLogger('cirx')

FIXTURES = ['sandbox.json']
RESOLVER_LIST = ["name", "smiles", "hashisy"]


class ChemicalStringTests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.factory = RequestFactory()
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
        for item in data:
            logger.info("representation %s" % item)
            logger.info(item.ens)
            logger.info(item.metadata)

            #self.assertTrue(representation.structures and len(representation.structures) >= 1)


