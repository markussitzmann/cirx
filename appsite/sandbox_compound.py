import logging
import os

from django.db.models import Q
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsite.settings")

from django.conf import settings
import django

django.setup()

from neon.views import ParentData


from django.db import connection, reset_queries
from resolver.models import *
from etl.registration import StructureRegistry

from ncicadd.identifier import Identifier

settings.DEBUG = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cirx")

reset_queries()

compounds = Compound.with_related_objects.by_compound_ids([20008, 20009]).all()

for compound in compounds:
    logger.info("C: %s" % compound)

    parents = {}
    for parent_type in StructureRegistry.NCICADD_TYPES:
        parents[parent_type.key] = ParentData(
            structure=getattr(compound.structure.parents, parent_type.attr),
            identifier=Identifier(hashcode=p.hashisy_key.padded, identifier_type=parent_type.public_string) if (p := getattr(compound.structure.parents, parent_type.attr)) else None,
            children_count=getattr(compound, parent_type.key + '_children_count')
        )

    logger.info("--> %s" % parents)

    for k, v in parents.items():
        if v.structure:
            logger.info("I %s %s" % (k, v.structure.compound))
        else:
            logger.info("I %s" % (k, ))




    #for parent_type, parent in parents.items():
    #    logger.info("P %s : %s : %s" % (
    #        parent_type.attr,
    #        parent.hashisy_key.padded if parent else None,
    #        Identifier(hashcode=parent.hashisy_key.padded, identifier_type=parent_type.public_string) if parent else None
    #    )
    #)

    #ficts_compound = compound.structure.parents.ficts_parent
    #ficus_compound = compound.structure.parents.ficus_parent
    #uuuuu_compound = compound.structure.parents.uuuuu_parent


    #logger.info("FICTS: %s" % ficts_compound.hashisy_key.padded if ficts_compound else None)
    #logger.info("FICuS: %s" % ficus_compound.hashisy_key.padded if ficus_compound else None)
    #logger.info("uuuuu: %s" % uuuuu_compound.hashisy_key.padded if uuuuu_compound else None)




# #compounds = Compound.objects.filter_by_names(["NSC-123", ]).all()
# #compounds = Compound.objects.annotated()[0:100]
# query = Compound.objects.annotated().filter(id=20008).filter(Q(annotated_inchi_is_standard=True) | Q(annotated_inchi__isnull=True))
#
# compounds = query.all()
#
# compound: Compound
# for compound in compounds:
#     logger.info("C %s %s %s" % (compound, compound.annotated_name, compound.ficts_children_count))
#     #logger.info("C %s %s" % (compound.get_next_by_added(), compound.get_previous_by_added()))
#     logger.info("C %s" % (compound.structure.parents, ))
#     inchi_association: StructureInChIAssociation
#     #for inchi_association in compound.structure.inchis.all():
#     logger.info("I %s %s %s" % (compound.annotated_inchitype, compound.annotated_inchikey, compound.annotated_inchi))
#     logger.info("N %s" % (compound.annotated_name))
#




# query = Compound.objects\
#     .prefetch_related(
#         'structure__names'
#     ).select_related(
#         'structure',
#         'structure__parents',
#         'structure__parents__ficts_parent',
#         'structure__parents__ficus_parent',
#         'structure__parents__uuuuu_parent'
#     ).annotate(
#         ficts_parent_structure=F('structure__parents__ficts_parent'),
#         annotated_name=F('structure__names__name__name')
#     )

#voted_choices = Choice.objects.filter(votes__gt=0)
#>>> voted_choices
#<QuerySet [<Choice: The sky>]>
#>>> prefetch = Prefetch('choice_set', queryset=voted_choices)
#>>> Question.objects.prefetch_related(prefetch).get().choice_set.all()
#<QuerySet [<Choice: The sky>]>


#structure_names = StructureNameAssociation.objects.select_related('name')
#prefetch = Prefetch('structure__names__name', queryset=structure_names)


# compounds = query \
#     .select_related('structure')\
#     .prefetch_related(
#         'structure__names__name',
#         'structure__ficts_children__structure',
#         'structure__ficus_children__structure',
#         'structure__uuuuu_children__structure',
#         'structure__ficts_children__structure__structure_file_records',
#         'structure__ficus_children__structure__structure_file_records',
#         'structure__uuuuu_children__structure__structure_file_records',
#         'structure__ficts_children__structure__structure_file_records__records',
#         'structure__ficus_children__structure__structure_file_records__records',
#         'structure__uuuuu_children__structure__structure_file_records__records',
#         'structure__ficts_children__structure__structure_file_records__records__release',
#         'structure__ficus_children__structure__structure_file_records__records__release',
#         'structure__uuuuu_children__structure__structure_file_records__records__release',
#     ).annotate(
#         ficts_children_count=Count('structure__ficts_children'),
#         ficus_children_count=Count('structure__ficus_children'),
#         uuuuu_children_count=Count('structure__uuuuu_children'),
#     )
#
#
#
# # response = compounds.filter(structure__parents__ficts_parent__isnull=False) \
# #     .exclude(structure__parents__ficts_parent=F('structure__parents__ficus_parent'))\
# #     .all()[0:100]
#
# response = compounds\
#     .filter(structure__parents__ficts_parent__isnull=False)\
#     .filter(ficts_children_count__gte=3)\
#     .exclude(structure__parents__ficts_parent=F('structure__parents__ficus_parent'))\
#     .all()[0:5]
#
# c: Compound
# for c in response:
#     logger.info("--------")
#     logger.info("C %s" % (c,))
#     logger.info("C %s" % (c.structure,))
#     logger.info("C %s" % (c.structure.parents.ficts_parent))
#     logger.info("C %s" % (c.structure.parents.ficus_parent))
#     for s in c.structure.ficts_children.all():
#         logger.info("S %s %s" % (s, s.structure.minimol.ens.get("E_SMILES")))
#         r: StructureFileRecord
#         for fr in s.structure.structure_file_records.all():
#             logger.info("R %s %s" % (fr, fr.records.all()))
#             for rr in fr.records.all():
#                 logger.info("--> %s %s" % (rr, rr.release))
#     logger.info("F %s" % (c.ficts_parent_structure))
#     for n in c.structure.names.all():
#         logger.info("N %s" % (n.name))
#
#     #for r in c.ficts_records:
#     #    logger.info("--> %s" % r)
#     #for x in c.structure.ficts_children.structure.structure_file_records.all():
#     #    logger.info("X %s" % (x))
#     #logger.info("N %s" % (c.structure.objects.prefetch_related('names').all()))
#
#
#
# #logger.info("Q %s" % query.count())

logger.info("-----------")
logger.info("COUNT %s", len(connection.queries))
logger.info("-----------")


for query in connection.queries:
    logger.info("%s" % query)
