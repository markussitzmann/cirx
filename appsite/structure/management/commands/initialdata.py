import logging
import os

from django.core.management.base import BaseCommand, CommandError

from custom.cactvs import CactvsHash, CactvsMinimol
from structure.models import Structure2, Name, NameType, StructureName, ResponseType

from pycactvs import Ens

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'loading some initial data'

    def handle(self, *args, **options):
        logger.info("loader")
        _loader()


def _loader():
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

    names = ['ethanol', 'benzene', 'warfarin', 'guanine', 'tylenol']
    name_type_obj = NameType.objects.get(id=7)

    for name in names:
        ens = Ens(name)
        logger.info("tuples: %s", name)
        name_obj, created = Name.objects.get_or_create(name=name)
        structure_obj, created = Structure2.objects.get_or_create(hashisy=CactvsHash(ens), minimol=CactvsMinimol(ens))

        structure_name_obj = StructureName(name=name_obj, structure=structure_obj, name_type=name_type_obj)
        structure_name_obj.save()

        #structure_obj.names.add(StructureName(name=name_obj, structure=structure_obj, name_type=name_type_obj))



    #logger.info("tuples: %s", l)

    print(os.getcwd())

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