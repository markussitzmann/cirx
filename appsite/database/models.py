import uuid

from django.db import models
from django.core.exceptions import *
from django.db.models import UniqueConstraint

from resolver.models import Publisher


class ContextTag(models.Model):
    tag = models.CharField(max_length=128, blank=False, null=False, unique=True)
    description = models.TextField(max_length=1500, blank=True, null=True)

    class Meta:
        verbose_name = "Context Teg"
        verbose_name_plural = "Context Tags"
        db_table = 'cir_database_context_tag'

    def __str__(self):
        return self.tag


class URIPattern(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uri = models.CharField(max_length=32768)
    category = models.CharField(max_length=16, choices=(
        ('schema', 'Schema'),
        ('uritemplate', 'URI Template (RFC6570)'),
        ('documentation', 'Documentation (HTML, PDF)'),
    ), default='uritemplate')
    description = models.TextField(max_length=32768, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-added']
        constraints = [
            UniqueConstraint(
                fields=['uri', 'category'],
                name='unique_uripattern_constraint'
            ),
        ]
        db_table = 'cir_database_uri_pattern'


class Database(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=768, null=False, blank=False)
    href = models.URLField(max_length=4096, null=True, blank=True)
    description = models.TextField(max_length=4096, null=True, blank=True)
    publisher = models.ForeignKey(Publisher, null=True, blank=True, on_delete=models.CASCADE)
    context_tags = models.ManyToManyField(ContextTag)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-added']
        constraints = [
            UniqueConstraint(
                fields=['name', 'publisher'],
                name='unique_database_constraint'
            ),
        ]
        db_table = 'cir_database'

    def __str__(self):
        return self.name


class Release(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    database = models.ForeignKey(Database, blank=False, null=False, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, blank=False, null=False, on_delete=models.CASCADE)
    description = models.TextField(max_length=2048, blank=True, null=True)
    href = models.URLField(max_length=4096, null=True, blank=True)
    record_uri_pattern = models.ManyToManyField(URIPattern)
    classification = models.CharField(
        max_length=32,
        db_column='class',
        blank=True,
        choices=(
            ('public', 'Public'),
            ('private', 'Private'),
            ('internal', 'Internal'),
            ('legacy', 'Legacy'),
        )
    )
    status = models.CharField(max_length=32, blank=True, choices=(('active', 'Show'), ('inactive', 'Hide')))
    version = models.CharField(max_length=255, null=True, blank=True)
    released = models.DateField(null=True, blank=True, verbose_name="Date Released")
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-added']
        constraints = [
            UniqueConstraint(
                fields=['database', 'publisher', 'version', 'released'],
                name='unique_database_release_constraint'
            ),
        ]
        db_table = 'cir_database_release'

    def version_name(self):
        date_string = "%s/%s" % (self.released.strftime('%m'), self.released.strftime('%Y'))
        if self.version:
            return "%s (%s)" % (self.version, date_string)
        else:
            return date_string

    def database_name(self):
        string = "%s (%s)" % (self.database.name, self.publisher.name)
        return string

    def __str__(self):
        version_name = self.version_name()
        string = "%s %s" % (self.database_name(), version_name)
        return string



