import logging
import os

from django.core.management.base import BaseCommand, CommandError

from custom.cactvs import CactvsHash, CactvsMinimol
from structure.models import Structure2, Name, NameType, StructureNames, ResponseType, StructureInChIs
from resolver.models import InChI, Organization, Publisher

from pycactvs import Ens

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'loading some initial data'

    def handle(self, *args, **options):
        logger.info("loader")
        _loader()


def _loader():
    init_response_type_data()
    init_name_type_data()
    init_organization_and_publisher_data()

    names = ['ethanol', 'benzene', 'warfarin', 'guanine', 'tylenol', 'caffeine']
    name_type_obj = NameType.objects.get(id=7)

    for name in names:
        ens = Ens(name)
        logger.info("tuples: %s", name)
        name_obj, created = Name.objects.get_or_create(name=name)

        structure_obj, structure_created = Structure2.objects.get_or_create_from_ens(ens)
        logger.info("Structure: %s %s" % (structure_obj, structure_created))

        structure_name_obj, name_created = StructureNames.objects.get_or_create(
            name=name_obj,
            structure=structure_obj,
            name_type=name_type_obj
        )

        inchi_obj, inchi_created = InChI.objects.get_or_create(ens.get('E_STDINCHI'))
        logger.info("InChI: %s %s" % (inchi_obj, inchi_created))

        structure_inchi_obj, structure_inchi_created = StructureInChIs.objects.get_or_create(
            structure=structure_obj,
            inchi=inchi_obj
        )



        # inchikey = ens.get('E_STDINCHIKEY')
        # inchi = ens.get('E_STDINCHI')
        #
        # logger.info("1 >>> %s | %s" % (inchikey, inchi))
        #
        # io = InChI.objects.get_or_create(key=inchikey)
        # logger.info("2 >>> %s | %s" % (io, io))

        #io.save()


def init_response_type_data():
    with open('./structure/management/raw-data/response-type.txt') as f:
        lines = f.readlines()
        response_type_dict = {}
        for line in lines:
            splitted = [e.strip() for e in line.split('|')]
            cleaned = [None if e == 'NULL' else e for e in splitted][1:-1]
            id, parent_type_id, url, method, parameter, base_mime_type = cleaned
            if parent_type_id:
                parent_type = response_type_dict[parent_type_id]
            else:
                parent_type = None
            response_type = ResponseType(
                id=id,
                parent_type=parent_type,
                url=url,
                method=method,
                parameter=parameter,
                base_mime_type=base_mime_type
            )
            response_type.save()
            response_type_dict[id] = response_type


def init_name_type_data():
    name_types = [
        'PUBCHEM_IUPAC_NAME',
        'PUBCHEM_IUPAC_OPENEYE_NAME',
        'PUBCHEM_IUPAC_CAS_NAME',
        'PUBCHEM_IUPAC_TRADITIONAL_NAME',
        'PUBCHEM_IUPAC_SYSTEMATIC_NAME',
        'PUBCHEM_GENERIC_REGISTRY_NAME',
        'PUBCHEM_SUBSTANCE_SYNONYM',
    ]

    for name_type in name_types:
        NameType.objects.get_or_create(string=name_type)


def init_organization_and_publisher_data():

    nih, created = Organization.objects.get_or_create(
        name="U.S. National Institutes of Health",
        abbreviation="NIH",
        category="government",
        href="https://www.nih.gov"
    )

    nci, created = Organization.objects.get_or_create(
        parent=nih,
        name="U.S. National Cancer Institute",
        abbreviation="NCI",
        category="government",
        href="https://www.cancer.gov"
    )

    nlm, created = Organization.objects.get_or_create(
        parent=nih,
        name="U.S. National Library of Medicine",
        abbreviation="NLM",
        category="government",
        href="https://www.nlm.nih.gov"
    )

    ncbi, created = Organization.objects.get_or_create(
        parent=nih,
        name="U.S. National Center for Biotechnology Information",
        abbreviation="NCBI",
        category="government",
        href="https://www.ncbi.nlm.nih.gov"
    )

    fiz, created = Organization.objects.get_or_create(
        name="FIZ Karlsruhe – Leibniz-Institut für Informationsinfrastruktur",
        abbreviation="FIZ Karlsruhe",
        category="public",
        href="https://www.fiz-karlsruhe.de"
    )

    sito, created = Organization.objects.get_or_create(
        name="Markus Sitzmann Cheminformatics & IT Consulting",
        abbreviation="SCIC",
        category="other",
        href=""
    )

    ncicadd, created = Publisher.objects.get_or_create(
        name="NCI Computer-Aided Drug Design (CADD) Group",
        category="group",
        href="https://cactus.nci.nih.gov",
        address="Frederick, MD 21702-1201, USA",
    )
    ncicadd.organizations.add(nci, nih)

    mn1, created = Publisher.objects.get_or_create(
        parent=ncicadd,
        name="Marc Nicklaus",
        category="person",
        email="mn1ahelix@gmail.com",
        address="Frederick, MD 21702-1201, USA",
        href="https://ccr.cancer.gov/staff-directory/marc-c-nicklaus",
        orcid="https://orcid.org/0000-0002-4775-7030"
    )
    mn1.organizations.add(nci, nih)

    sitp, created = Publisher.objects.get_or_create(
        name="Markus Sitzmann",
        category="person",
        email="markus.sitzmann@gmail.com",
        orcid="https://orcid.org/0000-0001-5346-1298"
    )
    sitp.organizations.add(sito, fiz)