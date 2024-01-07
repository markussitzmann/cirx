import re

from structure import formula


class SMILES:
    character_set = {
        'special': ['([\[\]\.\(\)\\\/#=@\-\+\%\|\?])', ],
        'numbers': ['\d'],
        'element_list': [
            'Li', 'Na', 'Rb', 'Cs', 'Fr', 'Be', 'Mg', 'Ca', 'Sr', 'Ba', 'Ra',
            'Sc', 'La', 'Ac', 'Ti', 'Zr', 'Hf', 'Nb', 'Ta', 'Cr', 'Mo', 'Fe',
            'Ru', 'Os', 'Co', 'Rh', 'Ir', 'Ni', 'Pd', 'Pt', 'Cu', 'Ag', 'Au',
            'Zn', 'Cd', 'Hg', 'Al', 'Ga', 'In', 'Tl', 'Si', 'Ge', 'Sn', 'Pb',
            'As', 'Sb', 'Bi', 'Se', 'Te', 'Po', 'Cl', 'Br', 'At', 'He', 'Ne',
            'Ar', 'Kr', 'Xe', 'Rn', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb',
            'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Th', 'Pa', 'Np', 'Pu', 'Am',
            'Cm', 'Bk', 'Cf', 'Es', 'F,', 'Md', 'No', 'Lr', 'Re', 'Mn', 'Re',
            'Tc', 'H', 'K', 'Y', 'V', 'W', 'B', 'C', 'N', 'P', 'O', 'S', 'F', 'I',
            'c', 'n', 's', 'o'
        ],
    }

    def __init__(self, string=None, strict_testing=False):
        self.string = None
        if strict_testing and not SMILES._test_smiles(string=string):
            raise SmilesError('no valid SMILES string')
        self.string = string
        self.html_formatted = self.string.replace('CC', 'C<wbr>C')

    @staticmethod
    def _test_smiles(string):
        # strings with the following pattern can be SMILES or Formula
        pattern = re.compile('^[A-Z][A-Z][a-z]$')
        if pattern.match(string):
            special_case = True
        else:
            special_case = False

        if not special_case and len(string) > 2:
            try:
                formula.Formula(string=string)
            except Exception as e:
                pass
            else:
                return False
        pattern_list = [
            (pattern_type, p) for (pattern_type, pattern_list) in SMILES.character_set.items() for p in pattern_list
        ]
        counter = {
            'special': 0,
            'numbers': 0,
            'element_list': 0
        }
        for item in pattern_list:
            t, p = item
            pattern = re.compile(p)
            string = pattern.sub('.', string)
            counter[t] += 1
            exit_pattern = re.compile('^\.+$')
            if exit_pattern.match(string):
                return counter['element_list'] >= 1
        return False


class SmilesError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
