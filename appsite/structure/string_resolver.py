import logging
import re
from collections import namedtuple
from typing import List, Dict, Optional, Tuple, Any

from django.conf import settings
from pycactvs import Ens, Dataset

from core.cactvs import CactvsHash
from core.common import NCICADD_TYPES
from resolver.models import Structure, Name, StructureNameAssociation, Dataset, \
    StructureInChIAssociation, InChIType, Record, NameAffinityClass
from structure.cas.number import String as CASNumber
from structure.inchi.identifier import InChIKey, InChIString
from structure.ncicadd.identifier import Identifier, RecordID, CompoundID
from structure.smiles import SMILES

logger = logging.getLogger('cirx')

ResolverData = namedtuple("ResolverData", "id resolver resolved exception")
ResolverParams = namedtuple("ResolverParams", "url_params resolver_list filter mode structure_index page columns rows")

OPERATOR_LIST = [
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


class ChemicalStructure:
    """Container class to keep a CACTVS ensemble and a Structure model object of the same chemical structure together"""

    def __init__(self, structure: Structure = None, ens: Ens = None, metadata: Dict = None, *arg, **kwargs):
        self._structure: Structure = structure
        self._ens: Ens = ens
        self._metadata: Dict = metadata if metadata else {}
        self._identifier = None
        self._hashisy = None
        self._ficts_parent = None
        self._ficus_parent = None
        self._uuuuu_parent = None
        if structure and not ens:
            self._ens = structure.minimol.ens
        elif ens and not structure:
            self._ens = ens
        elif ens and structure:
            hashcode = ens.get('E_HASHISY')
            h1 = structure.hash.int
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
        # TODO: needs improvements
        try:
            self._structure = Structure.with_related_objects.by_hashisy([self.hashisy]).first()
        except Exception as e:
            logger.warning("structure lookup with error:", e)
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

    def ficts_parent(self, only_lookup: bool = False) -> Optional['ChemicalStructure']:
        if self._ficts_parent:
            return self._ficts_parent
        self._ficts_parent = self._parent('ficts', only_lookup)
        return self._ficts_parent

    def ficus_parent(self, only_lookup: bool = True) -> Optional['ChemicalStructure']:
        if self._ficus_parent:
            return self._ficus_parent
        self._ficus_parent = self._parent('ficus', only_lookup)
        return self._ficus_parent

    def uuuuu_parent(self, only_lookup: bool = True) -> Optional['ChemicalStructure']:
        if self._uuuuu_parent:
            return self._uuuuu_parent
        self._uuuuu_parent = self._parent('uuuuu', only_lookup)
        return self._uuuuu_parent

    def _parent(self, parent_type: str, only_lookup: bool = False) -> Optional['ChemicalStructure']:
        parent_types = {identifier_type.key: identifier_type for identifier_type in NCICADD_TYPES}
        try:
            attr = parent_types[parent_type].attr
            if self.structure and hasattr(self.structure.parents, attr):
                parent_structure: Structure = getattr(self.structure.parents, attr)
                if parent_structure:
                    return ChemicalStructure(structure=parent_structure, ens=parent_structure.to_ens,
                                             metadata=self.metadata)
                if only_lookup:
                    # return self
                    return None
            if not only_lookup:
                parent: Ens = self.ens.get(parent_types[parent_type].parent_structure)
                ens = Ens(parent.get("E_MINIMOL"))
                cs = ChemicalStructure(ens=ens, metadata=self.metadata)
                return cs
            else:
                # return self
                return None
        except Exception as e:
            logger.error("creating parent structure failed: {}".format(e))

    def __del__(self):
        self._structure: Structure = None
        self._ens: Ens = None
        self._metadata: Dict = {}
        self._identifier = None
        self._hashisy = None
        self._ficts_parent = None
        self._ficus_parent = None
        self._uuuuu_parent = None
        del self._ens


class ChemicalString:

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
        self._resolver_data: Dict[str, List[ResolverData]] = dict()
        if resolver_list:
            pass
        else:
            resolver_list = settings.CIR_AVAILABLE_RESOLVERS

        if operator_list:
            pass
        else:
            operator_list = OPERATOR_LIST
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

        i = 0
        for resolver in resolver_list:
            self._resolver_data[resolver] = []
            try:
                resolver_method = getattr(self, '_resolve_' + resolver)
                data: List[ChemicalStructure] = resolver_method()
                chemical_structure: ChemicalStructure
                if not len(data):
                    raise ValueError('string resolver came back empty')
                for chemical_structure in data:
                    i += 1
                    if self.operator:
                        operator_method = getattr(self, '_operator_' + self.operator)
                        resolved = operator_method(chemical_structure)
                        self._resolver_data[resolver].append(ResolverData(
                            id=i,
                            resolver=resolver,
                            resolved=resolved,
                            exception=None
                        ))
                    else:
                        self._resolver_data[resolver].append(ResolverData(
                            id=i,
                            resolver=resolver,
                            resolved=[chemical_structure, ],
                            exception=None
                        ))
            except Exception as e:
                self._resolver_data[resolver].append(ResolverData(
                    id=None,
                    resolver=resolver,
                    resolved=None,
                    exception=ValueError('string not resolvable', e)
                ))
            if simple and len(self._resolver_data):
                break
        return

    @property
    def resolver_data(self) -> Dict[str, List[ResolverData]]:
        return self._resolver_data

    def _is_hashisy(self) -> Optional[str]:
        try:
            pattern = re.compile('(?P<hashcode>^[0-9a-fA-F]{16}$)', re.IGNORECASE)
            match = pattern.search(self.string)
            return match.group('hashcode')
        except Exception:
            return None

    def _resolve_hashisy(self) -> List[ChemicalStructure]:
        # pattern = re.compile('(?P<hashcode>^[0-9a-fA-F]{16}$)', re.IGNORECASE)
        # match = pattern.search(self.string)
        hashcode = self._is_hashisy()
        if not hashcode:
            return list()
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

    def _is_ncicadd_rid(self):
        try:
            record_id = RecordID(string=self.string)
            return record_id
        except Exception:
            return None

    def _resolve_ncicadd_rid(self) -> List[ChemicalStructure]:
        # record_id = RecordID(string=self.string)
        record_id = self._is_ncicadd_rid()
        if not record_id:
            return list()
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

    def _is_ncicadd_cid(self):
        try:
            compound = CompoundID(string=self.string)
            return compound
        except Exception:
            return None

    def _resolve_ncicadd_cid(self) -> List[ChemicalStructure]:
        compound = self._is_ncicadd_cid()
        if not compound:
            return list()
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

    def _is_ncicadd_sid(self) -> Optional[Any]:
        try:
            pattern = re.compile('^NCICADD(_|:)SID=(?P<sid>\d+$)', re.IGNORECASE)
            match = pattern.search(self.string)
            return match.group('sid')
        except Exception:
            return None

    def _resolve_ncicadd_sid(self) -> List[ChemicalStructure]:
        # pattern = re.compile('^NCICADD(_|:)SID=(?P<sid>\d+$)', re.IGNORECASE)
        # match = pattern.search(self.string)
        # resolved = None
        structure_id = self._is_ncicadd_sid()
        if not structure_id:
            return list()
        # if match:
        # structure_id = match.group('sid')
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

    def _is_ncicadd_identifier(self) -> Optional[Any]:
        try:
            return Identifier(string=self.string)
        except Exception:
            return None

    def _resolve_ncicadd_identifier(self) -> List[ChemicalStructure]:
        # identifier = Identifier(string=self.string)
        identifier = self._is_ncicadd_identifier()
        if not identifier:
            return list()
        cactvs_hash = CactvsHash(identifier.hashcode)
        structure = Structure.objects.get(hash=cactvs_hash)
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

    def _is_stdinchikey(self) -> Optional[Any]:
        try:
            inchikey_string = self.string.replace("InChIKey=", "")

            pattern_list = [InChIKey.PATTERN_STRING, InChIKey.PARTIAL_PATTERN_STRING_1,
                            InChIKey.PARTIAL_PATTERN_STRING_2]
            matched = False
            for pattern_string in pattern_list:
                pattern = re.compile(pattern_string)
                match = pattern.search(inchikey_string)
                if match:
                    return inchikey_string
            return None
        except Exception:
            return None

    def _resolve_stdinchikey(self) -> List[ChemicalStructure]:

        # inchikey_string = self.string.replace("InChIKey=", "")
        #
        # pattern_list = [InChIKey.PATTERN_STRING, InChIKey.PARTIAL_PATTERN_STRING_1, InChIKey.PARTIAL_PATTERN_STRING_2]
        # matched = False
        # for pattern_string in pattern_list:
        #     pattern = re.compile(pattern_string)
        #     match = pattern.search(inchikey_string)
        #     if match:
        #         matched = True

        # resolved = None
        # if matched:

        inchikey_string = self._is_stdinchikey()
        if not inchikey_string:
            return list()

        inchi_type = InChIType.objects.get(title="standard")
        associations = StructureInChIAssociation.with_related_objects.by_partial_inchikey(
            inchikeys=[inchikey_string, ],
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
        # return list()

    def _is_stdinchi(self) -> Optional[Any]:
        try:
            return InChIString(string=self.string)
        except Exception:
            return None

    def _resolve_stdinchi(self) -> List[ChemicalStructure]:
        # inchi = InChIString(string=self.string)
        inchi = self._is_stdinchi()
        if not inchi:
            return list()
        # if inchi.string:
        resolved = ChemicalStructure(
            ens=Ens(inchi.string),
            metadata={
                'query_type': 'stdinchi',
                'query_search_string': 'Standard InChI',
                'query_object': inchi,
                'query_string': self.string,
                'description': inchi.string
            }
        )
        return [resolved, ]
        # return list()

    def _is_smiles(self) -> Optional[Any]:
        try:
            return SMILES(string=self.string, strict_testing=True)
        except Exception:
            return None

    def _resolve_smiles(self) -> List[ChemicalStructure]:
        # smiles = SMILES(string=self.string, strict_testing=True)
        smiles = self._is_smiles()
        if not smiles:
            return list()
        # if smiles.string:
        resolved = ChemicalStructure(
            ens=Ens(smiles.string),
            metadata={
                'query_type': 'smiles',
                'query_search_string': 'SMILES string',
                'query_object': smiles,
                'query_string': self.string,
                'description': smiles.string
            }
        )
        return [resolved, ]
        # return list()

    def _is_cas_number(self) -> Optional[Any]:
        try:
            return CASNumber(string=self.string)
        except Exception:
            return None

    def _resolve_cas_number(self) -> List[ChemicalStructure]:
        cas_number = CASNumber(string=self.string)
        cas_number = self._is_cas_number()
        if not cas_number:
            return list()
        # if cas_number:
        affinity = {a.title: a for a in NameAffinityClass.objects.all()}
        associations = StructureNameAssociation \
            .with_related_objects \
            .by_name(names=[self.string, ], affinity_classes=[affinity['exact']])

        for association in associations.all():
            structure: Structure = association.structure
            chemical_structure = ChemicalStructure(structure=structure)
            chemical_structure._metadata = {
                'query_type': 'cas_number',
                'query_search_string': 'CAS Registry Number',
                'query_object': association.name.name,
                'query_string': self.string,
                'description': association.name.name
            }
            return [chemical_structure, ]
        # return list()

    def _is_name(self) -> Optional[Any]:
        return self.string

    def _resolve_name(self) -> List[ChemicalStructure]:
        # try:
        #     pattern = re.compile('(?P<nsc>^NSC\d+$)', re.IGNORECASE)
        #     match = pattern.search(self.string)
        #     if match:
        #         return False
        #     pattern = re.compile('(?P<zinc>^ZINC\d+$)', re.IGNORECASE)
        #     match = pattern.search(self.string)
        #     if match:
        #         return False
        #     _ = CASNumber(string=self.string)
        #     return False
        # except:
        #     pass

        name = self._is_name()
        if not name:
            return list()

        names = [name, ]
        if len(self.string) >= 3:
            names.append(self.string.lower())
            names.append(self.string.upper())
            names.append(self.string.capitalize())
            names = list(set(names))

        affinity = {a.title: a for a in NameAffinityClass.objects.all()}
        associations = StructureNameAssociation \
            .with_related_objects \
            .by_name(names=names, affinity_classes=[affinity['exact']])
        if not associations:
            associations = StructureNameAssociation \
                .with_related_objects \
                .by_name(names=names, affinity_classes=[affinity['narrow']])

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

    def _resolve_structure_representation(self) -> List[ChemicalStructure]:
        """
            this is a special resolver, it only attempts to resolver if there hasn't been found anything by other
            resolver modules
        """
        if (len(self._resolver_data.keys()) > 1
                or ("_resolver_structure_representation" in self._resolver_data.keys()
                    and len(self._resolver_data['structure_representation']) > 1)
        ):
            return list()
        resolved = ChemicalStructure(
            ens=Ens(self.string),
            metadata={
                'query_type': 'Cactvs-resolvable structure representation',
                'query_search_string': 'structure representation',
                'query_object': self.string,
                'query_string': self.string,
                'description': self.string
            }
        )
        return [resolved, ]

    # def _resolver_minimol(self) -> List[ChemicalStructure]:
    #     minimol = Minimol(string=self.string)
    #     if minimol and self._structure_representation_resolver(representation):
    #         chemical_structure = representation.structures[0]
    #         chemical_structure._metadata = {
    #             'query_type': 'minimol',
    #             'query_search_string': 'Cactvs minimol',
    #             'query_object': minimol,
    #             'query_string': self.string,
    #             'description': minimol.string
    #         }
    #         return True
    #     return False

    # def _resolver_packstring(self) -> List[ChemicalStructure]:
    #     pack_string = PackString(string=self.string)
    #     if pack_string and self._structure_representation_resolver(representation):
    #         chemical_structure = representation.structures[0]
    #         chemical_structure._metadata = {
    #             'query_type': 'packstring',
    #             'query_search_string': 'Cactvs pack string',
    #             'query_object': pack_string,
    #             'query_string': self.string,
    #             'description': pack_string.string
    #         }
    #         return True
    #     return False

    def _resolve_chemnavigator_sid(self) -> List[ChemicalStructure]:
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
                # representation.structures.append(chemical_structure)
                return [chemical_structure, ]
        return list()

    def _resolve_pubchem_sid(self) -> List[ChemicalStructure]:
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
                # representation.structures.append(chemical_structure)
                return [chemical_structure, ]
        return list()

    def _resolve_nsc_number(self) -> List[ChemicalStructure]:
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

    def _resolve_zinc_code(self) -> List[ChemicalStructure]:
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
                # representation.structures.append(chemical_structure)
                return [chemical_structure, ]
        return list()

    def _resolve_name_by_database(self) -> List[ChemicalStructure]:
        return self._resolver_name()

    def _resolve_name_by_cir(self) -> List[ChemicalStructure]:
        return self._resolver_name()

    #### OPERATORS ####

    @staticmethod
    def _operator_tautomers(structure: ChemicalStructure) -> List[ChemicalStructure]:

        structures = []
        description_list = []
        metadata = structure.metadata.copy()

        description_string = str(metadata['description']) + " tautomer 1" if 'description' in metadata else "tautomer 1"
        structure.metadata.update({'description': description_string})
        structures.append(structure)
        description_list.append(description_string)

        tautomer_index = 1
        tautomers = structure.ens.get("E_RESOLVER_TAUTOMERS")
        for tautomer in tautomers.ens():
            tautomer_index += 1
            chemical_structure = ChemicalStructure(ens=tautomer)
            tautomer_string = 'tautomer %s' % tautomer_index
            description_string = str(metadata['description']) + " " + tautomer_string \
                if 'description' in metadata else tautomer_string
            chemical_structure._metadata = {
                'description': description_string,
                'query_type': metadata['query_type'] if 'query_type' in metadata else None,
                'query_search_string': metadata['query_search_string'] if 'query_search_string' in metadata else None
            }
            structures.append(chemical_structure)
            description_list.append(description_string)

        return structures if structures else list()

    @staticmethod
    def _operator_stereoisomers(structure: ChemicalStructure) -> List[ChemicalStructure]:

        structures = []
        description_list = []
        metadata = structure.metadata.copy()

        description_string = str(
            metadata['description']) + " stereoisomer 1" if 'description' in metadata else "stereoisomer 1"
        structure.metadata.update({'description': description_string})
        structures.append(structure)
        description_list.append(description_string)

        stereoisomer_index = 1
        stereoisomers = structure.ens.get("E_STEREOISOMERS")
        for stereoisomer in stereoisomers.ens()[1:]:
            stereoisomer_index += 1
            chemical_structure = ChemicalStructure(ens=stereoisomer)
            stereoisomer_string = 'stereoisomer %s' % stereoisomer_index
            description_string = str(metadata['description']) + " " + stereoisomer_string \
                if 'description' in metadata else stereoisomer_string
            chemical_structure._metadata = {
                'description': description_string,
                'query_type': metadata['query_type'] if 'query_type' in metadata else None,
                'query_search_string': metadata['query_search_string'] if 'query_search_string' in metadata else None
            }
            structures.append(chemical_structure)
            description_list.append(description_string)

        return structures if structures else list()

    @staticmethod
    def _operator_ficts(structure: ChemicalStructure) -> List[ChemicalStructure]:
        ficts_parent = structure.ficts_parent(only_lookup=False)
        ficts_parent._metadata.update({
            'description': "FICTS parent of " + structure.metadata['description']
        })
        return [ficts_parent, ]

    @staticmethod
    def _operator_ficus(structure: ChemicalStructure) -> List[ChemicalStructure]:
        ficus_parent = structure.ficus_parent(only_lookup=False)
        ficus_parent._metadata.update({
            'description': "FICuS parent of " + structure.metadata['description']
        })
        return [ficus_parent, ]

    @staticmethod
    def _operator_uuuuu(structure: ChemicalStructure) -> List[ChemicalStructure]:
        uuuuu_parent = structure.uuuuu_parent(only_lookup=False)
        uuuuu_parent._metadata.update({
            'description': "uuuuu parent of " + structure.metadata['description']
        })
        return [uuuuu_parent, ]

    @staticmethod
    def _operator_parent(structure: ChemicalStructure) -> List[ChemicalStructure]:
        return ChemicalString._operator_ficts(structure)

    @staticmethod
    def _operator_normalize(structure: ChemicalStructure) -> List[ChemicalStructure]:
        return ChemicalString._operator_ficus(structure)

    @staticmethod
    def _operator_no_stereo(structure: ChemicalStructure):

        def _no_stereo_structure(ens: Ens):
            for prop in ['A_LABEL_STEREO', 'B_LABEL_STEREO', 'A_CIP_STEREO', 'B_CIP_STEREO', 'A_HSPECIAL']:
                ens.purge(prop)
            return Ens(ens.new('E_SMILES'))

        structures = []
        description_list = []
        metadata = structure.metadata.copy()

        no_stereo_structure = _no_stereo_structure(structure.ens)
        chemical_structure = ChemicalStructure(ens=no_stereo_structure)
        no_stereo_string = 'no stereo'
        description_string = str(metadata['description']) + " " + no_stereo_string \
            if 'description' in metadata else no_stereo_string
        chemical_structure._metadata = {
            'description': description_string,
            'query_type': metadata['query_type'] if 'query_type' in metadata else None,
            'query_search_string': metadata['query_search_string'] if 'query_search_string' in metadata else None
        }
        structures.append(chemical_structure)
        description_list.append(description_string)

        return structures if structures else list()

    @staticmethod
    def _operator_remove_hydrogens(structure: ChemicalStructure):

        def _remove_hydrogens(ens: Ens):
            ens.hstrip()
            return ens

        structures = []
        description_list = []
        metadata = structure.metadata.copy()

        ens = _remove_hydrogens(structure.ens)
        chemical_structure = ChemicalStructure(ens=ens)
        operation_string = 'remove hydrogen'
        description_string = str(metadata['description']) + " " + operation_string \
            if 'description' in metadata else operation_string
        chemical_structure._metadata = {
            'description': description_string,
            'query_type': metadata['query_type'] if 'query_type' in metadata else None,
            'query_search_string': metadata['query_search_string'] if 'query_search_string' in metadata else None
        }
        structures.append(chemical_structure)
        description_list.append(description_string)

        return structures if structures else list()

    @staticmethod
    def _operator_add_hydrogens(structure: ChemicalStructure):

        def _add_hydrogens(ens: Ens):
            ens.hadd()
            return ens

        structures = []
        description_list = []
        metadata = structure.metadata.copy()

        ens = _add_hydrogens(structure.ens)
        chemical_structure = ChemicalStructure(ens=ens)
        operation_string = 'add hydrogen'
        description_string = str(metadata['description']) + " " + operation_string \
            if 'description' in metadata else operation_string
        chemical_structure._metadata = {
            'description': description_string,
            'query_type': metadata['query_type'] if 'query_type' in metadata else None,
            'query_search_string': metadata['query_search_string'] if 'query_search_string' in metadata else None
        }
        structures.append(chemical_structure)
        description_list.append(description_string)

        return structures if structures else list()

    # def _operator_scaffold_sequence(self, representation):
    #     enslist = []
    #     dataset_list = []
    #     for structure in representation.with_related_objects:
    #         enslist.append(structure._ens)
    #     dataset = Dataset(self.cactvs, enslist=enslist)
    #     dataset_list.append((dataset, structure._metadata))
    #     structures = []
    #     description_list = []
    #     index = 1
    #     for dataset, metadata in dataset_list:
    #         scaffolds = dataset.get_scaffold_sequence()
    #         t_count = 1
    #         for ens in scaffolds.get_enslist():
    #             structure = ChemicalStructure(ens=ens, cactvs=self.cactvs)
    #             description_string = 'scaffold %s' % t_count
    #             structure._metadata = {
    #                 'description': description_string,
    #                 'query_type': metadata['query_type'],
    #                 'query_search_string': metadata['query_search_string']
    #             }
    #             structures.append(structure)
    #             index += 1
    #             t_count += 1
    #     representation._reference_dataset = dataset_list
    #     representation.scaffolds = scaffolds
    #     representation.description_list = description_list
    #     representation.with_related_objects = structures
    #     return representation

    def __len__(self):
        l = []
        [l.extend(s.structures) for s in self._representations]
        return len(l)


class ChemicalStructureError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
