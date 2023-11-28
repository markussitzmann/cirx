import hashlib
import operator
from functools import reduce
from typing import List, Dict, Union

from django.db import models
from django.db.models import Index, UniqueConstraint, Count, Q
from multiselectfield import MultiSelectField
from pycactvs import Ens

from core.cactvs import CactvsHash, CactvsMinimol
from core.fields import CactvsHashField, CactvsMinimolField
from resolver.defaults import http_verbs


class StructureManager(models.Manager):

    def get_or_create_from_ens(self, ens: Ens):
        return self.get_or_create(hashisy_key=CactvsHash(ens), minimol=CactvsMinimol(ens))


class StructureQuerySet(models.QuerySet):

    def _base_queryset(self):
        return self.select_related(
            'compound',
            'parents',
            'parents__ficts_parent',
            'parents__ficus_parent',
            'parents__uuuuu_parent',
            'parents__ficts_parent__hashisy',
            'parents__ficus_parent__hashisy',
            'parents__uuuuu_parent__hashisy',
            'parents__ficts_parent__compound',
            'parents__ficus_parent__compound',
            'parents__uuuuu_parent__compound',
            'hashisy',
        )

    def by_compound(self, compounds: List[Union['Compound', int]], ):
        queryset = self._base_queryset().filter(compound__in=compounds)
        return queryset

    def by_hashisy(self, hashisy_list: List[Union['CactvsHash', int, str, hex]], ):
        keys = [CactvsHash(h) for h in hashisy_list]
        queryset = self._base_queryset().filter(hashisy_key__in=keys)
        return queryset


class Structure(models.Model):
    hashisy_key = CactvsHashField(unique=True)
    minimol = CactvsMinimolField(null=False)
    entrypoints = models.ManyToManyField('EntryPoint', related_name='structures', blank=True)
    added = models.DateTimeField(auto_now_add=True)
    blocked = models.DateTimeField(auto_now=False, blank=True, null=True)

    objects = StructureManager()
    with_related_objects = StructureQuerySet.as_manager()

    class JSONAPIMeta:
        resource_name = 'structures'

    class Meta:
        db_table = 'cir_structure'
        verbose_name = "Structure"
        verbose_name_plural = "Structures"

    @property
    def to_ens(self) -> Ens:
        return self.minimol.ens

    @property
    def smiles(self) -> str:
        return self.to_ens.get("E_SMILES")

    def __str__(self):
        return "(Structure=%s: hashisy=%s smiles='%s')" % (self.id, self.hashisy_key.padded, self.smiles)

    def __repr__(self):
        return "NCICADD:SID={}".format(self.id)


class StructureHashisyManager(models.Manager):

    def bulk_create_from_hash_list(self, hashisy_key_list: List[CactvsHash], batch_size=1000) -> Dict[CactvsHash, Structure]:
        structure_hashkey_dict: Dict[CactvsHash, Structure] = Structure.objects.in_bulk(
            hashisy_key_list, field_name='hashisy_key'
        )
        structure_hashisy_list = [
            StructureHashisy(structure=structure_hashkey_dict[key], hashisy=key.padded)
            for key in hashisy_key_list
        ]
        StructureHashisy.objects.bulk_create(
            structure_hashisy_list,
            batch_size=batch_size,
            ignore_conflicts=True
        )
        return structure_hashkey_dict


class StructureHashisy(models.Model):
    structure = models.OneToOneField(
        'Structure',
        primary_key=True,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name='hashisy'
    )
    hashisy = models.CharField(max_length=16, null=False, blank=False, db_index=True)

    class Meta:
        db_table = 'cir_structure_hashisy'

    objects = StructureHashisyManager()


class StructureParentStructure(models.Model):
    structure = models.OneToOneField(
        'Structure',
        primary_key=True,
        blank=False,
        null=False,
        related_name='parents',
        on_delete=models.PROTECT
    )
    ficts_parent = models.ForeignKey(
        'Structure', blank=True, null=True, related_name='ficts_children', on_delete=models.PROTECT)
    ficus_parent = models.ForeignKey(
        'Structure', blank=True, null=True, related_name='ficus_children', on_delete=models.PROTECT)
    uuuuu_parent = models.ForeignKey(
        'Structure', blank=True, null=True, related_name='uuuuu_children', on_delete=models.PROTECT)

    class JSONAPIMeta:
        resource_name = 'structureparents'
    
    
    class Meta:
        db_table = 'cir_structure_parent_structure'
        verbose_name = "Structure Parent"
        verbose_name_plural = "Structure Parents"

    def __str__(self):
        return "(StructureParentStructure=%s: ficts=%s, ficus=%s, uuuuu=%s)" % \
               (self.structure_id, self.ficts_parent_id, self.ficus_parent_id, self.uuuuu_parent_id)


class InChIManager(models.Manager):
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
    title = models.CharField(max_length=32, unique=True, editable=False)
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

    def __str__(self):
        return "(InChIType=%s: %s)" % (self.id, self.title, )


class StructureInChIAssociationQuerySet(models.QuerySet):

    def _base_queryset(self):
        return self.select_related(
            'inchi',
            'structure',
            'structure__compound',
            'inchi_type'
        )

    def by_compound(
            self,
            compounds: List[Union['Compound', int]],
            inchi_types: List[Union['InChIType', int]] = None
    ):
        queryset = self._base_queryset().filter(structure__compound__in=compounds)
        if inchi_types:
            queryset = queryset.filter(
                inchi_type__in=inchi_types
            )
        return queryset

    def by_inchikey(
            self,
            inchikeys: List[Union['inchikey', str]],
            inchi_types: List[Union['InChIType', int]] = None
    ):
        queryset = self._base_queryset().filter(inchi__key__in=inchikeys)
        if inchi_types:
            queryset = queryset.filter(
                inchi_type__in=inchi_types
            )
        return queryset

    def by_partial_inchikey(
            self,
            inchikeys: List[Union[str]],
            inchi_types: List[Union['InChIType', int]] = None
    ):
        q = Q()
        for inchikey in inchikeys:
            splitted_inchikey = inchikey.split("-")
            number_of_elements = len(splitted_inchikey)
            if number_of_elements == 3:
                q |= Q(inchi__block1=splitted_inchikey[0], inchi__block2=splitted_inchikey[1], inchi__block3=splitted_inchikey[2])
            elif number_of_elements == 2:
                q |= Q(inchi__block1=splitted_inchikey[0], inchi__block2=splitted_inchikey[1])
            elif number_of_elements == 1:
                q |= Q(inchi__block1=splitted_inchikey[0])
            else:
                pass

        queryset = self._base_queryset().filter(q)
        if inchi_types:
            queryset = queryset.filter(
                inchi_type__in=inchi_types
            )
        return queryset

    def by_querydict(
            self,
            query_dicts: List[Dict],
            inchi_types: List[Union['InChIType', int]] = None
    ):
        q = Q()
        for d in query_dicts:
            q |= d
        #inchikeys = InChI.objects.filter(**inchikey_query)
        queryset = self._base_queryset().filter(q)
        if inchi_types:
            queryset = queryset.filter(
                inchi_type__in=inchi_types
            )
        return queryset


class StructureInChIAssociation(models.Model):
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
    inchi_type = models.ForeignKey(
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

    objects = models.Manager()
    with_related_objects = StructureInChIAssociationQuerySet.as_manager()

    class JSONAPIMeta:
        resource_name = 'structureinchiassociations'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['structure', 'inchi', 'inchi_type', 'save_opt'],
                name='unique_structure_inchi_association'
            ),
        ]
        db_table = 'cir_structure_inchi_associations'


class CompoundQuerySet(models.QuerySet):

    def by_compound_ids(self, ids: List[int]):
        queryset = self.select_related(
            'structure',
            'structure__parents',
            'structure__parents__ficts_parent',
            'structure__parents__ficus_parent',
            'structure__parents__uuuuu_parent',
            'structure__parents__ficts_parent__compound',
            'structure__parents__ficus_parent__compound',
            'structure__parents__uuuuu_parent__compound'
        ).annotate(
            ficts_children_count=Count('structure__ficts_children'),
            ficus_children_count=Count('structure__ficus_children'),
            uuuuu_children_count=Count('structure__uuuuu_children')
        ).filter(
            id__in=ids
        )
        return queryset


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

    objects = models.Manager()
    with_related_objects = CompoundQuerySet.as_manager()

    class Meta:
        db_table = 'cir_compound'

    def __str__(self):
        return "NCICADD:CID=%s" % self.id

    def __repr__(self):
        return "NCICADD:CID={}".format(self.id)


class RecordQuerySet(models.QuerySet):

    fetch_relations = [
        'structure_file_record',
        'structure_file_record__structure__parents',
        'structure_file_record__structure__parents__ficts_parent',
        'structure_file_record__structure__parents__ficus_parent',
        'structure_file_record__structure__parents__uuuuu_parent',
        'structure_file_record__structure__parents__ficts_parent__compound',
        'structure_file_record__structure__parents__ficus_parent__compound',
        'structure_file_record__structure__parents__uuuuu_parent__compound'
    ]

    def by_record_ids(self, ids: List[int]):
        queryset = self.select_related(*RecordQuerySet.fetch_relations).filter(
            id__in=ids
        )
        return queryset

    def by_regid_ids(self, regids: List[str]):
        queryset = self.select_related(*RecordQuerySet.fetch_relations).filter(
            regid__in=regids
        )
        return queryset

    def by_structure_ids(self, structure_ids: List[int]):
        queryset = self.select_related(*RecordQuerySet.fetch_relations).filter(
            structure_file_record__structure__parents__ficts_parent__in=structure_ids
        )
        return queryset


class Record(models.Model):
    name = models.ForeignKey('Name', on_delete=models.PROTECT, blank=False, null=False)
    regid = models.TextField(max_length=1500)
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

    objects = models.Manager()
    with_related_objects = RecordQuerySet.as_manager()

    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'version', 'release'], name='unique_record'),
        ]
        db_table = 'cir_record'

    def __str__(self):
        return "(Record=%s: regid=%s)" % (self.id, self.regid)

    def __repr__(self):
        return "NCICADD:RID={}".format(self.id)


class Name(models.Model):
    hash = models.UUIDField(null=False, blank=False, unique=True)
    name = models.TextField(max_length=1500)

    class Meta:
        db_table = 'cir_structure_name'

    def save(self, *args, **kwargs):
        self.hash = hashlib.md5(self.name.encode("UTF-8")).hexdigest()
        super(Name, self).save(*args, **kwargs)

    def __str__(self):
        return "(Name=%s: hash=%s name=%s)" % (self.id, self.hash, self.name, )

    def __repr__(self):
        return self.name


# class LoadName(models.Model):
#     hash = models.UUIDField(null=False, blank=False, unique=True)
#     name = models.TextField(max_length=1500)
# 
#     class Meta:
#         db_table = 'load_structure_name'
#         # constraints = [
#         #     UniqueConstraint(fields=['unique'], name='unique_record'),
#         # ]
# 
#     def save(self, *args, **kwargs):
#         self.hash = hashlib.md5(self.name.encode("UTF-8")).hexdigest()
#         super(Name, self).save(*args, **kwargs)
# 
#     def __str__(self):
#         return "(Name=%s: hash=%s name=%s)" % (self.id, self.hash, self.name, )
# 
#     def __repr__(self):
#         return self.name


class NameType(models.Model):
    title = models.CharField(max_length=64, unique=True, editable=False)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.SET_NULL, blank=True, null=True)
    public_string = models.TextField(max_length=64, blank=True, null=True)
    description = models.TextField(max_length=768, blank=True, null=True)

    class Meta:
        db_table = 'cir_name_type'

    def __str__(self):
        return "(NameType=%s: title=%s)" % (self.id, self.title, )


class NameAffinityClass(models.Model):
    title = models.CharField(max_length=32, unique=True, editable=False)
    rank = models.IntegerField(default=0, blank=False, null=False)
    description = models.TextField(max_length=32768, blank=True, null=True)

    class Meta:
        db_table = 'cir_name_affinity_class'

    def __str__(self):
        return "(NameAffinityClass=%s: %s)" % (self.id, self.title, )


class StructureNameAssociationQuerySet(models.QuerySet):

    def _base_queryset(self):
        return self.select_related(
            'name',
            'name_type',
            'affinity_class',
            'structure',
            'structure__compound'
        )

    def by_compound(
            self,
            compounds: List[Union['Compound', int]],
            name_types: List[Union['NameType', int]] = None,
            affinity_classes: List[Union['NameAffinityClass', int]] = None,
            minimum_confidence: float = 100
    ):
        queryset = self._base_queryset().filter(structure__compound__in=compounds, confidence__gte=minimum_confidence)
        if affinity_classes:
            queryset = queryset.filter(
                affinity_class__in=affinity_classes
            )
        if name_types:
            queryset = queryset.filter(
                name_type__in=name_types
            )
        return queryset

    def by_name(
            self,
            names: List[Union['Name', str]],
            name_types: List[Union['NameType', int]] = None,
            affinity_classes: List[Union['NameAffinityClass', int]] = None,
            minimum_confidence: float = 100
    ):
        name_filter = reduce(operator.or_, (Q(name__name__iexact=n) for n in names))
        queryset = self._base_queryset().filter(name_filter).filter(confidence__gte=minimum_confidence)

        if affinity_classes:
            queryset = queryset.filter(
                affinity_class__in=affinity_classes
            )
        if name_types:
            queryset = queryset.filter(
                name_type__in=name_types
            )
        return queryset


class StructureNameAssociation(models.Model):
    name = models.ForeignKey(
        Name,
        related_name='structures',
        on_delete=models.CASCADE
    )
    structure = models.ForeignKey(
        Structure,
        related_name='names',
        on_delete=models.CASCADE
    )
    name_type = models.ForeignKey(NameType, on_delete=models.RESTRICT)
    affinity_class = models.ForeignKey(NameAffinityClass, on_delete=models.RESTRICT)
    confidence = models.PositiveIntegerField(null=False, default=0)

    objects = models.Manager()
    with_related_objects = StructureNameAssociationQuerySet.as_manager()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'structure', 'name_type', 'affinity_class'],
                name='unique_structure_name_affinity'
            ),
            models.CheckConstraint(
                name="structure_name_association_confidence_limits",
                check=models.Q(confidence__range=(1, 100)),
            ),
        ]
        db_table = 'cir_structure_name_associations'

    def __str__(self):
        return "(StructureNameAssociations=%s: name=%s, structure=%s, name_type=%s, affinity=%s, confidence=%s)" % \
               (self.id, self.name_id, self.structure_id, self.name_type_id, self.affinity_class, self.confidence)


class Organization(models.Model):
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


class StructureFormula(models.Model):
    formula = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'cir_structure_formula'


class ResponseType(models.Model):
    parent_type = models.ForeignKey('ResponseType', null=True, blank=True, on_delete=models.CASCADE)
    url = models.CharField(max_length=128, unique=True)
    method = models.CharField(max_length=255, null=True, blank=True)
    parameter = models.CharField(max_length=1024, null=True, blank=True)
    base_mime_type = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Response Type"
        verbose_name_plural = "Response Types"
        db_table = 'cir_response_type'

    def child_types(self):
        return ResponseType.objects.get(parent_type=self.pk)

    def __str__(self):
        return self.url + ":" + self.method
