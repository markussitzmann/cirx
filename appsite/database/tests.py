import logging

from django.test import TestCase

from .models import Database

logger = logging.getLogger('cirx')


class DatabaseTests(TestCase):

    def createDatabase(self):
        database = Database(name="test")
        logger.info("database %s", database)
        self.assertTrue(True)
