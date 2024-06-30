import os

CIR_FILESTORE_ROOT = os.path.join("/filestore")
CIR_INSTORE_ROOT = os.path.join("/instore")

CIR_AVAILABLE_RESOLVERS = [
    'smiles',
    'stdinchikey',
    'stdinchi',
    # 'ncicadd_identifier',
    'hashisy',
    # 'chemspider_id',
    # 'chemnavigator_sid',
    # 'pubchem_sid',
    # 'emolecules_vid',
    'ncicadd_rid',
    'ncicadd_cid',
    'ncicadd_sid',
    'cas_number',
    # 'nsc_number',
    # 'zinc_code',
    # 'opsin',
    # 'name_pattern',
    'name',
    # 'SDFile',
    # 'minimol',
    'packstring',
    # 'structure_representation'
]

CIR_AVAILABLE_RESOLVER_OPERATORS = [
    'tautomers',
    'remove_hydrogens',
    'add_hydrogens',
    'ficts',
    'ficus',
    'uuuuu',
    'parent',
    'normalize',
    'stereoisomers',
    'no_stereo',
    # 'scaffold_sequence',
]

CIR_AVAILABLE_RESPONSE_TYPES = [
    {
        "name": "xnames",
        "method": "xnames",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "ficts",
        "method": "prop",
        "parameter": "E_FICTS_ID",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "ficus",
        "method": "prop",
        "parameter": "E_FICUS_ID",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "fictu",
        "method": "prop",
        "parameter": "E_FICTU_ID",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "ficuu",
        "method": "prop",
        "parameter": "E_FICUU_ID",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "uuuts",
        "method": "prop",
        "parameter": "E_UUUTS_ID",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "uuuus",
        "method": "prop",
        "parameter": "E_UUUUS_ID",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "uuutu",
        "method": "prop",
        "parameter": "E_UUUTU_ID",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "uuuuu",
        "method": "prop",
        "parameter": "E_UUUUU_ID",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "ficts_structure",
        "method": "prop",
        "parameter": "E_FICTS_STRUCTURE",
        "base_content_type": "text",
        "parent": "ficts"
    },
    {
        "name": "ficus_structure",
        "method": "prop",
        "parameter": "E_FICUS_STRUCTURE",
        "base_content_type": "text",
        "parent": "ficus"
    },
    {
        "name": "fictu_structure",
        "method": "prop",
        "parameter": "E_FICTU_STRUCTURE",
        "base_content_type": "text",
        "parent": "fictu"
    },
    {
        "name": "ficuu_structure",
        "method": "prop",
        "parameter": "E_FICUU_STRUCTURE",
        "base_content_type": "text",
        "parent": "ficuu"
    },
    {
        "name": "uuuts_structure",
        "method": "prop",
        "parameter": "E_UUUTS_STRUCTURE",
        "base_content_type": "text",
        "parent": "uuuts"
    },
    {
        "name": "uuuus_structure",
        "method": "prop",
        "parameter": "E_UUUUS_STRUCTURE",
        "base_content_type": "text",
        "parent": "uuuus"
    },
    {
        "name": "uuutu_structure",
        "method": "prop",
        "parameter": "E_UUUTU_STRUCTURE",
        "base_content_type": "text",
        "parent": "uuutu"
    },
    {
        "name": "uuuuu_structure",
        "method": "prop",
        "parameter": "E_UUUUU_STRUCTURE",
        "base_content_type": "text",
        "parent": "uuuuu"
    },
    {
        "name": "inchi",
        "method": "prop",
        "parameter": "E_INCHI",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "inchikey",
        "method": "prop",
        "parameter": "E_INCHIKEY",
        "base_content_type": "text",
        "parent": "inchi"
    },
    {
        "name": "smiles",
        "method": "prop",
        "parameter": "E_SMILES",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "pack",
        "method": "prop",
        "parameter": "packstring",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "names",
        "method": "names",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "cas",
        "method": "cas_numbers",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "cas_numbers",
        "method": "cas_numbers",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "stdinchi",
        "method": "prop",
        "parameter": "E_STDINCHI",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "stdinchikey",
        "method": "prop",
        "parameter": "E_STDINCHIKEY",
        "base_content_type": "text",
        "parent": "stdinchi"
    },
    {
        "name": "image",
        "method": "structure_image",
        "parameter": None,
        "base_content_type": "image",
        "parent": None
    },
    {
        "name": "sdf",
        "method": "molfile",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "molfile",
        "method": "molfile",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "hashisy",
        "method": "prop",
        "parameter": "E_HASHISY",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "gif",
        "method": "prop",
        "parameter": "structure_image",
        "base_content_type": "image",
        "parent": None
    },
    {
        "name": "iupac_name",
        "method": "iupac_name",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "file",
        "method": "molfile",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "twirl",
        "method": "molfile",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    # {
    #     "name": "urls",
    #     "method": "urls",
    #     "parameter": None,
    #     "base_content_type": "text",
    #     "parent": None
    # },
    {
        "name": "weight",
        "method": "prop",
        "parameter": "E_WEIGHT",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "mw",
        "method": "prop",
        "parameter": "E_WEIGHT",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "formula",
        "method": "prop",
        "parameter": "E_FORMULA",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "monoisotopic_mass",
        "method": "prop",
        "parameter": "E_MONOISOTOPIC_MASS",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "h_bond_donor_count",
        "method": "prop",
        "parameter": "E_NHDONORS",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "h_bond_acceptor_count",
        "method": "prop",
        "parameter": "E_NHACCEPTORS",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "effective_rotor_count",
        "method": "prop",
        "parameter": "E_EFFECTIVE_ROTOR_COUNT",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "xlogp2",
        "method": "prop",
        "parameter": "E_XLOGP2",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "rule_of_5_violation_count",
        "method": "prop",
        "parameter": "E_RULE_OF_5_VIOLATIONS",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "h_bond_center_count",
        "method": "prop",
        "parameter": "E_HYDROGEN_BOND_CENTER_COUNT",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "chemspider_id",
        "method": "chemspider_id",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "rotor_count",
        "method": "prop",
        "parameter": "E_ROTOR_COUNT",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "aromatic",
        "method": "prop",
        "parameter": "E_IS_AROMATIC",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "macrocyclic",
        "method": "prop",
        "parameter": "E_IS_MACROCYCLIC",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "is_aromatic",
        "method": "prop",
        "parameter": "E_IS_AROMATIC",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "is_macrocyclic",
        "method": "prop",
        "parameter": "E_IS_MACROCYCLIC",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "heteroatom_count",
        "method": "prop",
        "parameter": "E_HETERO_ATOM_COUNT",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "hydrogen_atom_count",
        "method": "prop",
        "parameter": "E_HYDROGEN_ATOM_COUNT",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "heavy_atom_count",
        "method": "prop",
        "parameter": "E_HEAVY_ATOM_COUNT",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "deprotonable_group_count",
        "method": "prop",
        "parameter": "E_DEPROTONABLE_GROUP_COUNT",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "protonable_group_count",
        "method": "prop",
        "parameter": "E_PROTONABLE_GROUP_COUNT",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "ring_count",
        "method": "prop",
        "parameter": "E_RING_COUNT",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "ringsys_count",
        "method": "prop",
        "parameter": "E_RINGSYS_COUNT",
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "ncicadd_sid",
        "method": "ncicadd_structure_id",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "ncicadd_cid",
        "method": "ncicadd_compound_id",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "ncicadd_rid",
        "method": "ncicadd_record_id",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    # {
    #     "name": "chemnavigator_sid",
    #     "method": "chemnavigator_sid",
    #     "parameter": None,
    #     "base_content_type": "text",
    #     "parent": None
    # },
    {
        "name": "pubchem_sid",
        "method": "pubchem_sid",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    # {
    #     "name": "emolecules_vid",
    #     "method": "emolecules_vid",
    #     "parameter": None,
    #     "base_content_type": "text",
    #     "parent": None
    # },
    # {
    #     "name": "emolecules_id",
    #     "method": "emolecules_vid",
    #     "parameter": None,
    #     "base_content_type": "text",
    #     "parent": None
    # },
    # {
    #     "name": "zinc_id",
    #     "method": "zinc_id",
    #     "parameter": None,
    #     "base_content_type": "text",
    #     "parent": None
    # },
    # {
    #     "name": "zinc_code",
    #     "method": "zinc_id",
    #     "parameter": None,
    #     "base_content_type": "text",
    #     "parent": None
    # },
    # {
    #     "name": "zinc",
    #     "method": "zinc_id",
    #     "parameter": None,
    #     "base_content_type": "text",
    #     "parent": None
    # },
    # {
    #     "name": "chemnavigator_id",
    #     "method": "chemnavigator_sid",
    #     "parameter": None,
    #     "base_content_type": "text",
    #     "parent": None
    # },
    {
        "name": "nsc_number",
        "method": "nsc_number",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    },
    {
        "name": "nsc",
        "method": "nsc_number",
        "parameter": None,
        "base_content_type": "text",
        "parent": None
    }
]
