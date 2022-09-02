import logging
from collections import defaultdict

from django.test import TestCase
from pycactvs import Molfile

from etl.models import StructureFileCollection
from resolver.models import Dataset, Publisher
from registration import Preprocessors

logger = logging.getLogger('cirx')


class PreprocessorTests(TestCase):

    fixtures = ['etl.json', 'resolver.json', ]

    def setUp(self):
        self.structure_file_collection = StructureFileCollection.objects.get(id=2)
        self.structure_file = self.structure_file_collection.files.all()[0]

        logger.info("FILE %s", self.structure_file)
        fname: str = self.structure_file.file.name
        molfile: Molfile = Molfile.Open(fname)
        molfile.set('record', 10)

        self.ens = molfile.read()

        for name in ['MOLI', 'Ambinter', 'DiscoveryGate']:
            d = Dataset.objects.get(name=name)
            d.delete()


    def tearDown(self):

        datasets = Dataset.objects.all()
        for dataset in datasets:
            logger.info("DATASET: %s", dataset)

        publishers = Publisher.objects.all()
        for publisher in publishers:
            logger.info("PUBLISHER: %s", publisher)

    def test_preprocessor(self):
        logger.info("----- preprocessor start ----")
        logger.info("C %s", self.structure_file_collection)
        logger.info("F %s", self.structure_file)
        logger.info("E %s", self.ens)

        record_data = {
            'hashisy_key': self.ens.get('E_HASHISY'),
            'index': 1,
            'preprocessors': defaultdict(dict)
        }

        preprocessor_names = [p.preprocessor_name for p in self.structure_file_collection.preprocessors.all()]
        for preprocessor_name in preprocessor_names:
            preprocessor = getattr(Preprocessors, preprocessor_name, None)
            record_data['preprocessors'][preprocessor_name] = preprocessor(self.structure_file, self.ens)

        for preprocessor_name in preprocessor_names:
            preprocessor_transaction_name = preprocessor_name + '_transaction'
            preprocessor_transaction = getattr(Preprocessors, preprocessor_transaction_name, None)
            preprocessor_transaction(self.structure_file, [record_data, ])









