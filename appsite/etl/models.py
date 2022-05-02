from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from database.models import Release
from custom.fields import CactvsHashField
from structure.models import Structure

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
    file = models.FileField(max_length=1024, upload_to="manual/", storage=fs)
    count = models.IntegerField(null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    processed = models.DateTimeField(auto_now=False, blank=True, null=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['collection', 'file'],
                name='unique_structure_file_constraint'
            ),
        ]
        db_table = 'cir_structure_file'

    def __str__(self):
        return "%s (%s)" % (self.file, self.count)


class StructureFileField(models.Model):
    name = models.CharField(max_length=768, null=False, blank=False, unique=True)
    structure_files = models.ManyToManyField(StructureFile, related_name="fields")

    class Meta:
        db_table = 'cir_structure_file_field'

    def __str__(self):
        return "%s" % self.name


class StructureFileRecord(models.Model):
    structure_file = models.ForeignKey(StructureFile, blank=False, null=False, on_delete=models.CASCADE)
    structure = models.ForeignKey(
        Structure,
        related_name='structure_file_records',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    number = models.IntegerField(null=False, blank=False)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    processed = models.DateTimeField(auto_now=False, blank=True, null=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['structure_file', 'number'],
                name='unique_structure_file__record_constraint'
            ),
        ]
        db_table = 'cir_structure_file_record'

    def __str__(self):
        return "%s (%s)" % (self.structure_file, self.number)
