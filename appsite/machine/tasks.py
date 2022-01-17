from pycactvs import Ens

from celery import shared_task


@shared_task
def ficus(structure):
    return Ens(structure).get('E_FICUS_ID')


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)
