import io
import os
import sys
from contextlib import redirect_stdout

sys.setdlopenflags(os.RTLD_GLOBAL|os.RTLD_NOW)

from pycactvs import Ens, Prop

# e = Ens("CCO")
# print(e.get("E_SMILES"))
#
#
# p = Prop("E_GIF")
# pprint(p.parameters)
#
# print(Prop.get(p, "file"))
# print(Prop.get(p, "fileformat"))
# #print(Prop.set(p, "format", "svg"))
#
# tmpfile = e.get("E_GIF")
#
# shutil.copyfile(tmpfile, "/home/app/test.png")


dgif = {
    'width': 200,
    'height': 250,
    'bgcolor': 'white',
    'atomcolor': 'black',
    'format': 'png',
    'header': 'Caffeine',
    'filename': '/home/app/caffeine.gif'
}

dsvg = {
    'width': 220,
    'height': 220,
    'bgcolor': 'white',
    'atomcolor': 'element',
    #'symbolfontsize': 32,
    'header': 'Caffeine',
    'filename': 'bytes',
    #'bonds': 4
}

#Prop.Setparam('E_GIF', 'width', 200, 'height', 250, 'bgcolor', 'white', 'atomcolor', 'black', 'format', 'svg', 'header', 'Caffeine', 'filename', '/home/app/caffeine.gif')

#Prop.Setparameter('E_GIF', dgif)
#Prop.Setparameter('E_SVG_IMAGE', dsvg)


#pprint(Prop.getparameterdict(Prop("E_SVG_IMAGE")))

#image = Ens.Get('CN1C=NC2=C1C(=O)N(C(=O)N2C)C', 'E_GIF')

#old_stdout = sys.stdout
#image = Ens.Get('CN1C=NC2=C1C(=O)N(C(=O)N2C)C', 'E_SVG_IMAGE')
#sys.stdout = old_stdout

#image = Ens.Get('CN1C=NC2=C1C(=O)N(C(=O)N2C)C', 'E_SVG')


#print(image)

#p = Prop("E_SVG_IMAGE")
#pprint(p.parameters)

dsvg = {
    'width': 220,
    'height': 220,
    'bgcolor': 'white',
    'atomcolor': 'element',
    # 'symbolfontsize': 32,
    'header': 'Caffeine',
    'filename': '/home/app/test.svg',
    # 'bonds': 4
}
Prop.Setparameter('E_SVG_IMAGE', dsvg)
f = Ens.Get('CN1C=NC2=C1C(=O)N(C(=O)N2C)C', 'E_SVG_IMAGE')
print(f)
print(os.path.isfile(f))


#with open(f, 'r'):
#    image = f.read()#
#
#print(image)

# import tempfile
# with tempfile.NamedTemporaryFile() as tmp:
#     dsvg = {
#         'width': 220,
#         'height': 220,
#         'bgcolor': 'white',
#         'atomcolor': 'element',
#         # 'symbolfontsize': 32,
#         'header': 'Caffeine',
#         'filename': tmp.name,
#         # 'bonds': 4
#     }
#     print(tmp.name)
#     Prop.Setparameter('E_SVG_IMAGE', dsvg)
#     Ens.Get('CN1C=NC2=C1C(=O)N(C(=O)N2C)C', 'E_SVG_IMAGE')
#     #print(f)

p = Prop.Ref('E_SVG_IMAGE')
print(p.altdatatypes)
p.datatype='xmlstring'
image = Ens.Get('c1nccc1', p)
print(image)

pp = Prop('E_SVG_IMAGE')
print(pp)
