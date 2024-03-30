# import csv
# import logging
# from typing import Dict, List
#
# from django.core.management.base import BaseCommand
#
# from resolver.models import Organization, Publisher
#
# logger = logging.getLogger('cirx')
#
#
# class Command(BaseCommand):
#     help = 'loading PubChem data sources'
#
#     def handle(self, *args, **options):
#         logger.info("init PubChem data sources")
#         _initpubchemsources()
#
#
# def read(fname) -> Dict:
#     with open(fname, mode='r', encoding="latin1") as infile:
#         reader = csv.DictReader(infile)
#         sources = []
#         for row in reader:
#             sources.append(row)
#
#         return {source['Source Name']: source for source in sources}
#
#
# def _initpubchemsources():
#
#     sources = read('./structure/management/data/pubchem/sources.csv')
#     for k, v in sources.items():
#         #print(k)
#         #print(v.keys())
#         print("----------")
#         print("%s %s %s" % (v['Source Name'], v['Source URL'], v['Description']))
#         print("%s" % (v['Source Category']))
#         print("-->%s" % (v['Organization']))
#         print("-->%s" % (v['Contact Full Name']))
#
#         organization, created = Organization.objects.get_or_create(name=v['Organization'])
#
#         publisher1, created = Publisher.objects.get_or_create(name=v['Source Name'], category='entity')
#         if created:
#             publisher1.organizations.add(organization)
#
#         publisher2, created = Publisher.objects.get_or_create(name=v['Contact Full Name'], category='person')
#         if created:
#             publisher2.parent = publisher1
#             publisher2.organizations.add(organization)
#             publisher2.save()
#
#     print("%s" % v.keys())
