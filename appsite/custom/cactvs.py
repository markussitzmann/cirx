from pycactvs import Ens


class CactvsMinimol:

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
            raise ValueError('no CACTVS ensemble hash available')

    def ens(self) -> Ens:
        return Ens(self._minimol)

    def minimol(self) -> bytes:
        return self._minimol

    def __eq__(self, other):
        if isinstance(other, CactvsMinimol):
            return CactvsHash(Ens(self.minimol())).int() == CactvsHash(Ens(other.minimol())).int()
        return False


class CactvsHash:

    MAXHASH = 2**64 - 1
    MINHASH = 0

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
            except RuntimeError:
                raise ValueError('no CACTVS ensemble hash available')
        else:
            try:
                self._integer: int = int(source, 16)
            except ValueError:
                raise ValueError('unknown input value type')

        if self._integer > CactvsHash.MAXHASH or self._integer < CactvsHash.MINHASH:
            raise ValueError('init value is outside scope')

    def unsigned_int(self) -> int:
        return self._integer

    def signed_int(self) -> int:
        return self._integer - CactvsHash.SIGNSHIFT

    def int(self) -> int:
        return self.unsigned_int()

    def padded(self) -> str:
        i = hex(self._integer)[2:]
        return str(i).zfill(16).upper()

    def __str__(self):
        return self.padded()

    def __repr__(self):
        return self.int()

    def __eq__(self, other):
        if isinstance(other, CactvsHash):
            return self.int() == other.int()
        return False

