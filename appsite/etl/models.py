from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from database.models import Release


fs = FileSystemStorage(location=settings.CIR_FILESTORE_ROOT)


class FileCollection(models.Model):
    file_location_pattern_string = models.CharField(
        max_length=2048, blank=True, null=True
    )
    release = models.ForeignKey(
        Release,
        related_name='collection',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cir_structure_file_collection'


class StructureFile(models.Model):
    collection = models.ForeignKey(
        FileCollection,
        related_name='files',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    name = models.FileField(max_length=1024, upload_to="manual/", storage=fs)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['collection', 'name'],
                name='unique_structure_file_constraint'
            ),
        ]
        db_table = 'cir_structure_file'






