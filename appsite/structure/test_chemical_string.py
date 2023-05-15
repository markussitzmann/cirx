import logging

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
        #["CCO", ['smiles', ], [8, ]],
        #["1AD375920BE60DAD", ['hashisy', ], [1, ]],
        #["Warfarin", ['name', ], [2, ]],
        #["NCICADD:CID=3", ['ncicadd_cid', ], [3, ]],
        ["E174572A915E4471-FICTS-01-1A", ['ncicadd_identifier', 'smiles', ], [8, SmilesError('no valid SMILES string')]],
        #["LFQSCWFLJHTTHZ-UHFFFAOYSA-N", ['stdinchikey', ], [8, ]],
        #["LFQSCWFLJHTTHZ-UHFFFAOYSA", ['stdinchikey', ], [8, ]],
        #["LFQSCWFLJHTTHZ", ['stdinchikey', ], [8, ]],
    ])
    def test(self, string, resolver_list, expectations):
        #expected_structure_id = expectations[0]
        logger.info("START string '{}' resolver {} expectations {}".format(string, resolver_list, expectations))
        chemical_string = ChemicalString(string=string, resolver_list=resolver_list)
        resolver_data = chemical_string.resolver_data
        item: ChemicalStructure
        for resolver, expectation in zip(resolver_list, expectations):
            resolved, exception = resolver_data[resolver]
            if isinstance(expectation, Exception):
                self.assertIsInstance(expectation, type(exception), "bla")
            else:
                logger.info("representation {}".format(resolved))
                logger.info("METADATA  {}".format(resolved.metadata))
                logger.info("STRUCTURE {}".format(resolved.structure.id))
                self.assertEqual(resolved.structure.id, expectation)

