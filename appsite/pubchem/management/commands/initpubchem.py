import csv
import logging
import re

from typing import Dict, Tuple

from django.core.management.base import BaseCommand

from pubchem.management.data.standardized import organizations as standardized_organizations
from pubchem.management.data.standardized import organization_type_strings as standardized_organization_type_strings

from resolver.models import Organization, Publisher

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'loading PubChem data sources'

    def handle(self, *args, **options):
        logger.info("init PubChem data sources")
        _initpubchemsources()


def create_organization(name, category, abbreviation=None, href=None, added=None, updated=None) -> Tuple[Organization, bool]:
    print(name, category)
    organization_obj, created = Organization.objects.get_or_create(
        name=name, abbreviation=abbreviation
    )
    if created:
        organization_obj.abbreviation = abbreviation
        organization_obj.category = category
        organization_obj.href = href
        if added:
            organization_obj.added = added
        if updated:
            organization_obj.updated = updated
        organization_obj.save()
    print(organization_obj, created)
    return organization_obj, created


def create_acronym(phrase):
    acronym = ""
    res_list = re.findall('[A-Z][^A-Z]*', phrase)
    for res in res_list:
        words = res.split()
        for word in words:
            acronym += word[0].upper()
    if len(acronym) == 1:
        acronym = phrase.upper()
    return acronym

def read(fname) -> Dict:
    with open(fname, mode='r', encoding="latin1") as infile:
        reader = csv.DictReader(infile)
        sources = []
        for row in reader:
            sources.append(row)

        return {source['Source Name']: source for source in sources}


def _initpubchemsources():
    sources = read('/filestore/pubchem/data-sources.csv')
    i = 0
    for column0, row in sources.items():

        i += 1
        #if i != 194: continue

        row_organization = row['Organization']
        if row['Organization'].strip() == '':
            row_organization = row['Source Name']

        standard = None
        for item in standardized_organizations:
            if row_organization in item.variation_dict().keys():
                standard = item.variation_dict()[row_organization]
        if standard:
            organization, organization_created = create_organization(**standard)
        else:
            for pattern in standardized_organization_type_strings:
                for old, new in pattern.variation_dict().items():
                    if row_organization.endswith(old):
                        row_organization = re.sub(old + '$', new, row_organization)
                        break
            organization, organization_created = create_organization(name=row_organization, category='none')

        print(row['Organization'], " : ", row['Source Name'])
        print("%s | ORGANIZATION %s" % (i, organization))


        publisher1_name = row['Source Name']
        publisher2_name = row['Contact Full Name']

        #organization, publisher1_created = Organization.objects.get_or_create(name=organization_name)

        publisher1, publisher1_created = Publisher.objects.get_or_create(name=publisher1_name, category='entity')
        if publisher1_created:
            publisher1.organizations.add(organization)

        publisher2, publisher2_created = Publisher.objects.get_or_create(name=publisher2_name, category='person')
        if publisher2_created:
            publisher2.parent = publisher1
            publisher2.organizations.add(organization)
            publisher2.save()

        #print("%s" % row.keys())

# import csv
# import datetime
# import json
# import logging
# import re
#
# import requests
# from django.core.management.base import BaseCommand
# from pycactvs import Ens
#
# from datetime import datetime
#
# from etl.models import StructureFileCollection, StructureFileCollectionPreprocessor, StructureFileField
# from resolver.models import Organization, Publisher, Structure, Name, NameType, StructureNameAssociation, \
#     ContextTag, Dataset, Release, InChIType, NameAffinityClass, ResponseType
#
# logger = logging.getLogger('cirx')
#
#
# class Command(BaseCommand):
#     help = 'init pubchem'
#
#     def handle(self, *args, **options):
#         logger.info("pubchem")
#         _loader()
#
# def _loader():
#    init_pubchem()
#
# def create_organization(name, abbreviation, category, href, date) -> Organization:
#     organization, created = Organization.objects.get_or_create(
#         name=name,
#     )
#     if created:
#         organization.abbreviation = abbreviation
#         organization.category = category
#         organization.href = href
#         organization.added = date
#         organization.updated = date
#         organization.save()
#     return organization
#
# def create_acronym(phrase):
#     acronym = ""
#     # words = phrase.split()
#     res_list = re.findall('[A-Z][^A-Z]*', phrase)
#     for res in res_list:
#         words = res.split()
#         for word in words:
#             acronym += word[0].upper()
#     if len(acronym) == 1:
#         acronym = phrase.upper()
#     return acronym
#
#
# def init_pubchem():
#
#     infile = "/filestore/pubchem/data-sources.csv"
#
#     source_categories = set()
#
#     pubchem_categories = {
#         'Journal Publishers': ['publishing'],
#         'NIH Initiatives': ['government'],
#         'Governmental Organizations': ['government'],
#         'Research and Development': ['research'],
#         'Curation Efforts': ['other'],
#         'Subscription Services': ['other'],
#         'siRNA Reagent Vendors': ['other'],
#         'Legacy Depositors': ['other'],
#         'Chemical Vendors': ['vendor']
#     }
#
#     with open(infile) as f:
#         counter = 0
#         reader = csv.reader(f, delimiter=',', quotechar='"')
#         for row in reader:
#             counter += 1
#             if len(row) != 23:
#                 raise ValueError("invalid row length")
#             if counter == 1:
#                 continue
#             source_name, live_count, on_hold_count, live_bioassay_count, live_biossay_count_on_hold_count, linked_substance_count, annotation_count, classification_count, source_category, source_url, source_id, organization, contact_name, contact_address, contact_city, contact_state, contact_postcode, contact_country, last_updated, description, license_url, license_note, pathway_count = row
#             print(last_updated)
#
#             # print(source_id, "\t", source_name, "\t", source_catetory)
#             print(source_id, "\t", source_name, "\t", contact_name)
#             # print(source_name, " : ", create_acronym(source_name))
#             for c in source_category.split(","):
#                 if c: source_categories.add(c.strip())
#
#             d = datetime.strptime(last_updated, "%Y/%m/%d")
#             k = source_category.split(",")
#             print(k)
#             if len(k) > 1:
#                 c = pubchem_categories[source_category.split(",")[0]]
#             else:
#                 c = 'none'
#
#
#             create_organization(
#                 source_name,
#                 create_acronym(source_name)[0:32],
#                 c,
#                 source_id,
#                 d
#             )
#
#
#     #print(source_categories)
#
