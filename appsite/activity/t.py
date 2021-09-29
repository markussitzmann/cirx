from csdb.base import *

from csdb.activity.db.schema import *
from csdb.activity.creator import GusarDataCreator
from csdb.media.db.schema import *


creator = GusarDataCreator(
	['CCO'], 
	['28fe290d08ee66eefbf18b9cb75c6a4e',]
)
structure_representation_hash = creator.get_structure_representations().keys()[0]
filter_criterion=and_(
	media_gusar_prediction_table.c.structure_representation_hash==structure_representation_hash,
	media_gusar_prediction_table.c.activity_gusar_endpoint_hash=='28fe290d08ee66eefbf18b9cb75c6a4e'
)

sql = select([media_gusar_prediction_table,]).where(filter_criterion)
print sql.execute().fetchall()

