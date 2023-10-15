# class Access(models.Model):
#     #id = models.AutoField(primary_key=True)
#     host = models.ForeignKey('AccessHost', on_delete=models.CASCADE)
#     client = models.ForeignKey('AccessClient', on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(auto_now=True, db_column="dateTime")
#
#     class Meta:
#         db_table = 'cir_access'
#         #db_table = u'chemical_structure_access'
#
#
# class AccessClient(models.Model):
#     #id = models.AutoField(primary_key=True)
#     string = models.CharField(max_length=255, unique=True)
#
#     class Meta:
#         db_table = 'cir_access_client'
#         #db_table = u'chemical_structure_access_client'
#
#
# class AccessHost(models.Model):
#     #id = models.AutoField(primary_key=True)
#     string = models.CharField(max_length=255, unique=True)
#     blocked = models.IntegerField()
#     lock_timestamp = models.DateTimeField(db_column="lock_time")
#     current_sleep_period = models.IntegerField()
#     force_sleep_period = models.IntegerField()
#     force_block = models.IntegerField()
#     organization = models.ManyToManyField('AccessOrganization', through='AccessHostOrganization')
#
#     class Meta:
#         db_table = 'cir_access_host'
#         #db_table = u'chemical_structure_access_host'
#
#
# class AccessOrganization(models.Model):
#     #id = models.AutoField(primary_key=True)
#     string = models.CharField(max_length=255, unique=True)
#
#     class Meta:
#         db_table = u'cir_access_organization'
#         #db_table = u'chemical_structure_access_organization'
#
#
# class AccessHostOrganization(models.Model):
#     host = models.ForeignKey(AccessHost, on_delete=models.CASCADE)
#     organization = models.ForeignKey(AccessOrganization, on_delete=models.CASCADE)
#
#     class Meta:
#         unique_together = (('host', 'organization'),)
#         db_table = u'cir_access_host_organization'
#         #db_table = u'chemical_structure_access_host_organization'
#
#
#
#
#
# class Response(models.Model):
#     #id = models.AutoField(primary_key=True)
#     type = models.ForeignKey('ResponseType', on_delete=models.CASCADE)
#     fromString = models.TextField()
#     response = models.TextField(db_column='string')
#     responseFile = models.FileField(max_length=255, upload_to="tmp")
#
#     class Meta:
#         db_table = u'cir_response'
#         #db_table = u'chemical_structure_response'
#
#
#     def json(self):
#         d = {'type': self.type, 'from': self.fromString, 'string': self.response}
#         return json.dumps(d)
#
#
# class UsageMonthList(models.Manager):
#     def get_query_set(self):
#         return super(UsageMonthList, self).get_query_set().order_by('-year', '-month')[1:13].values()
#
#
# class UsageMonth(models.Model):
#     month_year = models.CharField(primary_key=True, max_length=2)
#     month = models.IntegerField()
#     year = models.IntegerField()
#     requests = models.IntegerField()
#     ip_counts = models.IntegerField()
#     average = models.DecimalField(decimal_places=2, max_digits=5)
#
#     objects = models.Manager()
#     all_months_data = UsageMonthList()
#
#     @staticmethod
#     def get_data_dictionary():
#         data = UsageMonth.all_months_data.values()
#         data_dictionary = {'month_year': [], 'requests': [], 'ip_counts': []}
#         for element in data:
#             data_dictionary['month_year'].append(element['month_year'])
#             data_dictionary['requests'].append(element['requests'])
#             data_dictionary['ip_counts'].append(element['ip_counts'])
#         data_dictionary['month_year'].reverse()
#         data_dictionary['requests'].reverse()
#         data_dictionary['ip_counts'].reverse()
#         return data_dictionary
#
#     class Meta:
#         db_table = 'cir_usage_month'
#         #db_table = u'`chemical_structure_usage_month`'
#
#
# class UsageMonthDayList(models.Manager):
#     def get_query_set(self):
#         return super(UsageMonthDayList, self).get_query_set().order_by('month', 'day').values()
#
#
# class UsageMonthDay(models.Model):
#     month_day = models.CharField(primary_key=True, max_length=2)
#     month = models.IntegerField()
#     day = models.IntegerField()
#     requests = models.IntegerField()
#     ip_counts = models.IntegerField()
#
#     objects = models.Manager()
#     all_month_day_data = UsageMonthDayList()
#
#     @staticmethod
#     def get_data_dictionary():
#         data = UsageMonthDay.all_month_day_data.values()
#         data_dictionary = {'month_day': [], 'requests': [], 'ip_counts': []}
#         for element in data:
#             data_dictionary['month_day'].append(element['month_day'])
#             data_dictionary['requests'].append(element['requests'])
#             data_dictionary['ip_counts'].append(element['ip_counts'])
#         data_dictionary['month_day'].reverse()
#         data_dictionary['requests'].reverse()
#         data_dictionary['ip_counts'].reverse()
#         return data_dictionary
#
#     class Meta:
#         db_table = 'cir_usage_month_day'
#         #db_table = u'`chemical_structure_usage_month_day`'
#
#
# class UsageSeconds(models.Model):
#     requests = models.IntegerField(primary_key=True)
#
#     class Meta:
#         db_table = 'cir_usage_seconds'
#         #db_table = u'chemical_structure_usage_seconds'


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
