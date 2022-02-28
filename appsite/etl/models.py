from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from database.models import Release


fs = FileSystemStorage(location=settings.CIR_FILESTORE_ROOT)


class FileCollection(models.Model):
    release = models.ForeignKey(
        Release,
        related_name='collections',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    file_location_pattern_string = models.CharField(
        max_length=2048, blank=True, null=True
    )
    description = models.TextField(max_length=768, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['release', 'file_location_pattern_string'],
                name='unique_file_collection_constraint'
            ),
        ]
        db_table = 'cir_structure_file_collection'

    def __str__(self):
        if self.release:
            return "File Collection for %s" % self.release.release_name
        else:
            return "File Collection - no linked release (%s)" % self.id


class StructureFile(models.Model):
    collection = models.ForeignKey(
        FileCollection,
        related_name='files',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    name = models.FileField(max_length=1024, upload_to="manual/", storage=fs)
    count = models.IntegerField(null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    processed = models.DateTimeField(auto_now=False, blank=True, null=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['collection', 'name'],
                name='unique_structure_file_constraint'
            ),
        ]
        db_table = 'cir_structure_file'

    def __str__(self):
        return "%s (%s)" % (self.name, self.count)



