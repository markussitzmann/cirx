from chemical.structure.resolver import *
from chemical.structure.models import *
from chemical.database.ligand.views import *
from cactvs import *
import urllib2

c = Cactvs()

v = Version.objects.get(id=2)
p = PdbEntry.objects.get(id=200)
l = Ligand.objects.get(id=2000)

pview = PdbEntryView(p, v)

lview = LigandView(l, v)

#print view.get_citations()

print pview.get_annotations()
print pview.get_ligands()

print c.cmd('parray cactvs')

print lview.get_file().string

#print l.files.get(ligandfile__version=v).content.cactvs_packstring



