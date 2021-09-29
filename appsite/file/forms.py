from django import forms

class ChemicalFileUpload(forms.Form):
	file = forms.FileField(max_length=100, required=False)
	string = forms.CharField(
		max_length=64738,
		widget= forms.widgets.Textarea(), 
		required=False)

class ChemicalStringInput(forms.Form):
	string = forms.CharField(max_length=1024)
		