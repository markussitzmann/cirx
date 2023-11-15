import datetime
import json
import logging

import urllib.request

import requests
from django.core.management.base import BaseCommand
from pycactvs import Ens

from etl.models import StructureFileCollection, StructureFileCollectionPreprocessor, StructureFileField
from resolver.models import InChI, Organization, Publisher, Structure, Name, NameType, StructureNameAssociation, \
    ContextTag, Dataset, Release, InChIType, NameAffinityClass, ResponseType

logger = logging.getLogger('cirx')

MINI = True
INIT_PUBCHEM_COMPOUND = False
INIT_PUBCHEM_SUBSTANCE = False
INIT_CHEMBL = False
INIT_NCI = True
INIT_SANDBOX = True

# INIT_NCI must be True to use this option:
INIT_NCI_10000 = False


class Command(BaseCommand):
    help = 'loading some initial data'

    def handle(self, *args, **options):
        logger.info("loader")
        _loader()


def _loader():
    #init_structure_fields()
    init_name_type_data()
    init_response_type_data()
    init_dataset_context_type_data()
    init_organization_and_publisher_data()
    init_dataset()
    init_release()
    init_inchi_type()
    init_name_affinitiy_class()
    #init_structures()


def init_structures():


    names = ['ethanol', 'benzene', 'warfarin', 'guanine', 'tylenol', 'caffeine']
    name_type_obj = NameType.objects.get(id=7)

    for name in names:
        url = 'https://cactus.nci.nih.gov/chemical/structure/%s/pack' % name
        packed = requests.get(url)
        ens = Ens(packed.content)
        print(ens.get('E_SMILES'))
        logger.info("tuples: %s", name)
        name_obj, created = Name.objects.get_or_create(name=name)

        structure_obj, structure_created = Structure.objects.get_or_create_from_ens(ens)
        logger.info("Structure: %s %s" % (structure_obj, structure_created))

        structure_name_obj, name_created = StructureNameAssociation.objects.get_or_create(
            name=name_obj,
            affinity_class_id=1,
            structure=structure_obj,
            name_type=name_type_obj,
            confidence=100
        )

        # inchi_obj, inchi_created = InChI.objects.get_or_create(ens.get('E_STDINCHI'))
        # logger.info("InChI: %s %s" % (inchi_obj, inchi_created))

        # structure_inchi_obj, structure_inchi_created = StructureInChIs.objects.get_or_create(
        #     structure=structure_obj,
        #     inchi=inchi_obj
        # )


def init_response_type_data():
    with open('./etl/management/data/response-type.txt') as f:
        lines = f.readlines()
        response_type_dict = {}
        for line in lines:
            splitted = [e.strip() for e in line.split('|')]
            cleaned = [None if e == 'NULL' else e for e in splitted][1:-1]
            id, parent_type_id, url, method, parameter, base_mime_type = cleaned
            if parent_type_id:
                parent_type = response_type_dict[parent_type_id]
            else:
                parent_type = None
            response_type, created = ResponseType.objects.get_or_create(
                url=url,
            )
            response_type.parent_type = parent_type
            response_type.method = method
            response_type.parameter = parameter
            response_type.base_mime_type=base_mime_type
            response_type.save()
            response_type_dict[id] = response_type


def init_dataset_context_type_data():
    context_data = [
        ("other", None),
        ("screening", None),
        ("building blocks", None),
        ("toxicology", None),
        ("environmental", None),
        ("patent", None),
        ("journal", None),
        ("literature", None),
        ("natural product", None),
        ("imaging", None),
        ("contrast agent", None),
        ("meta", None),
        ("vendor", None),
        ("drug", None),
        ("SAR", None),
        ("QSAR", None),
        ("physicochemical property", None),
        ("ligand", None),
        ("small molecule", None),
        ("crystal-structure", None),
    ]

    for data in context_data:
        tag, description = data
        context_tag, created = ContextTag.objects.get_or_create(tag=tag)
        context_tag.description = description
        context_tag.save()


def init_name_type_data():

    regid, _ = NameType.objects.get_or_create(title="REGID", public_string="Registration ID", parent_id=None)
    name, _ = NameType.objects.get_or_create(title="NAME", public_string="Chemical Name or Synonym", parent_id=None)

    name_types = [
       # ('REGID', None, 'Registration ID'),
       # ('NAME', None, 'Chemical Name or Synonym'),
        ('PUBCHEM_IUPAC_NAME', name, 'PubChem IUPAC NAME'),
        ('PUBCHEM_IUPAC_OPENEYE_NAME', name, 'PubChem IUPAC OPENEYE NAME'),
        ('PUBCHEM_IUPAC_CAS_NAME', name, 'PubChem IUPAC CAS NAME'),
        ('PUBCHEM_IUPAC_TRADITIONAL_NAME', name, 'PubChem IUPAC TRADITIONAL NAME'),
        ('PUBCHEM_IUPAC_SYSTEMATIC_NAME', name, 'PubChem IUPAC SYSTEMATIC NAME'),
        ('PUBCHEM_GENERIC_REGISTRY_NAME', name, 'PubChem GENERIC REGISTRY NAME'),
        ('PUBCHEM_SUBSTANCE_SYNONYM', name, 'PubChem SUBSTANCE SYNONYM'),
        ('NSC_NUMBER', regid, 'NSC number'),
        ('NSC_NUMBER_PREFIXED', regid, 'NSC number prefixed'),
        ('PUBCHEM_SID', regid, 'PubChem SID'),
        ('PUBCHEM_CID', regid, 'PubChem CID'),
        #('MDL_NAME', regid, "MDL Name")
    ]


    for name_type in name_types:
        NameType.objects.get_or_create(title=name_type[0], public_string=name_type[2], parent=name_type[1])


def init_organization_and_publisher_data():

    nih, created = Organization.objects.get_or_create(
        name="U.S. National Institutes of Health",
    )
    nih.abbreviation = "NIH"
    nih.category = "government"
    nih.href = "https://www.nih.gov"
    nih.save()

    nci, created = Organization.objects.get_or_create(
        parent=nih,
        name="U.S. National Cancer Institute",

    )
    nci.abbreviation = "NCI"
    nci.category = "government"
    nci.href = "https://www.cancer.gov"
    nci.save()

    nlm, created = Organization.objects.get_or_create(
        parent=nih,
        name="U.S. National Library of Medicine",
    )
    nlm.abbreviation = "NLM"
    nlm.category = "government"
    nlm.href = "https://www.nlm.nih.gov"
    nlm.save()

    ncbi, created = Organization.objects.get_or_create(
        parent=nlm,
        name="U.S. National Center for Biotechnology Information",
    )
    ncbi.abbreviation = "NCBI"
    ncbi.category = "government"
    ncbi.href = "https://www.ncbi.nlm.nih.gov"
    ncbi.save()

    fiz, created = Organization.objects.get_or_create(
        name="FIZ Karlsruhe – Leibniz-Institut für Informationsinfrastruktur",
    )
    fiz.abbreviation = "FIZ Karlsruhe"
    fiz.category = "public"
    fiz.href = "https://www.fiz-karlsruhe.de"
    fiz.save()

    embl, created = Organization.objects.get_or_create(
        name="European Molecular Biology Laboratory",
    )
    embl.abbreviation = "EMBL"
    embl.category = "public"
    embl.href = "https://www.embl.org/"
    embl.save()

    ebi, created = Organization.objects.get_or_create(
        parent=embl,
        name="EMBL's European Bioinformatics Institute",
    )
    ebi.abbreviation = "EMBL-EBI"
    ebi.category = "public"
    ebi.href = "https://www.ebi.ac.uk/"
    ebi.save()

    # sito, created = Organization.objects.get_or_create(
    #     name="Markus Sitzmann Cheminformatics & IT Consulting",
    # )
    # sito.abbreviation = "SCIC"
    # sito.category = "other"
    # sito.href = ""
    # sito.save()

    ncicadd, created = Publisher.objects.get_or_create(
        name="NCI Computer-Aided Drug Design (CADD) Group",
        category = "group",
        href="https://cactus.nci.nih.gov",
    )
    ncicadd.address = "Frederick, MD 21702-1201, USA"
    ncicadd.organizations.add(nci, nih)
    ncicadd.save()

    mn1, created = Publisher.objects.get_or_create(
        parent=ncicadd,
        name="Marc Nicklaus",
        category="person",
        href="https://ccr.cancer.gov/staff-directory/marc-c-nicklaus",
        orcid="https://orcid.org/0000-0002-4775-7030"
    )
    mn1.email = "mn1ahelix@gmail.com"
    mn1.address = "Frederick, MD 21702-1201, USA"
    mn1.organizations.add(nci, nih)
    mn1.save()

    sitp, created = Publisher.objects.get_or_create(
        name="Markus Sitzmann",
        category="person",
        orcid="https://orcid.org/0000-0001-5346-1298"
    )
    sitp.email = "markus.sitzmann@gmail.com"
    #sitp.organizations.add(sito, fiz)
    sitp.save()

    pubchem_division, created = Publisher.objects.get_or_create(
        name="PubChem",
        category="division",
        href="https://pubchemdocs.ncbi.nlm.nih.gov/contact",
    )
    pubchem_division.address = "8600 Rockville Pike; Bethesda, MD  20894; USA"
    pubchem_division.email = "pubchem-help@ncbi.nlm.nih.gov"
    pubchem_division.organizations.add(ncbi, nlm)
    pubchem_division.save()

    chembl_team, created = Publisher.objects.get_or_create(
        name="ChEMBL Team",
        category="group",
        href="https://chembl.gitbook.io/chembl-interface-documentation/about",
    )
    chembl_team.organizations.add(embl, ebi)
    chembl_team.save()

    nci_dtp, created = Publisher.objects.get_or_create(
        name="DTP/NCI",
        category="division",
        href="https://dtp.cancer.gov/"
    )
    nci_dtp.organizations.add(nih, nci)
    nci_dtp.save()


def init_dataset():
    pubchem, created = Dataset.objects.get_or_create(
        name="PubChem",
        publisher=Publisher.objects.get(name="PubChem"),
    )
    pubchem.href = "https://pubchem.ncbi.nlm.nih.gov/"
    pubchem.description = "PubChem is an open chemistry database at the National Institutes of Health (NIH)"
    pubchem.context_tags.add(ContextTag.objects.get(tag="meta"))
    pubchem.save()

    chembl, created = Dataset.objects.get_or_create(
        name="ChEMBL",
        publisher=Publisher.objects.get(name="ChEMBL Team"),
    )
    chembl.href = "https://www.ebi.ac.uk/chembl/"
    chembl.description = "ChEMBL is a manually curated database of bioactive molecules with drug-like properties"
    chembl.context_tags.add(ContextTag.objects.get(tag="drug"))
    chembl.save()

    ncidb, created = Dataset.objects.get_or_create(
        name="DTP/NCI",
        publisher=Publisher.objects.get(name="DTP/NCI"),
    )
    ncidb.href = "https://dtp.cancer.gov/"
    ncidb.description = "NCI database"
    ncidb.context_tags.add(ContextTag.objects.get(tag="screening"))
    ncidb.save()

    sandbox, created = Dataset.objects.get_or_create(
        name="SANDBOX",
        publisher=Publisher.objects.get(name="Markus Sitzmann"),
    )
    sandbox.href = "https://sandbox.test/"
    sandbox.description = "sandbox"
    sandbox.context_tags.add(ContextTag.objects.get(tag="screening"))
    sandbox.save()


def init_release(
        mini=MINI,
        init_pubchem_compound=INIT_PUBCHEM_COMPOUND,
        init_pubchem_substance=INIT_PUBCHEM_SUBSTANCE,
        init_chembl=INIT_CHEMBL,
        init_nci=INIT_NCI,
        init_nci_10000=INIT_NCI_10000,
        init_sandbox=INIT_SANDBOX
    ):

    if init_chembl:
        chembl_preprocessor, created = StructureFileCollectionPreprocessor.objects.get_or_create(
            params=json.dumps({
                'regid': {'field': 'chembl_id', 'type': 'REGID'},
                'names': []
            })
        )

        chembl_db, created = Release.objects.get_or_create(
            dataset=Dataset.objects.get(name="ChEMBL"),
            publisher=Publisher.objects.get(name="ChEMBL Team"),
            version=29,
            released=None,
            downloaded=datetime.datetime(2022, 2, 1),
        )
        chembl_db.classification = 'public'
        chembl_db.status = 'active'
        chembl_db.description = "ChEMBL database"
        chembl_db.save()

        if mini:
            chembl_collection, created = StructureFileCollection.objects.get_or_create(
                release=chembl_db,
                file_location_pattern_string="MINI/chembl/29/chembl_29.sdf"
            )
        else:
            chembl_collection, created = StructureFileCollection.objects.get_or_create(
                release=chembl_db,
                file_location_pattern_string="chembl/29/chembl_29/chembl_29.*.sdf.gz"
            )
            chembl_collection.save()
        chembl_collection.preprocessors.add(
            chembl_preprocessor
        )
        chembl_collection.save()

    pubchem_ext_datasource_preprocessor, created = StructureFileCollectionPreprocessor.objects.get_or_create(
        name="pubchem_ext_datasource",
    )

    if init_pubchem_compound:
        pubchem_compound_preprocessor, created = StructureFileCollectionPreprocessor.objects.get_or_create(
            params=json.dumps({
                'regid': {'field': 'PUBCHEM_COMPOUND_CID', 'type': 'PUBCHEM_CID'},
                'names': [
                    {'field': 'PUBCHEM_IUPAC_OPENEYE_NAME', 'type': 'PUBCHEM_IUPAC_OPENEYE_NAME'},
                    {'field': 'PUBCHEM_IUPAC_CAS_NAME', 'type': 'PUBCHEM_IUPAC_CAS_NAME'},
                    {'field': 'PUBCHEM_IUPAC_NAME', 'type': 'PUBCHEM_IUPAC_NAME'},
                    {'field': 'PUBCHEM_IUPAC_SYSTEMATIC_NAME', 'type': 'PUBCHEM_IUPAC_SYSTEMATIC_NAME'},
                    {'field': 'PUBCHEM_IUPAC_TRADITIONAL_NAME', 'type': 'PUBCHEM_IUPAC_TRADITIONAL_NAME'},
                ]
            })
        )

        pubchem_compound, created = Release.objects.get_or_create(
            dataset=Dataset.objects.get(name="PubChem"),
            publisher=Publisher.objects.get(name="PubChem"),
            name="PubChem Compound",
            downloaded=datetime.datetime(2022, 2, 1),
        )
        pubchem_compound.classification = 'public'
        pubchem_compound.status = 'active'
        pubchem_compound.description = "PubChem Compound database"
        pubchem_compound.save()

        if mini:
            pubchem_compound_collection, created = StructureFileCollection.objects.get_or_create(
                release=pubchem_compound,
                file_location_pattern_string="MINI/pubchem/compound/Compound_*.sdf"
            )
        else:
            pubchem_compound_collection, created = StructureFileCollection.objects.get_or_create(
                release=pubchem_compound,
                file_location_pattern_string="pubchem/compound/Compound_*/*.sdf.gz"
            )
        pubchem_compound_collection.preprocessors.add(
            pubchem_compound_preprocessor
        )
        pubchem_compound_collection.save()

    if init_pubchem_substance:

        pubchem_substance_preprocessor, created = StructureFileCollectionPreprocessor.objects.get_or_create(
            params=json.dumps({
                'regid': {'field': 'PUBCHEM_SUBSTANCE_ID', 'type': 'PUBCHEM_SID'},
                'names': [
                    {'field': 'PUBCHEM_SUBSTANCE_SYNONYM', 'type': 'PUBCHEM_SUBSTANCE_SYNONYM'},
                    {'field': 'PUBCHEM_GENERIC_REGISTRY_NAME', 'type': 'PUBCHEM_GENERIC_REGISTRY_NAME'},
                ]
            })
        )

        pubchem_substance, created = Release.objects.get_or_create(
            dataset=Dataset.objects.get(name="PubChem"),
            publisher=Publisher.objects.get(name="PubChem"),
            name="PubChem Substance",
            released=None,
            downloaded=datetime.datetime(2022, 2, 1),
        )
        pubchem_substance.classification = 'public'
        pubchem_substance.status = 'active'
        pubchem_substance.description = "PubChem Substance database"
        pubchem_substance.save()

        if mini:
            pubchem_substance_collection, created = StructureFileCollection.objects.get_or_create(
                release=pubchem_substance,
                file_location_pattern_string="MINI/pubchem/substance/Substance_*.sdf"
            )
        else:
            pubchem_substance_collection, created = StructureFileCollection.objects.get_or_create(
                release=pubchem_substance,
                file_location_pattern_string="pubchem/substance/Substance_*/*.sdf.gz"
            )
        pubchem_substance_collection.preprocessors.add(
            pubchem_ext_datasource_preprocessor,
            pubchem_substance_preprocessor
        )
        pubchem_substance_collection.save()

    if init_nci:
        nci_db_preprocessor, created = StructureFileCollectionPreprocessor.objects.get_or_create(
            params=json.dumps({
                'regid': {'field': 'PUBCHEM_EXT_DATASOURCE_REGID', 'type': 'NSC_NUMBER'},
                'names': [
                    {'field': 'PUBCHEM_SUBSTANCE_SYNONYM', 'type': 'PUBCHEM_SUBSTANCE_SYNONYM'},
                    {'field': 'PUBCHEM_GENERIC_REGISTRY_NAME', 'type': 'PUBCHEM_GENERIC_REGISTRY_NAME'},
                ]
            })
        )

        nci_db, created = Release.objects.get_or_create(
            dataset=Dataset.objects.get(name="DTP/NCI"),
            publisher=Publisher.objects.get(name="PubChem"),
            name="DTP/NCI",
            released=None,
            downloaded=datetime.datetime(2022, 2, 1),
        )
        nci_db.description = 'NCI Database downloaded from PubChem'
        nci_db.classification = 'public'
        nci_db.status = 'active'
        nci_db.description = "NCI database"
        nci_db.save()

        open_nci_db, created = Release.objects.get_or_create(
            dataset=Dataset.objects.get(name="DTP/NCI"),
            publisher=Publisher.objects.get(name="NCI Computer-Aided Drug Design (CADD) Group"),
            released=None,
            downloaded=datetime.datetime(2022, 2, 1),
        )
        open_nci_db.name = "Open NCI Database"
        open_nci_db.classification = 'public'
        open_nci_db.status = 'active'
        open_nci_db.description = "NCI database"
        open_nci_db.save()

        if mini:
            if init_nci_10000:
                fname = "MINI/nci/NCI_DTP/NCI_DTP.*.10000.sdf.gz"
            else:
                fname = "MINI/nci/NCI_DTP/NCI_DTP.sdf"
            open_nci_db_collection, created = StructureFileCollection.objects.get_or_create(
                release=open_nci_db,
                file_location_pattern_string=fname
            )
            open_nci_db_collection.save()
        else:
            open_nci_db_collection, created = StructureFileCollection.objects.get_or_create(
                release=open_nci_db,
                file_location_pattern_string="nci/NCI_DTP/*.sdf.gz"
            )
            open_nci_db_collection.save()

        open_nci_db_collection.preprocessors.add(
            nci_db_preprocessor
        )
        open_nci_db_collection.save()

    if init_sandbox:
        sandbox_preprocessor, created = StructureFileCollectionPreprocessor.objects.get_or_create(
            params=json.dumps({
                'regid': {'field': 'E_ID', 'type': 'REGID'},
                'names': [
                    {'field': 'E_NAME', 'type': 'NAME'},
                    {'field': 'E_SYNONYM', 'type': 'NAME'},
                    {'field': 'E_ZINC_ID', 'type': 'REGID'},
                    {'field': 'E_NSC_NUMBER', 'type': 'NSC_NUMBER'},
                ]
            })
        )

        sandbox_db, created = Release.objects.get_or_create(
            dataset=Dataset.objects.get(name="SANDBOX"),
            publisher=Publisher.objects.get(name="Markus Sitzmann"),
            name="Sandbox Release",
            released=None,
            downloaded=datetime.datetime(2023, 5, 1),
        )
        sandbox_db.description = 'Sandbox'
        sandbox_db.classification = 'public'
        sandbox_db.status = 'active'
        sandbox_db.save()

        sandbox_db_collection, created = StructureFileCollection.objects.get_or_create(
            release=sandbox_db,
            file_location_pattern_string="sandbox/structures.sdf"
        )
        sandbox_db_collection.save()

        sandbox_db_collection.preprocessors.add(
            sandbox_preprocessor
        )
        sandbox_db_collection.save()


def init_name_affinitiy_class():

    affinitiy_classes = [
        ('exact', 0, 'Exact'),
        ('narrow', 1, 'Narrow'),
        ('broad', 2, 'Broad'),
        ('unknown', 5, 'Unknown'),
        ('unspecified', 4, 'Unspecified'),
        ('generic', 3, 'Generic'),
        ('related', 3, 'Related'),
    ]

    for item in affinitiy_classes:
        c, created = NameAffinityClass.objects.get_or_create(
            title=item[0]
        )
        c.rank = item[1]
        c.description = item[2]
        c.save()

def init_inchi_type():

    standard_inchi_type, created = InChIType.objects.get_or_create(
        title="standard"
    )
    standard_inchi_type.software_version = "1.06"
    standard_inchi_type.description = "Standard InChI"
    standard_inchi_type.is_standard = True
    standard_inchi_type.donotaddh = True
    standard_inchi_type.save()

    original_inchi_type, created = InChIType.objects.get_or_create(
        title="original"
    )
    original_inchi_type.software_version = "1.06"
    original_inchi_type.description = "InChI with FixedH layer and RecMet option"
    original_inchi_type.is_standard = False
    original_inchi_type.donotaddh = True
    original_inchi_type.fixedh = True
    original_inchi_type.recmet = True
    original_inchi_type.save()

    tauto_inchi_type, created = InChIType.objects.get_or_create(
        title="xtauto"
    )
    tauto_inchi_type.software_version = "1.06"
    tauto_inchi_type.description = "experimental InChI with FixedH layer, RecMet option and experimental tauto options" \
                                   "KET and T15 options set"
    tauto_inchi_type.is_standard = False
    tauto_inchi_type.donotaddh = True
    tauto_inchi_type.fixedh = True
    tauto_inchi_type.recmet = True
    tauto_inchi_type.ket = True
    tauto_inchi_type.t15 = True
    tauto_inchi_type.save()

    tautox_inchi_type, created = InChIType.objects.get_or_create(
        title="xtautox"
    )
    tautox_inchi_type.software_version = "1.06T"
    tautox_inchi_type.description = "experimental InChI with FixedH layer, RecMet option and experimental tauto options " \
                                    "KET, T15 including NCI tautomer options set"
    tautox_inchi_type.is_standard = False
    tautox_inchi_type.donotaddh = True
    tautox_inchi_type.fixedh = True
    tautox_inchi_type.recmet = True
    tautox_inchi_type.ket = True
    tautox_inchi_type.t15 = True
    tautox_inchi_type.pt_22_00 = True
    tautox_inchi_type.pt_16_00 = True
    tautox_inchi_type.pt_06_00 = True
    tautox_inchi_type.pt_39_00 = True
    tautox_inchi_type.pt_13_00 = True
    tautox_inchi_type.pt_18_00 = True
    tautox_inchi_type.save()


def init_structure_fields():

    fields = [
        'E_WEIGHT',
        'E_TPSA',
        'E_TAUTOMER_COUNT',
        'E_STEREO_COUNT',
        'E_STDINCHIKEY',
        'E_STDINCHI',
        'E_SCREEN',
        'E_PUBCHEM_XREF_EXT_ID',
        'E_*PUBCHEM_XLOGP3_AA*',
        'E_PUBCHEM_XLOGP3',
        'E_*PUBCHEM_SUBSTANCE_VERSION*',
        'E_*PUBCHEM_SUBSTANCE_SYNONYM*',
        'E_*PUBCHEM_SUBSTANCE_ID*',
        'E_PUBCHEM_SUBSTANCE_COMMENT',
        'E_*PUBCHEM_OPENEYE_ISO_SMILES*',
        'E_*PUBCHEM_OPENEYE_CAN_SMILES*',
        'E_*PUBCHEM_IUPAC_OPENEYE_NAME*',
        'E_*PUBCHEM_IUPAC_NAME_MARKUP*',
        'E_*PUBCHEM_IUPAC_CAS_NAME*',
        'E_PUBCHEM_GENERIC_REGISTRY_NAME',
        'E_PUBCHEM_EXT_SUBSTANCE_URL',
        'E_PUBCHEM_EXT_DATASOURCE_URL',
        'E_PUBCHEM_EXT_DATASOURCE_REGID',
        'E_PUBCHEM_EXT_DATASOURCE_NAME',
        'E_*PUBCHEM_COORDINATE_TYPE*',
        'E_*PUBCHEM_COMPOUND_ID_TYPE*',
        'E_PUBCHEM_COMPOUND_CANONICALIZED',
        'E_*PUBCHEM_COMPONENT_COUNT*',
        'E_*PUBCHEM_CID_ASSOCIATIONS*',
        'E_NROTBONDS',
        'E_NHDONORS',
        'E_NHACCEPTORS',
        'E_MONOISOTOPIC_MASS',
        'E_IUPAC_TRADITIONAL_NAME',
        'E_IUPAC_SYSTEMATIC_NAME',
        'E_IUPAC_PREFERRED_NAME',
        'E_ISOTOPE_COUNT',
        'E_HEAVY_ATOM_COUNT',
        'E_FORMULA',
        'E_EXACT_MASS',
        'E_COMPLEXITY',
        'E_CID',
        'E_CHEMBL_ID',
        'E_CHARGE'
    ]

    for field in fields:
        f, created = StructureFileField.objects.get_or_create(
            field_name=field
        )