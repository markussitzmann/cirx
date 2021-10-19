from chemical.structure.resolver import *
from cactvs import *

c = Cactvs()

#s = ChemicalString(string="ADVPTQAUNPRNPO", resolver_list=['ncicadd_stdinchikey'], cactvs = c)
#
#print s.interpretations


#s = ChemicalString(string="ADVPTQAUNPRNPO", resolver_list=['chemspider_stdinchikey'], cactvs = c)
#print s.interpretations


#s = ChemicalString(string="ChemSpider_id=660", resolver_list=['chemspider_id'], cactvs = c)
#print s.interpretations


s = ChemicalString(string="tautomers:guanine", resolver_list=['name'], cactvs = c)
print s.interpretations