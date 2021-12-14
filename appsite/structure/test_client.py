import logging

from django.test import TestCase, SimpleTestCase, Client

from pycactvs import Ens

from custom.cactvs import CactvsHash, CactvsMinimol
from structure.models import Structure2, InChI
from resolver import ChemicalStructure

logger = logging.getLogger('cirx')


class StructureClientTests(TestCase):
    fixtures = ['structure.json', 'database.json']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def tearDown(self):
        logger.info("ens list >>> %s", Ens.List())

    def test_request(self):
        response = self.client.get('/chemical/structure/CCO/stdinchikey')
        self.assertEqual(response.status_code, 200)
