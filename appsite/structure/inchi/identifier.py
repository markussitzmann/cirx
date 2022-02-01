import re
import uuid
from pycactvs import Ens
from typing import Dict


class InChIKey:

    DEFAULT_PREFIX = "InChIKey="
    PATTERN_STRING = '(?P<block1>[A-Z]{14})-(?P<block2>[A-Z]{8}(S|N)[A-Z]{1})-(?P<block3>[A-Z]{1}$)'
    PATTERN_STRING_WITH_PREFIX = \
        '(?P<prefix>^%s)(?P<block1>[A-Z]{14})-(?P<block2>[A-Z]{8}(S|N)[A-Z]{1})-(?P<block3>[A-Z]{1}$)' % DEFAULT_PREFIX

    def __init__(
            self,
            key=None,
            block1=None,
            block2=None,
            block3=None,
            safe_options=None,
            version_string=None,
            *args,
            **kwargs
    ):
        if args:
            key = args
        if key is None and block1 is not False:
            key = block1
            if block2:
                key += "-%s" % block2
            if block2 and block3:
                key += "-%s" % block3
        self.element = {'_key': key, 'safe_options': safe_options, 'version_string': version_string}
        pattern_list = [InChIKey.PATTERN_STRING, InChIKey.PATTERN_STRING_WITH_PREFIX]
        if not bool([self._validate(key, pattern) for pattern in pattern_list if self._validate(key, pattern)]):
            raise InChIKeyError('InChIKey is not resolvable')

    def _validate(self, key, pattern_string):
        pattern = re.compile(pattern_string)
        match = pattern.search(key)
        if match:
            identifier = match.groupdict()
            self.element.update(identifier)
            self.element['prefix'] = InChIKey.DEFAULT_PREFIX
            self.element['version'] = ord(self.element['block2'][-1:]) - 64
            self.element['is_standard'] = self.element['block2'][-2:-1] == 'S'
            self.element['blocks'] = (self.element['block1'], self.element['block2'], self.element['block3'])
            self.element['well_formatted'] = '%s%s-%s-%s' % (
                self.element['prefix'], self.element['block1'], self.element['block2'], self.element['block3'])
            self.element['well_formatted_no_prefix'] = '%s-%s-%s' % (
                self.element['block1'], self.element['block2'], self.element['block3'])
            return True
        return False

    @property
    def model_dict(self) -> Dict:
        return {
            'id': self._calculate_uuid(),
            'version': self.element['version'],
            'block1': self.element['block1'],
            'block2': self.element['block2'],
            'block3': self.element['block3'],
            'key': self.element['well_formatted_no_prefix'],
            'is_standard': self.element['is_standard'],
            'safe_options': self.element['safe_options'],
            'version_string': self.element['version_string']
        }

    def _calculate_uuid(self):
        return uuid.uuid5(uuid.NAMESPACE_URL, "/".join([
            self.element['well_formatted_no_prefix'],
            self.element['safe_options'] if self.element['safe_options'] else ''
        ]))

    def __eq__(self, other):
        selfh = self.element['well_formatted_no_prefix']
        otherh = self.element['well_formatted_no_prefix']
        return selfh == otherh

    def __str__(self):
        return self.element['well_formatted_no_prefix']


class InChIString:
    DEFAULT_VERSION = '1'
    DEFAULT_PREFIX = "InChI="
    PATTERN_STRING = '^(?P<version>.{1,2})/(?P<layers>.+$)'
    PATTERN_STRING_WITH_PREFIX = '^(?P<prefix>%s)(?P<version>.{1,2})/(?P<layers>.+$)' % DEFAULT_PREFIX

    def __init__(
            self,
            string: str = None,
            key: InChIKey = None,
            *arg,
            **kwarg
    ):
        self.element = {'_string': string, '_key': key}
        pattern_list = [InChIString.PATTERN_STRING, InChIString.PATTERN_STRING_WITH_PREFIX]
        if not bool([self._validate(string, pattern) for pattern in pattern_list if self._validate(string, pattern)]):
            raise InChIError('InChI string is not valid or does not match InChI key')

    def _string_key_match(self, key: InChIKey) -> bool:
        if not key:
            return True
        try:
            _k = self._calculate_inchikey()
            if not key.element['well_formatted'] == _k.element['well_formatted']:
                return False
            return True
        except Exception:
            return False

    def _calculate_inchikey(self) -> InChIKey:
        try:
            ens = Ens(self.element['well_formatted'])
            if self.element['is_standard']:
                k = InChIKey(ens.get('E_STDINCHIKEY'))
            else:
                k = InChIKey(ens.get('E_INCHIKEY'))
            return k
        except Exception:
            raise InChIError("can not calculate InChIKey")

    def _validate(self, string: str, pattern_string: str) -> bool:
        pattern = re.compile(pattern_string)
        match = pattern.search(string)
        if match:
            identifier = match.groupdict()
            self.element.update(identifier)
            self.element['prefix'] = InChIString.DEFAULT_PREFIX
            self.element['is_standard'] = self.element['version'][-1:] == 'S'
            self.element['version'] = self.element['version'][:1]
            if self.element['is_standard']:
                self.element['well_formatted'] = '%s%sS/%s' % (
                    self.element['prefix'], self.element['version'], self.element['layers']
                )
            else:
                self.element['well_formatted'] = '%s%s/%s' % (
                    self.element['prefix'], self.element['version'], self.element['layers']
                )
            if self.element['_key']:
                if self._string_key_match(
                    key=self.element['_key']
                ):
                    self.element.update(self.element['_key'].model_dict)
                    return True
                return False
            else:
                self.element.update(self._calculate_inchikey().model_dict)
                return True
        return False

    @property
    def model_dict(self) -> Dict:
        return {
            'id': self.element['id'],
            'version': self.element['version'],
            'block1': self.element['block1'],
            'block2': self.element['block2'],
            'block3': self.element['block3'],
            'key': self.element['key'],
            'string': self.element['well_formatted'],
            'is_standard': self.element['is_standard'],
            'safe_options': self.element['safe_options'],
            'version_string': self.element['version_string']
        }

    def __eq__(self, other):
        selfh = self.element['well_formatted']
        otherh = self.element['well_formatted']
        return selfh == otherh

    def __str__(self):
        return self.element['well_formatted']


class InChIError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InChIKeyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
