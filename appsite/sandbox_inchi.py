import logging
import os

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Prefetch
from django.db.models.functions import Coalesce

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsite.settings")

from django.conf import settings
import django
django.setup()

from django.db import connection, reset_queries
from resolver.models import *

settings.DEBUG = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cirx")

reset_queries()

#query = StructureInChIAssociation.objects.select_related('structure', 'structure__compound')\
#   .values('structure__id', count=Count('inchi_id')).filter(structure__compound__id__isnull=True)[:100]

#query = StructureInChIAssociation.objects\
#   .values('inchi_id', 'structure_id').annotate(count=Count('structure'))[:1000]

query = InChI.objects.annotate(Count('structures'))[200000:201000]

logger.info("---------------------------")
for item in query.all():
   logger.info("--- %s %s" % (item, item.structures__count))
   for structure in item.structures.all():
      logger.info(" S %s %s" % (structure.inchitype, structure.structure))

# #names = Name.objects.prefetch_related(
# #    ''
# #)
#
# #structure_ids = [690600, 209505, 686728, 706412]
#
# compounds = range(1,700000)
#
# inchitypes = ['standard', 'xtauto']
#
#
# inchi_associations = StructureInChIAssociation.with_related_objects.by_compounds_and_inchitype(
#    compounds=compounds,
#    #inchitypes=inchitypes
# ).filter(structure_count__gt=1).all()
#
# for a in inchi_associations:
#    logger.info(">> %s %s %s", a, a.inchitype, a.structure_count)
#
# #logger.info("C %s" % len(inchi_associations))
#
# #standard = inchi_associations.filter(inchitype='standard')
# #xtauto = inchi_associations.filter(inchitype='xtauto')
#
#
# inchis = {a.inchitype.id: a for a in inchi_associations}
# logger.info("---> %s", inchis)
#
# # for a in inchi_associations:
# #    logger.info("N %s %s -> %s" % (a.inchi, a.software_version, a))


#logger.info("I %s %s" % (standard, xtauto))

#for a in name_associations:
#   logger.info("N %s %s -> %s" % (a.name, a.affinity_class, a.structure))
#
#logger.info("C %s" % associations.count())

# query: QuerySet = Name.objects.prefetch_related(
#     'structures',
#     'structures__name_type',
#     'structures__structure'
# #).annotate(
# #    annotated_name_type=F('structures__name_type'),
# #    annotated_structure=F('structures__structure'),
# #    annotated_affinity_class=F('structures__affinity_class'),
# #    annotated_confidence=F('structures__confidence')
# ).filter(
#     structures__structure__in=structure_ids,
#     structures__affinity_class__in=affinity_classes,
#     structures__confidence__gte=95
# ).distinct()

#Coalesce('summary', 'headline').desc()

#logger.info("N %s C %s" % (query, 0))
#for q in query.order_by('annotated_structure').all():
#    logger.info("Q %s %s %s : %s %s " % (
#        q.name,
#        q.annotated_name_type,
#        q.annotated_structure,
#        q.annotated_affinity_class,
#        q.annotated_confidence
#    ))

#logger.info("X %s" % query.distinct().values('structures__structure'))

#for v in query.values('structures__structure', 'name', 'annotated_name_type', 'annotated_affinity_class', 'annotated_confidence').order_by('structures__structure'):
#    logger.info("V %s" % v)


# for n in query.all():
#     logger.info("%s %s" % (n, n.structures.filter(structure__in=structure_ids).all()))
#     #for a in n.structures.filter(structure__in=structure_ids).all():
#     #    logger.info("A %s : %s %s : %s %s %s | %s" % (a.name.name, a.id, a.structure_id, a.name_type_id, a.affinity_class, a.confidence, a))

# #prefetch = Prefetch()
# #prefetch = Prefetch('parents__ficts_parent', queryset=Structure.objects.all(), to_attr='ficts_parent_structure')
#
# affinity_classes = ['exact', 'narrow']
#
# #query = Structure.objects.match_names(['exact', 'narrow']).filter(annotated_name__in=["Warfarin",])
#
# query = Structure.objects.select_related('parents', 'hashisy', 'parents__ficts_parent') \
#             .filter(names__affinity_class__in=affinity_classes) \
#             .annotate(
#                 annotated_name=F('names__name__name'),
#                 annotated_affinity_class=F('names__affinity_class')
#             )
#
#
# # NSC56362 51390-22-8 NSC280834"
#
# # structure = Structure.objects.prefetch_related('names', 'names__name').get(id=690600)
# # names = structure.names.all()
# # for name in names:
# #     print(name.name)
#
# structures = query\
#     .filter(annotated_name__in=["NSC123", "NSC-123", "123", "10-Methylphenothiazine 5-oxide", "2234-09-5", "Phenothiazine, 5-oxide"])\
#     .all()
#
# logger.info("1 COUNT %s", len(connection.queries))
# items = structures.values("id", "annotated_name", "annotated_affinity_class", "minimol")
#
# logger.info("2 COUNT %s", len(connection.queries))
# logger.info("--> COUNT %s", len(structures))
#
# logger.info("3 COUNT %s", len(connection.queries))
# for item in items:
#     logger.info("I %s %s ", item, item['minimol'].ens.get("E_SMILES"))
#
# #response = structures
#
# logger.info("3 COUNT %s", len(connection.queries))
#
#
#logger.info("%s" % structures)

logging.info("connection count: %s" % (len(connection.queries)))

#for item in structures:
#    logger.info("ID %s | %s %s %s" % (item.id, item.hashisy, item.annotated_name, item.smiles))

logger.info("-----------")
logger.info("COUNT %s", len(connection.queries))
logger.info("-----------")


#or query in connection.queries:
#   logger.info("%s" % query)

