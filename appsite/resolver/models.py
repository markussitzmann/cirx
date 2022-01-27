import uuid

from django.core.exceptions import FieldError
from django.db import models
from django.db.models import Index, UniqueConstraint
from django.forms import model_to_dict
from multiselectfield import MultiSelectField
from pycactvs import Ens

from structure.inchi.identifier import InChIKey, InChIString
from resolver import defaults

class InChIManager(models.Manager):

    def create_inchi(self, *args, **kwargs) -> 'InChI':
        if 'string' not in kwargs and 'key' not in kwargs:
            raise ValueError
        inchi = InChI.create(*args, **kwargs)
        return inchi

    def get_or_create_from_ens(self, ens: Ens) -> 'InChI':
        # TODO: improve
        try:
            inchikey = ens.get('E_STDINCHIKEY')
            inchi = ens.get('E_STDINCHI')
            i = InChI.create(key=inchikey, string=inchi)
            d = model_to_dict(i)
            d.pop('entrypoints', [])
            return self.get_or_create(id=i.id, **d)
        except Exception as e:
            raise ValueError(e)


class InChI(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    version = models.IntegerField(default=1)
    version_string = models.CharField(max_length=64)
    block1 = models.CharField(max_length=14)
    block2 = models.CharField(max_length=10)
    block3 = models.CharField(max_length=1)
    key = models.CharField(max_length=27, blank=True, null=True)
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
        db_table = 'cir_inchi'

    @classmethod
    def create(cls, *args, **kwargs):
        if 'url_prefix' in kwargs:
            inchiargs = kwargs.pop('url_prefix')
            inchi = cls(*args, inchiargs)
        else:
            inchi = cls(*args, **kwargs)
        k = None
        s = None
        if 'key' in kwargs and kwargs['key']:
            k = InChIKey(kwargs['key'])

        if 'string' in kwargs and kwargs['string']:
            s = InChIString(kwargs['string'])
            e = Ens(kwargs['string'])
            if s.element['is_standard']:
                _k = InChIKey(e.get('E_STDINCHIKEY'))
            else:
                _k = InChIKey(e.get('E_INCHIKEY'))
            if k:
                if not k.element['well_formatted'] == _k.element['well_formatted']:
                    raise FieldError("InChI key does not represent InChI string")
            else:
                k = _k

        inchi.key = k.element['well_formatted_no_prefix']
        inchi.version = k.element['version']
        inchi.is_standard = k.element['is_standard']
        inchi.block1 = k.element['block1']
        inchi.block2 = k.element['block2']
        inchi.block3 = k.element['block3']
        if s:
            inchi.string = s.element['well_formatted']
        inchi.id = uuid.uuid5(uuid.NAMESPACE_URL, "/".join([
            inchi.key,
            str(kwargs.get('safe_options', None)),
        ]))
        return inchi

    def __str__(self):
        return self.key


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
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
        organization.id = uuid.uuid5(uuid.NAMESPACE_URL, kwargs.get('name'))
        return organization

    def __str__(self):
        return self.name


class Publisher(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.SET_NULL, null=True)
    organization = models.ForeignKey('Organization', related_name='publishers', on_delete=models.SET_NULL, null=True)
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
                fields=['organization', 'parent', 'name', 'href', 'orcid'],
                name='unique_publisher_constraint'
            ),
        ]
        db_table = 'cir_publisher'

    @classmethod
    def create(cls, *args, **kwargs):
        publisher = cls(*args, **kwargs)
        publisher.id = uuid.uuid5(uuid.NAMESPACE_URL, "/".join([
            str(kwargs.get('organization', None)),
            str(kwargs.get('parent', None)),
            str(kwargs.get('href', None)),
            str(kwargs.get('orcid', None)),
            kwargs.get('name')
        ]))
        return publisher

    def __str__(self):
        return "%s[%s]" % (self.name, self.category)


class EntryPoint(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
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
        entrypoint.id = uuid.uuid5(uuid.NAMESPACE_URL, "/".join([
            str(kwargs.get('parent', None)),
            str(kwargs.get('publisher')),
            kwargs.get('href'),
        ]))
        return entrypoint

    def __str__(self):
        return "%s [%s]" % (self.publisher, self.href)


class EndPoint(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    entrypoint = models.ForeignKey('EntryPoint', related_name='endpoints', on_delete=models.SET_NULL, null=True)
    uri = models.CharField(max_length=32768)
    accept_header_media_types = models.ManyToManyField('MediaType', related_name='accepting_endpoints')
    content_media_types = models.ManyToManyField('MediaType', related_name='delivering_endpoints')
    request_schema_endpoint = models.ForeignKey('EndPoint', related_name='schema_requesting_endpoints',
                                                on_delete=models.SET_NULL, null=True)
    response_schema_endpoint = models.ForeignKey('EndPoint', related_name='schema_responding_endpoints',
                                                 on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=16, choices=(
        ('schema', 'Schema'),
        ('uritemplate', 'URI Template (RFC6570)'),
        ('documentation', 'Documentation (HTML, PDF)'),
    ), default='uritemplate')
    request_methods = MultiSelectField(choices=defaults.http_verbs, default=['GET'])
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
        endpoint.id = uuid.uuid5(uuid.NAMESPACE_URL, "/".join([
            str(kwargs.get('entrypoint')),
            kwargs.get('uri'),
        ]))
        return endpoint

    def __str__(self):
        return "%s[%s]" % (self.entrypoint, self.uri)


class MediaType(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
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
        mediatype.id = uuid.uuid5(uuid.NAMESPACE_URL, "/".join([
            str(kwargs.get('name'))
        ]))
        return mediatype

    def __str__(self):
        return "%s" % self.name
