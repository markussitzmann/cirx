import hashlib
import logging

import psycopg2
from django.core.exceptions import FieldError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase

from .models import InChI, Name


class NameTest(TestCase):

    def setUp(self):
        pass

    def test_save_name(self):
        name = "ethanol"
        name_obj = Name.objects.create(name=name)
        name_obj.save()

        first_name_obj = Name.objects.first()
        self.assertTrue(hashlib.md5(name.encode("UTF-8")).hexdigest(), first_name_obj)

    def test_save_repeat_name(self):
        name = "ethanol"
        name_obj = Name.objects.create(name=name)
        name_obj.save()

        try:
            with transaction.atomic():
                name_obj_conflict = Name.objects.create(name=name)
                name_obj_conflict.save()
            self.fail("saving a duplicate succeeded but should not")
        except Exception as e:
           pass

        first_name_obj = Name.objects.get(id=1)
        self.assertTrue(hashlib.md5(name.encode("UTF-8")).hexdigest(), first_name_obj)


class IdentifierTest(TestCase):

    def setUp(self):
        pass

    def test_save_and_retrieve(self):
        inchi = InChI.create(key="LFQSCWFLJHTTHZ-UHFFFAOYSA-N", string="InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3")
        inchi.save()

        i = InChI.objects.first()
        print(i)
        print(i.uid)
        print(i.string)
        self.assertTrue(i.version == 1)
        self.assertTrue(i.is_standard is True)
        self.assertTrue(str(i.uid) == 'bd69d81f-f929-510f-8206-4edb124c187f')
        self.assertTrue(str(i.string) == 'InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3')
        self.assertTrue(str(i.key) == 'LFQSCWFLJHTTHZ-UHFFFAOYSA-N')
        self.assertTrue(str(i.block1) == 'LFQSCWFLJHTTHZ')
        self.assertTrue(str(i.block2) == 'UHFFFAOYSA')
        self.assertTrue(str(i.block3) == 'N')


    # def test_only_inchi(self):
    #     inchi = InChI.create(string="InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3")
    #     inchi.save()
    #
    #     i = InChI.objects.first()
    #
    #     self.assertTrue(i.version == 1)
    #     self.assertTrue(str(i.string) == 'InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3')
    #     self.assertTrue(str(i.key) == 'LFQSCWFLJHTTHZ-UHFFFAOYSA-N')
    #     self.assertTrue(str(i.block1) == 'LFQSCWFLJHTTHZ')
    #     self.assertTrue(str(i.block2) == 'UHFFFAOYSA')
    #     self.assertTrue(str(i.block3) == 'N')


    def test_only_inchikey(self):
        inchi = InChI.create(key="LFQSCWFLJHTTHZ-UHFFFAOYSA-N")
        inchi.save()

        i = InChI.objects.first()
        self.assertTrue(i.version == 1)
        self.assertTrue(i.string is None)
        self.assertTrue(str(i.key) == 'LFQSCWFLJHTTHZ-UHFFFAOYSA-N')
        self.assertTrue(str(i.block1) == 'LFQSCWFLJHTTHZ')
        self.assertTrue(str(i.block2) == 'UHFFFAOYSA')
        self.assertTrue(str(i.block3) == 'N')


    def test_save_multiple(self):

        inchi = InChI.create(key="LFQSCWFLJHTTHZ-UHFFFAOYSA-N")
        inchi.save()

        with self.assertRaises(IntegrityError):
            inchi2 = InChI.create(key="LFQSCWFLJHTTHZ-UHFFFAOYSA-N")
            inchi2.save()

        inchi3 = InChI.create(string='InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3')
        inchi3.save()

        self.assertTrue(InChI.objects.count(), 1)


    # def test5(self):
    #     with self.assertRaises(FieldError):
    #         InChI.create(key="LFQSCWFLJHTTZZ-UHFFFAOYSA-N", string="InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3")
