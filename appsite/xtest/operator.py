from chemical.structure.dispatcher import *
from chemical.structure.resolver import *
from django.http import  *

r = HttpRequest()
u = URLmethod('smiles', request = r)

u.parser('tautomers:guanine')

#s = ChemicalString(string='tautomers:guanine')
	
#print s.interpretations

