from django.forms.widgets import Input
from django import forms

### widget

class Html5SearchInput(Input):
	input_type='search'

### forms

class AppsAddStructureForm(forms.Form):
	#structure_term_input = forms.CharField(label="",widget=forms.TextInput(attrs={'type': 'search', 'size':'50'}))
	#structure_term_input = forms.CharField(widget=Html5SearchInput(attrs={'placeholder': 'Use chemical identifier, e.g. Standard InChI/InChIKey, SMILES, chemical names', 'autocorrect': 'off', 'autocapitalize': 'off'}), required=False)
	structure_term_input = forms.CharField(widget=Html5SearchInput(attrs={'autocorrect': 'off', 'autocapitalize': 'off'}), required=False)

	#structure_term_input.widget = forms.TextInput(attrs={'type': 'search', 'size': 10, 'title': 'Search',})
	structure_list_input = forms.CharField(label="",widget=forms.widgets.Textarea(attrs={'rows':'15'}))

class CSLSForm(forms.Form):
	structure_input = forms.CharField(label="",widget=forms.widgets.Textarea(attrs={'rows':'15'}))
	
class CIRForm(forms.Form):
	identifier = forms.CharField(label="Structure Identifier",widget=forms.TextInput(attrs={'size':'20'}))
	representation = forms.ChoiceField(
		label="Representation:",
		choices=(
			('stdinchikey', 'Standard InChIKey'),
			('stdinchi','Standard InChI'),
			('smiles', 'SMILES'),
			('ficts', 'FICTS Identifier'),
			('ficus', 'FICuS Identifier'),
			('uuuuu', 'uuuuu Identifier'),
			('hashisy', 'Cactvs HASHISY'),
			('sdf', 'SD File'),
			('names', 'Names'),
			('iupac_name', 'IUPAC Name'),
			('cas', 'CAS Registry Number'),
			('chemspider_id', 'ChemSpider ID'),
			('image', 'GIF Image'),
			('twirl', 'TwirlyMol (3D)'),
			('mw', 'Molecular Weight'),
			('formula', 'Chemical Formula'),
			('h_bond_donor_count', 'Number of Hydrogen Bond Donors'),
			('h_bond_acceptor_count', 'Number of Hydrogen Bond Acceptors'),
			('h_bond_center_count', 'Number of Hydrogen Bond Acceptors and Donors'),
			('rule_of_5_violation_count', 'Number of Rule of 5 Violations'),
			('rotor_count', 'Number of Freely Rotatable Bonds'),
			('effective_rotor_count', 'Number of Effectively Rotatable Bonds'),
			('ring_count', 'Number of Rings'),
			('ringsys_count', 'Number of Ring Systems'),
		)
	)
	
class ChemicalNameInput(forms.Form):
	nameString = forms.CharField(label="",widget=forms.TextInput(attrs={'size':'50'}))


class ChemicalFileUpload(forms.Form):
	file = forms.FileField(label="File:")


class CAPForm(forms.Form):
	structure_input = forms.CharField(label="Structure Input", widget=forms.widgets.Textarea(attrs={'rows':'16'}))	


class PatentForm(forms.Form):
	patent_number_input = forms.CharField(label="Patent Number", widget=forms.TextInput(attrs={'size':'20'}))
