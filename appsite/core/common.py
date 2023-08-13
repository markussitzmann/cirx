from collections import namedtuple
from pycactvs import Prop

Identifier = namedtuple('Identifier', 'property parent_structure attr public_string key')
InChIAndSaveOpt = namedtuple('InChIAndSaveOpt', 'inchi saveopt')
InChITypeTuple = namedtuple('InChITypes', 'id property key softwareversion software options')


NCICADD_TYPES = [
    Identifier('E_UUUUU_ID', 'E_UUUUU_STRUCTURE', 'uuuuu_parent', 'uuuuu', 'uuuuu'),
    Identifier('E_FICUS_ID', 'E_FICUS_STRUCTURE', 'ficus_parent', 'FICuS', 'ficus'),
    Identifier('E_FICTS_ID', 'E_FICTS_STRUCTURE', 'ficts_parent', 'FICTS', 'ficts'),
]


INCHI_TYPES = [
    InChITypeTuple(
        'standard',
        'E_STDINCHI',
        'E_STDINCHIKEY',
        Prop.Ref('E_STDINCHI').softwareversion,
        Prop.Ref('E_STDINCHI').software,
        ""
    ),
    InChITypeTuple(
        'original',
        'E_INCHI',
        'E_INCHIKEY',
        Prop.Ref('E_INCHI').softwareversion,
        Prop.Ref('E_INCHI').software,
        "SAVEOPT  RECMET NOWARNINGS FIXEDH"
    ),
    InChITypeTuple(
        'xtauto',
        'E_INCHI',
        'E_INCHIKEY',
        Prop.Ref('E_INCHI').softwareversion,
        Prop.Ref('E_INCHI').software,
        "SAVEOPT  RECMET NOWARNINGS KET 15T"
    ),
    InChITypeTuple(
        'xtautox',
        'E_TAUTO_INCHI',
        'E_TAUTO_INCHIKEY',
        Prop.Ref('E_TAUTO_INCHI').softwareversion,
        Prop.Ref('E_TAUTO_INCHI').software,
        "SAVEOPT DONOTADDH RECMET NOWARNINGS KET 15T PT_22_00 PT_16_00 PT_06_00 PT_39_00 PT_13_00 PT_18_00"
    ),
]