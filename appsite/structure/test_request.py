import logging

from django.test import TestCase, Client, RequestFactory
from parameterized import parameterized
from pycactvs import Ens

from dispatcher import Dispatcher

logger = logging.getLogger('cirx')

FIXTURES = ['structure.json', 'database.json']

class DispatcherTests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        logger.info("ens list >>> %s", Ens.List())

    @parameterized.expand([
        ["CCO", "hashisy", (["E174572A915E4471"], "text/plain")],
        ["CCO", "ficts", (["E174572A915E4471-FICTS-01-1A"], "text/plain")],
    ])
    def test_request(self, string, representation, expected):
        url: str = "/chemical/structure/" + string + "/" + representation
        request = self.factory.get(url)

        parameters = request.GET.copy()
        operator_parameter = None
        if 'operator' in parameters:
            operator_parameter = parameters['operator']
        if operator_parameter:
            string = "%s:%s" % (operator_parameter, string)

        dispatcher = Dispatcher(request=request, representation=representation)

        resolved_string, representation, response, content_type = dispatcher.parse(string)
        logger.info("r > %s : %s : %s : %s" % (resolved_string, representation, response, content_type))

        self.assertEqual(response, expected[0])
        self.assertEqual(content_type, expected[1])


class StructureClientTests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        logger.info("ens list >>> %s", Ens.List())

    def test_request(self):
        response = self.client.get('/chemical/structure/CCO/stdinchikey')
        self.assertEqual(response.status_code, 200)
