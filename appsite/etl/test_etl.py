import logging
from time import sleep

from celery import group
from celery.result import AsyncResult
from django.test import TestCase, SimpleTestCase
from etl.tasks import *

logger = logging.getLogger('cirx')



class EtlTests(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sandbox(self):
        logger.info("----- start ----")


        #task = count_box_task.s(1)
        #result = task.delay()

        task_list = (count_box_task.s(1) | chunk_creator_task.s(chunk_box_task.s()))
        logger.info(task_list)
        result = task_list.delay()

        logger.info("----- submitted ----")

        logger.info(result.status)
        #logger.info(result.children[0].get())
        #logger.info(result.children[1].get())


        sleep(10)
        for k, v in result.collect(intermediate=False):
            logger.info("%s : %s" % (k.successful(), v))

        #print(result.parent.graph)

        #ar: AsyncResult = result.get()
        #logger.info(out)



        logger.info("----- end ----")









