import logging
import os

from django.db.models import Prefetch, Count

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsite.settings")

from django.conf import settings
import django

django.setup()

from django.db import connection, reset_queries
from resolver.models import *
from etl.models import StructureFileRecord


settings.DEBUG = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cirx")

reset_queries()

#compounds = Compound.objects.filter_by_names(["NSC-123", ]).all()
#compounds = Compound.objects.annotated()[0:100]
compounds = [Compound.objects.annotated().filter(id=1252).first(),]

compound: Compound
for compound in compounds:
    logger.info("C %s %s %s" % (compound, compound.annotated_name, compound.ficts_children_count))
    #logger.info("C %s %s" % (compound.get_next_by_added(), compound.get_previous_by_added()))
    logger.info("C %s" % (compound.structure.parents, ))
    inchi_association: StructureInChIAssociation
    #for inchi_association in compound.structure.inchis.all():
    logger.info("I %s %s %s" % (compound.annotated_inchitype, compound.annotated_inchikey, compound.annotated_inchi))





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
