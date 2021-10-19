from django.core.files import File
from django.core.paginator import Paginator
from django.http import HttpRequest, QueryDict

from resolver import *


# if settings.TEST:
#	from TEST_cactvs import *
# else:
#	from cactvs import *

# _cactvs_loader = __import__(settings.CACTVS_PATH, globals(), locals, settings.CACTVS_FROMLIST)
# Cactvs = _cactvs_loader.Cactvs
# Ens = _cactvs_loader.Ens
# Dataset = _cactvs_loader.Dataset
# Molfile = _cactvs_loader.Molfile
# CactvsError = _cactvs_loader.CactvsError


# from cactvs import Cactvs, Ens, Dataset, Molfile


class URLmethod:

    def __init__(self, representation, request=None, parameters=None, output_format='plain'):
        response_type = ResponseType.objects.get(url=representation)
        self.type = response_type
        self.base_mime_type = response_type.base_mime_type
        self.method = response_type.method
        self.url_parameters = request.GET.copy()
        self.representation = representation
        self.mime_type = None
        self.output_format = output_format
        self.response_list = []
        if not parameters:
            self.parameters = response_type.parameter
        else:
            self.parameters = parameters

    def __repr__(self):
        response = ''
        if not self.response_list:
            return ''
        if self.mime_type == 'image/gif':
            response = self.response_list
        else:
            response_list = self.response_list
            for item in self.response_list:
                response = response + "%s\n" % (item,)
        return response[0:-1]

    class Representation:

        def __init__(self):
            self.attributes = {}

        def __getitem__(self, key):
            return self.attributes[key]

        def __setitem__(self, key, item):
            self.attributes[key] = item
            return key

        def __repr__(self):
            response = ""
            mime_type = self['mime_type']
            if mime_type == 'image/gif':
                pass
            else:
                for item in self['response']:
                    response = response + "%s\n" % (item,)
            return response

    def parser(self, string):
        # self.cactvs = settings.CACTVS.client_is_up(return_instance=True)
        parse = getattr(self, self.method, self.parameters)
        response = parse(string)
        mime_type = self.mime_type
        representation = self.representation
        response = [string, representation, response, mime_type]
        # try:
        #	self.cactvs.__del__()
        # except:
        #	pass
        return response

    def urls(self, string):
        # cactvs = self.cactvs
        propname = self.parameters
        base_mime_type = self.base_mime_type
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        structure_index = parameters.get('structure_index', None)
        filter = parameters.get('filter', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list, cactvs=cactvs).interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        full_ensemble_list = []
        representation_list = []
        for interpretation in interpretations:
            structure_response_list = []
            response_list = []
            for structure in interpretation.structures:
                try:
                    compound = structure.object.compound
                except:
                    compound = None
                else:
                    database_records = compound.get_records(group_key='database')['content'].values()
                    for records in database_records:
                        for record in records:
                            database = record['database']
                            release = record['release']
                            if database.has_key('record_url_scheme') and record['database_record_external_identifier']:
                                r = record.copy()
                                r['url_scheme'] = database['record_url_scheme']
                                r['external_id'] = r['database_record_external_identifier']
                                r['database_name'] = database['name']
                                r['publisher'] = database['publisher']['name']
                                r['classification'] = 'none'
                                if compound.id == r['uuuuu_compound']:
                                    r['classification'] = 'parent'
                                if compound.id == r['ficus_compound']:
                                    r['classification'] = 'parent'
                                if compound.id == r['ficts_compound']:
                                    r['classification'] = 'exact'
                                if not filter or filter == r['classification']:
                                    response_list.append(r)
                                    self.response_list.append(str(r['url_scheme']['string'] + r['external_id']))
                            if release.has_key('record_url_scheme') and record['release_record_external_identifier']:
                                r = record.copy()
                                r['url_scheme'] = release['record_url_scheme']
                                r['external_id'] = r['release_record_external_identifier']
                                r['database_name'] = database['name']
                                r['publisher'] = release['publisher']['name']
                                r['classification'] = 'none'
                                if compound.id == r['uuuuu_compound']:
                                    r['classification'] = 'parent'
                                if compound.id == r['ficus_compound']:
                                    r['classification'] = 'parent'
                                if compound.id == r['ficts_compound']:
                                    r['classification'] = 'exact'
                                if not filter or filter == r['classification']:
                                    response_list.append(r)
                                    self.response_list.append(str(r['url_scheme']['string'] + r['external_id']))
                representation = {
                    'base_mime_type': self.base_mime_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'compound': compound,
                    'url_records': response_list,
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.mime_type = "text/plain"
            self.response_list = self._unique(self.response_list)
        return representation_list

    def pubchem_sid(self, string):
        # cactvs = self.cactvs
        propname = self.parameters
        base_mime_type = self.base_mime_type
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        structure_index = parameters.get('structure_index', None)
        # filter = parameters.get('filter', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list, cactvs=cactvs).interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        full_ensemble_list = []
        representation_list = []
        all_interpretation_response_list = []
        for interpretation in interpretations:
            for structure in interpretation.structures:
                response_list = []
                try:
                    compound = structure.object.compound
                except:
                    compound = None
                else:
                    # database = Database.objects.get(id=9)
                    database_records = compound.get_records()['content'].values()
                    for records in database_records:
                        for record in records:
                            # database = record['database']
                            # release = record['release']
                            if record['release_record_external_identifier'] and compound.id == record['ficus_compound']:
                                response = str(record['release_record_external_identifier'])
                                response_list.append(response)
                                all_interpretation_response_list.append(response)
                # dummy
                representation = {
                    'base_mime_type': self.base_mime_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': response_list,
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.mime_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    def emolecules_vid(self, string):
        # cactvs = self.cactvs
        propname = self.parameters
        base_mime_type = self.base_mime_type
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        structure_index = parameters.get('structure_index', None)
        # filter = parameters.get('filter', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list, cactvs=cactvs).interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        full_ensemble_list = []
        representation_list = []
        all_interpretation_response_list = []
        for interpretation in interpretations:
            for structure in interpretation.structures:
                response_list = []
                try:
                    compound = structure.object.compound
                except:
                    compound = None
                else:
                    database = Database.objects.get(id=120)
                    database_records = compound.get_records(database=database)['content'].values()
                    for records in database_records:
                        for record in records:
                            if compound.id == record['ficus_compound']:
                                response = str(record['database_record_external_identifier'])
                                response_list.append(response)
                                all_interpretation_response_list.append(response)
                # dummy
                representation = {
                    'base_mime_type': self.base_mime_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': response_list,
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.mime_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    def zinc_id(self, string):
        # cactvs = self.cactvs
        propname = self.parameters
        base_mime_type = self.base_mime_type
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        structure_index = parameters.get('structure_index', None)
        # filter = parameters.get('filter', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list, cactvs=cactvs).interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        full_ensemble_list = []
        representation_list = []
        all_interpretation_response_list = []
        for interpretation in interpretations:
            for structure in interpretation.structures:
                response_list = []
                try:
                    compound = structure.object.compound
                except:
                    compound = None
                else:
                    database = Database.objects.get(id=100)
                    database_records = compound.get_records(database=database)['content'].values()
                    for records in database_records:
                        for record in records:
                            if compound.id == record['ficus_compound']:
                                response = str(record['database_record_external_identifier'])
                                response_list.append(response)
                                all_interpretation_response_list.append(response)
                # dummy
                representation = {
                    'base_mime_type': self.base_mime_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': response_list,
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.mime_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    def nsc_number(self, string):
        # cactvs = self.cactvs
        propname = self.parameters
        base_mime_type = self.base_mime_type
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        structure_index = parameters.get('structure_index', None)
        # filter = parameters.get('filter', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list, cactvs=cactvs).interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        full_ensemble_list = []
        representation_list = []
        all_interpretation_response_list = []
        for interpretation in interpretations:
            for structure in interpretation.structures:
                response_list = []
                try:
                    compound = structure.object.compound
                except:
                    pass
                else:
                    database = Database.objects.get(id=64)
                    database_records = compound.get_records(database=database)['content'].values()
                    for records in database_records:
                        for record in records:
                            if compound.id == record['ficus_compound']:
                                response = 'NSC%s' % str(record['database_record_external_identifier'])
                                response_list.append(response)
                                all_interpretation_response_list.append(response)
                representation = {
                    'base_mime_type': self.base_mime_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': self._unique(response_list),
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.mime_type = "text/plain"
            self.response_list = self._unique(all_interpretation_response_list)
        return representation_list

    def chemnavigator_sid(self, string):
        # cactvs = self.cactvs
        propname = self.parameters
        base_mime_type = self.base_mime_type
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        structure_index = parameters.get('structure_index', None)
        # filter = parameters.get('filter', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list, cactvs=cactvs).interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        full_ensemble_list = []
        representation_list = []
        all_interpretation_response_list = []
        for interpretation in interpretations:
            for structure in interpretation.structures:
                response_list = []
                # ens = structure.ens
                try:
                    compound = structure.object.compound
                except:
                    compound = None
                else:
                    database = Database.objects.get(id=9)
                    database_records = compound.get_records(database=database)['content'].values()
                    for records in database_records:
                        for record in records:
                            if compound.id == record['ficus_compound']:
                                response = str(record['database_record_external_identifier'])
                                response_list.append(response)
                                all_interpretation_response_list.append(response)
                # dummy
                representation = {
                    'base_mime_type': self.base_mime_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': response_list,
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.mime_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    def ncicadd_record_id(self, string):
        # cactvs = self.cactvs
        propname = self.parameters
        base_mime_type = self.base_mime_type
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        structure_index = parameters.get('structure_index', None)
        # filter = parameters.get('filter', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list, cactvs=cactvs).interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        full_ensemble_list = []
        representation_list = []
        all_interpretation_response_list = []
        for interpretation in interpretations:
            for structure in interpretation.structures:
                response_list = []
                try:
                    compound = structure.object.compound
                except:
                    compound = None
                else:
                    database_records = compound.get_records(group_key='database')['content'].values()
                    for records in database_records:
                        for record in records:
                            # database = record['database']
                            # release = record['release']
                            response = record['object']
                            response_list.append(response)
                            all_interpretation_response_list.append(response)
                # dummy
                representation = {
                    'base_mime_type': self.base_mime_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': response_list,
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.mime_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    def ncicadd_compound_id(self, string):
        # cactvs = self.cactvs
        propname = self.parameters
        base_mime_type = self.base_mime_type
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        structure_index = parameters.get('structure_index', None)
        # filter = parameters.get('filter', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list, cactvs=cactvs).interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        full_ensemble_list = []
        representation_list = []
        all_interpretation_response_list = []
        for interpretation in interpretations:
            for structure in interpretation.structures:
                response_list = []
                try:
                    response = structure.object.compound.__str__()
                except:
                    compound = None
                response_list.append(response)
                all_interpretation_response_list.append(response)
                # dummy
                representation = {
                    'base_mime_type': self.base_mime_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': [response, ],
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.mime_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    def ncicadd_structure_id(self, string):
        # cactvs = self.cactvs
        propname = self.parameters
        base_mime_type = self.base_mime_type
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        structure_index = parameters.get('structure_index', None)
        # filter = parameters.get('filter', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list, cactvs=cactvs).interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        full_ensemble_list = []
        representation_list = []
        all_interpretation_response_list = []
        for interpretation in interpretations:
            for structure in interpretation.structures:
                response_list = []
                response = structure.object.__str__()
                response_list.append(response)
                all_interpretation_response_list.append(response)
                # dummy
                representation = {
                    'base_mime_type': self.base_mime_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': [response, ],
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.mime_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    def prop(self, string):
        # cactvs = self.cactvs
        propname = self.parameters
        base_mime_type = self.base_mime_type
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        structure_index = parameters.get('structure_index', None)
        mode = parameters.get('mode', 'simple')
        page = parameters.get('page', None)
        columns = parameters.get('columns', None)
        rows = parameters.get('rows', None)
        if resolver_list:
            resolver_list = resolver_list.split(',')

        interpretations = ChemicalString(string=string, resolver_list=resolver_list, cactvs=cactvs).interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        full_ensemble_list = []
        representation_list = []
        for interpretation in interpretations:
            for structure in interpretation.structures:
                full_ensemble_list.append(structure.ens)
                if self.output_format == 'xml':
                    if hasattr(structure, 'ens'):
                        ens = structure.ens
                    else:
                        ens = Ens(cactvs, structure.object.minimol)
                    # dataset is used to have the same object as below for the plain text output
                    dataset = Dataset(cactvs, enslist=[ens, ])
                    if base_mime_type == 'text':
                        response_list = dataset.get(propname, parameters=parameters, new=True)
                    elif base_mime_type == 'image':
                        response_list = dataset.get_image(parameters=parameters).hash_list
                    response_list = self._unique(response_list)
                    representation = {
                        'base_mime_type': self.base_mime_type,
                        'id': interpretation.id,
                        'string': string,
                        'structure': structure,
                        'response': response_list,
                        'index': index,
                    }
                    representation_list.append(representation)
                    index += 1
        # end of interpretation loop
        if self.output_format == 'plain':
            if structure_index:
                i = int(structure_index)
                ens_list = [full_ensemble_list[i], ]
            elif len(full_ensemble_list) == 1:
                ens_list = [full_ensemble_list[0], ]
            else:
                ens_list = full_ensemble_list
            if columns and rows and page:
                user_page_num = int(page)
                user_columns, columns = int(columns), int(columns)
                user_rows = int(rows)
                dataset_size = len(ens_list)
                rows = dataset_size / user_columns
                if dataset_size % user_columns:
                    rows += 1
                parameters.update({'rows': rows, 'columns': columns})
                if not user_rows == rows:
                    rows = user_rows
                    if rows > 25: rows = 25
                    parameters.update({'rows': rows, })
                    page_size = rows * columns
                    paginator = Paginator(ens_list, page_size)
                    ens_list = paginator.page(page).object_list
                # dummy
            dataset = Dataset(cactvs, enslist=ens_list)
            if base_mime_type == 'text':
                self.mime_type = "text/plain"
                response_list = dataset.get(propname, parameters=parameters, new=True)
                response_list = self._unique(response_list)
            elif base_mime_type == 'image':
                # unique for structures that come from different resolvers:
                # dataset.unique()
                image = dataset.get_image(parameters=parameters, www_media_path=settings.MEDIA_ROOT + 'tmp')
                f = open(image.file, 'r')
                image_file = File(f)
                image_file.url = image.file
                image_file.image = f.read()
                response_list = image_file.image
                self.mime_type = "image/gif"
            self.response_list = response_list
        return representation_list

    def cas(self, string):
        url_parameters = self.url_parameters.copy()
        url_parameters.__setitem__('filter', 'pubchem_generic_registry_name')
        self.url_parameters = url_parameters
        return self.names(string)

    def iupac_name(self, string):
        url_parameters = self.url_parameters.copy()
        url_parameters.__setitem__('filter', 'pubchem_iupac_name')
        self.url_parameters = url_parameters
        return self.names(string)

    def names(self, string):
        # cactvs = self.cactvs
        base_mime_type = self.base_mime_type
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        structure_index = parameters.get('structure_index', None)
        response_index = parameters.get('index', None)
        filter = parameters.get('filter', None)
        if filter:
            filter = filter.lower()
        mode = parameters.get('mode', 'simple')
        parameters = self.url_parameters
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list, cactvs=cactvs).interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        representation_list = []
        names_list = []
        for interpretation in interpretations:
            # representation = self.Representation()
            for structure in interpretation.structures:
                name_sets = NameCache(structure=structure.object)['classified_name_object_sets']
                names = []
                classification_strings = NameType.objects.all()
                for key, value in name_sets.items():
                    key_string = classification_strings.filter(id=key)[0].string.lower()
                    for n in list(value):
                        if filter and not filter == key_string.lower():
                            continue
                        names.append({'class': key_string, 'name': n.name})
                names_list.append(names)
                if self.output_format == 'xml':
                    representation = {
                        'base_mime_type': self.base_mime_type,
                        'id': interpretation.id,
                        'string': string,
                        'structure': structure,
                        'names': names,
                        'index': index,
                    }
                    representation_list.append(representation)
                    index += 1
        # end of interpretation loop
        if self.output_format == 'plain':
            if structure_index:
                i = int(structure_index)
                names_list = [names_list[i], ]
            response_list = []
            for names in names_list:
                for n in names:
                    if filter:
                        if not n['class'] == str(filter):
                            continue
                    response_list.append(str(n['name']))
            self.mime_type = "text/plain"
            self.response_list = self._unique(response_list)
            if response_index:
                i = int(response_index)
                self.response_list = [self.response_list[i], ]
        return representation_list

    def chemspider_id(self, string):
        # cactvs = self.cactvs
        base_mime_type = self.base_mime_type
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        structure_index = parameters.get('structure_index', None)
        response_index = parameters.get('index', None)
        mode = parameters.get('mode', 'simple')
        parameters = self.url_parameters
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list, cactvs=cactvs).interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        representation_list = []
        for interpretation in interpretations:
            chemspider_id_list = []
            chemspider = ExternalResolver(name="chemspider",
                                          url_scheme="http://www.chemspider.com/inchi-resolver/REST.ashx?q=%s\&of=%s")
            for structure in interpretation.structures:
                ens = structure.ens
                smiles = ens.get('smiles').replace('#', '%23')
                response = chemspider.resolve(smiles, 'csid')
                if response['status'] and response['string']:
                    chemspider_id_raw_list = self._unique(response['string'].split())
                    for chemspider_id in chemspider_id_raw_list:
                        chemspider_id_list.append(chemspider_id)
                else:
                    continue
                for chemspider_id in chemspider_id_raw_list:
                    if self.output_format == 'xml':
                        representation = {
                            'base_mime_type': self.base_mime_type,
                            'id': interpretation.id,
                            'string': string,
                            'structure': structure,
                            'response': [chemspider_id, ],
                            'resolver': structure.metadata['query_type'],
                            'index': index,
                            'description': structure.metadata['description']
                        }
                        representation_list.append(representation)
                        index += 1
        # end of interpretation loop
        if self.output_format == 'plain':
            if structure_index:
                i = int(structure_index)
                chemspider_id_list = [chemspider_id_list[i], ]
            self.mime_type = "text/plain"
            self.response_list = self._unique(chemspider_id_list)
            if response_index:
                i = int(response_index)
                self.response_list = [self.response_list[i], ]
        return representation_list

    def twirl(self, string):
        url_parameters = self.url_parameters.copy()
        url_parameters.__setitem__('get3d', 1)
        self.url_parameters = url_parameters
        self.prop(string)
        return self

    def chemdoodle(self, string):
        url_parameters = self.url_parameters.copy()
        url_parameters.__setitem__('get3d', 1)
        self.url_parameters = url_parameters
        self.prop(string)
        return self

    def _unique(self, list):
        # creates a unique list without changing the order of the remaining list elements
        set = {}
        return [set.setdefault(element, element) for element in list if element not in set]


class Resolver(object):
    def __init__(self):
        self.identifier = None
        self.representation = None
        # dirty, but a fake request is needed to get use the resolver without http
        request = HttpRequest()
        request.GET = QueryDict('')
        self.request = request

    def resolve(self, identifier, representation):
        url_method = URLmethod(representation, self.request)
        url_method.parser(identifier)
        return url_method.response_list
