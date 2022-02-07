from django import template

register = template.Library()

@register.filter(name='beautify')
def beautify(value, arg=None):
	if arg=="boolean":
		if value==True:
			return "yes"
		if value==False:
			return "no"
	if arg=="chemical_string_type":
		if value=="name_by_cir":
			return "chemical name (Chemical Identifier Resolver)"
		if value=="name_by_opsin":
			return "IUPAC name (OPSIN)"
		if value=="smiles":
			return "SMILES string"
		if value=="cas_number":
			return "generic registry number"
		if value=="stdinchikey":
			return "Standard InChIKey"
	if arg=="chemical_string_type_short_cap":
		if value=="name_by_cir":
			return "Chemical Name (CIR)"
		if value=="name_by_opsin":
			return "IUPAC Name (OPSIN)"
		if value=="smiles":
			return "SMILES String"
		if value=="cas_number":
			return "Generic Registry Number"
		if value=="stdinchikey":
			return "Standard InChIKey"
	if arg=="operator_string":	
		s = value.split(':')
		if len(s)>1:
			return '%s of %s' % (s[0].capitalize(), s[1].capitalize())
		else:
			return value
	if arg=="strip_operator_string":	
		s = value.split(':')
		if len(s)>1:
			return '%s' % (s[1].capitalize(),)
		else:
			return value
	if arg=="smiles":
		n=10
		l = [value[i:i+n] for i in range(0, len(value), n)]
		return '<wbr>'.join(l)
	if arg=="short_smiles":
		n=10
		if len(value)>50:
			s = [value[i:i+n] for i in range(0, len(value[0:50]), n)]
			return '<wbr>'.join(s) + '...'
		else:
			s = value
			return s
		

	return value



#beautify = register.filter('beautify', beautify)
