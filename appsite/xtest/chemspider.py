from chemical.structure.resolver import *

#s = ChemicalString(string='ChemSpider_ID=660', resolver_list=['chemspider_id'])

#print s.interpretations
#print s.interpretations[0].structures[0].ens['atom:xyz']


#s = ChemicalString(string='RCINICONZNJXQF-MZXODVADSA-N', resolver_list=['chemspider_stdinchikey'])

#resolver = ExternalResolver(name = "chemspider", url_scheme="http://inchis.chemspider.com/REST.ashx?q=%s\&of=%s")
#response = resolver.resolve('InChIKey=RCINICONZNJXQF-MZXODVADSA-N', 'sdf')
#response = resolver.resolve('ADVPTQAUNPRNPO', 'sdf')
#print response

print 'hallo'
s = ChemicalString(string='ADVPTQAUNPRNPO', resolver_list=['chemspider_stdinchikey'])

print s._interpretations[0].structures[0]._ens['smiles']
