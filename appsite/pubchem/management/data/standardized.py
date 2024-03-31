from dataclasses import dataclass
from typing import Optional, List, Dict, Union


@dataclass(frozen=True)
class StandardDataItem:
    standard: Union[Dict, str]
    variations: List[str]

    def variation_dict(self):
        return {v: self.standard for v in self.variations}


@dataclass(frozen=True)
class OrganizationItem(StandardDataItem):
    id_hint: Optional[int] = None


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
            ' INC.',
            ' INC',
        ]
    ),
    StandardDataItem(
        standard=', Ltd.',
        variations=[
            ', Ltd.',
            ', Ltd',
            ', Ltd',
            ', LTD.',
            'LTD',
            ' ltd',
            ' Ltd',
            ' Ltd.',

        ]
    ),
    StandardDataItem(
        standard='Co., Ltd.',
        variations=[
            'Co., Ltd.',
            'Co,Ltd.',
            'Co.,Ltd.',
            'Co, Ltd.',
            'co, Ltd.',
            'CO., Ltd.',
            'CO., LTD.',
            'Co.,Ltd',
            'co.,lttd',
            'Co,.Ltd',
            'Co.,Ltd.',
            'Co,.Ltd',
            'Co., LTD.',
            'Co.,ltd.',
            'Co.,Ltd.  '
        ]
    ),
]

organizations: List[OrganizationItem] = [
    OrganizationItem(
        id_hint=1,
        standard={
            'name': 'U.S. National Cancer Institute',
            'category': 'government',
            'abbreviation': 'NCI'
        },
        variations=[
            'NCI',
            'National Cancer Institute',
            'National Cancer Institute (NCI)',
            'NIH / National Cancer Institute'
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'U.S. Environmental Protection Agency',
            'category': 'government',
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
            'U.S. Environmental Protection Agency (EPA) Research',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'ATPase-Kinase Pharmacophores',
            'abbreviation': 'AKP'
        },
        variations=[
            'ATPase-Kinase Pharmacophores (AKP)',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Aromsyn Co., Ltd.',
            'abbreviation': None
        },
        variations=[
            'Aromsyn Co.,Ltd.  '
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Chemical Abstracts Service',
            'abbreviation': 'CAS'
        },
        variations=[
            'CAS'
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Royal Society of Chemistry',
            'category': 'society',
            'abbreviation': 'RSC'
        },
        variations=[
            'Royal Society of Chemistry'
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Karlsruhe Institute of Technology',
            'category': 'academia',
            'abbreviation': 'KIT'
        },
        variations=[
            'KIT'
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'U.S. Drug Enforcement Administration',
            'category': 'regulatory',
            'abbreviation': 'DEA'
        },
        variations=[
            'The United States Drug Enforcement Administration (DEA)'
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'U.S. Food and Drug Administration',
            'category': 'regulatory',
            'abbreviation': 'FDA'
        },
        variations=[
            'U.S. Food and Drug Administration',
            'FDA',
            'US FDA',
            'U.S. FDA'
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Human Protein Atlas',
            'abbreviation': 'HPA'
        },
        variations=[
            'Human Protein Atlas (HPA)',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'U.S. National Center for Advancing Translational Sciences',
            'category': 'government',
            'abbreviation': 'NCATS'
        },
        variations=[
            'NIH/National Center for Advancing Translational Sciences (NCATS)',
            'NIH/NCATS'
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'U.S. National Institute of Allergy and Infectious Diseases',
            'category': 'government',
            'abbreviation': 'NIAID'
        },
        variations=[
            'NIAID, NIH',
            'National Institute of Allergy and Infectious Diseases, NIH'
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'European Medicines Agency',
            'category': 'government',
            'abbreviation': 'EMA'
        },
        variations=[
            'European Medicines Agency',
            'European Medicines Agency (EMA)',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'World Health Organization',
            'category': 'government',
            'abbreviation': 'WHO'
        },
        variations=[
            'World Health Organization (WHO)',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'U.S. National Institutes of Health',
            'category': 'government',
            'abbreviation': 'NIH'
        },
        variations=[
            'National Institutes of Health',
            'NIH'
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'U.S. National Center for Biotechnology Information',
            'category': 'government',
            'abbreviation': 'NCBI'
        },
        variations=[
            'National Institutes of Health',
            'NIH'
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'U.S. National Institute of Standards and Technology',
            'category': 'government',
            'abbreviation': 'NIST'
        },
        variations=[
            'National Institute of Standards and Technology (NIST)',
            'NIST'
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'U.S. Chemical Safety and Hazard Investigation Board',
            'category': 'government',
            'abbreviation': 'CSB'
        },
        variations=[
            'U.S. Chemical Safety and Hazard Investigation Board (CSB)',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'U.S. National Library of Medicine',
            'category': 'government',
            'abbreviation': 'NLM'
        },
        variations=[
            'National Library of Medicine',
            'NLM'
        ]
    ),
]
