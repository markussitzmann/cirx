from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from resolver.models import Structure, Release, NameType

fs = FileSystemStorage(location=settings.CIR_FILESTORE_ROOT)


class StructureFileCollectionPreprocessor(models.Model):
    name = models.CharField(max_length=2048, null=False, blank=False, default="generic")
    params = models.JSONField(null=False, blank=False, default=dict)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'params'],
                name='unique_file_collection_preprocessor_constraint'
            ),
        ]
        db_table = 'cir_structure_file_collection_preprocessor'

    def __str__(self):
        return "%s" % self.name


class StructureFileCollection(models.Model):
    release = models.ForeignKey(
        Release,
        related_name='collections',
        blank=False,
        null=False,
        on_delete=models.CASCADE
    )
    preprocessors = models.ManyToManyField(
        'StructureFileCollectionPreprocessor',
        related_name="collections"
    )
    file_location_pattern_string = models.CharField(
        max_length=2048, blank=False, null=False, default="*"
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
        StructureFileCollection,
        related_name='files',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    file = models.FileField(max_length=1024, upload_to="manual/", storage=fs)
    count = models.IntegerField(null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    #processed = models.DateTimeField(auto_now=False, blank=True, null=True)

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


class StructureFileNormalizationStatus(models.Model):
    structure_file = models.OneToOneField(
        'StructureFile',
        primary_key=True,
        blank=False,
        null=False,
        related_name='normalization_status',
        on_delete=models.CASCADE,
    )
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    finished = models.BooleanField(default=False)

    class Meta:
        db_table = 'cir_structure_file_normalization_status'

    def __str__(self):
        return "normalization status %s (%s)" % (
            self.updated,
            self.finished
        )


class StructureFileInChIStatus(models.Model):
    structure_file = models.OneToOneField(
        'StructureFile',
        primary_key=True,
        blank=False,
        null=False,
        related_name='inchi_status',
        on_delete=models.CASCADE,
    )
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    finished = models.BooleanField(default=False)

    class Meta:
        db_table = 'cir_structure_file_inchi_status'

    def __str__(self):
        return "inchi status %s (%s)" % (
            self.updated,
            self.finished
        )


class StructureFileField(models.Model):
    field_name = models.CharField(max_length=768, null=False, blank=False, unique=True)
    structure_files = models.ManyToManyField(StructureFile, related_name="fields")

    class Meta:
        db_table = 'cir_structure_file_field'

    def __str__(self):
        return "%s" % self.field_name


class ReleaseNameField(models.Model):
    release = models.ForeignKey(
        Release,
        related_name='name_fields',
        blank=False,
        null=False,
        on_delete=models.RESTRICT
    )
    structure_file_field = models.ForeignKey(
        StructureFileField,
        related_name='name_fields',
        blank=False,
        null=False,
        on_delete=models.RESTRICT
    )
    name_type = models.ForeignKey(
        NameType,
        related_name='name_fields',
        blank=False,
        null=False,
        on_delete=models.RESTRICT
    )
    is_regid = models.BooleanField(default=False)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['release', 'structure_file_field', 'name_type'],
                name='unique_release_name_field_constraint'
            ),
        ]
        db_table = 'cir_release_name_field'


class StructureFileRecord(models.Model):
    structure_file = models.ForeignKey(
        StructureFile,
        related_name='structure_file_records',
        blank=False,
        null=False,
        on_delete=models.CASCADE
    )
    structure = models.ForeignKey(
        Structure,
        related_name='structure_file_records',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    number = models.IntegerField(null=False, blank=False)
    releases = models.ManyToManyField(Release,
        through='StructureFileRecordRelease',
        related_name="records"
    )
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


class StructureFileRecordRelease(models.Model):
    structure_file_record = models.ForeignKey(
        StructureFileRecord,
        related_name='structure_file_record_releases',
        blank=False,
        null=False,
        on_delete=models.CASCADE
    )
    release = models.ForeignKey(
        Release,
        related_name='structure_file_records',
        blank=False,
        null=False,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['structure_file_record', 'release'],
                name='unique_structure_file_record_release_constraint'
            ),
        ]
        db_table = 'cir_structure_file_record_releases'
