from django.db.models import BigIntegerField, BinaryField

from django.utils.translation import gettext_lazy as _

from custom.cactvs import CactvsHash, CactvsMinimol


class CactvsHashField(BigIntegerField):
    empty_strings_allowed = False
    description = _("Cactvs Hashcode field")

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is not None:
            if connection.vendor == 'postgresql':
                return value.signed_int()
        return value.int()

    def get_prep_value(self, value):
        return value

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        if connection.vendor == 'postgresql':
            return CactvsHash(value, signed=True)
        return CactvsHash(value)

    def to_python(self, value):
        if isinstance(value, CactvsHash):
            return value
        if value is None:
            return value
        return CactvsHash(value)


class CactvsMinimolField(BinaryField):
    empty_strings_allowed = False
    description = _("Cactvs Hashcode field")

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is not None:
            return value.minimol()
        return value

    def get_prep_value(self, value):
        return value

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return CactvsMinimol(value.tobytes())

    def to_python(self, value):
        if isinstance(value, CactvsMinimol):
            return value
        if value is None:
            return value
        return CactvsMinimol(value.tobytes())
