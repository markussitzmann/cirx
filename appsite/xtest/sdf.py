import urllib2
from cactvs import *


sdf = """C2H3O
SItclcactv02251111172D 0   0.00000     0.00000

  6  5  0  0  0  0  0  0  0  0999 V2000
    2.0000    0.2500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    2.8660   -0.2500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    3.7321    0.2500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    2.4675   -0.7249    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    3.2646   -0.7249    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    4.2690   -0.0600    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  2  4  1  0  0  0  0
  2  5  1  0  0  0  0
  3  6  1  0  0  0  0
M  END
$$$$
"""

sdf = """[NO NAME]
  CHEMW2  0228112234222D                              
Created with ChemWriter - http://chemwriter.com
  4  3  0  0  0  0            999 V2000
    6.3472   -5.4056    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.2132   -4.9056    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.0793   -5.4056    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.0793   -6.4056    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  2  0  0  0  0
  3  4  1  0  0  0  0
M  END
"""

c = Cactvs()
e = Ens(c, sdf, mode='hadd')
print e.get('smiles', new=True)

#sdf = sdf.replace('\n', "\\n")

#url = '/TEST_chemical/structure/%s/smiles?operator=add_hydrogens' % urllib2.quote(sdf)

#print url

#resolver = urllib2.urlopen(url)
#response = resolver.read()

#print response
print "--------------"
