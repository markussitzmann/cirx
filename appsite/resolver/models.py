import uuid

from django.db import models, IntegrityError
from django.db.models import Index, UniqueConstraint
from multiselectfield import MultiSelectField

from resolver.defaults import http_verbs
from structure.inchi.identifier import InChIString


class InChIManager(models.Manager):

    def create(self, string=None, *args, **kwargs):
        if not string and 'string' not in kwargs:
            raise IntegrityError('InChI string required for creation of InChI instance')
        inchi = InChIString(string, *args, **kwargs)
        return super(InChIManager, self).create(**inchi.model_dict)

    def get_or_create(self, string=None, *args, **kwargs):
        if not string and 'string' not in kwargs:
            raise IntegrityError('InChI string required for creation of InChI instance')
        inchi = InChIString(string, *args, **kwargs)
        return super(InChIManager, self).get_or_create(**inchi.model_dict)


class InChI(models.Model):

    id = models.UUIDField(primary_key=True, editable=False)
    version = models.IntegerField(default=1)
    version_string = models.CharField(max_length=64, blank=True, null=True)
    block1 = models.CharField(max_length=14)
    block2 = models.CharField(max_length=10)
    block3 = models.CharField(max_length=1)
    key = models.CharField(max_length=27)
    string = models.CharField(max_length=32768, blank=True, null=True)
    is_standard = models.BooleanField(default=False)
    safe_options = models.CharField(max_length=2, default=None, null=True)
    entrypoints = models.ManyToManyField('EntryPoint', related_name='inchis', blank=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = InChIManager()

    indexes = Index(
        fields=['version', 'block1', 'block2', 'block3'],
        name='inchi_index'
    )

    class JSONAPIMeta:
        resource_name = 'inchis'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['version', 'block1', 'block2', 'block3'],
                name='unique_inchi_constraint'
            ),
        ]
        verbose_name = "InChI"
        verbose_name_plural = "InChIs"
        db_table = 'cir_inchi'

    @classmethod
    def create(cls, *args, **kwargs):
        inchi = cls(*args, **kwargs)
        return inchi

    def __str__(self):
        return self.key


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=32768)
    abbreviation = models.CharField(max_length=32, blank=True, null=True)
    category = models.CharField(max_length=16, choices=(
        ('regulatory', 'Regulatory'),
        ('government', 'Government'),
        ('academia', 'Academia'),
        ('company', 'Company'),
        ('vendor', 'Vendor'),
        ('research', 'Research'),
        ('publishing', 'Publishing'),
        ('provider', 'Provider'),
        ('public', 'Public'),
        ('society', "Society"),
        ('charity', "Charity"),
        ('other', 'Other'),
        ('none', 'None'),
    ), default='none')
    href = models.URLField(max_length=4096, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    indexes = Index(
        fields=['name', 'abbreviation'],
        name='organization_index'
    )

    class JSONAPIMeta:
        resource_name = 'organizations'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['parent', 'name'],
                name='unique_organization_constraint'
            ),
        ]
        db_table = 'cir_organization'


    @classmethod
    def create(cls, *args, **kwargs):
        organization = cls(*args, **kwargs)
        return organization

    def __str__(self):
        return self.name


class Publisher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.SET_NULL, null=True)
    organizations = models.ManyToManyField('Organization', related_name='publishers', blank=True)
    category = models.CharField(max_length=16, choices=(
        ('entity', 'Entity'),
        ('service', 'Service'),
        ('network', 'Network'),
        ('division', 'Division'),
        ('group', 'Group'),
        ('person', 'Person'),
        ('other', 'Other'),
        ('none', 'None'),
    ), default='none')
    name = models.CharField(max_length=1024)
    email = models.EmailField(max_length=254, blank=True, null=True)
    address = models.CharField(max_length=8192, blank=True, null=True)
    href = models.URLField(max_length=4096, blank=True, null=True)
    orcid = models.URLField(max_length=4096, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    indexes = Index(
        fields=['name'],
        name='publisher_index'
    )

    class JSONAPIMeta:
        resource_name = 'publishers'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['parent', 'name', 'category', 'href', 'orcid'],
                name='unique_publisher_constraint'
            ),
        ]
        db_table = 'cir_publisher'

    @classmethod
    def create(cls, *args, **kwargs):
        publisher = cls(*args, **kwargs)
        return publisher

    def __str__(self):
        return "%s" % self.name


class EntryPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='children', null=True)
    category = models.CharField(max_length=16, choices=(
        ('self', 'Self'),
        ('site', 'Site'),
        ('api', 'API'),
        ('resolver', 'Resolver'),
    ), default='site')
    publisher = models.ForeignKey("Publisher", related_name="entrypoints", on_delete=models.SET_NULL, null=True)
    href = models.URLField(max_length=4096)
    entrypoint_href = models.URLField(max_length=4096, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=32768, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    indexes = Index(
        fields=['name'],
        name='entrypoint_index'
    )

    class JSONAPIMeta:
        resource_name = 'entrypoints'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['parent', 'publisher', 'href'],
                name='unique_entrypoint_constraint'
            ),
        ]
        db_table = 'cir_entrypoint'

    @classmethod
    def create(cls, *args, **kwargs):
        entrypoint = cls(*args, **kwargs)
        return entrypoint

    def __str__(self):
        return "%s [%s]" % (self.publisher, self.href)


class EndPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entrypoint = models.ForeignKey('EntryPoint', related_name='endpoints', on_delete=models.SET_NULL, null=True)
    uri = models.CharField(max_length=32768)
    accept_header_media_types = models.ManyToManyField(
        'MediaType',
        related_name='accepting_endpoints'
    )
    content_media_types = models.ManyToManyField(
        'MediaType',
        related_name='delivering_endpoints'
    )
    request_schema_endpoint = models.ForeignKey(
        'EndPoint',
        related_name='schema_requesting_endpoints',
        on_delete=models.SET_NULL,
        null=True
    )
    response_schema_endpoint = models.ForeignKey(
        'EndPoint',
        related_name='schema_responding_endpoints',
        on_delete=models.SET_NULL,
        null=True
    )
    category = models.CharField(max_length=16, choices=(
        ('schema', 'Schema'),
        ('uritemplate', 'URI Template (RFC6570)'),
        ('documentation', 'Documentation (HTML, PDF)'),
    ), default='uritemplate')
    request_methods = MultiSelectField(choices=http_verbs, default=['GET'])
    description = models.TextField(max_length=32768, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class JSONAPIMeta:
        resource_name = 'endpoints'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['entrypoint', 'uri'],
                name='unique_endpoint_constraint'
            ),
        ]
        db_table = 'cir_endpoint'

    def full_path_uri(self):
        if self.entrypoint:
            return self.entrypoint.href + "/" + self.uri
        else:
            return self.uri

    @classmethod
    def create(cls, *args, **kwargs):
        endpoint = cls(*args, **kwargs)
        return endpoint

    def __str__(self):
        return "%s[%s]" % (self.entrypoint, self.uri)


class MediaType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1024, blank=False, null=False, unique=True)
    description = models.TextField(max_length=32768, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class JSONAPIMeta:
        resource_name = 'mediatypes'

    class Meta:
        db_table = 'cir_media_type'

    @classmethod
    def create(cls, *args, **kwargs):
        mediatype = cls(*args, **kwargs)
        return mediatype

    def __str__(self):
        return "%s" % self.name
