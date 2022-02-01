import re
import urllib

import logging
from typing import List, Dict

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.db import NotSupportedError
from pycactvs import Ens, Dataset

from custom.cactvs import CactvsHash
from structure.cas.number import String as CASNumber
from structure.inchi.identifier import InChIString, InChIKey, InChIError
from structure.minimol import Minimol
from structure.ncicadd.identifier import Identifier, RecordID, CompoundID
from structure.packstring import PackString
from structure.smiles import SMILES

logger = logging.getLogger('cirx')



#import cas.number
#import file.sdf
#import inchi.identifier
#import ncicadd.identifier
#import packstring
#import smiles

from database.models import Database
from structure.models import Structure2, Record, Compound, Name, StructureNames
from resolver.models import InChI


# from sets import Set

# try:
#     from jpype import *
# except:
#     pass

# _cactvs_loader = __import__(settings.CACTVS_PATH, globals(), locals(), settings.CACTVS_FROMLIST)
# Cactvs = _cactvs_loader.Cactvs
# Ens = _cactvs_loader.Ens
# Dataset = _cactvs_loader.Dataset
# Molfile = _cactvs_loader.Molfile
# CactvsError = _cactvs_loader.CactvsError

# import djangosphinx.apis.current as sphinxapi


class ChemicalName:

    def __init__(self, exact_string=None, pattern=None):

        self.names = None

        if pattern:
            self.pattern = pattern
            self.query_set = Name_Fulltext.search.query(string=pattern).set_options(
                mode=sphinxapi.SPH_MATCH_EXTENDED).select_related()
            self.metadata = self.query_set._sphinx
            self.names = self.query_set[0:100]
            structure_name_objects = StructureNames.objects.filter(name__in=self.names)
            structure_names = {}
            structure_rank = 1
            for structure_name in structure_name_objects:
                try:
                    k = structure_name.structure
                except:
                    continue
                if structure_names.has_key(k):
                    structure_names[k]['names'].append(structure_name.name)
                else:
                    structure_names[k] = {}
                    structure_names[k]['names'] = [structure_name.name, ]
                    structure_names[k]['rank'] = structure_rank
                    structure_rank += 1
            structure_name_list = []
            for structure, name_list in structure_names.items():
                name_list['structure'] = structure
                structure_name_list.append(name_list)
            self.structure_names = structure_name_list


class ChemicalStructure:
    """Container class to keep a CACTVS ensemble and a Structure model object of the
       of the same chemical structure together"""

    def __init__(self, resolved: Structure2 = None, ens: Ens = None):
        self._resolved = resolved
        self._ens = ens
        self._metadata = {}
        if resolved and not ens:
            ens = resolved.minimol.ens
            hashisy = Identifier(hashcode=ens.get('E_HASHISY')).integer
            self._ens = ens
            self.hashisy = hashisy
        elif ens and not resolved:
            hashisy = Identifier(hashcode=ens.get('E_HASHISY')).integer
            self.hashisy = hashisy
            try:
                self._resolved = Structure2.objects.get(hashisy=CactvsHash(hashisy))
            except Exception as e:
                #self.resolved = None
                self._resolved = Structure2(minimol=ens.get('E_MINIMOL'), hashisy=hashisy)
        elif ens and resolved:
            h1 = resolved.hashisy.int()
            h2 = Identifier(hashcode=ens.get('E_HASHISY')).integer
            if not h1 == h2:
                raise ChemicalStructureError('ens and object hashcode mismatch')

    @property
    def ens(self) -> Ens:
        if self._ens:
            return self._ens
        else:
            return Ens(self._resolved.minimol)

    @property
    def metadata(self) -> dict:
        return self._metadata


class ChemicalStructureError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ChemicalString:

    class Interpretation:

        def __init__(self):
            self.type = ""
            self.type_string = ""
            self.query_object = None
            self.structures = []
            self.description_list = []
            self.id = 0

        def __repr__(self):
            return "<< %s (number of structures: %s) >>" % (self.type, self.structures)

    def __init__(
            self,
            string,
            operator=None,
            resolver_list=None,
            operator_list=None,
            simple: bool = False,
            debug: bool = False
    ):
        self.string = string.strip()
        self._interpretations = []
        if resolver_list:
            pass
        else:
            resolver_list = settings.AVAILABLE_RESOLVERS

        if operator_list:
            pass
        else:
            operator_list = [
                'tautomers',
                'remove_hydrogens',
                'add_hydrogens',
                'ficts',
                'ficus',
                'uuuuu',
                'parent',
                'normalize',
                'stereoisomers',
                'scaffold_sequence',
                'no_stereo'
            ]
        self.operator = None
        if not operator:
            for o in operator_list:
                expression = '^(?P<operator>%s):(?P<string>.+)$' % o
                pattern = re.compile(expression, re.IGNORECASE)
                match = pattern.search(self.string)
                if match:
                    self.operator = match.group('operator')
                    self.string = match.group('string')
                    break
        else:
            self.operator = operator
        i = 1

        for resolver in resolver_list:
            if not debug:
                try:
                    resolver_method = getattr(self, '_resolver_' + resolver)
                    interpretation = self.Interpretation()
                    if resolver_method(interpretation):
                        interpretation.id = i
                        if self.operator:
                            operator_method = getattr(self, '_operator_' + self.operator)
                            interpretation = operator_method(interpretation)
                        self._interpretations.append(interpretation)
                        i += 1
                except Exception as e:
                    logger.error(e)
                    pass
            else:
                resolver_method = getattr(self, '_resolver_' + resolver)
                interpretation = self.Interpretation()
                if resolver_method(interpretation):
                    interpretation.id = i
                    if self.operator:
                        operator_method = getattr(self, '_operator_' + self.operator)
                        interpretation = operator_method(interpretation)
                    self._interpretations.append(interpretation)
                    i += 1
            if simple and len(self._interpretations):
                break
        return

    @property
    def interpretations(self) -> List[Interpretation]:
        return self._interpretations

    def _resolver_hashisy(self, interpretation_object):
        pattern = re.compile('(?P<hashcode>^[0-9a-fA-F]{16}$)', re.IGNORECASE)
        match = pattern.search(self.string)
        hashcode = match.group('hashcode')
        hashcode_int = int(match.group('hashcode'), 16)
        chemical_structure = ChemicalStructure(resolved=Structure2.objects.get(hashisy=hashcode_int))
        if chemical_structure:
            chemical_structure._metadata = {
                'query_type': 'hashisy',
                'query_search_string': 'Cactvs HASHISY hashcode',
                'query_object': hashcode,
                'query_string': self.string,
                'description': hashcode
            }
            interpretation_object.structures.append(chemical_structure)
            return True
        return False

    def _resolver_ncicadd_rid(self, interpretation_object):
        record_id = RecordID(string=self.string)
        record = Record.objects.get(id=record_id.rid)
        chemical_structure = ChemicalStructure(resolved=record.get_structure())
        if chemical_structure:
            chemical_structure._metadata = {
                'query_type': 'ncicadd_rid',
                'query_search_string': 'NCI/CADD Record ID',
                'query_object': record_id,
                'query_string': self.string,
                'description': record.id,
                'record': record
            }
            interpretation_object.structures.append(chemical_structure)
            return True
        return False

    def _resolver_ncicadd_cid(self, interpretation_object):
        compound_id = CompoundID(string=self.string)
        compound = Compound.objects.get(id=compound_id.cid)
        structure = compound.get_structure()
        chemical_structure = ChemicalStructure(resolved=structure)
        if chemical_structure:
            chemical_structure._metadata = {
                'query_type': 'ncicadd_cid',
                'query_search_string': 'NCI/CADD Compound ID',
                'query_object': compound_id,
                'query_string': self.string,
                'description': compound.id,
                'compound': compound
            }
            interpretation_object.structures.append(chemical_structure)
            return True
        return False

    def _resolver_ncicadd_sid(self, interpretation_object):
        pattern = re.compile('^NCICADD(_|:)SID=(?P<sid>\d+$)', re.IGNORECASE)
        match = pattern.search(self.string)
        if match:
            structure_id = match.group('sid')
            structure = Structure2.objects.get(id=structure_id)
            chemical_structure = ChemicalStructure(resolved=structure)
            if chemical_structure:
                chemical_structure._metadata = {
                    'query_type': 'ncicadd_sid',
                    'query_search_string': 'NCI/CADD Structure ID',
                    'query_object': structure.id,
                    'query_string': self.string,
                    'description': self.string,
                }
                interpretation_object.structures.append(chemical_structure)
                return True
        return False

    def _resolver_ncicadd_identifier(self, interpretation_object):
        identifier = Identifier(string=self.string)
        structure = Structure2.objects.get(hashisy=identifier.integer)
        chemical_structure = ChemicalStructure(resolved=structure)
        if chemical_structure:
            identifier_search_type_string = 'NCI/CADD Identifier (%s)' % identifier.type
            chemical_structure._metadata = {
                'query_type': 'ncicadd_identifier',
                'query_search_string': identifier_search_type_string,
                'query_object': identifier,
                'query_string': self.string,
                'description': identifier
            }
            interpretation_object.structures.append(chemical_structure)
            return True
        return False

    def _resolver_stdinchikey(self, interpretation_object):
        #identifier = InChIKey(key=self.string)
        identifier = InChI.create(key=self.string)
        # if not k.is_standard:
        #	return False
        #inchikey_query = identifier.query()
        inchikeys = InChI.objects.filter(id=identifier.id)
        structure_set = []
        description_list = []
        for inchikey in inchikeys:
            #structures = inchikey.structure_set.all()
            structures: List[Structure2] = inchikey.structures.all()
            full_key = InChIKey(
                block1=identifier.block1,
                block2=identifier.block2,
                block3=identifier.block3,
            )
            for structure in structures:
                # ens = Ens(self.cactvs, structure.object.minimol)
                chemical_structure = ChemicalStructure(resolved=structure)
                chemical_structure._metadata = {
                    'query_type': 'stdinchikey',
                    'query_search_string': 'Standard InChIKey',
                    'query_object': identifier,
                    'query_string': self.string,
                    'description': full_key.element['well_formatted']
                }
                structure_set.append(chemical_structure)
        if inchikeys:
            interpretation_object.structures = structure_set
            return True
        return False

    def _resolver_stdinchi(self, interpretation_object):
        identifier = InChI(string=self.string)
        if identifier and self._structure_representation_resolver(interpretation_object):
            chemical_structure = interpretation_object.structures[0]
            chemical_structure._metadata = {
                'query_type': 'stdinchi',
                'query_search_string': 'Standard InChI',
                'query_object': identifier,
                'query_string': self.string,
                'description': identifier.string
            }
            return True
        return False

    def _resolver_chemnavigator_sid(self, interpretation_object):
        pattern = re.compile('^ChemNavigator(_|:)SID=(?P<sid>\d+$)', re.IGNORECASE)
        match = pattern.search(self.string)
        if match:
            chemnavigator_id = match.group('sid')
            # TODO: id = 9 is dangerous
            database = Database.objects.get(id=9)
            record = Record.objects.get(database_record_external_identifier=chemnavigator_id, database=database)
            structure = record.get_structure()
            chemical_structure = ChemicalStructure(resolved=structure)
            if chemical_structure:
                chemical_structure._metadata = {
                    'query_type': 'chemnavigator_sid',
                    'query_search_string': 'ChemNavigator SID',
                    'query_object': self.string,
                    'query_string': self.string,
                    'description': self.string,
                }
                interpretation_object.structures.append(chemical_structure)
                return True
        return False

    def _resolver_pubchem_sid(self, interpretation_object):
        pattern = re.compile('^PubChem(_|:)SID=(?P<sid>\d+$)', re.IGNORECASE)
        match = pattern.search(self.string)
        if match:
            pubchem_sid = match.group('sid')
            # database = Database.objects.get(id=9)
            # TODO: dirty, very dirty:
            record = Record.objects.get(release_record_external_identifier=pubchem_sid)
            structure = record.get_structure()
            chemical_structure = ChemicalStructure(resolved=structure)
            if chemical_structure:
                chemical_structure._metadata = {
                    'query_type': 'pubchem_sid',
                    'query_search_string': 'PubChem SID',
                    'query_object': self.string,
                    'query_string': self.string,
                    'description': self.string,
                }
                interpretation_object.structures.append(chemical_structure)
                return True
        return False

    def _resolver_emolecules_vid(self, interpretation_object):
        pattern = re.compile('^eMolecules(_|:)(ID|VID)=(?P<vid>\d+$)', re.IGNORECASE)
        match = pattern.search(self.string)
        if match:
            emolecules_id = match.group('vid')
            database = Database.objects.get(id=120)
            record = Record.objects.get(database_record_external_identifier=emolecules_id, database=database)
            structure = record.get_structure()
            chemical_structure = ChemicalStructure(resolved=structure)
            if chemical_structure:
                chemical_structure._metadata = {
                    'query_type': 'emolecules_vid',
                    'query_search_string': 'eMolecules VID',
                    'query_object': self.string,
                    'query_string': self.string,
                    'description': self.string,
                }
                interpretation_object.structures.append(chemical_structure)
                return True
        return False

    # def _resolver_chemspider_id(self, interpretation_object):
    #     pattern = re.compile('^ChemSpider(_|:)ID=(?P<csid>\d+$)', re.IGNORECASE)
    #     match = pattern.search(self.string)
    #     s = self.string
    #     if match:
    #         chemspider_id = match.group('csid')
    #         resolver = ExternalResolver(name="chemspider",
    #                                     url_scheme="http://www.chemspider.com/inchi-resolver/REST.ashx?q=%s&of=%s")
    #         response = resolver.resolve(chemspider_id, 'sdf')
    #
    #         if response['status'] and response['string']:
    #             # self.string = response['string']
    #             if self._structure_representation_resolver(interpretation_object, representation=response['string']):
    #                 structure = interpretation_object.structures[0]
    #                 structure.metadata = {
    #                     'query_type': 'chemspider_id',
    #                     'query_search_string': 'ChemSpider ID',
    #                     'query_object': response,
    #                     'query_string': s,
    #                     'description': s
    #                 }
    #                 # self.string = ''
    #                 return True
    #     return False

    # def _resolver_chemspider_stdinchikey(self, interpretation_object):
    #     k = inchi.identifier.Key(key=self.string)
    #     resolver = ExternalResolver(name="chemspider",
    #                                 url_scheme="http://www.chemspider.com/inchi-resolver/REST.ashx?q=%s&of=%s")
    #     response = resolver.resolve(k.well_formatted, 'sdf')
    #     if response['status']:
    #         f = file.sdf.SDFile(string=response['string'])
    #         description_list = []
    #         structure_set = []
    #         dataset = Dataset(self.cactvs, [])
    #         for record in f.records:
    #             ens = Ens(self.cactvs, record)
    #             dataset.extend([ens])
    #         dataset.unique()
    #         for ens in dataset.get_enslist():
    #             structure = ChemicalStructure(ens=ens, cactvs=self.cactvs)
    #             try:
    #                 full_key = ens.get('stdinchikey')
    #             except:
    #                 full_key = None
    #                 continue
    #             structure.metadata = {
    #                 'query_type': 'chemspider_stdinchikey',
    #                 'query_search_string': 'Standard InChIKey',
    #                 'query_object': k,
    #                 'query_string': self.string,
    #                 'description': full_key
    #             }
    #             structure_set.append(structure)
    #         interpretation_object.structures = structure_set
    #         interpretation_object._reference_dataset = dataset
    #         return True
    #     return False

    # def _resolver_name_by_chemspider(self, interpretation_object):
    #     return self._resolver_chemspider_name(interpretation_object)

    # def _resolver_chemspider_name(self, interpretation_object):
    #     try:
    #         pattern = re.compile('^ChemNavigator(_|:)SID=(?P<sid>\d+$)', re.IGNORECASE)
    #         match = pattern.search(self.string)
    #         if match:
    #             return
    #     except:
    #         pass
    #     #		try:
    #     #			cas_number = cas.number.String(string = self.string)
    #     #			return False
    #     #		except:
    #     #			pass
    #     try:
    #         inchi = inchi.identifier.String(string=self.string)
    #         return False
    #     except:
    #         pass
    #     try:
    #         k = inchi.identifier.Key(key=self.string)
    #         return False
    #     except:
    #         pass
    #     try:
    #         s = smiles.SMILES(string=self.string, strict_testing=True)
    #         return False
    #     except:
    #         pass
    #     resolver = ExternalResolver(name="chemspider",
    #                                 url_scheme="http://www.chemspider.com/inchi-resolver/REST.ashx?q=%s&of=%s")
    #     response = resolver.resolve(self.string, 'sdf')
    #     print
    #     response
    #     if response['status']:
    #         f = file.sdf.SDFile(string=response['string'])
    #         description_list = []
    #         structure_set = []
    #         dataset = Dataset(self.cactvs, [])
    #         for record in f.records:
    #             ens = Ens(self.cactvs, record)
    #             # a very dirty hack
    #             cs_cmd = "ens purge %s A_RADICAL" % ens.cs_handle
    #             self.cactvs.cmd(cs_cmd)
    #             cs_cmd = "ens hadd %s" % ens.cs_handle
    #             self.cactvs.cmd(cs_cmd)
    #             dataset.extend([ens])
    #         dataset.unique()
    #         for ens in dataset.get_enslist():
    #             structure = ChemicalStructure(ens=ens, cactvs=self.cactvs)
    #             # try:
    #             #	full_key = ens.get('stdinchikey')
    #             # except:
    #             #	full_key = None
    #             #	continue
    #             structure.metadata = {
    #                 'query_type': 'name_by_chemspider',
    #                 'query_search_string': 'chemical name (ChemSpider)',
    #                 'query_object': self.string,
    #                 'query_string': self.string,
    #                 'description': self.string
    #             }
    #             structure_set.append(structure)
    #         interpretation_object.structures = structure_set
    #         interpretation_object._reference_dataset = dataset
    #         return True
    #     return False

    def _resolver_nsc_number(self, interpretation_object):
        pattern = re.compile('^(NSC_Number=NSC|NSC_Number=|NSC=|NSC)(?P<nsc>\d+)$', re.IGNORECASE)
        match = pattern.search(self.string)
        if match:
            self.string = match.group('nsc')
            nsc_number_string = 'NSC%s' % self.string
            # TODO: that is not gonna work
            database = Database.objects.get(id=64)
            record = Record.objects.filter(database=database, database_record_external_identifier=self.string)[0]
            if record:
                structure = record.get_structure()
                chemical_structure = ChemicalStructure(resolved=structure)
                chemical_structure._metadata = {
                    'query_type': 'nsc_number',
                    'query_search_string': 'NSC number',
                    'query_object': pattern,
                    'query_string': self.string,
                    'description': nsc_number_string
                }
                interpretation_object.structures.append(chemical_structure)
                return True
        return False

    def _resolver_zinc_code(self, interpretation_object):
        pattern = re.compile('^(zinc_code=|)(?P<zinc>ZINC\d+$)', re.IGNORECASE)
        match = pattern.search(self.string)
        if match:
            self.string = match.group('zinc')
            name = Name.objects.get(name=self.string)
            if name:
                structure_object = name.get_structure()
                chemical_structure = ChemicalStructure(resolved=structure_object)
                chemical_structure._metadata = {
                    'query_type': 'zinc_code',
                    'query_search_string': 'ZINC code',
                    'query_object': name,
                    'query_string': self.string,
                    'description': name.name
                }
                interpretation_object.structures.append(chemical_structure)
                return True
        return False

    def _resolver_cas_number(self, interpretation_object):
        cas_number = CASNumber(string=self.string)
        name = Name.objects.get(name=self.string)
        if name:
            structure = name.get_structure()
            chemical_structure = ChemicalStructure(resolved=structure)
            chemical_structure._metadata = {
                'query_type': 'cas_number',
                'query_search_string': 'CAS Registry Number',
                'query_object': name,
                'query_string': self.string,
                'description': name.name
            }
            interpretation_object.structures.append(chemical_structure)
            return True
        return False

    # def _resolver_iupac_name_by_opsin(self, interpretation_object):
    #     return self._resolver_opsin(interpretation_object)
    #
    # def _resolver_name_by_opsin(self, interpretation_object):
    #     return self._resolver_opsin(interpretation_object)
    #
    # def _resolver_opsin(self, interpretation_object):
    #     try:
    #         cas_number = cas.number.String(string=self.string)
    #         return False
    #     except:
    #         cas_number = cas.number.String(string=self.string)
    #         pass
    #     try:
    #         inchi = inchi.identifier.String(string=self.string)
    #         return False
    #     except:
    #         pass
    #     try:
    #         k = inchi.identifier.Key(key=self.string)
    #         return False
    #     except:
    #         pass
    #     try:
    #         s = smiles.SMILES(string=self.string, strict_testing=True)
    #         return False
    #     except:
    #         pass
    #
    #     url = settings.OPSIN_URL_PATTERN % self.string
    #     url = url.encode('utf8')
    #     url = url.replace(' ', '%20')
    #     resolver = urllib.urlopen(url)
    #     opsin_smiles = resolver.read()
    #     s = smiles.SMILES(string=opsin_smiles, strict_testing=True)
    #     if s and self._structure_representation_resolver(interpretation_object, representation=s.string):
    #         structure = interpretation_object.structures[0]
    #         structure.metadata = {
    #             'query_type': 'name_by_opsin',
    #             'query_search_string': 'IUPAC name (OPSIN)',
    #             'query_object': self.string,
    #             'query_string': self.string,
    #             'description': self.string
    #         }
    #         # self.string = keep_string
    #         return True
    #     # self.string = keep_string
    #     return False

    def _resolver_name_by_database(self, interpretation_object):
        return self._resolver_name(interpretation_object)

    def _resolver_name_by_cir(self, interpretation_object):
        return self._resolver_name(interpretation_object)

    def _resolver_name(self, interpretation_object):
        try:
            pattern = re.compile('(?P<nsc>^NSC\d+$)', re.IGNORECASE)
            match = pattern.search(self.string)
            if match:
                return False
            pattern = re.compile('(?P<zinc>^ZINC\d+$)', re.IGNORECASE)
            match = pattern.search(self.string)
            if match:
                return False
            cas_number = CASNumber(string=self.string)
            return False
        except:
            pass
        name = Name.objects.get(name=self.string)
        if name:
            structure = name.get_structure()
            chemical_structure = ChemicalStructure(resolved=structure)
            chemical_structure._metadata = {
                'query_type': 'name_by_cir',
                'query_search_string': 'chemical name (CIR)',
                'query_object': name,
                'query_string': self.string,
                'description': name.name
            }
            interpretation_object.structures.append(chemical_structure)
            return True
        return False

    def _resolver_name_pattern(self, interpretation_object):
        pattern = self.string
        resolved_name_list = ChemicalName(pattern=pattern)
        structure_names = resolved_name_list.structure_names
        metadata = resolved_name_list.metadata
        if structure_names:
            structure_names = sorted(structure_names, key=lambda k: k['rank'])

            for structure_name in structure_names:
                structure = structure_name['structure']
                chemical_structure = ChemicalStructure(resolved=structure)
                chemical_structure._metadata = {
                    'query_type': 'name_pattern',
                    'query_search_string': 'chemical name pattern',
                    'query_object': self.string,
                    'query_string': self.string,
                    'description': structure_name['names'][0].name
                }
                interpretation_object.structures.append(chemical_structure)
            return True
        return False

    def _resolver_smiles(self, interpretation_object):
        smiles_string = SMILES(string=self.string, strict_testing=True)
        if smiles_string and self._structure_representation_resolver(interpretation_object):
            chemical_structure = interpretation_object.structures[0]
            chemical_structure._metadata = {
                'query_type': 'smiles',
                'query_search_string': 'SMILES string',
                'query_object': smiles_string,
                'query_string': self.string,
                'description': smiles_string.string
            }
            return True
        return False

    def _resolver_minimol(self, interpretation_object):
        minimol = Minimol(string=self.string)
        if minimol and self._structure_representation_resolver(interpretation_object):
            chemical_structure = interpretation_object.structures[0]
            chemical_structure._metadata = {
                'query_type': 'minimol',
                'query_search_string': 'Cactvs minimol',
                'query_object': minimol,
                'query_string': self.string,
                'description': minimol.string
            }
            return True
        return False

    def _resolver_packstring(self, interpretation_object):
        pack_string = PackString(string=self.string)
        if pack_string and self._structure_representation_resolver(interpretation_object):
            chemical_structure = interpretation_object.structures[0]
            chemical_structure._metadata = {
                'query_type': 'packstring',
                'query_search_string': 'Cactvs pack string',
                'query_object': pack_string,
                'query_string': self.string,
                'description': pack_string.string
            }
            return True
        return False

    # def _resolver_SDFile(self, interpretation_object):
    #     f = file.sdf.SDFile(string=self.string)
    #     if f and self._structure_representation_resolver(interpretation_object):
    #         structure = interpretation_object.structures[0]
    #         structure.metadata = {
    #             'query_type': 'sdfile',
    #             'query_search_string': 'SD file string',
    #             'query_object': f,
    #             'query_string': self.string,
    #             'description': self.string,
    #             'unescaped_string': f.unescaped_string
    #         }
    #         return True
    #     return False

    def _structure_representation_resolver(self, interpretation_object, representation=None):
        # if not self.cactvs:
        #     self.cactvs = Cactvs()
        try:
            if not representation:
                string = self.string
            else:
                string = representation
            string = string.replace("\\n", '\n')
            # TODO: hadd is missing
            #ens = Ens(string, mode='hadd')
            ens = Ens(string)
        except Exception as e:
            logger.error(e)
            return False
        else:
            # TODO: is_search_structure needs replacement
            #if ens.is_search_structure():
            #    return False
            interpretation_object.type = 'structure'
            interpretation_object.type_string = 'chemical structure string'
            interpretation_object.query_object = ens
            interpretation_object._ens = ens
            try:
                hashcode = Identifier(hashcode=ens.get('E_HASHISY'))
                try:
                    structure = Structure2.objects.get(hashisy=CactvsHash(hashcode.integer))
                    chemical_structure = ChemicalStructure(resolved=structure, ens=ens)
                    interpretation_object.structures.append(chemical_structure)
                except (Structure2.DoesNotExist, RuntimeError) as e1:
                    logger.error(e1)
                    #ficts = Identifier(hashcode=ens.getForceTimeout('ficts_id', 5000, 'hashisy', new=True))
                    ficts = Identifier(hashcode=ens.get('E_FICTS_ID'))
                    try:
                        structure = Structure2.objects.get(hashisy=CactvsHash(ficts.integer))
                        chemical_structure = ChemicalStructure(resolved=structure, ens=ens)
                        interpretation_object.structures.append(chemical_structure)
                    except (Structure2.DoesNotExist, RuntimeError) as e2:
                        logger.error(e2)
                        chemical_structure = ChemicalStructure(ens=ens)
                        interpretation_object.structures.append(chemical_structure)
            except Exception as e3:
                logger.error(e3)
                chemical_structure = ChemicalStructure(ens=ens)
                interpretation_object.structures.append(chemical_structure)
                interpretation_object.string = self.string
        return True

    def _operator_tautomers(self, interpretation):
        # ens_list = []
        # for structure in interpretation.structures:
        #     ens_list.append(structure.ens)
        # dataset = Dataset(ens_list)
        # # TODO: This is fishy - found during refactoring:
        # metadata = structure.metadata

        structures = []
        description_list = []
        index = 1
        dataset: Dataset = Dataset()

        for interpretation_structure in interpretation.structures:
            interpretation_structure_ens = interpretation_structure.ens
            metadata = interpretation_structure.metadata.copy()

            description_string = metadata['description'] + " tautomer 1" \
                if 'description' in metadata else "tautomer 1"
            interpretation_structure.metadata.update({'description': description_string})
            structures.append(interpretation_structure)
            description_list.append(description_string)
            dataset.add(interpretation_structure_ens)

            t_count = 1
            tautomers = interpretation_structure_ens.get("E_RESOLVER_TAUTOMERS")
            for tautomer in tautomers.ens():
                t_count += 1
                structure = ChemicalStructure(ens=tautomer)
                tautomer_string = 'tautomer %s' % t_count
                description_string = metadata['description'] + " " + tautomer_string \
                    if 'description' in metadata else tautomer_string
                structure._metadata = {
                    'description': description_string,
                    'query_type': metadata['query_type'] if 'query_type' in metadata else None,
                    'query_search_string': metadata['query_search_string'] if 'query_search_string' in metadata else None
                }
                structures.append(structure)
                description_list.append(description_string)
                dataset.add(tautomer)
                index += 1

        interpretation._reference_dataset = dataset
        interpretation.tautomers = tautomers
        interpretation.description_list = description_list
        interpretation.structures = structures
        return interpretation

    # def _operator_tautomers(self, interpretation):
    #     ens_list = []
    #     for structure in interpretation.structures:
    #         ens_list.append(structure.ens)
    #     dataset = Dataset(ens_list)
    #     # TODO: This is fishy - found during refactoring:
    #     metadata = structure.metadata
    #
    #     structures = []
    #     description_list = []
    #     index = 1
    #
    #     t_count = 1
    #     for ens in dataset.ens():
    #         tautomers = ens.get("E_RESOLVER_TAUTOMERS")
    #         for tautomer in tautomers.ens():
    #             structure = ChemicalStructure(ens=tautomer)
    #             description_string = 'tautomer %s' % t_count
    #             structure.metadata = {
    #                 'description': description_string,
    #                 'query_type': metadata['query_type'] if 'query_type' in metadata else None,
    #                 'query_search_string': metadata['query_search_string'] if 'query_search_string' in metadata else None
    #             }
    #             structures.append(structure)
    #             index += 1
    #             t_count += 1
    #
    #     interpretation._reference_dataset = dataset
    #     interpretation.tautomers = tautomers
    #     interpretation.description_list = description_list
    #     interpretation.structures = structures
    #     return interpretation

    def _operator_remove_hydrogens(self, interpretation):
        enslist = []
        dataset_list = []
        for structure in interpretation.structures:
            enslist.append(structure._ens)
        dataset = Dataset(self.cactvs, enslist=enslist)
        dataset_list.append((dataset, structure._metadata))
        structures = []
        description_list = []
        index = 1
        for dataset, metadata in dataset_list:
            no_hydrogens = dataset.get_no_hydrogens()
            count = 1
            for ens in no_hydrogens.get_enslist():
                structure = ChemicalStructure(ens=ens, cactvs=self.cactvs)
                description_string = 'no hydrogens %s' % count
                structure._metadata = {
                    'description': description_string,
                    'query_type': metadata['query_type'],
                    'query_search_string': metadata['query_search_string']
                }
                structures.append(structure)
                index += 1
                count += 1
        interpretation._reference_dataset = dataset_list
        interpretation.no_hydrogens = no_hydrogens
        interpretation.description_list = description_list
        interpretation.structures = structures
        return interpretation

    def _operator_add_hydrogens(self, interpretation):
        enslist = []
        dataset_list = []
        for structure in interpretation.structures:
            enslist.append(structure._ens)
        dataset = Dataset(self.cactvs, enslist=enslist)
        dataset_list.append((dataset, structure._metadata))
        structures = []
        description_list = []
        index = 1
        for dataset, metadata in dataset_list:
            hydrogens = dataset.get_hydrogens()
            count = 1
            for ens in hydrogens.get_enslist():
                structure = ChemicalStructure(ens=ens, cactvs=self.cactvs)
                description_string = 'hydrogens %s' % count
                structure._metadata = {
                    'description': description_string,
                    'query_type': metadata['query_type'],
                    'query_search_string': metadata['query_search_string']
                }
                structures.append(structure)
                index += 1
                count += 1
        interpretation._reference_dataset = dataset_list
        interpretation.hydrogens = hydrogens
        interpretation.description_list = description_list
        interpretation.structures = structures
        return interpretation

    def _operator_no_stereo(self, interpretation):
        enslist = []
        dataset_list = []
        for structure in interpretation.structures:
            enslist.append(structure._ens)
        dataset = Dataset(self.cactvs, enslist=enslist)
        dataset_list.append((dataset, structure._metadata))
        structures = []
        description_list = []
        index = 1
        for dataset, metadata in dataset_list:
            no_stereo = dataset.get_no_stereo()
            count = 1
            for ens in no_stereo.get_enslist():
                structure = ChemicalStructure(ens=ens, cactvs=self.cactvs)
                description_string = 'no_stereo %s' % count
                structure._metadata = {
                    'description': description_string,
                    'query_type': metadata['query_type'],
                    'query_search_string': metadata['query_search_string']
                }
                structures.append(structure)
                index += 1
                count += 1
        interpretation._reference_dataset = dataset_list
        interpretation.no_stereo = no_stereo
        interpretation.description_list = description_list
        interpretation.structures = structures
        return interpretation

    def _operator_ficts(self, interpretation):
        enslist = []
        dataset_list = []
        for structure in interpretation.structures:
            enslist.append(structure._ens)
        dataset = Dataset(self.cactvs, enslist=enslist)
        dataset_list.append((dataset, structure._metadata))
        structures = []
        description_list = []
        index = 1
        for dataset, metadata in dataset_list:
            ficts = dataset.get_ficts_parent_structure()
            count = 1
            for ens in ficts.get_enslist():
                structure = ChemicalStructure(ens=ens, cactvs=self.cactvs)
                description_string = 'ficts %s' % count
                structure._metadata = {
                    'description': description_string,
                    'query_type': metadata['query_type'],
                    'query_search_string': metadata['query_search_string']
                }
                structures.append(structure)
                index += 1
                count += 1
        interpretation._reference_dataset = dataset_list
        interpretation.ficts = ficts
        interpretation.description_list = description_list
        interpretation.structures = structures
        return interpretation

    def _operator_parent(self, interpretation):
        return self._operator_ficus(interpretation)

    def _operator_normalize(self, interpretation):
        return self._operator_ficus(interpretation)

    def _operator_ficus(self, interpretation):
        enslist = []
        dataset_list = []
        for structure in interpretation.structures:
            enslist.append(structure._ens)
        dataset = Dataset(self.cactvs, enslist=enslist)
        dataset_list.append((dataset, structure._metadata))
        structures = []
        description_list = []
        index = 1
        for dataset, metadata in dataset_list:
            ficus = dataset.get_ficus_parent_structure()
            count = 1
            for ens in ficus.get_enslist():
                structure = ChemicalStructure(ens=ens, cactvs=self.cactvs)
                description_string = 'ficus %s' % count
                structure._metadata = {
                    'description': description_string,
                    'query_type': metadata['query_type'],
                    'query_search_string': metadata['query_search_string']
                }
                structures.append(structure)
                index += 1
                count += 1
        interpretation._reference_dataset = dataset_list
        interpretation.ficus = ficus
        interpretation.description_list = description_list
        interpretation.structures = structures
        return interpretation

    def _operator_uuuuu(self, interpretation):
        enslist = []
        dataset_list = []
        for structure in interpretation.structures:
            enslist.append(structure._ens)
        dataset = Dataset(self.cactvs, enslist=enslist)
        dataset_list.append((dataset, structure._metadata))
        structures = []
        description_list = []
        index = 1
        for dataset, metadata in dataset_list:
            uuuuu = dataset.get_uuuuu_parent_structure()
            count = 1
            for ens in uuuuu.get_enslist():
                structure = ChemicalStructure(ens=ens, cactvs=self.cactvs)
                description_string = 'uuuuu %s' % count
                structure._metadata = {
                    'description': description_string,
                    'query_type': metadata['query_type'],
                    'query_search_string': metadata['query_search_string']
                }
                structures.append(structure)
                index += 1
                count += 1
        interpretation._reference_dataset = dataset_list
        interpretation.uuuuu = uuuuu
        interpretation.description_list = description_list
        interpretation.structures = structures
        return interpretation

    def _operator_stereoisomers(self, interpretation):
        enslist = []
        dataset_list = []
        for structure in interpretation.structures:
            enslist.append(structure._ens)
        dataset = Dataset(self.cactvs, enslist=enslist)
        dataset_list.append((dataset, structure._metadata))
        structures = []
        description_list = []
        index = 1
        for dataset, metadata in dataset_list:
            stereoisomers = dataset.get_stereoisomers()
            count = 1
            for ens in stereoisomers.get_enslist():
                structure = ChemicalStructure(ens=ens, cactvs=self.cactvs)
                description_string = 'stereoisomer %s' % count
                structure._metadata = {
                    'description': description_string,
                    'query_type': metadata['query_type'],
                    'query_search_string': metadata['query_search_string']
                }
                structures.append(structure)
                index += 1
                count += 1
        interpretation._reference_dataset = dataset_list
        interpretation.stereoisomers = stereoisomers
        interpretation.description_list = description_list
        interpretation.structures = structures
        return interpretation

    def _operator_scaffold_sequence(self, interpretation):
        enslist = []
        dataset_list = []
        for structure in interpretation.structures:
            enslist.append(structure._ens)
        dataset = Dataset(self.cactvs, enslist=enslist)
        dataset_list.append((dataset, structure._metadata))
        structures = []
        description_list = []
        index = 1
        for dataset, metadata in dataset_list:
            scaffolds = dataset.get_scaffold_sequence()
            t_count = 1
            for ens in scaffolds.get_enslist():
                structure = ChemicalStructure(ens=ens, cactvs=self.cactvs)
                description_string = 'scaffold %s' % t_count
                structure._metadata = {
                    'description': description_string,
                    'query_type': metadata['query_type'],
                    'query_search_string': metadata['query_search_string']
                }
                structures.append(structure)
                index += 1
                t_count += 1
        interpretation._reference_dataset = dataset_list
        interpretation.scaffolds = scaffolds
        interpretation.description_list = description_list
        interpretation.structures = structures
        return interpretation

    def __len__(self):
        l = []
        [l.extend(s.structures) for s in self._interpretations]
        return len(l)
