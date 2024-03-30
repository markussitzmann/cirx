from dataclasses import dataclass
from typing import Optional, List, Dict, Union


@dataclass(frozen=True)
class StandardDataItem:
    standard: Union[Dict, str]
    variations: List[str]

    def variation_dict(self):
        return {v: self.standard for v in self.variations}


organization_type_strings: List[StandardDataItem] = [
    StandardDataItem(
        standard=', LCC',
        variations=[
            ', LLC',
            ' LLC',
            ' LLC.'
        ]
    ),
    StandardDataItem(
        standard=', Inc.',
        variations=[
            ', Inc.',
            ', Inc',
            ' inc',
            ' Inc',
            ' Inc.',
            ' INC.'
        ]
    ),
    StandardDataItem(
        standard=', Ltd.',
        variations=[
            ', Ltd.',
            ', Ltd',
            ' ltd',
            ' Ltd',
            ', Ltd'
        ]
    ),
]

organizations: List[StandardDataItem] = [
    StandardDataItem(
        standard={
            'name': 'U.S. National Cancer Institute',
            'abbreviation': 'NCI'
        },
        variations=[
            'NCI',
            'National Cancer Institute',
            'National Cancer Institute (NCI)',
            'NIH / National Cancer Institute'
        ]
    ),
    StandardDataItem(
        standard={
            'name': 'U.S. Environmental Protection Agency',
            'abbreviation': 'EPA'
        },
        variations=[
            'EPA',
            'US EPA',
            'U.S. EPA',
            'US Environmental Protection Agency',
            'US Environmental Protection Agency (EPA)',
            'U.S. Environmental Protection Agency (EPA)',
            'US Environmental Protection Agency - EPA',
            'U.S. Environmental Protection Agency',
        ]
    ),
    StandardDataItem(
        standard={
            'name': 'ATPase-Kinase Pharmacophores',
            'abbreviation': 'AKP'
        },
        variations=[
            'ATPase-Kinase Pharmacophores (AKP)',
        ]
    ),
]
