import datetime
import logging
import os

from django.core.management.base import BaseCommand, CommandError

from custom.cactvs import CactvsHash, CactvsMinimol
#from database.models import
from etl.models import StructureFileCollection, StructureFileCollectionPreprocessor, StructureFileField, \
    ReleaseNameField
from structure.models import  ResponseType
from resolver.models import InChI, Organization, Publisher, Structure, Name, NameType, StructureNameAssociation, ContextTag, \
    Dataset, Release, InChIType

from pycactvs import Ens

logger = logging.getLogger('cirx')


class Command(BaseCommand):
    help = 'loading some initial data'

    def handle(self, *args, **options):
        logger.info("loader")
        _loader()


def _loader():
    init_structure_fields()
    init_name_type_data()
    init_response_type_data()
    init_dataset_context_type_data()
    init_organization_and_publisher_data()
    init_dataset()
    init_release()
    init_inchi_type()
    #init_structures()


def init_structures():
    names = ['ethanol', 'benzene', 'warfarin', 'guanine', 'tylenol', 'caffeine']
    name_type_obj = NameType.objects.get(id=7)

    for name in names:
        ens = Ens(name)
        logger.info("tuples: %s", name)
        name_obj, created = Name.objects.get_or_create(name=name)

        structure_obj, structure_created = Structure.objects.get_or_create_from_ens(ens)
        logger.info("Structure: %s %s" % (structure_obj, structure_created))

        structure_name_obj, name_created = StructureNameAssociation.objects.get_or_create(
            name=name_obj,
            structure=structure_obj,
            name_type=name_type_obj
        )

        inchi_obj, inchi_created = InChI.objects.get_or_create(ens.get('E_STDINCHI'))
        logger.info("InChI: %s %s" % (inchi_obj, inchi_created))

        # structure_inchi_obj, structure_inchi_created = StructureInChIs.objects.get_or_create(
        #     structure=structure_obj,
        #     inchi=inchi_obj
        # )


def init_response_type_data():
    with open('./structure/management/data/response-type.txt') as f:
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
            response_type = ResponseType(
                parent_type=parent_type,
                url=url,
                method=method,
                parameter=parameter,
                base_mime_type=base_mime_type
            )
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
    name_types = [
        ('REGID', 'Registration ID'),
        ('PUBCHEM_IUPAC_NAME', 'PubChem IUPAC NAME'),
        ('PUBCHEM_IUPAC_OPENEYE_NAME', 'PubChem IUPAC OPENEYE NAME'),
        ('PUBCHEM_IUPAC_CAS_NAME', 'PubChem IUPAC CAS NAME'),
        ('PUBCHEM_IUPAC_TRADITIONAL_NAME', 'PubChem IUPAC TRADITIONAL NAME'),
        ('PUBCHEM_IUPAC_SYSTEMATIC_NAME', 'PubChem IUPAC SYSTEMATIC NAME'),
        ('PUBCHEM_GENERIC_REGISTRY_NAME', 'PubChem GENERIC REGISTRY NAME'),
        ('PUBCHEM_SUBSTANCE_SYNONYM', 'PubChem SUBSTANCE SYNONYM'),
        ('NSC_NUMBER', 'NSC number'),
        ('NSC_NUMBER_PREFIXED', 'NSC number prefixed'),
        ('PUBCHEM_SID', 'PubChem SID'),
        ('PUBCHEM_CID', 'PubChem CID'),
    ]

    for name_type in name_types:
        NameType.objects.get_or_create(id=name_type[0], public_string=name_type[1])


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


def init_release(
        mini=False,
        init_pubchem_compound=False,
        init_pubchem_substance=True,
        init_chembl=False,
        init_nci=False
    ):

    pubchem_ext_datasource_preprocessor, created = StructureFileCollectionPreprocessor.objects.get_or_create(
        preprocessor_name="pubchem_ext_datasource",
    )

    if init_pubchem_compound:
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

        name_type = NameType.objects.get(id="PUBCHEM_CID")
        structure_file_field = StructureFileField.objects.filter(field_name="E_CID").first()
        release_name_field, created = ReleaseNameField.objects.get_or_create(
            release=pubchem_compound,
            structure_file_field=structure_file_field,
            name_type=name_type
        )
        release_name_field.is_regid = True
        release_name_field.save()

        if mini:
            pubchem_compound_collection, created = StructureFileCollection.objects.get_or_create(
                release=pubchem_compound,
                file_location_pattern_string="pubchem/compound/Compound_*.mini.sdf"
            )
        else:
            pubchem_compound_collection, created = StructureFileCollection.objects.get_or_create(
                release=pubchem_compound,
                file_location_pattern_string="pubchem/compound/Compound_*.sdf.gz"
            )
        pubchem_compound_collection.save()

    if init_pubchem_substance:
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

        name_type = NameType.objects.get(id="PUBCHEM_SID")
        structure_file_field = StructureFileField.objects.filter(field_name="E_*PUBCHEM_SUBSTANCE_ID*").first()
        release_name_field, created = ReleaseNameField.objects.get_or_create(
            release=pubchem_substance,
            structure_file_field=structure_file_field,
            name_type=name_type
        )
        release_name_field.is_regid = True
        release_name_field.save()

        if mini:
            pubchem_substance_collection, created = StructureFileCollection.objects.get_or_create(
                release=pubchem_substance,
                file_location_pattern_string="pubchem/substance/Substance_*.mini.sdf"
            )
        else:
            pubchem_substance_collection, created = StructureFileCollection.objects.get_or_create(
                release=pubchem_substance,
                file_location_pattern_string="pubchem/substance/Substance_*.sdf.gz"
            )
        pubchem_substance_collection.preprocessors.add(pubchem_ext_datasource_preprocessor)
        pubchem_substance_collection.save()

    if init_chembl:
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
                file_location_pattern_string="chembl/29/chembl_29.mini.sdf"
            )
            chembl_collection.save()
        else:
            chembl_collection, created = StructureFileCollection.objects.get_or_create(
                release=chembl_db,
                file_location_pattern_string="chembl/29/chembl_29.sdf.gz"
            )
            chembl_collection.save()

    if init_nci:
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
            open_nci_db_collection, created = StructureFileCollection.objects.get_or_create(
                release=open_nci_db,
                file_location_pattern_string="nci/NCI_DTP.mini.sdf"
            )
            open_nci_db_collection.save()
        else:
            open_nci_db_collection, created = StructureFileCollection.objects.get_or_create(
                release=open_nci_db,
                file_location_pattern_string="nci/NCI_DTP.sdf.gz"
            )
            open_nci_db_collection.save()


def init_inchi_type():

    standard_inchi_type, created = InChIType.objects.get_or_create(
        id="standard",
    )
    standard_inchi_type.software_version = "1.06"
    standard_inchi_type.description = "Standard InChI"
    standard_inchi_type.is_standard = True
    standard_inchi_type.donotaddh = True
    standard_inchi_type.save()

    original_inchi_type, created = InChIType.objects.get_or_create(
        id="original",

    )
    original_inchi_type.software_version = "1.06",
    original_inchi_type.description = "InChI with FixedH layer and RecMet option",
    original_inchi_type.is_standard = False
    original_inchi_type.donotaddh = True
    original_inchi_type.fixedh = True
    original_inchi_type.recmet = True
    original_inchi_type.save()

    tauto_inchi_type, created = InChIType.objects.get_or_create(
        id="xtauto"
    )
    tauto_inchi_type.software_version = "1.06",
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
        id="xtautox",

    )
    tautox_inchi_type.software_version = "1.06T",
    tautox_inchi_type.description = "experimental InChI with FixedH layer, RecMet option and experimental tauto options " \
                                    "KET, T15 including NCI tautomer options set",
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