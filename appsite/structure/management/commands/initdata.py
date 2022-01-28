import logging
import os

from django.core.management.base import BaseCommand, CommandError

from custom.cactvs import CactvsHash, CactvsMinimol
from structure.models import Structure2, Name, NameType, StructureNames, ResponseType, StructureInChIs
from resolver.models import InChI, Organization

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
    #init_organization_data()

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

        inchi_obj, inchi_created = InChI.objects.get_or_create_from_ens(ens)
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


def init_organization_data():

    nih = Organization.objects.create_organization(
        name="National Institutes of Health",
        abbreviation="NIH",
        category="government",
        href="https://www.nih.gov"
    )

    nci = Organization.objects.create_organization(
        parent=nih,
        name="National Cancer Institute",
        abbreviation="NCI",
        category="government",
        href="https://www.cancer.gov"
    )
    Organization.objects.get_or_create(nci)

