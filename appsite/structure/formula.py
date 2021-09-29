import re

class Formula:
	
	element_list = [
		'Li','Na','Rb','Cs','Fr','Be','Mg','Ca','Sr','Ba','Ra',
		'Sc','La','Ac','Ti','Zr','Hf','Nb','Ta','Cr','Mo','Fe',
		'Ru','Os','Co','Rh','Ir','Ni','Pd','Pt','Cu','Ag','Au',
		'Zn','Cd','Hg','Al','Ga','In','Tl','Si','Ge','Sn','Pb',
		'As','Sb','Bi','Se','Te','Po','Cl','Br','At','He','Ne',
		'Ar','Kr','Xe','Rn','Ce','Pr','Nd','Pm','Sm','Eu','Gd',
		'Tb','Dy','Ho','Er','Tm','Yb','Lu','Th','Pa','Np','Pu',
		'Am','Cm','Bk','Cf','Es','Fm','Md','No','Lr','Mn','Re',
		'Tc',
		'C','H','K','Y','V','W','B','N','P','O','S','F','U','I',
		'D','T'
	]
	
	element_expression = {
		'S': 'S(?!i|r|m|c|n|b|e)',
		'F': 'F(?!m|r|e)',
		'O': 'O(?!s)',
		'N': 'N(?!a|b|i|d|e|o|p|d)',
		'P': 'P(?!u|d|t|o|a|b|r|m)',
		'C': 'C(?!a|s|r|o|e|m|l|u|d|f)',
		'H': 'H(?!f|o|e|g)',
		'I': 'I(?!r|n)',
		'K': 'K(?!r)',
		'B': 'B(?!r|e|a|i|k)',
		'Y': 'Y(?!b)',
		'D': 'D(?!y)',
		'T': 'T(?!m|b|h|i|e|h)'
	}
	
	element_hill_order = element_list[:]
	element_hill_order.sort()
	element_hill_carbon_order = element_hill_order[:]
	del element_hill_carbon_order[element_hill_carbon_order.index('C')]
	del element_hill_carbon_order[element_hill_carbon_order.index('H')]
	element_hill_carbon_order = ['C', 'H'] + element_hill_carbon_order
	
	def __init__(self, string = None):
		self.string = None
		self.element_count = {}
		self.html_formatted = None
		self.well_formatted = None
		if not self._test_formula(string = string):
			raise FormulaError('no valid chemical formula string')
		self.string = string
		self.well_formatted = self._well_formatted()
		self.html_formatted = self._html_formatted()

	def _get_element_expression_list(self, list):
		element_expression_list = []
		for element in list:
			try:
				element_expression_list.append(Formula.element_expression[element])
			except:
				element_expression_list.append(element)
		return element_expression_list
	
	def _well_formatted(self):
		formula = ''
		if self.element_count.has_key('C'):
			element_list = Formula.element_hill_carbon_order
		else:
			element_list = Formula.element_hill_order
		for element in element_list:
			if self.element_count.has_key(element):
				formula = formula + element
				if self.element_count[element] > 1:
					formula = formula + self.element_count[element]
		return formula

	def _html_formatted(self):
		element_pattern = re.compile(r'\D+')
		count_pattern = re.compile(r'\d+')
		formula = self.well_formatted
		formatted_formula = ''
		while len(formula):
			e = element_pattern.match(formula)
			formatted_formula = formatted_formula + formula[0:e.end()]
			formula = formula[e.end():]
			try:
				c = count_pattern.match(formula)
				formatted_count = "<sub>%s</sub>" % c.group()
				formatted_formula = formatted_formula + formatted_count
				formula = formula[c.end():]
			except:
				pass
		return formatted_formula
			
	def _test_formula(self, string):
		pattern = re.compile('^[A-Z]')
		if not pattern.match(string):
			return False
		element_list = Formula.element_list
		element_expression_list = self._get_element_expression_list(Formula.element_list)
		formula_string = string
		element_count_dict = {}
		pattern = '(?P<element>%s)(?P<element_count>(\d*))'
		element_assigned_list = []
		for element in element_expression_list:
			element_symbol = element.split('(')[0]
			if element_symbol in element_assigned_list:
				return False
			p = pattern % element
			expression = re.compile(p)
			match = expression.search(formula_string)
			formula_string = expression.sub('', formula_string, 1)
			try:
				key = match.groupdict()['element']
			except:
				pass
			else:
				element_assigned_list.append(key)
				try:
					item = match.groupdict()['element_count']
				except:
					pass
				else:
					try:
						if item == '':
							element_count_dict[key] = 1
						else:
							element_count_dict[key] = item
					except:
						element_count_dict[key] = 1
		if len(formula_string):
			return False
		self.element_count = element_count_dict
		return True
						
	def __str__(self):
		return self.well_formatted


class FormulaError(Exception):
	
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return repr(self.value)