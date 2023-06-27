import logging
import re
from collections import namedtuple
from typing import List, Dict

from django.conf import settings
from pycactvs import Ens, Dataset

from custom.cactvs import CactvsHash
from structure.cas.number import String as CASNumber
from structure.inchi.identifier import InChIKey
from structure.minimol import Minimol
from structure.ncicadd.identifier import Identifier, RecordID, CompoundID
from structure.packstring import PackString
from structure.smiles import SMILES

logger = logging.getLogger('cirx')


ResolverData = namedtuple("ResolverData", "id resolver resolved exception")
ResolverParams = namedtuple("ResolverParams", "url_params, resolver_list filter mode structure_index page columns rows")




#import cas.number
#import file.sdf
#import inchi.identifier
#import ncicadd.identifier
#import packstring
#import smiles

#from database.models import Database
#from structure.models import Record, Compound
from resolver.models import InChI, Structure, Name, StructureNameAssociation, Dataset, \
    StructureInChIAssociation, InChIType, Record, NameAffinityClass




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


# class ChemicalName:
#
#     def __init__(self, exact_string=None, pattern=None):
#
#         self.names = None
#
#         if pattern:
#             self.pattern = pattern
#             self.query_set = Name_Fulltext.search.query(string=pattern).set_options(
#                 mode=sphinxapi.SPH_MATCH_EXTENDED).select_related()
#             self.metadata = self.query_set._sphinx
#             self.names = self.query_set[0:100]
#             structure_name_objects = StructureNameAssociation.objects.filter(name__in=self.names)
#             structure_names = {}
#             structure_rank = 1
#             for structure_name in structure_name_objects:
#                 try:
#                     k = structure_name.structure
#                 except:
#                     continue
#                 if structure_names.has_key(k):
#                     structure_names[k]['names'].append(structure_name.name)
#                 else:
#                     structure_names[k] = {}
#                     structure_names[k]['names'] = [structure_name.name, ]
#                     structure_names[k]['rank'] = structure_rank
#                     structure_rank += 1
#             structure_name_list = []
#             for structure, name_list in structure_names.items():
#                 name_list['structure'] = structure
#                 structure_name_list.append(name_list)
#             self.structure_names = structure_name_list


class ChemicalStructure:
    """Container class to keep a CACTVS ensemble and a Structure model object of the
       of the same chemical structure together"""

    def __init__(self, structure: Structure = None, ens: Ens = None, metadata: Dict = None, *arg, **kwargs):
        self._structure: Structure = structure
        self._ens: Ens = ens
        self._metadata: Dict = metadata if metadata else {}
        self._identifier = None
        self._hashisy = None
        if structure and not ens:
            self._ens = structure.minimol.ens
        elif ens and not structure:
            self._ens = ens
        elif ens and structure:
            hashcode = ens.get('E_HASHISY')
            h1 = structure.hashisy_key.int
            h2 = Identifier(hashcode=hashcode).integer
            if not h1 == h2:
                raise ChemicalStructureError('ens and object hashcode mismatch')
            self._ens = ens
            self._structure = structure
            self._identifier = h2
            self._hashisy = hashcode
        else:
            raise ValueError('wrong arguments')

    @property
    def ens(self) -> Ens:
        if self._ens:
            return self._ens
        self._ens = Ens(self._structure.minimol)
        return self._ens

    @property
    def structure(self) -> Structure:
        if self._structure:
            return self._structure
        #TODO: needs improvements
        try:
            self._structure = Structure.objects.get(hashisy_key=CactvsHash(self.ens.get('E_HASHISY')))
        except Structure.DoesNotExist:
            self._structure = None
        return self._structure

    @property
    def identifier(self) -> Identifier:
        if self._identifier:
            return self._identifier
        self._identifier = Identifier(hashcode=self.ens.get('E_HASHISY'))
        return self._identifier

    @property
    def hashisy(self) -> str:
        if self._hashisy:
            return self._hashisy
        self._hashisy = self.ens.get('E_HASHISY')
        return self._hashisy

    @property
    def metadata(self) -> dict:
        return self._metadata


class ChemicalStructureError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# @dataclass
# class StructureData:
#     id: int
#     structures: List[ChemicalStructure] = []


class ChemicalString:

    # class StructureData():
    #
    #     def __init__(self):
    #         #self.type = ""
    #         #self.type_string = ""
    #         self.query_object = None
    #         self.structures = []
    #         self.description_list = []
    #         self.id = 0
    #
    #     def __repr__(self):
    #         return "type=%s (number of structures: %s)" % (self.type, len(self.structures))

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
        self._resolver_data: Dict[str, ResolverData] = dict()
        if resolver_list:
            pass
        else:
            resolver_list = settings.CIR_AVAILABLE_RESOLVERS

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
            try:
                resolver_method = getattr(self, '_resolver_' + resolver)
                data: List[ChemicalStructure] = resolver_method()
                item: ChemicalStructure
                if not len(data):
                    raise ValueError('string resolver came back empty')
                i = 0
                for item in data:
                    i += 1
                    if self.operator:
                        operator_method = getattr(self, '_operator_' + self.operator)
                        resolved = operator_method(item)
                        self._resolver_data[resolver] = ResolverData(
                            id=i,
                            resolver=resolver,
                            resolved=resolved,
                            exception=None
                        )
                    else:
                        self._resolver_data[resolver] = ResolverData(
                            id=i,
                            resolver=resolver,
                            resolved=[item, ],
                            exception=None
                        )
            except Exception as e:
                self._resolver_data[resolver] = ResolverData(
                    id=None,
                    resolver=resolver,
                    resolved=None,
                    exception=ValueError('string not resolvable', e)
                )
            if simple and len(self._resolver_data):
                break
        return

    @property
    def resolver_data(self) -> Dict[str, ResolverData]:
        return self._resolver_data

    def _resolver_hashisy(self):
        pattern = re.compile('(?P<hashcode>^[0-9a-fA-F]{16}$)', re.IGNORECASE)
        match = pattern.search(self.string)
        hashcode = match.group('hashcode')
        structure = Structure.with_related_objects.by_hashisy(hashisy_list=[hashcode, ]).first()
        resolved = ChemicalStructure(
            structure=structure,
            metadata={
                'query_type': 'hashisy',
                'query_search_string': 'Cactvs HASHISY hashcode',
                'query_object': hashcode,
                'query_string': self.string,
                'description': hashcode
            }
        )
        return [resolved, ] if resolved else list()

    def _resolver_ncicadd_rid(self) -> List[ChemicalStructure]:
        record_id = RecordID(string=self.string)
        record: Record = Record.with_related_objects.by_record_ids([record_id.rid, ]).first()
        structure: Structure = record.structure_file_record.structure
        resolved = ChemicalStructure(
            # TODO: incorrect
            structure=structure,
            metadata={
                'query_type': 'ncicadd_rid',
                'query_search_string': 'NCI/CADD Record ID',
                'query_object': record_id,
                'query_string': self.string,
                'description': record.id,
                'record': record
            }
        )
        return [resolved, ] if resolved else list()

    def _resolver_ncicadd_cid(self) -> List[ChemicalStructure]:
        compound = CompoundID(string=self.string)
        structure = Structure.with_related_objects.by_compound(compounds=[compound.cid, ]).first()
        resolved = ChemicalStructure(
            structure=structure,
            metadata={
                'query_type': 'ncicadd_cid',
                'query_search_string': 'NCI/CADD Compound ID',
                'query_object': compound,
                'query_string': self.string,
                'description': compound.cid,
                'compound': compound
            }

        )
        return [resolved, ] if resolved else list()

    def _resolver_ncicadd_sid(self) -> List[ChemicalStructure]:
        pattern = re.compile('^NCICADD(_|:)SID=(?P<sid>\d+$)', re.IGNORECASE)
        match = pattern.search(self.string)
        resolved = None
        if match:
            structure_id = match.group('sid')
            structure = Structure.objects.get(id=structure_id)
            resolved = ChemicalStructure(
                structure=structure,
                metadata={
                    'query_type': 'ncicadd_sid',
                    'query_search_string': 'NCI/CADD Structure ID',
                    'query_object': structure.id,
                    'query_string': self.string,
                    'description': self.string,
                }
            )
        return [resolved, ] if resolved else list()

    def _resolver_ncicadd_identifier(self) -> List[ChemicalStructure]:
        identifier = Identifier(string=self.string)
        hashisy_key = CactvsHash(identifier.hashcode)
        structure = Structure.objects.get(hashisy_key=hashisy_key)
        identifier_search_type_string = 'NCI/CADD Identifier (%s)' % identifier.type
        resolved: ChemicalStructure = ChemicalStructure(
            structure=structure,
            metadata={
                'query_type': 'ncicadd_identifier',
                'query_search_string': identifier_search_type_string,
                'query_object': identifier,
                'query_string': self.string,
                'description': identifier
            }
        )
        return [resolved, ] if resolved else list()

    def _resolver_stdinchikey(self) -> List[ChemicalStructure]:
        inchi_type = InChIType.objects.get(title="standard")
        associations = StructureInChIAssociation.with_related_objects.by_partial_inchikey(
            inchikeys=[self.string, ],
            inchi_types=[inchi_type, ]
        ).all()
        resolved_list = list()
        for association in associations:
            structure = association.structure
            identifier = InChIKey(key=association.inchi.key)
            resolved = ChemicalStructure(
                structure=structure,
                metadata={
                    'query_type': 'stdinchikey',
                    'query_search_string': 'Standard InChIKey',
                    'query_object': identifier,
                    'query_string': self.string,
                    'description': identifier.element['well_formatted']
                }
            )
            resolved_list.append(resolved)
        return resolved_list

    def _resolver_stdinchi(self) -> List[ChemicalStructure]:
        identifier = InChI(string=self.string)
        if identifier and self._structure_representation_resolver(representation):
            chemical_structure = representation.structures[0]
            chemical_structure._metadata = {
                'query_type': 'stdinchi',
                'query_search_string': 'Standard InChI',
                'query_object': identifier,
                'query_string': self.string,
                'description': identifier.string
            }
            return True
        return False

    def _resolver_chemnavigator_sid(self) -> List[ChemicalStructure]:
        pattern = re.compile('^ChemNavigator(_|:)SID=(?P<sid>\d+$)', re.IGNORECASE)
        match = pattern.search(self.string)
        if match:
            chemnavigator_id = match.group('sid')
            # TODO: id = 9 is dangerous
            database = Dataset.objects.get(id=9)
            record = Record.objects.get(database_record_external_identifier=chemnavigator_id, database=database)
            structure = record.get_structure()
            chemical_structure = ChemicalStructure(structure=structure)
            if chemical_structure:
                chemical_structure._metadata = {
                    'query_type': 'chemnavigator_sid',
                    'query_search_string': 'ChemNavigator SID',
                    'query_object': self.string,
                    'query_string': self.string,
                    'description': self.string,
                }
                #representation.structures.append(chemical_structure)
                return [chemical_structure, ]
        return list()

    def _resolver_pubchem_sid(self) -> List[ChemicalStructure]:
        pattern = re.compile('^PubChem(_|:)SID=(?P<sid>\d+$)', re.IGNORECASE)
        match = pattern.search(self.string)
        if match:
            pubchem_sid = match.group('sid')
            # database = Database.objects.get(id=9)
            # TODO: dirty, very dirty:
            record = Record.objects.get(release_record_external_identifier=pubchem_sid)
            structure = record.get_structure()
            chemical_structure = ChemicalStructure(structure=structure)
            if chemical_structure:
                chemical_structure._metadata = {
                    'query_type': 'pubchem_sid',
                    'query_search_string': 'PubChem SID',
                    'query_object': self.string,
                    'query_string': self.string,
                    'description': self.string,
                }
                #representation.structures.append(chemical_structure)
                return [chemical_structure, ]
        return list()

    # def _resolver_emolecules_vid(self, representation: Representation):
    #     pattern = re.compile('^eMolecules(_|:)(ID|VID)=(?P<vid>\d+$)', re.IGNORECASE)
    #     match = pattern.search(self.string)
    #     if match:
    #         emolecules_id = match.group('vid')
    #         database = Dataset.objects.get(id=120)
    #         record = Record.objects.get(database_record_external_identifier=emolecules_id, database=database)
    #         structure = record.get_structure()
    #         chemical_structure = ChemicalStructure(resolved=structure)
    #         if chemical_structure:
    #             chemical_structure._metadata = {
    #                 'query_type': 'emolecules_vid',
    #                 'query_search_string': 'eMolecules VID',
    #                 'query_object': self.string,
    #                 'query_string': self.string,
    #                 'description': self.string,
    #             }
    #             representation.structures.append(chemical_structure)
    #             return True
    #     return False

    def _resolver_nsc_number(self) -> List[ChemicalStructure]:
        pattern = re.compile('^(NSC_Number=NSC|NSC_Number=|NSC=|NSC)(?P<nsc>\d+)$', re.IGNORECASE)
        match = pattern.search(self.string)
        if match:
            self.string = match.group('nsc')
            nsc_number_string = 'NSC%s' % self.string
            # TODO: that is not gonna work
            database = Dataset.objects.get(id=64)
            record = Record.objects.filter(database=database, database_record_external_identifier=self.string)[0]
            if record:
                structure = record.get_structure()
                chemical_structure = ChemicalStructure(structure=structure)
                chemical_structure._metadata = {
                    'query_type': 'nsc_number',
                    'query_search_string': 'NSC number',
                    'query_object': pattern,
                    'query_string': self.string,
                    'description': nsc_number_string
                }
                representation.structures.append(chemical_structure)
                return [chemical_structure, ]
        return list()

    def _resolver_zinc_code(self) -> List[ChemicalStructure]:
        pattern = re.compile('^(zinc_code=|)(?P<zinc>ZINC\d+$)', re.IGNORECASE)
        match = pattern.search(self.string)
        if match:
            self.string = match.group('zinc')
            name = Name.objects.get(name=self.string)
            if name:
                structure_object = name.get_structure()
                chemical_structure = ChemicalStructure(structure=structure_object)
                chemical_structure._metadata = {
                    'query_type': 'zinc_code',
                    'query_search_string': 'ZINC code',
                    'query_object': name,
                    'query_string': self.string,
                    'description': name.name
                }
                #representation.structures.append(chemical_structure)
                return [chemical_structure, ]
        return list()

    def _resolver_cas_number(self) -> List[ChemicalStructure]:
        cas_number = CASNumber(string=self.string)
        name = Name.objects.get(name=self.string)
        if name:
            structure = name.get_structure()
            chemical_structure = ChemicalStructure(structure=structure)
            chemical_structure._metadata = {
                'query_type': 'cas_number',
                'query_search_string': 'CAS Registry Number',
                'query_object': name,
                'query_string': self.string,
                'description': name.name
            }
            #representation.structures.append(chemical_structure)
            return [chemical_structure, ]
        return list()

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

    def _resolver_name_by_database(self) -> List[ChemicalStructure]:
        return self._resolver_name()

    def _resolver_name_by_cir(self) -> List[ChemicalStructure]:
        return self._resolver_name()

    def _resolver_name(self) -> List[ChemicalStructure]:
        try:
            pattern = re.compile('(?P<nsc>^NSC\d+$)', re.IGNORECASE)
            match = pattern.search(self.string)
            if match:
                return False
            pattern = re.compile('(?P<zinc>^ZINC\d+$)', re.IGNORECASE)
            match = pattern.search(self.string)
            if match:
                return False
            _ = CASNumber(string=self.string)
            return False
        except:
            pass
        #name = Name.objects.get(name=self.string)

        exact = NameAffinityClass.objects.get(title='exact')
        associations = StructureNameAssociation\
            .with_related_objects\
            .by_name(names=[self.string, ], affinity_classes=[exact, ])\

        resolved_list = []
        for association in associations.all():
            structure: Structure = association.structure
            resolved: ChemicalStructure = ChemicalStructure(
                structure=structure,
                metadata={
                    'query_type': 'name_by_cir',
                    'query_search_string': 'chemical name (CIR)',
                    'query_object': association.name.name,
                    'query_string': self.string,
                    'description': association.name.name
                }
            )
            resolved_list.append(resolved)
        return resolved_list

    # def _resolver_name_pattern(self, representation: Representation):
    #     pattern = self.string
    #     resolved_name_list = ChemicalName(pattern=pattern)
    #     structure_names = resolved_name_list.structure_names
    #     #metadata = resolved_name_list.metadata
    #     if structure_names:
    #         structure_names = sorted(structure_names, key=lambda k: k['rank'])
    #
    #         for structure_name in structure_names:
    #             structure = structure_name['structure']
    #             chemical_structure = ChemicalStructure(resolved=structure)
    #             chemical_structure._metadata = {
    #                 'query_type': 'name_pattern',
    #                 'query_search_string': 'chemical name pattern',
    #                 'query_object': self.string,
    #                 'query_string': self.string,
    #                 'description': structure_name['names'][0].name
    #             }
    #             representation.structures.append(chemical_structure)
    #         return True
    #     return False

    def _resolver_smiles(self) -> List[ChemicalStructure]:
        smiles_string = SMILES(string=self.string, strict_testing=True)
        data = self._structure_representation_resolver(smiles_string.string)
        if smiles_string and len(data):
            resolved = ChemicalStructure(
                ens=data[0].ens,
                structure=data[0].structure,
                metadata={
                    'query_type': 'smiles',
                    'query_search_string': 'SMILES string',
                    'query_object': smiles_string,
                    'query_string': self.string,
                    'description': smiles_string.string
                }
            )
            return [resolved, ]
        return list()

    def _resolver_minimol(self) -> List[ChemicalStructure]:
        minimol = Minimol(string=self.string)
        if minimol and self._structure_representation_resolver(representation):
            chemical_structure = representation.structures[0]
            chemical_structure._metadata = {
                'query_type': 'minimol',
                'query_search_string': 'Cactvs minimol',
                'query_object': minimol,
                'query_string': self.string,
                'description': minimol.string
            }
            return True
        return False

    def _resolver_packstring(self) -> List[ChemicalStructure]:
        pack_string = PackString(string=self.string)
        if pack_string and self._structure_representation_resolver(representation):
            chemical_structure = representation.structures[0]
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

    def _structure_representation_resolver(self, representation_string=None) -> List[ChemicalStructure]:
        # if not self.cactvs:
        #     self.cactvs = Cactvs()
        try:
            if not representation_string:
                string = self.string
            else:
                string = representation_string
            string = string.replace("\\n", '\n')
            # TODO: hadd is missing
            #ens = Ens(string, mode='hadd')
            ens = Ens(string)
        except Exception as e:
            logger.error(e)
            return list()
        else:
            # TODO: is_search_structure needs replacement
            #if ens.is_search_structure():
            #    return False
            chemical_structure = ChemicalStructure(ens=ens)
            chemical_structure.type = 'structure'
            chemical_structure.type_string = 'chemical structure string'
            chemical_structure.query_object = ens
            chemical_structure._ens = ens
            try:
                hashcode = Identifier(hashcode=ens.get('E_HASHISY'))
                try:
                    structure = Structure.objects.get(hashisy_key=CactvsHash(hashcode.integer))
                    chemical_structure = ChemicalStructure(structure=structure, ens=ens)
                    chemical_structure.type = 'structure'
                    chemical_structure.type_string = 'chemical structure string'
                    chemical_structure.query_object = ens
                    chemical_structure._ens = ens
                    #chemical_structure.structures.append(chemical_structure)
                    return [chemical_structure, ]
                except (Structure.DoesNotExist, RuntimeError) as e1:
                    logger.error(e1)
                    #ficts = Identifier(hashcode=ens.getForceTimeout('ficts_id', 5000, 'hashisy', new=True))
                    ficts = Identifier(hashcode=ens.get('E_FICTS_ID'))
                    try:
                        structure = Structure.objects.get(hashisy=CactvsHash(ficts.integer))
                        chemical_structure = ChemicalStructure(structure=structure, ens=ens)
                        chemical_structure.type = 'structure'
                        chemical_structure.type_string = 'chemical structure string'
                        chemical_structure.query_object = ens
                        chemical_structure._ens = ens
                        #representation.structures.append(chemical_structure)
                        return [chemical_structure, ]
                    except (Structure.DoesNotExist, RuntimeError) as e2:
                        logger.error(e2)
                        chemical_structure = ChemicalStructure(ens=ens)
                        chemical_structure.type = 'structure'
                        chemical_structure.type_string = 'chemical structure string'
                        chemical_structure.query_object = ens
                        #representation.structures.append(chemical_structure)
                        return [chemical_structure, ]
            except Exception as e3:
                logger.error(e3)
                #chemical_structure = ChemicalStructure(ens=ens)
                chemical_structure = ChemicalStructure(ens=ens)
                chemical_structure.type = 'structure'
                chemical_structure.type_string = 'chemical structure string'
                chemical_structure.query_object = ens
                #representation.structures.append(chemical_structure)
                #representation.string = self.string
                return [chemical_structure, ]

        #return list()

    def _operator_tautomers(self, structure: ChemicalStructure) -> List[ChemicalStructure]:
        # ens_list = []
        # for structure in interpretation.structures:
        #     ens_list.append(structure.ens)
        # dataset = Dataset(ens_list)
        # # TODO: This is fishy - found during refactoring:
        # metadata = structure.metadata

        structures = []
        description_list = []
        index = 1
        #dataset: Dataset = Dataset()


        #for structure in resolved.structure:
        #interpretation_structure_ens = structure.ens
        metadata = structure.metadata.copy()

        description_string = str(metadata['description']) + " tautomer 1" \
            if 'description' in metadata else "tautomer 1"
        structure.metadata.update({'description': description_string})
        structures.append(structure)
        description_list.append(description_string)
        #dataset.add(structure.ens)

        t_count = 1
        tautomers = structure.ens.get("E_RESOLVER_TAUTOMERS")
        for tautomer in tautomers.ens():
            t_count += 1
            chemical_structure = ChemicalStructure(ens=tautomer)
            tautomer_string = 'tautomer %s' % t_count
            description_string = str(metadata['description']) + " " + tautomer_string \
                if 'description' in metadata else tautomer_string
            chemical_structure._metadata = {
                'description': description_string,
                'query_type': metadata['query_type'] if 'query_type' in metadata else None,
                'query_search_string': metadata['query_search_string'] if 'query_search_string' in metadata else None
            }
            structures.append(chemical_structure)
            description_list.append(description_string)
            #dataset.add(tautomer)
            index += 1

        ###

        return structures if structures else list()

        #representation._reference_dataset = dataset
        #representation.tautomers = tautomers
        #representation.description_list = description_list
        #representation.structures = structures
        #return representation

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

    def _operator_remove_hydrogens(self, representation):
        enslist = []
        dataset_list = []
        for structure in representation.structures:
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
        representation._reference_dataset = dataset_list
        representation.no_hydrogens = no_hydrogens
        representation.description_list = description_list
        representation.with_related_objects = structures
        return representation

    def _operator_add_hydrogens(self, representation):
        enslist = []
        dataset_list = []
        for structure in representation.structures:
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
        representation._reference_dataset = dataset_list
        representation.hydrogens = hydrogens
        representation.description_list = description_list
        representation.with_related_objects = structures
        return representation

    def _operator_no_stereo(self, representation):
        enslist = []
        dataset_list = []
        for structure in representation.structures:
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
        representation._reference_dataset = dataset_list
        representation.no_stereo = no_stereo
        representation.description_list = description_list
        representation.with_related_objects = structures
        return representation

    def _operator_ficts(self, representation):
        enslist = []
        dataset_list = []
        for structure in representation.structures:
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
        representation._reference_dataset = dataset_list
        representation.ficts = ficts
        representation.description_list = description_list
        representation.with_related_objects = structures
        return representation

    def _operator_parent(self, interpretation):
        return self._operator_ficus(interpretation)

    def _operator_normalize(self, interpretation):
        return self._operator_ficus(interpretation)

    def _operator_ficus(self, representation):
        enslist = []
        dataset_list = []
        for structure in representation.structures:
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
        representation._reference_dataset = dataset_list
        representation.ficus = ficus
        representation.description_list = description_list
        representation.with_related_objects = structures
        return representation

    def _operator_uuuuu(self, representation):
        enslist = []
        dataset_list = []
        for structure in representation.with_related_objects:
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
        representation._reference_dataset = dataset_list
        representation.uuuuu = uuuuu
        representation.description_list = description_list
        representation.with_related_objects = structures
        return representation

    def _operator_stereoisomers(self, representation):
        enslist = []
        dataset_list = []
        for structure in representation.with_related_objects:
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
        representation._reference_dataset = dataset_list
        representation.stereoisomers = stereoisomers
        representation.description_list = description_list
        representation.with_related_objects = structures
        return representation

    def _operator_scaffold_sequence(self, representation):
        enslist = []
        dataset_list = []
        for structure in representation.with_related_objects:
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
        representation._reference_dataset = dataset_list
        representation.scaffolds = scaffolds
        representation.description_list = description_list
        representation.with_related_objects = structures
        return representation

    def __len__(self):
        l = []
        [l.extend(s.structures) for s in self._representations]
        return len(l)
