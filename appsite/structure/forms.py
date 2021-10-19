from django import forms


class ChemicalStringInput(forms.Form):
    chemicalString = forms.CharField(label="", widget=forms.TextInput(attrs={'size': '80'}))


class ChemicalResolverInput(forms.Form):
    identifier = forms.CharField(label="Structure Identifier", widget=forms.TextInput(attrs={'size': '20'}))
    representation = forms.ChoiceField(
        label="Representation:",
        choices=(
            ('stdinchikey', 'Standard InChIKey'),
            ('stdinchi', 'Standard InChI'),
            ('smiles', 'SMILES'),
            ('ficts', 'FICTS Identifier'),
            ('ficus', 'FICuS Identifier'),
            ('uuuuu', 'uuuuu Identifier'),
            ('hashisy', 'Cactvs HASHISY'),
            ('file?format=sdf', 'SD File'),
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
    nameString = forms.CharField(label="", widget=forms.TextInput(attrs={'size': '50'}))


class ChemicalFileUpload(forms.Form):
    file = forms.FileField(label="File:")
