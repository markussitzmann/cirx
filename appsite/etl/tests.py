import glob
import logging
import os

from pycactvs import Molfile, Ens
from unittest import skip

from django.test import SimpleTestCase, TestCase
from django.conf import settings

from etl.models import FileCollection, StructureFile
from registration import FileRegistry

logger = logging.getLogger('cirx')

#fpath = os.path.join(settings.CIR_FILESTORE_ROOT, 'nci', 'NCI_DTP.sdf')
fpath = os.path.join(settings.CIR_FILESTORE_ROOT, 'pubchem', 'substance', 'Substance_095000001_095500000.sdf')


class FileRegistrationTests(TestCase):
    fixtures = ["etl.json"]

    def setUp(self):
        self.file_collections = FileCollection.objects.all()

    def test_register_files(self):
        for file_collection in self.file_collections:
            processor = FileRegistry(file_collection)
            file_list = processor.register()
            logger.info("file list : %s" % file_list)

    # def test_register_files2(self):
    #     for file_collection in self.file_collections:
    #         logger.info(">>> %s %s", file_collection, file_collection.file_location_pattern_string)
    #         file_name_list = glob.glob(
    #             os.path.join(settings.CIR_FILESTORE_ROOT, file_collection.file_location_pattern_string),
    #             recursive=True
    #         )
    #         for name in file_name_list:
    #             f, created = StructureFile.objects.get_or_create(
    #                 collection=file_collection,
    #                 name=name
    #             )
    #         logger.info(">>> %s", file_name_list)



class MolfileTests(TestCase):
    fixtures = ["etl.json"]

    def setUp(self):
        self.molfile = Molfile.Open(fpath)

    def shutDown(self):
        logger.info(">>> %s", Ens.List())

    @skip
    def test_loop(self):
        logger.info(self.molfile)

        def loopfunction(ens):
            ficus = ens.get('E_HASHISY')
            smiles = ens.get('E_MINIMOL')
            props = self.molfile.fields
            logger.info("%s %s %s" % (ficus, '', props))
        Molfile.Loop(fpath, function=loopfunction, maxloop=1000)

    def test_loop2(self):
        logger.info("---- start ---")

        while True:
            logger.info("---- ens ---")
            fields = list()
            try:
                ens = self.molfile.read()
            except RuntimeError as e:
                break
            fields.append(self.molfile.fields)
            logger.info("%s %s %s" % (ens, '', fields))

    @skip
    def test_file_pattern(self):
        collections = FileCollection.objects.all()
        for collection in collections:
            logger.info(collection.file_location_pattern_string)
            file_name_list = glob.glob(
                os.path.join(settings.CIR_FILESTORE_ROOT, collection.file_location_pattern_string),
                recursive=True
            )
            logger.info(file_name_list)
            for file_name in file_name_list:

                molfile = Molfile.Open(file_name)

                molfile_count = molfile.count()
                molfile_props = molfile.props()

                logger.info("count: %s %s" % (molfile_count, file_name))
                logger.info("props: %s" % (molfile_props,))

                StructureFile.objects.get_or_create(
                    name=file_name,
                    count=molfile_count
                )

            files = StructureFile.objects.all()
            for file in files:
                logger.info("%s : %s", file.count, file.name)

