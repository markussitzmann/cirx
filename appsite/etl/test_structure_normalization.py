import logging
import math

from django.db.models import QuerySet
from pycactvs import Ens

from django.test import TestCase

from cactvs import SpecialCactvsHash
from etl.models import StructureFileCollection, StructureFileRecord, StructureFile
from registration import FileRegistry, StructureRegistry
from resolver.models import Structure, Dataset, Release, NameType, Name

logger = logging.getLogger('cirx')


class StructureNormalizationTests(TestCase):

    fixtures = ['register.json']

    def setUp(self):
        logger.info("----- structure normalization set up ----")
        #StructureRegistry.CHUNK_SIZE = 10

        # self.structure_file_collection = StructureFileCollection.objects.get(id=2)
        # logger.info("COLLECTION %s", self.structure_file_collection)
        # for f in self.structure_file_collection.files.all():
        #     logger.info("FILE %s", f)
        #
        # for t in NameType.objects.all():
        #     logger.info("NAME TYPE %s : %s :", t.id, t.parent)
        #
        # for r in StructureFileRecord.objects.all():
        #     logger.info("NAME TYPE %s : %s :", r.id, r)

    def tearDown(self):
        logger.info("----- structure normalization tear down ----")
        # logger.info("ENS COUNT: %s" % len(Ens.List()))
        # for n in Name.objects.all():
        #     logger.info("NAME %s : %s :", n.id, n)

    def test_file_registry(self):
        logger.info("----- structure normalization test ----")

        files = StructureFile.objects.all()
        for file in files:
            logger.info("--> %s %s" % (file.id, file))

        t = self.mapper_test(files[6].id)
        logger.info("R --> %s : %s" % (len(t[0]), t))

        n = StructureRegistry.normalize_structures((files[6].id, [r['structure__id'] for r in t[0]]))
        logger.info("N --> %s" % (n, ))

        StructureRegistry.update_normalization_status(files[6].id)

        # registry = FileRegistry(self.structure_file_collection)
        # registry.register_files()
        #
        # for file in self.structure_file_collection.files.all():
        #     logger.info("----- %s ----", file)
        #     FileRegistry.count_and_save_structure_file(file.id)
        #     FileRegistry.register_structure_file_record_chunk(file.id, 0, 100)
        #
        # structure_count = Structure.objects.count()
        # logger.info("STRUCTURE %s", structure_count)
        # #self.assertEqual(structure_count, 195)
        #
        # structure_file_record_count = StructureFileRecord.objects.count()
        # logger.info("RECORD %s", structure_file_record_count)
        # #self.assertEqual(structure_file_record_count, 201)
        #
        # dataset_count = Dataset.objects.count()
        # logger.info("DATASETS %s", dataset_count)
        #
        # release_count = Release.objects.count()
        # logger.info("RELEASES %s", release_count)
        #
        # for t in NameType.objects.all():
        #     logger.info("NAME TYPE %s : %s :", t.id, t.parent)
        #
        # for r in StructureFileRecord.objects.all():
        #     logger.info("NAME TYPE %s : %s :", r.id, r)

        #for n in Name.objects.all():
        #   logger.info("NAME %s ", n)

        #self.assertEqual(release_count, 201)



    # @skip
    # def test_json_field(self):
    #     for p in StructureFileCollectionPreprocessor.objects.all():
    #         logger.info("PREPROCESSOR %s %s" % (p, p.params))
    #         d = json.loads(p.params)
    #         logger.info("D %s" % d["test"])



    def mapper_test(self, structure_file_id):
        try:
            structure_file = StructureFile.objects.get(id=structure_file_id)
            records: QuerySet = StructureFileRecord.objects \
                .select_related('structure') \
                .values('structure__id') \
                .filter(
                    structure_file=structure_file,
                    structure__compound__isnull=True,
                    structure__blocked__isnull=True,
                ).exclude(
                    structure__hashisy_key=SpecialCactvsHash.ZERO.hashisy
                ).exclude(
                    structure__hashisy_key=SpecialCactvsHash.MAGIC.hashisy
                ).order_by('structure__id')
        except Exception as e:
            logger.error("structure file and count not available")
            raise Exception(e)
        count = len(records)
        chunk_size = StructureRegistry.CHUNK_SIZE
        chunk_number = math.ceil(count / chunk_size)
        #chunks = range(0, chunk_number)

        chunks = [records[i:i + min(chunk_size, count)] for i in range(0, count, chunk_size)]
        return chunks


        #callback = subtask(callback)
        #return group(callback.clone([structure_file_id, chunk, chunk_size]) for chunk in chunks)()


