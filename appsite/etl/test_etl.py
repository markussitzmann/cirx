import logging

from celery import group
from django.test import TestCase, SimpleTestCase
from etl.tasks import count_box_task

logger = logging.getLogger('cirx')



class EtlTests(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sandbox(self):
        logger.info("----- start ----")

        #task = group(count_box_task.s(i) for i in range(10))

        task = count_box_task.s(1)
        result = task.delay()

        logger.info("----- submitted ----")

        # logger.info(result)
        # logger.info(result.successful())
        # logger.info(result.ready())
        # logger.info(result.waiting())


        logger.info(result.status)

        logger.info("----- end ----")









