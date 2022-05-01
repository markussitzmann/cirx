from enum import Enum

from pycactvs import Ens

from structure.ncicadd.identifier import Identifier


class IdentifierType(Enum):
    FICTS = "FICTS"
    FICuS = "FICuS"
    uuuuu = "uuuuu"


class CactvsMinimol(object):

    def __init__(self, source):
        if isinstance(source, bytes):
            try:
                self._minimol = Ens(source).get('E_MINIMOL')
            except RuntimeError:
                raise ValueError('no valid byte sequence')
        elif isinstance(source, Ens):
            try:
                self._minimol = source.get('E_MINIMOL')
            except RuntimeError:
                raise ValueError('no valid CACTVS ens')
        else:
            raise ValueError('CACTVS ensemble can not be created from source')

    @property
    def ens(self) -> Ens:
        return Ens(self._minimol)

    @property
    def minimol(self) -> bytes:
        return self._minimol

    def __eq__(self, other):
        if isinstance(other, CactvsMinimol):
            return CactvsHash(Ens(self._minimol)).int == CactvsHash(Ens(other._minimol)).int
        return False


class CactvsHash(object):

    MAXHASH = 2**64 - 1
    MINHASH = 0
    VERSION_STRING = "01"

    SIGNSHIFT = (1 << 63)

    def __init__(self, source, signed=False):

        if isinstance(source, int):
            if signed:
                self._integer: int = source + CactvsHash.SIGNSHIFT
            else:
                self._integer: int = source
        elif isinstance(source, str):
            self._integer: int = int('0x' + source, 16)
        elif isinstance(source, Ens):
            try:
                self._integer: int = int('0x' + source.get('E_HASHISY'), 16)
            except RuntimeError as e:
                raise ValueError('no CACTVS ensemble hash available', e)
        else:
            try:
                self._integer: int = int(source, 16)
            except ValueError:
                raise ValueError('unknown input value type')

        if self._integer > CactvsHash.MAXHASH or self._integer < CactvsHash.MINHASH:
            raise ValueError('init value is outside scope')

    @property
    def unsigned_int(self) -> int:
        return self._integer

    @property
    def signed_int(self) -> int:
        return self._integer - CactvsHash.SIGNSHIFT

    @property
    def int(self) -> int:
        return self.unsigned_int

    @property
    def padded(self) -> str:
        i = hex(self._integer)[2:]
        return str(i).zfill(16).upper()

    def format_as(self, identifier_type: IdentifierType) -> Identifier:
        return Identifier(integer=self.int, identifier_type=identifier_type.value)

    def __str__(self):
        return self.padded

    def __repr__(self):
        return str(self.int)

    def __eq__(self, other):
        if isinstance(other, CactvsHash):
            return self.int == other.int
        return False

    def __hash__(self):
        return self._integer

