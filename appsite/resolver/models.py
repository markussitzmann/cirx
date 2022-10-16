import uuid
from typing import List

from pycactvs import Ens

from django.db import models, IntegrityError
from django.db.models import Index, UniqueConstraint
from multiselectfield import MultiSelectField

from resolver.defaults import http_verbs

from custom.cactvs import CactvsHash, CactvsMinimol
from custom.fields import CactvsHashField, CactvsMinimolField
from structure.inchi.identifier import InChIString


class StructureManager(models.Manager):

    def get_or_create_from_ens(self, ens: Ens):
        return self.get_or_create(hashisy=CactvsHash(ens), minimol=CactvsMinimol(ens))


class Structure(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hashisy_key = CactvsHashField(unique=True)
    minimol = CactvsMinimolField(null=False)
    names = models.ManyToManyField(
        'Name',
        through='StructureNameAssociation',
        related_name="structures"
    )
    entrypoints = models.ManyToManyField('EntryPoint', related_name='structures', blank=True)
    added = models.DateTimeField(auto_now_add=True)
    blocked = models.DateTimeField(auto_now=False, blank=True, null=True)

    #indexes = Index(
    #    fields=['ficts_parent', 'ficus_parent', 'uuuuu_parent', 'hashisy_key', 'hashisy'],
    #    name='structure_index'
    #)

    class JSONAPIMeta:
        resource_name = 'structures'

    class Meta:
        db_table = 'cir_structure'
        verbose_name = "Structure"
        verbose_name_plural = "Structures"

    objects = StructureManager()

    @property
    def to_ens(self) -> Ens:
        return self.minimol.ens

    def __str__(self):
        return "[%s] %s" % (self.hashisy_key.padded, self.to_ens.get("E_SMILES"))


class StructureHashisy(models.Model):
    structure = models.OneToOneField(
        'Structure',
        primary_key=True,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
    )
    hashisy = models.CharField(max_length=16, null=False, blank=False, db_index=True)

    class Meta:
        db_table = 'cir_structure_hashisy'


class StructureParentStructure(models.Model):
    structure = models.OneToOneField(
        'Structure',
        primary_key=True,
        blank=False,
        null=False,
        on_delete=models.PROTECT
    )
    ficts_parent = models.ForeignKey(
        'Structure', blank=True, null=True, related_name='ficts_children', on_delete=models.PROTECT)
    ficus_parent = models.ForeignKey(
        'Structure', blank=True, null=True, related_name='ficus_children', on_delete=models.PROTECT)
    uuuuu_parent = models.ForeignKey(
        'Structure', blank=True, null=True, related_name='uuuuu_children', on_delete=models.PROTECT)

    class Meta:
        db_table = 'cir_structure_parent'


class InChIManager(models.Manager):

    #def create(self, string=None, *args, **kwargs):
    #    if not string and 'string' not in kwargs:
    #        raise IntegrityError('InChI string required for creation of InChI instance')
    #    inchi = InChIString(string, *args, **kwargs)
    #    return super(InChIManager, self).create(**inchi.model_dict)

    #def get_or_create(self, string=None, *args, **kwargs):
    #    if not string and 'string' not in kwargs:
    #        raise IntegrityError('InChI string required for creation of InChI instance')
    #    inchi = InChIString(string, *args, **kwargs)
    #    return super(InChIManager, self).get_or_create(**inchi.model_dict)

    def bulk_get_from_objects(self, object_list: List['InChI']):
        inchi_list = []
        for o in object_list:
            if o.pk:
                inchi_list.append(o)
            else:
                i = InChI.objects.get(
                    block1=o.block1,
                    block2=o.block2,
                    block3=o.block3
                )
                inchi_list.append(i)
        return inchi_list

class InChI(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.IntegerField(default=1, blank=False, null=False)
    block1 = models.CharField(max_length=14, blank=False, null=False)
    block2 = models.CharField(max_length=10, blank=False, null=False)
    block3 = models.CharField(max_length=1, blank=False, null=False)
    key = models.CharField(max_length=27)
    string = models.CharField(max_length=32768, blank=True, null=True)
    entrypoints = models.ManyToManyField('EntryPoint', related_name='inchis', blank=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = InChIManager()

    indexes = Index(
        fields=['block1', 'block2', 'block3', 'version'],
        name='inchi_index'
    )

    class JSONAPIMeta:
        resource_name = 'inchis'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['block1', 'block2', 'block3', 'version'],
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


class InChIType(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False)
    software_version = models.CharField(max_length=16, default=None, blank=True, null=True)
    description = models.TextField(max_length=32768, blank=True, null=True)
    is_standard = models.BooleanField(default=False)
    newpsoff = models.BooleanField(default=False)
    donotaddh = models.BooleanField(default=False)
    snon = models.BooleanField(default=False)
    srel = models.BooleanField(default=False)
    srac = models.BooleanField(default=False)
    sucf = models.BooleanField(default=False)
    suu = models.BooleanField(default=False)
    sluud = models.BooleanField(default=False)
    recmet = models.BooleanField(default=False)
    fixedh = models.BooleanField(default=False)
    ket = models.BooleanField(default=False)
    t15 = models.BooleanField(default=False)
    pt_22_00 = models.BooleanField(default=False)
    pt_16_00 = models.BooleanField(default=False)
    pt_06_00 = models.BooleanField(default=False)
    pt_39_00 = models.BooleanField(default=False)
    pt_13_00 = models.BooleanField(default=False)
    pt_18_00 = models.BooleanField(default=False)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class JSONAPIMeta:
        resource_name = 'inchitypes'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=[
                    'software_version',
                    'is_standard',
                    'newpsoff',
                    'donotaddh',
                    'snon',
                    'srel',
                    'srac',
                    'sucf',
                    'suu',
                    'sluud',
                    'recmet',
                    'fixedh',
                    'ket',
                    't15',
                    'pt_22_00',
                    'pt_16_00',
                    'pt_06_00',
                    'pt_39_00',
                    'pt_13_00',
                    'pt_18_00',
                ],
                name='inchi_type_constraint'
            ),
        ]
        db_table = 'cir_inchi_type'


class StructureInChIAssociation(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    structure = models.ForeignKey(
        Structure,
        related_name='inchis',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    inchi = models.ForeignKey(
        InChI,
        related_name='structures',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    inchitype = models.ForeignKey(
        InChIType,
        related_name='associations',
        on_delete=models.RESTRICT,
        blank=False,
        null=False
    )
    software_version = models.CharField(max_length=16, default="1", blank=False, null=False)
    save_opt = models.CharField(max_length=2, default="", blank=True, null=False)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    indexes = Index(
        fields=['inchi_key'],
        name='structure_inchi_association_index'
    )

    class JSONAPIMeta:
        resource_name = 'structureInchiAssociations'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['structure', 'inchi', 'inchitype', 'save_opt'],
                name='unique_structure_inchi_association'
            ),
        ]
        db_table = 'cir_structure_inchi_associations'


class Compound(models.Model):
    structure = models.OneToOneField(
        'Structure',
        blank=False,
        null=False,
        on_delete=models.PROTECT
    )
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    blocked = models.DateTimeField(auto_now=False, blank=True, null=True)

    class Meta:
        db_table = 'cir_compound'

    def __str__(self):
        return "NCICADD:CID=%s" % self.id

    def __repr__(self):
        return "NCICADD:CID=%s" % self.id


class Record(models.Model):
    regid = models.ForeignKey('Name', on_delete=models.PROTECT, blank=False, null=False)
    version = models.IntegerField(default=1, blank=False, null=False)
    release = models.ForeignKey('Release', blank=False, null=False, on_delete=models.CASCADE)
    dataset = models.ForeignKey('Dataset', blank=False, null=False, on_delete=models.RESTRICT)
    structure_file_record = models.ForeignKey(
        'etl.StructureFileRecord',
        blank=False,
        null=False,
        related_name="records",
        on_delete=models.PROTECT
    )
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['regid', 'version', 'release'], name='unique_record'),
        ]
        db_table = 'cir_record'

    def __str__(self):
        return "NCICADD:RID=%s" % self.regid


class Name(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=1500, unique=True)

    class Meta:
        db_table = 'cir_structure_name'

    # def get_structure(self):
    #     return self.structure.get()

    def __str__(self):
        return "Name='%s'" % (self.name, )

    def __repr__(self):
        return self.name


class NameType(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.SET_NULL, blank=True, null=True)
    public_string = models.TextField(max_length=64, blank=True, null=True)
    description = models.TextField(max_length=768, blank=True, null=True)

    class Meta:
        db_table = 'cir_name_type'


class StructureNameAssociation(models.Model):
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE)
    name_type = models.ForeignKey(NameType, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'structure', 'name_type'], name='unique_structure_names'),
        ]
        db_table = 'cir_structure_names'


class Organization(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
        ('generic', 'Generic'),
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
                fields=['name', 'category'],
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
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.SET_NULL, null=True, blank=True)
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
        ('generic', 'Generic'),
    ), default='none')
    name = models.CharField(max_length=1024, blank=False, null=False)
    description = models.TextField(max_length=32768, blank=True, null=True)
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
                fields=['name', 'category'],
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
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
                fields=['category', 'href'],
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
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    request_methods = MultiSelectField(choices=http_verbs, default=['GET'], max_length=16)
    description = models.TextField(max_length=32768, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class JSONAPIMeta:
        resource_name = 'endpoints'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['category', 'uri'],
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
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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


class ContextTag(models.Model):
    tag = models.CharField(max_length=128, blank=False, null=False, unique=True)
    description = models.TextField(max_length=1500, blank=True, null=True)

    class Meta:
        verbose_name = "Context Teg"
        verbose_name_plural = "Context Tags"
        db_table = 'cir_dataset_context_tag'

    def __str__(self):
        return "%s" % self.tag


class URIPattern(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uri = models.CharField(max_length=32768)
    category = models.CharField(max_length=16, choices=(
        ('schema', 'Schema'),
        ('uritemplate', 'URI Template (RFC6570)'),
        ('documentation', 'Documentation (HTML, PDF)'),
    ), default='uritemplate')
    name = models.CharField(max_length=768, null=False, blank=False)
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
        db_table = 'cir_dataset_uri_pattern'


class Dataset(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
                name='unique_dataset_constraint'
            ),
        ]
        db_table = 'cir_dataset'

    def __str__(self):
        return "%s" % self.name


class Release(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.SET_NULL, blank=True, null=True)
    dataset = models.ForeignKey(Dataset, related_name='releases', blank=False, null=False, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, related_name='releases', blank=False, null=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=768, null=False, blank=False)
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
    version = models.CharField(max_length=255, null=False, blank=False, default="0")
    released = models.DateField(null=True, blank=True, verbose_name="Date Released")
    downloaded = models.DateField(null=True, blank=True, verbose_name="Date Downloaded")
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-added']
        constraints = [
            UniqueConstraint(
                fields=['dataset', 'publisher', 'name', 'version', 'downloaded', 'released'],
                name='unique_dataset_release_constraint'
            ),
        ]
        db_table = 'cir_dataset_release'

    @property
    def version_string(self):
        if self.version:
            return self.version
        if self.released:
            date_string = "(%s/%s)" % (self.released.strftime('%m'), self.released.strftime('%Y'))
            return date_string
        else:
            return None

    @property
    def release_name(self):
        if self.name:
            return self.name
        else:
            if self.version_string:
                string = "%s %s" % (self.dataset.name, self.version_string)
            else:
                string = "%s (%s)" % (self.dataset.name, self.publisher)
            return string

    def __str__(self):
        return "%s" % self.release_name