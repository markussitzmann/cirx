import logging
from unittest import skip

from django.test import TestCase
from parameterized import parameterized

from etl.models import StructureFileRecord
from resolver.models import InChIManager, InChI, Structure, StructureInChIAssociation, Name, StructureNameAssociation

from identifier import InChIKey, InChIString

logger = logging.getLogger('cirx')

FIXTURES = ['mini.json']


class ResolverModelTests(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        pass

    def tearDown(self):
        inchis = InChI.objects.count()
        logger.info("InChI count %s" % inchis)

        inchi_associations = StructureInChIAssociation.objects.count()
        logger.info("InChI association %s" % inchi_associations)

        names = Name.objects.count()
        logger.info("Names %s" % names)

        name_associations = StructureNameAssociation.objects.count()
        logger.info("Name association %s" % name_associations)

    def test_structure(self):
        logging.info("---------")

        structure: Structure = Structure.objects.get(id=100)
        logger.info("Structure %s", structure)

        ficus_parent: Structure = structure.parents.ficus_parent
        logger.info("Structure %s", ficus_parent)


        i = structure.inchis.filter(inchitype='standard').get()

        logger.info("InChI %s %s" % (i, i.inchi.key))

        filtered_structure = Structure.objects\
            .filter(inchis__inchitype='standard', inchis__inchi__key=i.inchi.key).get()

        logger.info("Structure %s %s" % (filtered_structure, filtered_structure.smiles))

        names = filtered_structure.names.all()

        logger.info("Name %s" % (names,))

        record: StructureFileRecord = structure.structure_file_records.first()

        logger.info("Records %s" % (record,))

        names = record.names.all()

        for name in names:
            logger.info("Name %s %s" % (name.id, name))

        for a in record.structurefilerecordnameassociation_set.all():
            logger.info("A %s" % (a, ))

    # @parameterized.expand([
    #     ['LFQSCWFLJHTTHZ-UHFFFAOYSA-N', 'InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3', (1, True)],
    #     #[None, 'InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3', (1, True)],
    #     #['BSYNRYMUTXBXSQ-UHFFFAOYSA-N', (2, False)],
    # ])
    # def test_inchi(self, key, string, expectations):
    #     logger.info("------------- Test InChI models (%s) -------------" % key)
    #     expected_count, expected_status = expectations
    #
    #     if key:
    #         inchistring = InChIString(string=string, key=InChIKey(key))
    #     else:
    #         inchistring = InChIString(string=string)
    #
    #     logger.info("S >>> %s" % inchistring.element)
    #     logger.info("S >>> %s" % inchistring.model_dict)
    #
    #     inchi_1 = InChI.objects.get_or_create(string)
    #     inchi_2 = InChI.objects.get_or_create(string=string, key=InChIKey(key))
    #     inchi_3 = InChI.objects.get_or_create(key=InChIKey(key))
    #
    #
    #     logger.info("IS >>>> %s : %s", inchi_1, inchi_2, inchi_3)
    #
    #
    #
    #
    #
    #     requested = InChI.objects.filter(block1="LFQSCWFLJHTTHZ").all()
    #     logger.info("R >>>> %s", requested)
    #
    #
    #     # inchi2, created = InChI.objects.get_or_create(key=key)
    #     # logger.info("2 >>> %s %s" % (inchi2.id, created))
    #
    #     #model = InChI(**inchistring.model_dict)
    #     #model.save()
    #     #logger.info("M >>> %s" % model)
    #
    #
    # @parameterized.expand([
    #     ['QTXVAVXCBMYBJW-UHFFFAOYSA-N', 'QTXVAVXCBMYBJW-UHFFFAOYSA-N', (1, True)],
    #     ['QTXVAVXCBMYBJW-UHFFFAOYSA-N', 'BSYNRYMUTXBXSQ-UHFFFAOYSA-N', (2, False)],
    # ])
    # @skip
    # def test_inchi_model(self, string1, string2, expectations):
    #     logger.info("------------- Test InChI models (%s) -------------" % string1)
    #     expected_count, expected_status = expectations
    #
    #     inchi1: InChI = InChI.objects.create_inchi(key=string1)
    #     logger.info("I1 >>> %s %s %s" % (inchi1, inchi1.pk, inchi1._state))
    #     inchi1.save()
    #
    #     inchi2: InChI = InChI.objects.create_inchi(key=string2)
    #     logger.info("I2 >>> %s %s %s" % (inchi2, inchi2.pk, inchi2._state))
    #     fetched, created = InChI.objects.get_or_create(id=inchi2.id)
    #
    #     count = InChI.objects.count()
    #
    #     self.assertEqual(count, expected_count)
    #     if expected_status:
    #         self.assertEqual(inchi1, fetched)
    #     else:
    #         self.assertNotEqual(inchi1, fetched)



