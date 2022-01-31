import logging

from django.test import TestCase, SimpleTestCase

from pycactvs import Ens

from custom.cactvs import CactvsHash
from external_resolver import ChemicalStructure

logger = logging.getLogger('cirx')


class CactvsHashTests(SimpleTestCase):

    def test_cactvs_hash(self):
        self.assertEqual(CactvsHash("F").unsigned_int(), 15)
        self.assertEqual(CactvsHash("0F").unsigned_int(), 15)
        self.assertEqual(CactvsHash(0xf).unsigned_int(), 15)
        self.assertEqual(CactvsHash(0xf).padded(), "000000000000000F")
        self.assertEqual(CactvsHash("0F").padded(), "000000000000000F")
        self.assertEqual(CactvsHash("F").padded(), "000000000000000F")
        self.assertEqual(CactvsHash(0).padded(), "0000000000000000")

        self.assertEqual(CactvsHash("F").signed_int(), -9223372036854775793)
        self.assertEqual(CactvsHash("FFFFFFFFFFFFFFFF").signed_int(), 9223372036854775807)
        self.assertEqual(CactvsHash(0).signed_int(), -9223372036854775808)

    def test_too_big(self):
        self.assertRaises(ValueError, CactvsHash, "FFFFFFFFFFFFFFFFFFF")

    def test_from_ens(self):
        cactvs_hash = CactvsHash(Ens("CCO"))
        logger.info("hash %s", cactvs_hash)
        self.assertEqual(cactvs_hash.padded(), "E174572A915E4471")
