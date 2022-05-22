import json

from django.db import models
from django.db.models import UniqueConstraint, Index
from pycactvs import Ens

from custom.cactvs import CactvsHash, CactvsMinimol
from custom.fields import CactvsHashField, CactvsMinimolField
from database.models import Database, Release


class StructureManager(models.Manager):

    def get_or_create_from_ens(self, ens: Ens):
        return self.get_or_create(hashisy=CactvsHash(ens), minimol=CactvsMinimol(ens))


class Structure(models.Model):
    hashisy = CactvsHashField(unique=True)
    minimol = CactvsMinimolField(null=False)
    ficts_parent = models.ForeignKey(
        'Structure', blank=True, null=True, related_name='ficts_children', on_delete=models.PROTECT)
    ficus_parent = models.ForeignKey(
        'Structure', blank=True, null=True, related_name='ficus_children', on_delete=models.PROTECT)
    uuuuu_parent = models.ForeignKey(
        'Structure', blank=True, null=True, related_name='uuuuu_children', on_delete=models.PROTECT)
    names = models.ManyToManyField(
        'Name',
        through='StructureNames',
        related_name="structures"
    )
    inchis = models.ManyToManyField(
        'resolver.InChI',
        through='StructureInChIs',
        related_name="structures"
    )
    added = models.DateTimeField(auto_now_add=True)
    blocked = models.DateTimeField(auto_now=False, blank=True, null=True)

    indexes = Index(
        fields=['ficts_parent', 'ficus_parent', 'uuuuu_parent'],
        name='structure_index'
    )

    class Meta:
        db_table = 'cir_structure'
        verbose_name = "Structure"
        verbose_name_plural = "Structures"

    objects = StructureManager()

    def has_compound(self) -> bool:
        has_compound = False
        try:
            has_compound = (self.compound is not None)
        except Compound.DoesNotExist:
            pass
        return has_compound

    @property
    def to_ens(self) -> Ens:
        return self.minimol.ens

    def __str__(self):
        return "[%s] %s" % (self.hashisy.padded, self.to_ens.get("E_SMILES"))


class Record(models.Model):
    regid = models.ForeignKey('Name', on_delete=models.PROTECT)
    version = models.IntegerField(default=1, blank=False, null=False)
    release = models.ForeignKey(Release, blank=False, null=False, on_delete=models.CASCADE)
    database = models.ForeignKey(Database, blank=False, null=False, on_delete=models.RESTRICT)
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
        return "NCICADD:RID=%s" % self.id


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


# class Record(models.Model):
#     regid = models.ForeignKey('Name', on_delete=models.PROTECT)
#     version = models.IntegerField(default=1, blank=False, null=False)
#     release = models.ForeignKey(Release, blank=False, null=False, on_delete=models.CASCADE)
#     database = models.ForeignKey(Database, blank=False, null=False, on_delete=models.RESTRICT)
#     structure_file_record = models.ForeignKey(
#         'etl.StructureFileRecord',
#         blank=False,
#         null=False,
#         related_name="records",
#         on_delete=models.PROTECT
#     )
#     added = models.DateTimeField(auto_now_add=True)
#     modified = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         constraints = [
#             UniqueConstraint(fields=['regid', 'version', 'release'], name='unique_record'),
#         ]
#         db_table = 'cir_record'
#
#     def __str__(self):
#         return "NCICADD:RID=%s" % self.id
#
#
# class Compound(models.Model):
#     structure = models.OneToOneField(
#         'Structure',
#         blank=False,
#         null=False,
#         on_delete=models.PROTECT
#     )
#     added = models.DateTimeField(auto_now_add=True)
#     modified = models.DateTimeField(auto_now=True)
#     blocked = models.DateTimeField(auto_now=False, blank=True, null=True)
#
#     class Meta:
#         db_table = 'cir_compound'
#
#     def __str__(self):
#         return "NCICADD:CID=%s" % self.id
#
#     def __repr__(self):
#         return "NCICADD:CID=%s" % self.id


class StructureInChIs(models.Model):
    structure = models.ForeignKey('Structure', on_delete=models.CASCADE)
    inchi = models.ForeignKey('resolver.InChI', on_delete=models.CASCADE)
    software_version_string = models.CharField(max_length=64, default=None, blank=True, null=True)
    save_options = models.CharField(max_length=2, default=None, blank=True, null=True)


    class Meta:
        constraints = [
            UniqueConstraint(fields=['structure', 'inchi', 'software_version_string', 'save_options'], name='unique_structure_inchis'),
        ]
        db_table = 'cir_structure_inchis'


class Name(models.Model):
    name = models.TextField(max_length=1500, unique=True)

    class Meta:
        db_table = 'cir_structure_name'

    def get_structure(self):
        return self.structure.get()

    def __str__(self):
        return "Name='%s'" % (self.name, )

    def __repr__(self):
        return self.name


class NameType(models.Model):
    string = models.CharField(max_length=64, unique=True, blank=False, null=False)
    public_string = models.TextField(max_length=64, blank=False, null=False)
    description = models.TextField(max_length=768, blank=True, null=True)

    class Meta:
        db_table = 'cir_name_type'


class StructureNames(models.Model):
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE)
    name_type = models.ForeignKey(NameType, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'structure', 'name_type'], name='unique_structure_names'),
        ]
        db_table = 'cir_structure_names'


class StructureFormula(models.Model):
    formula = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'cir_structure_formula'


class RecordNames(models.Model):
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    name_type = models.ForeignKey(NameType, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'record', 'name_type'], name='unique_record_names'),
        ]
        db_table = 'cir_record_names'


class ResponseType(models.Model):
    parent_type = models.ForeignKey('ResponseType', null=True, blank=True, on_delete=models.CASCADE)
    url = models.CharField(max_length=128)
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



# class StructureCactvsHash(models.Model):
#     #id = models.IntegerField(primary_key=True)
#     hashisy = CactvsHashField(unique=True)
#     minimol = models.BinaryField(null=True)
#     name = models.TextField(max_length=255)
#
#     class Meta:
#         db_table = 'cir_structure_hash'


# class Structure(models.Model):
#     id = models.IntegerField(primary_key=True)
#     hashisy = models.BigIntegerField(unique=True)
#     minimol = models.TextField(max_length=1500)
#     names = models.ManyToManyField('Name', through='StructureName', related_name="structure")
#     standard_inchis = models.ManyToManyField('StandardInChI',
#                                              through='StructureStandardInChI',
#                                              related_name="structure_set")
#
#     class Meta:
#         db_table = 'cir_structure'
#         #db_table = u'`chemical_structure`.`structure`'
#
#     # def get_short_display_names(self, query=None):
#     #     structure_names = NameCache(self)
#     #     return_list = structure_names.get_display_list()
#     #     return return_list
#     #
#     # def get_hashcode(self):
#     #     hashcode = ncicadd.Identifier(integer=self.hashisy)
#     #     return hashcode.hashcode
#     #
#     # def get_standard_inchi(self):
#     #     inchi_string = inchi.String(string=self.standard_inchis.get().string)
#     #     return inchi_string
#     #
#     # def get_standard_inchikey(self):
#     #     inchi_key = inchi.Key(
#     #         layer1=self.standard_inchis.get().key_layer1,
#     #         layer2=self.standard_inchis.get().key_layer2,
#     #         layer3=self.standard_inchis.get().key_layer3
#     #     )
#     #     return inchi_key
#
#     def __str__(self):
#         return 'NCICADD:SID=%s' % self.id


# class StructureImage(models.Model):
#     #id = models.IntegerField(primary_key=True)
#     hashisy = models.IntegerField(unique=True)
#     small = models.TextField(max_length=65535)
#     medium = models.TextField(max_length=65535)
#     large = models.TextField(max_length=65535)
#
#     class Meta:
#         db_table = 'cir_structure_image'
#         #db_table = u'`chemical_structure_image`'


# class StandardInChI(models.Model):
#     #id = models.IntegerField(primary_key=True)
#     version = models.IntegerField(db_column='version_id')
#     key_layer1 = models.CharField(max_length=14, db_column='key_layer1')
#     key_layer2 = models.CharField(max_length=10, db_column='key_layer2')
#     key_layer3 = models.CharField(max_length=1, db_column='key_layer3')
#     string = models.CharField(max_length=1500)
#
#     indexes = Index(
#         fields=['version', 'key_layer1', 'key_layer2', 'key_layer3', 'string'],
#         name='index_standard_inchi'
#     )
#
#     # objects = models.Manager()
#     # inchi_set = StandardInChIStructureManager()
#
#     class Meta:
#         constraints = [
#             UniqueConstraint(
#                 fields=['version', 'key_layer1', 'key_layer2', 'key_layer3'],
#                 name='unique_standard_inchi_key'
#             ),
#         ]
#         db_table = 'cir_structure_standard_inchi'
#
#         #db_table = u'`chemical_inchi`.`standard_inchi`'
#
#     def get_structure(self):
#         # .all()[0] is dirty but there are some issues (there are stdinchis
#         # with more than one of our unique structures
#         return self.structurestandardinchi_set.all()[0].structure
#
#     # def get_structures(self, query):
#     #     # cleaner method
#     #     t = StandardInChI.objects.filter(**i.query())
#     #     return t


# class StructureStandardInChI(models.Model):
#     structure = models.ForeignKey('Structure2', on_delete=models.CASCADE)
#     standard_inchi = models.ForeignKey('StandardInChI', db_column='standard_inchi_id', on_delete=models.CASCADE)
#
#     class Meta:
#         db_table = 'cir_structure_standard_inchis'
#         #db_table = u'`chemical_inchi`.`structure_standard_inchi`'


# class InChIManager(models.Manager):
#
#     def get_or_create_from_ens(self, ens: Ens):
#         inchikey = ens.get('E_STDINCHIKEY')
#         inchi = ens.get('E_STDINCHI')
#         i = InChI.create(key=inchikey, string=inchi)
#         d = model_to_dict(i)
#         return self.get_or_create(id=i.id, **d)


# class InChI(models.Model):
#     id = models.UUIDField(primary_key=True, editable=False)
#     version = models.IntegerField(default=1)
#     version_string = models.CharField(max_length=64)
#     block1 = models.CharField(max_length=14)
#     block2 = models.CharField(max_length=10)
#     block3 = models.CharField(max_length=1)
#     key = models.CharField(max_length=27, blank=True, null=True)
#     string = models.CharField(max_length=32768, blank=True, null=True)
#     is_standard = models.BooleanField(default=False)
#     safe_options = models.CharField(max_length=2, default=None, null=True)
#     entrypoints = models.ManyToManyField('EntryPoint', related_name='inchis')
#     added = models.DateTimeField(auto_now_add=True)
#     modified = models.DateTimeField(auto_now=True)
#
#     objects = InChIManager()
#
#     indexes = Index(
#         fields=['version', 'block1', 'block2', 'block3'],
#         name='inchi_index'
#     )
#
#     class Meta:
#         constraints = [
#             UniqueConstraint(
#                 fields=['version', 'block1', 'block2', 'block3'],
#                 name='unique_inchi_constraint'
#             ),
#         ]
#         verbose_name = "InChI"
#         db_table = 'cir_inchi'
#
#     @classmethod
#     def create(cls, *args, **kwargs):
#         if 'url_prefix' in kwargs:
#             inchiargs = kwargs.pop('url_prefix')
#             inchi = cls(*args, inchiargs)
#         else:
#             inchi = cls(*args, **kwargs)
#         k = None
#         s = None
#         if 'key' in kwargs and kwargs['key']:
#             k = InChIKey(kwargs['key'])
#
#         if 'string' in kwargs and kwargs['string']:
#             s = InChIString(kwargs['string'])
#             e = Ens(kwargs['string'])
#             if s.element['is_standard']:
#                 _k = InChIKey(e.get('E_STDINCHIKEY'))
#             else:
#                 _k = InChIKey(e.get('E_INCHIKEY'))
#             if k:
#                 if not k.element['well_formatted'] == _k.element['well_formatted']:
#                     raise FieldError("InChI key does not represent InChI string")
#             else:
#                 k = _k
#
#         inchi.key = k.element['well_formatted_no_prefix']
#         inchi.version = k.element['version']
#         inchi.is_standard = k.element['is_standard']
#         inchi.block1 = k.element['block1']
#         inchi.block2 = k.element['block2']
#         inchi.block3 = k.element['block3']
#         if s:
#             inchi.string = s.element['well_formatted']
#         inchi.id = uuid.uuid5(uuid.NAMESPACE_URL, "/".join([
#             inchi.key,
#             str(kwargs.get('safe_options', None)),
#         ]))
#         return inchi
#
#     def __str__(self):
#         return self.key





# class Name_Fulltext(models.Model):
#     name = models.CharField(max_length=1000)
#     objects = models.Manager()
#     search = djangosphinx.SphinxSearch(index="structure_names")
#
#     class Meta:
#         db_table = u'`chemical_name`.`name`'


# class Name(models.Model):
#     id = models.IntegerField(primary_key=True)
#     name = models.TextField(max_length=1500, unique=True)
#     classification_list = None
#
#     class Meta:
#         db_table = u'`chemical_name`.`name`'





# class StructureNameTypes(models.Model):
#     structure_name = models.ForeignKey('StructureName', related_name='name_types', on_delete=models.CASCADE)
#     name_type = models.ForeignKey('NameType', on_delete=models.CASCADE)
#
#     class Meta:
#         db_table = 'cir_structure_name_types'
#         #db_table = u'`chemical_name`.`structure_name_classification`'




# class Record(models.Model):
#     #id = models.IntegerField(primary_key=True)
#     #cocoa_id = models.IntegerField(db_column="cocoa_structure_id")
#     release = models.ForeignKey(Release, on_delete=models.CASCADE)
#     database = models.ForeignKey(Database, on_delete=models.CASCADE)
#     ficts_compound = models.IntegerField(db_column='ficts_compound_id')
#     ficus_compound = models.IntegerField(db_column='ficus_compound_id')
#     uuuuu_compound = models.IntegerField(db_column='uuuuu_compound_id')
#     database_record_external_identifier = models.CharField(max_length=100)
#     release_record_external_identifier = models.CharField(max_length=100)
#     revision = models.IntegerField(db_column="revision_id")
#
#     class Meta:
#         db_table = 'cir_record_lookup'
#         #db_table = u'`chemical`.`record_lookup`'
#
#     def get_structure(self):
#         a = self.compound_associations.get(type=1)
#         return a.compound.structure
#
#     def __str__(self):
#         return "NCICADD:RID=%s" % self.id
#
#
# class Compound(models.Model):
#     #id = models.IntegerField(primary_key=True)
#     structure = models.OneToOneField('Structure2', related_name="compound", on_delete=models.CASCADE)
#
#     class Meta:
#         db_table = 'cir_compound'
#         #db_table = u'`chemical`.`compound`'
#
#     def __str__(self):
#         return "NCICADD:CID=%s" % self.id
#
#     def __repr__(self):
#         return "NCICADD:CID=%s" % self.id
#
#     def get_structure(self):
#         return self.structure
#
#     def retrieve_distinct_record_set(self):
#         record_set = set()
#         record_list = Record.objects.filter(compound_associations__compound__id=self.id)
#         record_set.update(record_list)
#         return record_set
#
#     def record_relevance(self, record):
#         relevance = 1
#         if record['ficts_compound'] == self.id:
#             relevance += 10000
#         if record['ficus_compound'] == self.id:
#             relevance += 1000
#         if record['uuuuu_compound'] == self.id:
#             relevance += 100
#         relevance += int(record['release']['date_released'].strftime('%Y'))
#         relevance = -1 * relevance
#         return relevance
#
#     def get_records(self, group_key=None, database=None, release=None, context=None, max_records=10000, public=True):
#         record_set = set()
#         for identifier in ['ficts', 'ficus', ' uuuuu']:
#             filter_string = '%s_compound = %s' % (identifier, self.id)
#             if release:
#                 filter_string += ', release = %s' % (release.id,)
#             if database:
#                 filter_string += ', database = %s' % (database.id,)
#             if context:
#                 filter_string += ', database__context__id = %s' % (context.id,)
#             query_string = "Record.objects.select_related().filter(%s)[0:%s]" % (filter_string, max_records)
#             record_list = eval(query_string)
#             record_set.update(record_list)
#
#         # build the matchlist
#         matchlist = {'content': {}, 'metadata': {}}
#         matchlist['metadata']['size'] = 0
#         matchlist['metadata']['database_set'] = []
#
#         cached_databases = DatabaseDataCache()
#
#         for recordObject in record_set:
#             if public and recordObject.release.classification == "internal":
#                 continue
#             if recordObject.release.status == "inactive":
#                 continue
#             matchlist['metadata']['size'] += 1
#             matchlist['metadata']['database_set'].append(recordObject.database)
#             record = {'object': recordObject, 'key': recordObject.__str__(),
#                       'release': cached_databases['releases'][recordObject.release.id],
#                       'database': cached_databases['databases'][recordObject.database.id],
#                       'ficts_compound': recordObject.ficts_compound, 'ficus_compound': recordObject.ficus_compound,
#                       'uuuuu_compound': recordObject.uuuuu_compound,
#                       'ficts_compound_key': "NCICADD:CID=%s" % recordObject.ficts_compound,
#                       'ficus_compound_key': "NCICADD:CID=%s" % recordObject.ficus_compound,
#                       'uuuuu_compound_key': "NCICADD:CID=%s" % recordObject.uuuuu_compound,
#                       'release_record_external_identifier': recordObject.release_record_external_identifier,
#                       'database_record_external_identifier': recordObject.database_record_external_identifier}
#             record['relevance'] = self.record_relevance(record)
#             if group_key:
#                 try:
#                     cmd = 'matchlist["content"][recordObject.%s].append(record)' % (group_key,)
#                     exec(cmd)
#                 except:
#                     cmd = 'matchlist["content"][recordObject.%s] = [record,]' % (group_key,)
#                     exec(cmd)
#             else:
#                 try:
#                     matchlist["content"]["records"].append(record)
#                 except:
#                     matchlist["content"]["records"] = [record, ]
#
#         database_set = set(matchlist['metadata']['database_set'])
#         matchlist['metadata']['database_set'] = database_set
#         matchlist['metadata']['database_count'] = len(database_set)
#         return matchlist


class AssociationType(models.Model):
    #id = models.IntegerField(primary_key=True)
    string = models.CharField(max_length=48)
    property = models.CharField(max_length=48)
    display_name = models.CharField(max_length=48)

    class Meta:
        db_table = u'cir_record_compound_association_type'
        #db_table = u'`chemical`.`association_type`'


class Association(models.Model):
    record = models.ForeignKey('Record', related_name='compound_associations', on_delete=models.CASCADE)
    compound = models.ForeignKey('Compound', related_name='record_associations', on_delete=models.CASCADE)
    type = models.ForeignKey('AssociationType', on_delete=models.CASCADE)

    class Meta:
        db_table = 'cir_record_compound_associations'
        #db_table = u'`chemical`.`association`'



class Access(models.Model):
    #id = models.AutoField(primary_key=True)
    host = models.ForeignKey('AccessHost', on_delete=models.CASCADE)
    client = models.ForeignKey('AccessClient', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True, db_column="dateTime")

    class Meta:
        db_table = 'cir_access'
        #db_table = u'chemical_structure_access'


class AccessClient(models.Model):
    #id = models.AutoField(primary_key=True)
    string = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'cir_access_client'
        #db_table = u'chemical_structure_access_client'


class AccessHost(models.Model):
    #id = models.AutoField(primary_key=True)
    string = models.CharField(max_length=255, unique=True)
    blocked = models.IntegerField()
    lock_timestamp = models.DateTimeField(db_column="lock_time")
    current_sleep_period = models.IntegerField()
    force_sleep_period = models.IntegerField()
    force_block = models.IntegerField()
    organization = models.ManyToManyField('AccessOrganization', through='AccessHostOrganization')

    class Meta:
        db_table = 'cir_access_host'
        #db_table = u'chemical_structure_access_host'


class AccessOrganization(models.Model):
    #id = models.AutoField(primary_key=True)
    string = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = u'cir_access_organization'
        #db_table = u'chemical_structure_access_organization'


class AccessHostOrganization(models.Model):
    host = models.ForeignKey(AccessHost, on_delete=models.CASCADE)
    organization = models.ForeignKey(AccessOrganization, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('host', 'organization'),)
        db_table = u'cir_access_host_organization'
        #db_table = u'chemical_structure_access_host_organization'





class Response(models.Model):
    #id = models.AutoField(primary_key=True)
    type = models.ForeignKey('ResponseType', on_delete=models.CASCADE)
    fromString = models.TextField()
    response = models.TextField(db_column='string')
    responseFile = models.FileField(max_length=255, upload_to="tmp")

    class Meta:
        db_table = u'cir_response'
        #db_table = u'chemical_structure_response'


    def json(self):
        d = {'type': self.type, 'from': self.fromString, 'string': self.response}
        return json.dumps(d)


class UsageMonthList(models.Manager):
    def get_query_set(self):
        return super(UsageMonthList, self).get_query_set().order_by('-year', '-month')[1:13].values()


class UsageMonth(models.Model):
    month_year = models.CharField(primary_key=True, max_length=2)
    month = models.IntegerField()
    year = models.IntegerField()
    requests = models.IntegerField()
    ip_counts = models.IntegerField()
    average = models.DecimalField(decimal_places=2, max_digits=5)

    objects = models.Manager()
    all_months_data = UsageMonthList()

    @staticmethod
    def get_data_dictionary():
        data = UsageMonth.all_months_data.values()
        data_dictionary = {'month_year': [], 'requests': [], 'ip_counts': []}
        for element in data:
            data_dictionary['month_year'].append(element['month_year'])
            data_dictionary['requests'].append(element['requests'])
            data_dictionary['ip_counts'].append(element['ip_counts'])
        data_dictionary['month_year'].reverse()
        data_dictionary['requests'].reverse()
        data_dictionary['ip_counts'].reverse()
        return data_dictionary

    class Meta:
        db_table = 'cir_usage_month'
        #db_table = u'`chemical_structure_usage_month`'


class UsageMonthDayList(models.Manager):
    def get_query_set(self):
        return super(UsageMonthDayList, self).get_query_set().order_by('month', 'day').values()


class UsageMonthDay(models.Model):
    month_day = models.CharField(primary_key=True, max_length=2)
    month = models.IntegerField()
    day = models.IntegerField()
    requests = models.IntegerField()
    ip_counts = models.IntegerField()

    objects = models.Manager()
    all_month_day_data = UsageMonthDayList()

    @staticmethod
    def get_data_dictionary():
        data = UsageMonthDay.all_month_day_data.values()
        data_dictionary = {'month_day': [], 'requests': [], 'ip_counts': []}
        for element in data:
            data_dictionary['month_day'].append(element['month_day'])
            data_dictionary['requests'].append(element['requests'])
            data_dictionary['ip_counts'].append(element['ip_counts'])
        data_dictionary['month_day'].reverse()
        data_dictionary['requests'].reverse()
        data_dictionary['ip_counts'].reverse()
        return data_dictionary

    class Meta:
        db_table = 'cir_usage_month_day'
        #db_table = u'`chemical_structure_usage_month_day`'


class UsageSeconds(models.Model):
    requests = models.IntegerField(primary_key=True)

    class Meta:
        db_table = 'cir_usage_seconds'
        #db_table = u'chemical_structure_usage_seconds'


############

# class NameCache:
#
#     def __init__(self, structure):
#         self.attributes = {'structure': structure, 'structure_names': (self.get_structure_names())[0],
#                            'name_set': (self.get_structure_names())[1],
#                            'classified_name_sets': (self.get_structure_names())[2],
#                            'classified_name_object_sets': (self.get_structure_names())[3]}
#
#     def get_structure_names(self):
#         try:
#             return self.attributes['names']
#         except:
#             structure_names = StructureName.objects.select_related('name').filter(structure=self['structure'])
#             names = []
#             name_set = set()
#             classified_name_sets = {}
#             classified_name_object_sets = {}
#             for n in structure_names:
#                 name_dict = {'name_object': n.name}
#                 name_dict['name_string'] = name_dict['name_object'].name
#                 name_dict['structure_name_object'] = n
#                 name_dict['classifications'] = n.classification.all().values()
#                 names.append(name_dict)
#                 name = name_dict['name_string']
#                 name_set.add(name)
#                 name_object = name_dict['name_object']
#                 for classification in name_dict['classifications']:
#                     class_name = classification['id']
#                     try:
#                         classified_name_sets[class_name].add(name)
#                         classified_name_object_sets[class_name].add(name_object)
#                     except:
#                         classified_name_sets[class_name] = {name}
#                         classified_name_object_sets[class_name] = {name_object}
#             return [names, name_set, classified_name_sets, classified_name_object_sets]
#
#     def get_display_list(self, query_string=None):
#         name_set_1 = set()
#         name_set_2 = set()
#         if query_string and query_string in self.attributes['name_set']:
#             name_set_1 = {query_string}
#         name_sets = self.attributes['classified_name_sets']
#         try:
#             name_set_1.update(list(name_sets[1]))
#         except:
#             pass
#         for key_length in [(2, 5), (3, 1), (4, 1), (5, 1), (6, 3), (7, 8)]:
#             key = key_length[0]
#             length = key_length[1]
#             try:
#                 name_set_2.update(list(name_sets[key])[0:length])
#             except:
#                 pass
#         add_list = list(name_set_2)
#         add_list.sort()
#         return_list = list(name_set_1) + add_list
#         return return_list
#
#     def __getitem__(self, key):
#         return self.attributes[key]
