import logging

from django.test import TestCase
from parameterized import parameterized

from resolver.models import InChIManager, InChI

logger = logging.getLogger('cirx')

#FIXTURES = ['structure.json', 'database.json']


class ResolverModelTests(TestCase):
    #fixtures = FIXTURES

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @parameterized.expand([
        ['QTXVAVXCBMYBJW-UHFFFAOYSA-N', 'QTXVAVXCBMYBJW-UHFFFAOYSA-N', (1, True)],
        ['QTXVAVXCBMYBJW-UHFFFAOYSA-N', 'BSYNRYMUTXBXSQ-UHFFFAOYSA-N', (2, False)],
    ])

    def test_inchi(self, string1, string2, expectations):
        logger.info("------------- Test InChI models (%s) -------------" % string1)
        expected_count, expected_status = expectations

        inchi1: InChI = InChI.objects.create_inchi(key=string1)
        logger.info("I1 >>> %s %s %s" % (inchi1, inchi1.pk, inchi1._state))
        inchi1.save()

        inchi2: InChI = InChI.objects.create_inchi(key=string2)
        logger.info("I2 >>> %s %s %s" % (inchi2, inchi2.pk, inchi2._state))
        fetched, created = InChI.objects.get_or_create(id=inchi2.id)

        count = InChI.objects.count()

        self.assertEqual(count, expected_count)
        if expected_status:
            self.assertEqual(inchi1, fetched)
        else:
            self.assertNotEqual(inchi1, fetched)


