import re


class PackString:

    def __init__(self, string=None):
        self.string = None
        if not self._test_packstring(string=string):
            raise PackStringError('no valid pack string')
        self.string = string

    def _test_packstring(self, string):

        expression = re.compile('^eJ.+$')
        if expression.match(string):
            return True
        return False


class PackStringError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
