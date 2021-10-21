import logging

from django.core.management.base import BaseCommand, CommandError
from structure.models import Structure

from pycactvs import Ens

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'loading some initial data'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        logger.info("loader")
        _loader()


        # for poll_id in options['poll_ids']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)
        #
        #     poll.opened = False
        #     poll.save()
        #
        #     self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))


def _loader():

    names = ['ethanol', 'benzene', 'warfarin', 'guanine', 'tylenol']
    enslist = [(name, Ens(name),) for name in names]
    tuples = [(name, Structure(hashisy=int(ens.get('E_HASHISY'), 16) - 9223372036854775808, minimol=ens.get('E_MINIMOL'))) for name, ens in enslist]

    l = [structure.save() for name, structure in tuples]


    logger.info("tuples: %s", l)