import csv
import os
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsite.settings")

from django.conf import settings
import django

#django.setup()

from resolver.models import Organization


def create_organization(name, abbreviation, category, href, date) -> Organization:
    organization, created = Organization.objects.get_or_create(
        name=name,
    )
    if created:
        organization.abbreviation = abbreviation
        organization.category = category
        organization.href = href
        organization.added = date
        organization.updated = date
        organization.save()
    return organization


def create_acronym(phrase):
    acronym = ""
    #words = phrase.split()
    res_list = re.findall('[A-Z][^A-Z]*', phrase)
    for res in res_list:
        words = res.split()
        for word in words:
            acronym += word[0].upper()
    if len(acronym) == 1:
        acronym = phrase.upper()
    return acronym


infile = "/filestore/pubchem/data-sources.csv"

source_categories = set()

pubchem_categories = {
    'Journal Publishers': ['publishing'],
    'NIH Initiatives': ['government'],
    'Governmental Organizations': ['government'],
    'Research and Development': ['research'],
    'Curation Efforts': ['other'],
    'Subscription Services': ['other'],
    'siRNA Reagent Vendors': ['other'],
    'Legacy Depositors': ['other'],
    'Chemical Vendors': ['vendor']
}

with open(infile) as f:
    counter = 0
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for row in reader:
        counter += 1
        if len(row) != 23:
            raise ValueError("invalid row length")
        if counter == 1:
            continue
        source_name, live_count, on_hold_count, live_bioassay_count, live_biossay_count_on_hold_count, linked_substance_count, annotation_count, classification_count, source_category, source_url, source_id, organization, contact_name, contact_address, contact_city, contact_state, contact_postcode, contact_country, last_updated, description, license_url, license_note, pathway_count = row
        #print(source_id, "\t", source_name, "\t", source_catetory)
        print(source_id, "\t", source_name, "\t", contact_name)
        #print(source_name, " : ", create_acronym(source_name))
        for c in source_category.split(","):
            if c: source_categories.add(c.strip())

        create_organization(
            source_name,
            create_acronym(source_name),
            pubchem_categories[source_category.split(",")[0]],
            source_id,
            last_updated
        )


    print(counter)

print(source_categories)
