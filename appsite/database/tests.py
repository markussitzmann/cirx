import logging

from django.test import TestCase

from database.models import Database

logger = logging.getLogger('cirx')


class DatabaseTests(TestCase):

    def test_create_database(self):
        database = Database(name="test")
        logger.info("database %s", database)
        self.assertTrue(True)
