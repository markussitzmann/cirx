import re


class RecordID:
    PREFIX_LIST = ["NCICADD:RID=", "NCICADD_RID="]

    def __init__(self, string=None, id=None, prefix_list=PREFIX_LIST):
        self._set(string=string)

    def _set(self, string=None, id=None, prefix_list=PREFIX_LIST):
        self._reset()
        if self._test_string(string):
            pass
        else:
            raise IdentifierError('string is not resolvable')

    def _reset(self):
        self.string = None
        self.rid = None
        self.prefix = None

    def _test_string(self, string, prefix_list=PREFIX_LIST):
        for prefix in prefix_list:
            patternString = '(?P<prefix>%s)(?P<rid>\d+$)' % prefix
            pattern = re.compile(patternString, re.IGNORECASE)
            try:
                match = pattern.search(string)
                self.rid = match.group('rid')
                self.prefix = match.group('prefix')
                return True
            except:
                pass
        return False


class CompoundID:
    PREFIX_LIST = ["NCICADD:CID=", "NCICADD_CID=", ]

    def __init__(self, string=None, id=None, prefix_list=PREFIX_LIST):
        self._set(string=string)

    def _set(self, string=None, id=None, prefix_list=PREFIX_LIST):
        self._reset()
        if self._test_string(string):
            pass
        else:
            raise IdentifierError('string is not resolvable')

    def _reset(self):
        self.string = None
        self.rid = None
        self.prefix = None

    def _test_string(self, string, prefix_list=PREFIX_LIST):
        for prefix in prefix_list:
            patternString = '(?P<prefix>%s)(?P<cid>\d+$)' % prefix
            pattern = re.compile(patternString, re.IGNORECASE)
            try:
                match = pattern.search(string)
                self.cid = match.group('cid')
                self.prefix = match.group('prefix')
                return True
            except:
                pass
        return False


class Identifier:
    DEFAULT_VERSION = '01'
    MAGIC_HASHCODE = 'FFFFFFFFFFFFFFFF'
    ZERO_HASHCODE = '0000000000000000'

    def __init__(self, string=None, integer=None, hashcode=None, type=None, version=DEFAULT_VERSION, checksum=None):
        self._set(string, integer, hashcode, type, version, checksum)

    def _set(self, string=None, integer=None, hashcode=None, type=None, version=DEFAULT_VERSION, checksum=None):
        args = 0
        for v in [string, integer, hashcode]:
            if v:
                args += 1
        if args > 1:
            raise IdentifierError('more than one identifier representation given')

        self._reset()

        resolver_list = []
        if string:
            resolver_list = ['_test_long_string', '_test_short_string']
            arg = string

        if integer:
            resolver_list = ['_test_integer']
            arg = integer

        if hashcode:
            resolver_list = ['_test_hashcode']
            arg = hashcode

        resolved = False
        for resolver in resolver_list:
            try:
                test = getattr(self, resolver)
                if test(arg):
                    resolved = True
                    break
            except:
                pass

        if resolved:
            if type and not self._test_type(type):
                raise IdentifierError('unknown type')
            if version and not self._test_version(version):
                raise IdentifierError('invalid version')
        else:
            raise IdentifierError('identifier is not resolvable')

        if self.checksum:
            if self._test_checksum(self.checksum, self.hashcode, self.type):
                self.string = "%s-%s-%s-%s" % (self.hashcode, self.type, self.version, self.checksum)
            else:
                raise IdentifierError('format error')
        else:
            if self.type and self.version:
                self.string = "%s-%s-%s" % (self.hashcode, self.type, self.version)
            else:
                self.string = self.hashcode

    def _reset(self):
        self.string = None
        self.hashcode = None
        self.type = None
        self.version = None
        self.checksum = None
        self.integer = None

    def _test_type(self, type):
        pattern = re.compile('(?P<type>FICTS|FICuS|FICTU|FICUU|Parent|uuuTS|uuuuS|uuuTu|uuuuu)$', re.IGNORECASE)
        match = pattern.search(str(type))
        if match:
            self.type = type.upper().replace("U", "u")
            return True
        return False

    def _test_version(self, version):
        pattern = re.compile('(?P<version>\d{2})', re.IGNORECASE)
        match = pattern.search(str(version))
        if match:
            self.version = version.upper()
            return True
        return False

    def _checksum_string(self, hashcode, type):
        if self._test_hashcode(hashcode) and self._test_type(type):
            try:
                string = "%s-%s" % (hashcode.upper(), type.upper().replace("U", "u"))
                checksum_string = hex(sum([ord(string[i]) for i in range(len(string))]) % 256)[2:].upper()
            except:
                raise IdentifierError('checksum calculation failed')
            else:
                return checksum_string.zfill(2)
        else:
            raise IdentifierError('checksum calculation failed')

    def _test_checksum(self, checksum, hashcode, type):
        correct_checksum = self._checksum_string(hashcode, type)
        if checksum:
            if checksum.upper() == correct_checksum:
                self.checksum = correct_checksum
                return True
            else:
                return False
        else:
            self.checksum = correct_checksum
            return True
        return False

    def _test_long_string(self, string):
        pattern = re.compile('(?P<hashcode>^.{16})-(?P<type>.{5,6})-(?P<version>.{2})-(?P<checksum>.{2}$)',
                             re.IGNORECASE)
        match = pattern.search(string)
        if match:
            identifier = match.groupdict()
            hashcode_match = self._test_hashcode(identifier['hashcode'])
            if not hashcode_match:
                return False
            checksum_match = self._test_checksum(identifier['checksum'], identifier['hashcode'], identifier['type'])
            if not checksum_match:
                return False
            type_match = self._test_type(identifier['type'])
            if not type_match:
                return False
            hashcode_match = self._test_hashcode(identifier['hashcode'])
            if not hashcode_match:
                return False
            version_match = self._test_version(identifier['version'])
            if not version_match:
                return False
            return True
        return False

    def _test_short_string(self, string):
        pattern = re.compile('(?P<hashcode>^.{16})-(?P<type>.{5,6})-(?P<version>.{2}$)', re.IGNORECASE)
        match = pattern.search(string)
        if match:
            identifier = match.groupdict()
            hashcode_match = self._test_hashcode(identifier['hashcode'])
            if not hashcode_match:
                return False
            type_match = self._test_type(identifier['type'])
            if not type_match:
                return False
            hashcode_match = self._test_hashcode(identifier['hashcode'])
            if not hashcode_match:
                return False
            version_match = self._test_version(identifier['version'])
            if not version_match:
                return False
            return True
        return False

    def _test_integer(self, value):
        pattern = re.compile('(?P<integer>^[0-9]*$)')
        match = pattern.search(str(value))
        if match:
            identifier = match.groupdict()
            self.integer = int(identifier['integer'])
            self.hashcode = hex(self.integer)[2:].replace('L', '').upper().zfill(16)
            return True
        else:
            return False

    def _test_hashcode(self, hashcode):
        pattern = re.compile('(?P<hashcode>^[0-9a-fA-F]{16})', re.IGNORECASE)
        match = pattern.search(str(hashcode))
        hashcode = match.groupdict()
        if match:
            self.hashcode = hashcode['hashcode'].zfill(16)
            self.integer = int(hashcode['hashcode'], 16)
            return True
        return False

    def __str__(self):
        return self.string

    def __repr__(self):
        return self.string

    def set_checksum(self):
        # pdb.set_trace()
        h = self.hashcode
        t = self.type
        v = self.version.zfill(2)
        c = self._checksum_string(h, t).zfill(2)

        string = "%s-%s-%s-%s" % (h, t, v, c)

        self._set(string=string)


class IdentifierError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
