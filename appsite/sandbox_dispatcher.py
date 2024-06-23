import io
import os
import sys
from contextlib import redirect_stdout

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsite.settings")

from django.conf import settings
import django

django.setup()

from resolver.models import NameAffinityClass, StructureNameAssociation
from string_resolver import ChemicalStructure

from dispatcher import Dispatcher
from settings import CIR_AVAILABLE_RESPONSE_TYPES

sys.setdlopenflags(os.RTLD_GLOBAL | os.RTLD_NOW)

from pycactvs import Ens, Prop

print('---- Start ----')

# response_types = CIR_AVAILABLE_RESPONSE_TYPES
# dispatcher = Dispatcher(None, "xnames")
# data = dispatcher.parse("CCO")
#
# for name in data.response.simple[0].content[0:50]:
#     print(name)

ens = Ens("C3=C(C(C2=C(O)C1=CC=CC=C1OC2=O)CC(=O)C)C=CC=C3")
#ens = Ens("CCO")

affinity = {a.title: a for a in NameAffinityClass.objects.all()}

resolved = ChemicalStructure(ens = ens)
compounds = []
ficts_parent = resolved.ficts_parent(only_lookup=False)
if ficts_parent and ficts_parent.structure:
    compounds.append(ficts_parent.structure.compound)
ficus_parent = resolved.ficus_parent(only_lookup=False)
if not len(compounds) and ficus_parent and ficus_parent.structure:
    compounds.append(ficus_parent.structure.compound)
associations = StructureNameAssociation.with_related_objects.by_compound(
    compounds,
    affinity_classes=[affinity['exact'], ]
).filter(name_type__parent__title='NAME', name_type=5).order_by('name__name').all()
# names = [association.name.name for association in associations]

for association in associations[0:50]:
    print(str(association) + " // " + association.name.name)