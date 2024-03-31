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
        standard=', LCC.',
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
            'Limited'

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
            'Co.,Ltd.',
            'Co., Limited'
        ]
    ),
    StandardDataItem(
        standard='Corp.',
        variations=[
            'Corp.',
            'Corp',
            'corp',
        ]
    ),
    StandardDataItem(
        standard='Co.',
        variations=[
            'Co',
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
            'NIH / National Cancer Institute',
            'MTDP, CCR, NCI'
        ]
    ),
    # CHECK
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
            'EPA Chemical Information and Testing Branch', #check
            'Office of Pollution Prevention and Toxics (7403M), US EPA'
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'ATPase-Kinase Pharmacophores',
            'category': 'none',
            'abbreviation': 'AKP'
        },
        variations=[
            'ATPase-Kinase Pharmacophores (AKP)',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Aromsyn Co., Ltd.',
            'category': 'none',
            'abbreviation': None
        },
        variations=[
            'Aromsyn Co.,Ltd.  '
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Chemical Abstracts Service',
            'category': 'non-profit',
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
    #Check
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
            'U.S. FDA',
            'Division of Drug Information, CDER, FDA',
            'Office of the Center Director, Center for Drug Evaluation and Research, FDA'
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Human Protein Atlas',
            'category': 'none',
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
            'NIST',
            'NIST  Physical Measurement Laboratorys'
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
    OrganizationItem(
        standard={
            'name': 'BerrChemical Co., Ltd.',
            'category': 'company',
        },
        variations=[
            'BerrChemical Company, Ltd.',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Boehringer Ingelheim',
            'category': 'company',
        },
        variations=[
            'Boehringer Ingelheim',
            'Boehringer-Ingelheim',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Active Chem-Block Shanghai',
            'category': 'company',
        },
        variations=[
            'Active chem-block shanghai',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Beijing Acemol Technology Co., Ltd.',
            'category': 'company',
        },
        variations=[
            'Beijing acemol technology Co.,Ltd',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'ChemProbes',
            'category': 'company',
        },
        variations=[
            'ChemProbes, stock solutions in DMSO',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Creasyn Finechem Tianjin Co., Ltd.',
            'category': 'company',
        },
        variations=[
            'Creasyn Finechem(Tianjin) Co., Ltd.',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Central Salt and Marine Chemicals Research Institute',
            'category': 'research',
            'abbreviation': 'CSIR'
        },
        variations=[
            'CSIR-Central Salt and Marine Chemicals Research Institute',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Dana Farber Cancer Institute',
            'category': 'research',
        },
        variations=[
            'Dana-Farber Cancer Institute',
            'Dana Farber Cancer Institute',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Cambridge Crystallographic Data Centre',
            'category': 'research',
            'abbreviation': 'CCDC'
        },
        variations=[
            'Cambridge Crystallographic Data Centre',
        ]
    ),
    OrganizationItem(
        standard={
            'name': 'Eidgenössische Technische Hochschule Zürich',
            'category': 'academia',
            'abbreviation': 'ETH Zürich'
        },
        variations=[
            'ETH Zurich',
        ]
    ),
    #### CHECK: gehört zu Cambridge University
    OrganizationItem(
        standard={
            'name': 'Cancer Research UK Cambridge Institute',
            'category': 'research',
            'abbreviation': 'CRUK CRI'
        },
        variations=[
            'CRUK CRI',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'University of North Carolina at Chapel Hill',
            'category': 'academia',
        },
        variations=[
            'Baker Lab, The University of North Carolina at Chapel Hill',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Boston University',
            'category': 'academia',
        },
        variations=[
            'Boston University',
            'Boston University School of Medicine'
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'University of Geneva',
            'category': 'academia',
        },
        variations=[
            'University of Geneva',
            'Athena Mineralogy, University of Geneva'
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'International Atomic Energy Agency',
            'category': 'academia',
            'abbreviation': 'IAEA'
        },
        variations=[
            'Atomic Mass Data Center (AMDC), International Atomic Energy Agency (IAEA)',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Tata Memorial Centre',
            'category': 'academia',
        },
        variations=[
            'Advanced Centre for Treatment, Research & Education in Cancer (ACTREC) Tata Memorial Centre',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Tata Memorial Centre',
            'category': 'academia',
        },
        variations=[
            'Advanced Centre for Treatment, Research & Education in Cancer (ACTREC) Tata Memorial Centre',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'The University of Auckland',
            'category': 'academia',
        },
        variations=[
            'Auckland Cancer Society Research Centre, The University of Auckland',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Baylor College of Medicine',
            'category': 'academia',
        },
        variations=[
            'Baylor College of Medicine, Dept. of Molecular Physiology and Biophysics',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Sri Venkateswara University',
            'category': 'academia',
        },
        variations=[
            'Bhaskar Lab, Department of Zoology, Sri Venkateswara University',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'National University of Singapore',
            'category': 'academia',
        },
        variations=[
            'Bioinformatics and Drug Design (BIDD) Group,  National University of Singapore',
            'Bioinformatics and Drug Design Group/National University of Singapore'
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Duke University',
            'category': 'academia',
        },
        variations=[
            'Chemistry Department, Duke University',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Institute of Molecular Genetics of the Czech Academy of Sciences',
            'category': 'research',
        },
        variations=[
            'CZ-OPENSCREEN, Institute of Molecular Genetics of the Czech Academy of Sciences',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'University of Edinburgh',
            'category': 'academia',
        },
        variations=[
            'Deanery of Biomedical Sciences, University of Edinburgh',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'IIT Guwahati',
            'category': 'academia',
        },
        variations=[
            'Department of Biosciences and Bioengineering, IIT Guwahati',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Anna University, Chennai-113',
            'category': 'academia',
        },
        variations=[
            'Department of Biotechnology,E-YUVA Centre, Anna University, Chennai-113',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'University of Calicut',
            'category': 'academia',
        },
        variations=[
            'Department of Biotechnology, University of Calicut',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Stanford University',
            'category': 'academia',
        },
        variations=[
            'Department of Chemical and Systems Biology, Stanford University',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Aarhus University',
            'category': 'academia',
        },
        variations=[
            'Department of Chemistry, Aarhus University',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'São Paulo State University',
            'category': 'academia',
        },
        variations=[
            'Department of Chemistry and Biochemistry (DQB), Faculty of Sciences and Technology, Unesp',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Broad Institute',
            'category': 'academia',
        },
        variations=[
            'Broad Institute',
            'Broad Institute of Harvard & MIT/Chemical Biology Program'
        ]
    ),
    #### CHECK: Yang Lab, CAS-MPG Partner Institute for Computational Biology, Shanghai Institute of Nutrition and Health, Shanghai Institutes for Biological Sciences, Chinese Academy of Sciences
    OrganizationItem(
        standard={
            'name': 'Chinese Academy of Sciences',
            'category': 'academia',
        },
        variations=[
            'CAS-MPG Partner Institute for Computational Biology,Shanghai Institute of Nutrition and Health, CAS'
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Research Center for Molecular Medicine of the Austrian Academy of Sciences',
            'category': 'academia',
            'abbreviation': 'CeMM'
        },
        variations=[
            'CeMM - Research Center for Molecular Medicine of the Austrian Academy of Sciences'
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Cardiff University',
            'category': 'academia',
        },
        variations=[
            'Cardiff University School of Medicine'
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'University of California',
            'category': 'academia',
            'abbreviation': 'UC'
        },
        variations=[
            'Cell and Developmental Biology, Division of Biological Sciences, University of California San Diego',
            'University of California San Diego',
            'University of California, San Diego',
            'University of California, Los Angeles',
            'University of California, Irvine (UCI)',
            'University of California, Davis',
            'UCLA',
            'UC Santa Cruz',
            'UCSD', #san diego
            'UCSF',  #san francisco
            'UCSF Taunton Lab',
            'UC Davis',
            'Department of Chemistry and Biochemistry, UCLA'
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'University of Illinois',
            'category': 'academia',
            'abbreviation': 'UI'
        },
        variations=[
            'CENAPT at UIC, College of Pharmacy',
            'University of Illinois at Chicago',
            'University of Illinois at Urbana-Champaign',
            'University of Illinois'
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'University of Arkansas',
            'category': 'academia',
            'abbreviation': 'UA'
        },
        variations=[
            'University of Arkansas for Medical Sciences',
            'University of Arkansas For Medical Sciences',
        ]
    ),
#### CHECK:
    OrganizationItem(
        standard={
            'name': 'Universität zu Köln',
            'category': 'academia',
        },
        variations=[
            'Universitaet zu Koeln',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'European Bioinformatics Institute',
            'category': 'none',
            'abbreviation': 'EMBL-EBI'
        },
        variations=[
            'European Bioinformatics Institute (EMBL-EBI)',
            'ChEMBL group, European Bioinformatics Institute (EMBL-EBI)'
        ]
    ),
    #### CHECK: Beltsville Human Nutrition Research Center, ARS, USDA
    OrganizationItem(
        standard={
            'name': 'U.S. Department of Agriculture',
            'category': 'government',
            'abbreviation': 'USDA'
        },
        variations=[
            'BHNRC, ARS, USDA',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Centers for Disease Control and Prevention',
            'category': 'government',
            'abbreviation': 'CDC'
        },
        variations=[
            'CDC',
            'CDC-ATSDR'
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'University of Luxembourg',
            'category': 'academia',
        },
        variations=[
            'Environmental Cheminformatics, Luxembourg Centre for Systems Biomedicine, University of Luxembourg',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'The University of Georgia',
            'category': 'academia',
        },
        variations=[
            'Department of Infectious Diseases, College of Veterinary Medicine at The University of Georgia',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'University of Arizona',
            'category': 'academia',
        },
        variations=[
            'Department of Geosciences, University of Arizona',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'University College London',
            'category': 'academia',
            'abbreviation': 'UCL'
        },
        variations=[
            'University College London',
            'UCL',
            'UCL Respiratory, Division of Medicine, University College London'
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'University of Cambridge',
            'category': 'academia',
        },
        variations=[
            'Univerisyt of Cambridge',
        ]
    ),
    #### CHECK:
    OrganizationItem(
        standard={
            'name': 'Yale University',
            'category': 'academia',
        },
        variations=[
            'Department of Comparative Medicine, Yale University',
        ]
    ),
    ### Check
    OrganizationItem(
        standard={
            'name': 'University of Alberta',
            'category': 'academia',
        },
        variations=[
            'Department of Computational and Biological Sciences',
        ]
    ),
    ### Check
    OrganizationItem(
        standard={
            'name': 'University of Kyoto',
            'category': 'academia',
        },
        variations=[
            'Department of Systems Biosciences for Drug Discovery, Kyoto UNIV.',
        ]
    ),
    ### Check
    OrganizationItem(
        standard={
            'name': 'Washington University School of Medicine',
            'category': 'academia',
        },
        variations=[
            'Department of Genetics, Washington University School of Medicine',
            'McDonnell Genome Institute, Washington University School of Medicine'
        ]
    ),




]
