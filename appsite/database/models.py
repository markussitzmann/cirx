from django.db import models
from django.core.exceptions import *


class Context(models.Model):
    id = models.AutoField(primary_key=True)
    record_string = models.TextField(max_length=1500)
    database_string = models.TextField(max_length=1500)

    class Meta:
        db_table = 'cir_database_context'
        #db_table = u'`chemical_database`.`context`'

    def __str__(self):
        return self.database_string


class URL(models.Model):
    id = models.AutoField(primary_key=True)
    string = models.URLField()

    class Meta:
        verbose_name = 'URL'
        ordering = ['string']
        db_table = 'cir_database_url'
        #db_table = u'`chemical_database`.`url`'


    def get_string(self):
        return self.string

    def __str__(self):
        return self.string.replace('http://', '')

    def __repr__(self):
        return self.string


class RecordURLScheme(models.Model):
    id = models.AutoField(primary_key=True)
    string = models.URLField()

    class Meta:
        verbose_name = 'Record URL Scheme'
        db_table = 'cir_database_record_url_scheme'
        #db_table = u'`chemical_database`.`record_url_scheme`'

    def __str__(self):
        if len(self.string) < 100:
            return self.string.replace('http://', '')
        else:
            string = self.string[:50] + '[...]' + self.string[-50:] + ' (URL string truncated !)'
            return string.replace('http://', '')


class Database(models.Model):
    id = models.AutoField(primary_key=True)
    publisher = models.ForeignKey('Publisher', null=True, on_delete=models.CASCADE)
    context = models.ForeignKey('Context', blank=True, null=True, on_delete=models.CASCADE)
    url = models.ForeignKey('URL', blank=True, null=True, verbose_name="URL", on_delete=models.CASCADE)
    record_url_scheme = models.ForeignKey('RecordURLScheme',
                                          blank=True, null=True, verbose_name="Record URL Scheme",
                                          on_delete=models.CASCADE)
    name = models.CharField(max_length=768)
    original_name = models.CharField(max_length=768, blank=True, verbose_name="Original Name")
    description = models.TextField(max_length=1500, blank=True)
    date_added = models.DateTimeField(blank=True)
    date_modified = models.DateTimeField(blank=True)

    class Meta:
        ordering = ['-id']
        db_table = 'cir_database'
        #db_table = u'`chemical_database`.`database`'

    def __str__(self):
        return self.name


class Release(models.Model):
    id = models.AutoField(primary_key=True)
    database = models.ForeignKey('Database', on_delete=models.CASCADE)
    publisher = models.ForeignKey('Publisher', null=True, on_delete=models.CASCADE)
    url = models.ForeignKey('URL', blank=True, null=True, verbose_name="URL", on_delete=models.CASCADE)
    record_url_scheme = models.ForeignKey('RecordURLScheme', blank=True, null=True, verbose_name="Record URL Scheme",
                                          on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(max_length=1500, blank=True)
    original_name = models.CharField(max_length=255, blank=True, verbose_name="Original Name")
    version = models.CharField(max_length=255, blank=True)
    date_released = models.DateField(blank=True, verbose_name="Date Released")
    classification = models.CharField(max_length=32, db_column='class', blank=True,
                                      choices=(('public', 'Public'), ('private', 'Private'), ('internal', 'Internal',)))
    status = models.CharField(max_length=32, blank=True, choices=(('active', 'Show'), ('inactive', 'Hide')))
    file_name_pattern = models.CharField(max_length=255, blank=True, verbose_name="File Name Pattern")
    cocoa_release_id = models.IntegerField(blank=True, verbose_name="COCOA ID")
    csls_id = models.IntegerField(blank=True, verbose_name="CSLS ID")
    pubchem_id = models.IntegerField(blank=True, verbose_name="PubChem Database ID")
    date_added = models.DateTimeField(blank=True)
    date_modified = models.DateTimeField(blank=True)

    class Meta:
        db_table = 'cir_database_release'
        #db_table = u'`chemical_database`.`release`'

    def version_name(self):
        date_string = "%s/%s" % (self.date_released.strftime('%m'), self.date_released.strftime('%Y'))
        if self.version:
            return "%s (%s)" % (self.version, date_string)
        else:
            return date_string

    def database_name(self):
        if self.publisher == self.database.publisher:
            if self.name:
                return self.name
            else:
                string = "%s" % (self.database.name,)
                return string
        else:
            if self.name:
                string = "%s (%s)" % (self.name, self.publisher.name)
                return self.name
            else:
                string = "%s (%s)" % (self.database.name, self.publisher.name)
                return string

    def __str__(self):
        version_name = self.version_name()
        string = "%s %s" % (self.database_name(), version_name)
        return string


class Publisher(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.ForeignKey('URL', blank=True, null=True, verbose_name="URL", on_delete=models.CASCADE)
    organization = models.ForeignKey('Organization', blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    group = models.CharField(max_length=255, blank=True, verbose_name="Group/Institute")
    contact = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['name', ]
        db_table = 'cir_database_publisher'
        #db_table = u'`chemical_database`.`publisher`'

    def __str__(self):
        return self.name


class Organization(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.ForeignKey('URL', blank=True, null=True, verbose_name="URL", on_delete=models.CASCADE)
    name = models.CharField(max_length=1500)
    date_added = models.DateTimeField(blank=True)
    date_modified = models.DateTimeField(blank=True)

    class Meta:
        ordering = ['name']
        db_table = 'cir_database_organization'
        #db_table = u'`chemical_database`.`organization`'


    def __str__(self):
        return self.name


# this is used for C2 speed up
class DatabaseDataCache:

    def __init__(self):
        self.cached = {'contexts': self.get_contexts(), 'urls': self.get_urls(),
                       'record_url_schemes': self.get_record_url_schemes(), 'organizations': self.get_organizations(),
                       'publishers': self.get_publishers(), 'databases': self.get_databases(),
                       'releases': self.get_releases()}

    def get_contexts(self, context=None):
        try:
            return self.cached['contexts']
        except:
            context_dict = {}
            if context:
                contexts = Context.objects.filter(context=context).values()
            else:
                contexts = Context.objects.all().values()
            for c in contexts:
                context_dict[c['id']] = c
            return context_dict

    def get_urls(self, url=None):
        try:
            return self.cached['urls']
        except:
            url_dict = {}
            if url:
                urls = URL.objects.filter(url=url).values()
            else:
                urls = URL.objects.all().values()
            for u in urls:
                url_dict[u['id']] = u
            return url_dict

    def get_record_url_schemes(self, record_url_scheme=None):
        try:
            return self.cached['record_url_schemes']
        except:
            record_url_scheme_dict = {}
            if record_url_scheme:
                record_url_scheme = RecordURLScheme.objects.filter(record_url_scheme=record_url_scheme).values()
            else:
                record_url_scheme = RecordURLScheme.objects.all().values()
            for u in record_url_scheme:
                record_url_scheme_dict[u['id']] = u
            return record_url_scheme_dict

    def get_organizations(self, organization=None):
        try:
            return self.cached['organizations']
        except:
            organization_dict = {}
            if organization:
                organizations = Organization.objects.filter(organization=organization).values()
            else:
                organizations = Organization.objects.all().values()
            for o in organizations:
                key = o['id']
                organization_dict[key] = o
                if o['url_id']:
                    url_key = o['url_id']
                    organization_dict[key]['url'] = self.get_urls()[url_key]
            return organization_dict

    def get_publishers(self, publisher=None):
        try:
            return self.cached['publishers']
        except:
            publisher_dict = {}
            if publisher:
                publishers = Publisher.objects.filter(publisher=publisher).values()
            else:
                publishers = Publisher.objects.all().values()
            for p in publishers:
                key = p['id']
                publisher_dict[key] = p
                if p['url_id']:
                    url_key = p['url_id']
                    publisher_dict[key]['url'] = self.get_urls()[url_key]
                if p['organization_id']:
                    organization_key = p['organization_id']
                    publisher_dict[key]['organization'] = self.get_organizations()[organization_key]
            return publisher_dict

    def get_databases(self, database=None):
        try:
            return self.cached['databases']
        except:
            database_dict = {}
            if database:
                databases = Database.objects.filter(database=database).values()
            else:
                databases = Database.objects.all().values()
            for d in databases:
                key = d['id']
                database_dict[key] = d
                if d['publisher_id']:
                    publisher_key = d['publisher_id']
                    database_dict[key]['publisher'] = self.get_publishers()[publisher_key]
                if d['context_id']:
                    context_key = d['context_id']
                    database_dict[key]['context'] = self.get_contexts()[context_key]
                if d['url_id']:
                    url_key = d['url_id']
                    database_dict[key]['url'] = self.get_urls()[url_key]
                if d['record_url_scheme_id']:
                    record_url_scheme_key = d['record_url_scheme_id']
                    database_dict[key]['record_url_scheme'] = self.get_record_url_schemes()[record_url_scheme_key]
            return database_dict

    def get_releases(self, release=None):
        try:
            return self.cached['releases']
        except:
            release_dict = {}
            if release:
                releases = Release.objects.filter(release=release).values()
            else:
                releases = Release.objects.all().values()
            for r in releases:
                key = r['id']
                release_dict[key] = r
                if r['database_id']:
                    database_key = r['database_id']
                    release_dict[key]['database'] = self.get_databases()[database_key]
                if r['publisher_id']:
                    publisher_key = r['publisher_id']
                    release_dict[key]['publisher'] = self.get_publishers()[publisher_key]
                if r['url_id']:
                    url_key = r['url_id']
                    release_dict[key]['url'] = self.get_urls()[url_key]
                if r['record_url_scheme_id']:
                    record_url_scheme_key = r['record_url_scheme_id']
                    release_dict[key]['record_url_scheme'] = self.get_record_url_schemes()[record_url_scheme_key]
                date_string = "%s/%s" % (r['date_released'].strftime('%m'), r['date_released'].strftime('%Y'))
                if r['version']:
                    release_dict[key]['version_string'] = "%s (%s)" % (r['version'], date_string)
                else:
                    release_dict[key]['version_string'] = date_string
            return release_dict

    def __getitem__(self, key):
        return self.cached[key]
