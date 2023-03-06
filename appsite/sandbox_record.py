import logging
import os

from django.db.models import Prefetch, OuterRef, Subquery
from django.db.models.functions import JSONObject

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsite.settings")

from django.conf import settings
import django
django.setup()

from django.db import connection, reset_queries
from resolver.models import *
from etl.models import *


settings.DEBUG = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cirx")

reset_queries()

s = Structure.objects.filter(id=OuterRef('annotated_ficts_parent'))
#>>> Post.objects.annotate(newest_commenter_email=Subquery(newest.values('email')[:1]))

# Brand.objects.annotate(
#     log__last__code=Subquery(
#         Log.objects.filter(
#             content_type__model=Brand._meta.model_name,
#             object_id=OuterRef('pk')
#         ).order_by('-created_at').values('code')[:1]
#     )
# )

# MainModel.objects.annotate(
#     last_object=RelatedModel.objects.filter(mainmodel=OuterRef("pk"))
#     .order_by("-date_created")
#     .values(
#         data=JSONObject(
#             id="id", body="body", date_created="date_created"
#         )
#     )[:1]
# )

# records = Record.objects\
#     .select_related(
#         'structure_file_record',
#         'structure_file_record__structure',
#         'structure_file_record__structure__parents'
#     ).annotate(
#         annotated_structure=F('structure_file_record__structure'),
#         annotated_ficts_parent=F('structure_file_record__structure__parents__ficts_parent'),
#         annotated_ficus_parent=F('structure_file_record__structure__parents__ficus_parent'),
#         annotated_uuuuu_parent=F('structure_file_record__structure__parents__uuuuu_parent')
#     ).annotate(
#         ficts_structure=Structure.objects.filter(id=OuterRef("annotated_ficts_parent")).values(
#             data=JSONObject(id="id", minimol="minimol", names="names")
#         )[:1],
#         ficts_structure_names=F('structure_file_record__structure__parents__ficts_parent__names')
#     ).filter(
#         annotated_structure=97333
#     )

records = Record.objects\
    .select_related(
        'structure_file_record',
        'structure_file_record__structure',
        'structure_file_record__structure__parents'
    ).prefetch_related(
        'structure_file_record__structure__parents__ficts_parent__names',
    ).annotate(
        annotated_structure=F('structure_file_record__structure'),
        annotated_ficts_parent=F('structure_file_record__structure__parents__ficts_parent'),
        annotated_ficts_compound=F('structure_file_record__structure__parents__ficts_parent__compound'),
        annotated_ficus_parent=F('structure_file_record__structure__parents__ficus_parent'),
        annotated_uuuuu_parent=F('structure_file_record__structure__parents__uuuuu_parent')
    ).annotate(
        ficts_structure=Structure.objects.filter(id=OuterRef("annotated_ficts_parent")).values(
            data=JSONObject(id="id", minimol="minimol", names="names")
        )[:1]
    ).filter(
        annotated_structure=97333
    )


print("DDONE")
#sfr = StructureFileRecord.objects.select_related('structure')
#print(sfr)

r: Record = records.first()
logger.info(r)
logger.info("S %s" % type(r.annotated_structure))
logger.info("FICTS %s %s" % (r.annotated_ficts_parent, r.ficts_structure))
logger.info("FICUS %s" % r.annotated_ficus_parent)
logger.info("uuuuu %s" % r.annotated_uuuuu_parent)
logger.info("----> %s" % r.annotated_ficts_compound)


#print(str(r.structure_file_record.molfile))

for q in connection.queries:
    logger.info(q)
logger.info(len(connection.queries))

