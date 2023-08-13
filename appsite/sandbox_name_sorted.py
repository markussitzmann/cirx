import logging
import os

from django.db.models import Prefetch
from django.db.models.functions import Coalesce

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsite.settings")

from django.conf import settings
import django

django.setup()

from django.db import connection, reset_queries

from structure.string_resolver import ChemicalStructure
from resolver.models import *

settings.DEBUG = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cirx")

reset_queries()

compounds = [7278,]
names = ["Aspirin", ]

warfarin_smiles = [
    'C1=CC=CC2=C1C(=O)C(=C(O2)O)C(C3=CC=CC=C3)C=C(O)C',
    'C1=CC=CC3=C1C(=C(C(C2=CC=CC=C2)CC(=O)C)C(O3)=O)O',
    'C1=CC=CC3=C1C(=O)C(C(C2=CC=CC=C2)CC(O)=C)C(O3)=O',
    'C1=CC=CC2=C1C(=O)C(=C(O2)O)C(C3=CC=CC=C3)CC(=O)C',
    'C1=CC=CC3=C1C(=C(C(C2=CC=CC=C2)C=C(O)C)C(O3)=O)O',
    'C1=CC=CC3=C1C(=C(C(C2=CC=CC=C2)CC(O)=C)C(O3)=O)O',
    'C1=CC=CC3=C1C(=O)C(C(C2=CC=CC=C2)C=C(O)C)C(O3)=O',
    'C1=CC=CC3=C1C(=O)C(C(C2=CC=CC=C2)CC(=O)C)C(O3)=O',
    'C1=CC=CC2=C1C(=O)C(=C(O2)O)C(C3=CC=CC=C3)CC(O)=C'
]

exact = NameAffinityClass.objects.filter(title="exact").first()
narrow = NameAffinityClass.objects.filter(title="narrow").first()
broad = NameAffinityClass.objects.filter(title="broad").first()

for smiles in warfarin_smiles:
    chemical_structure = ChemicalStructure(ens=Ens(smiles))
    if chemical_structure.structure:
        #compounds = [c.ficus_parent_id for c in chemical_structure.structure.parents.ficus_parent.compound]
        #compounds = [compound, ]
        compounds = [chemical_structure.structure.parents.ficus_parent.compound]
        logger.info("-------- {} --------".format(compounds))

        name_associations = StructureNameAssociation.with_related_objects.by_compound(
            compounds=compounds,
            affinity_classes=[exact, narrow, ]
        ).filter(name_type__parent__title='NAME').all()

        associations = name_associations.order_by('affinity_class__rank', 'name__name', '-name_type__parent').all()
        logger.info("--> {}".format(len(associations)))
        for a in associations:
            logger.info("R {} P {} T {} AF {} NAME {}"
                        .format(a.affinity_class.rank, a.name_type.id, a.name_type.title, a.affinity_class.title, a.name.name))

#pubchem_substance_synonym = NameType.objects.filter(title="PUBCHEM_SUBSTANCE_SYNONYM").first()


# name_associations = StructureNameAssociation.with_related_objects.by_compound(
#   compounds=compounds,
#   affinity_classes=[exact, ]
# ).filter(name_type__parent__title='NAME').all()
#
# # for a in name_associations.all():
# #     logger.info("COMPOUND %s %s %s -> %s : %s" % (
# #         a.name,
# #         a.affinity_class,
# #         a.name_type,
# #         a.structure,
# #         a.structure.compound.id
# #     ))
#
# # compound_associations = StructureNameAssociation.with_related_objects.by_name(
# #    names=names,
# #    name_types=[pubchem_substance_synonym, ],
# #    affinity_classes=affinity_classes
# # )
#
# for a in name_associations.order_by('affinity_class__rank', 'name__name', '-name_type__parent').all():
#     logger.info("R {} P {} T {} AF {} NAME {}".format(a.affinity_class.rank, a.name_type.id, a.name_type.title, a.affinity_class.title, a.name.name))
#

logger.info("-----------")
logger.info("COUNT %s", len(connection.queries))
logger.info("-----------")

