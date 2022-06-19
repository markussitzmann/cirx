import functools
import io
from distutils.util import strtobool
from typing import List, Dict, Tuple, Any

import logging

from django.conf import settings
from pycactvs import Ens, Dataset, Molfile

from django.core.files import File
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpRequest, QueryDict

from structure.models import ResponseType
from resolver.models import NameType
from structure.string_resolver import ChemicalString, ChemicalStructure

logger = logging.getLogger('cirx')


class Dispatcher:
    def __init__(self, representation, request, parameters=None, output_format='plain'):
        response_type = ResponseType.objects.get(url=representation)
        self.type = response_type
        self.base_content_type = response_type.base_mime_type
        self.method = response_type.method
        self.url_parameters: HttpRequest.GET = request.GET.copy()
        self.representation = representation
        self.content_type = None
        self.output_format = output_format
        self.response_list = []
        #self.simple_mode: bool = self._use_simple_mode()

        if not parameters:
            self.parameters = response_type.parameter
        else:
            self.parameters = parameters

    def __repr__(self):
        repr_string = ''
        if not self.response_list:
            return ''
        if self.content_type == 'image/gif':
            repr_string = self.response_list
        else:
            # response_list = self.response_list
            for item in self.response_list:
                repr_string = repr_string + "%s\n" % (item,)
        return repr_string[0:-1]

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

    def parse(self, string):
        parser_method = getattr(self, self.method, self.parameters)
        parser_response = parser_method(string)
        content_type = self.content_type
        representation = self.representation
        return [string, representation, parser_response, content_type]

    def urls(self, string):
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        filter = parameters.get('filter', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        representation_list = []
        for interpretation in interpretations:
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
                    'base_mime_type': self.base_content_type,
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
            self.content_type = "text/plain"
            self.response_list = self._unique(self.response_list)
        return self.representation_list

    def pubchem_sid(self, string):
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
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
                representation = {
                    'base_mime_type': self.base_content_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': response_list,
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.content_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    def emolecules_vid(self, string):
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
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
                representation = {
                    'base_mime_type': self.base_content_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': response_list,
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.content_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    def zinc_id(self, string):
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
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
                    'base_mime_type': self.base_content_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': response_list,
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.content_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    def nsc_number(self, string):
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
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
                    'base_mime_type': self.base_content_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': self._unique(response_list),
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.content_type = "text/plain"
            self.response_list = self._unique(all_interpretation_response_list)
        return representation_list

    def chemnavigator_sid(self, string):
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
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
                    'base_mime_type': self.base_content_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': response_list,
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.content_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    def ncicadd_record_id(self, string):
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
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
                    'base_mime_type': self.base_content_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': response_list,
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.content_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    def ncicadd_compound_id(self, string):
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
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
                    'base_mime_type': self.base_content_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': [response, ],
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.content_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    def ncicadd_structure_id(self, string):
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
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
                    'base_mime_type': self.base_content_type,
                    'id': interpretation.id,
                    'string': string,
                    'structure': structure,
                    'response': [response, ],
                    'index': index,
                }
                representation_list.append(representation)
                index += 1
        if self.output_format == 'plain':
            self.content_type = "text/plain"
            self.response_list = all_interpretation_response_list
        return representation_list

    @staticmethod
    def _create_dataset_from_resolver_string(string: str, resolver_list: List[str], simple: bool, index: int = -1) -> Dataset:
        interpretations = ChemicalString(string=string, resolver_list=resolver_list).interpretations
        return Dispatcher._create_dataset(interpretations, simple, index)

    @staticmethod
    def _create_dataset(interpretations: List[ChemicalString.Interpretation], simple: bool, structure_index: int = -1) -> Dataset:
        structure_lists: List[List[ChemicalStructure]] = [
            interpretation.structures for interpretation in ([interpretations[0]] if simple else interpretations)
        ]
        ens_list: List[Ens] = [
            structure.ens for structure_list in structure_lists for structure in structure_list
        ]
        dataset: Dataset
        if structure_index > 0:
            dataset = Dataset(ens_list[structure_index])
        else:
            dataset = Dataset(ens_list)
        return dataset

    @staticmethod
    def _create_dataset_page(dataset: Dataset, rows: int, columns: int, page: int) -> Dataset:
        try:
            page_size: int = rows * columns
            paginator: Paginator = Paginator(dataset.ens(), page_size)
            return Dataset(paginator.page(page).object_list)
        except (EmptyPage, ZeroDivisionError):
            return Dataset()

    @staticmethod
    def _use_simple_mode(output_format: str, simple_mode: bool) -> bool:
        if output_format == 'xml' and not simple_mode:
            return False
        return True

    @staticmethod
    def _prepare_params(query_dict: QueryDict) -> Tuple[Dict, int]:
        url_param_dict = query_dict.copy().dict()
        structure_index: int = -1
        if 'structure_index' in url_param_dict:
            structure_index = int(url_param_dict.get('structure_index', -1))
            del url_param_dict['structure_index']
        if 'get3d' in url_param_dict:
            writeflags = url_param_dict.get('writeflags', [])
            if 'write3d' not in writeflags and strtobool(url_param_dict['get3d']):
                writeflags.append('write3d')
                url_param_dict['writeflags'] = writeflags
            del url_param_dict['get3d']
        return url_param_dict, structure_index

    def _interpretations(self, string: str, structure_index: int = -1) -> Tuple[List[ChemicalString.Interpretation], bool]:
        url_params = self.url_parameters.copy()
        if 'resolver' in url_params:
            resolver_list = url_params.get('resolver').split(',')
        else:
            resolver_list = settings.CIR_AVAILABLE_RESOLVERS
        simple: bool = self._use_simple_mode(
            output_format=self.output_format,
            simple_mode=('mode' in url_params and url_params == 'simple')
        )
        interpretations = ChemicalString(string=string, resolver_list=resolver_list, simple=simple).interpretations
        if structure_index > 0:
            interpretations = [interpretations[structure_index], ]
        return interpretations, simple

    def molfilestring(self, string: str) -> Any:
        url_params, structure_index = self._prepare_params(self.url_parameters.copy())
        interpretations: List[ChemicalString.Interpretation]
        simple: bool
        interpretations, simple = self._interpretations(string)
        if not simple:
            raise NotImplemented
        dataset: Dataset = self._create_dataset(interpretations, simple=simple, structure_index=structure_index)
        molfile_string_response: bytes = Molfile.String(dataset, url_params)
        response = None
        # TODO: this is too trusty and needs improvements
        try:
            response = molfile_string_response.decode(encoding='utf-8')
            self.content_type = "text/plain"
        except UnicodeDecodeError:
            response = io.BytesIO(molfile_string_response).getvalue()
            self.content_type = "application/octet-stream"
        finally:
            self.response_list = [response, ]
        return response

    def prop(self, string: str) -> List:
        url_params, structure_index = self._prepare_params(self.url_parameters.copy())
        prop = self.parameters
        index: int = 1
        interpretations: List[ChemicalString.Interpretation]
        simple: bool
        interpretations, simple = self._interpretations(string, structure_index=structure_index)
        for interpretation in interpretations:
            structure: ChemicalStructure
            for structure in interpretation.structures:
                prop_val = structure.ens.get(prop, parameters=url_params)
                if simple:
                    structure_response = prop_val
                else:
                    structure_response = {
                        'base_mime_type': self.base_content_type,
                        'id': interpretation.id,
                        'string': string,
                        'structure': structure,
                        'response': [prop_val, ],
                        'index': index,
                    }
                self.response_list.append(structure_response)
                index += 1
        if simple:
            return self._unique(self.response_list)
        else:
            return self.response_list

    # def xxprop(self, string: str) -> List:
    #     url_params = self.url_parameters.copy()
    #     prop = self.parameters
    #     if 'resolver' in url_params:
    #         resolver_list = url_params.get('resolver').split(',')
    #     else:
    #         resolver_list = settings.AVAILABLE_RESOLVERS
    #     simple: bool = self._use_simple_mode(
    #         output_format=self.output_format,
    #         simple_mode=('mode' in url_params and url_params == 'simple')
    #     )
    #     interpretations = ChemicalString(string=string, resolver_list=resolver_list).interpretations
    #     if simple:
    #         dataset: Dataset = self._create_dataset(interpretations, True)
    #         if 'rows' in url_params and 'columns' in url_params and 'page' in url_params:
    #             rows, columns, page = url_params['rows'], min(url_params['columns'], 25), url_params['page']
    #             dataset = self._create_dataset_page(dataset, int(rows), int(columns), int(page))
    #         if self.base_content_type == 'text':
    #             self.content_type = "text/plain"
    #             self.response_list = self._unique(dataset.get(prop))
    #     else:
    #         index: int = 1
    #         for interpretation in interpretations:
    #             structure: ChemicalStructure
    #             for structure in interpretation.structures:
    #                 prop_val = structure.ens.get(prop, parameters=url_params)
    #                 #response = self._unique(prop_val)
    #                 structure_response = {
    #                     'base_mime_type': self.base_content_type,
    #                     'id': interpretation.id,
    #                     'string': string,
    #                     'structure': structure,
    #                     'response': [prop_val, ],
    #                     'index': index,
    #                 }
    #                 self.response_list.append(structure_response)
    #                 index += 1
    #     return self.response_list
    #
    # def xprop(self, string):
    #     propname = self.parameters
    #     base_content_type = self.base_content_type
    #     parameters = self.url_parameters.copy()
    #     resolver_list = parameters.get('resolver', settings.AVAILABLE_RESOLVERS)
    #     structure_index = parameters.get('structure_index', None)
    #     mode = parameters.get('mode', 'simple')
    #     page = parameters.get('page', None)
    #     columns = parameters.get('columns', None)
    #     rows = parameters.get('rows', None)
    #     #if resolver_list:
    #     #    resolver_list = resolver_list.split(',')
    #     interpretations = ChemicalString(string=string, resolver_list=resolver_list).interpretations
    #     index = 1
    #     if not self.output_format == 'xml' and mode == 'simple':
    #         interpretations = [interpretations[0], ]
    #     full_ensemble_list = []
    #     response_collector_list = []
    #     for interpretation in interpretations:
    #         structure: ChemicalStructure
    #         for structure in interpretation.structures:
    #             full_ensemble_list.append(structure.ens)
    #             if self.output_format == 'xml':
    #                 # if hasattr(structure, 'ens'):
    #                 #     ens = structure._ens
    #                 # else:
    #                 #     ens = Ens(structure._resolved.minimol)
    #                 # dataset is used to have the same object as below for the plain text output
    #                 dataset = Dataset([structure.ens, ])
    #                 if base_content_type == 'text':
    #                     response_collector_list = dataset.get(propname, parameters=parameters)
    #                 elif base_content_type == 'image':
    #                     response_collector_list = dataset.get_image(parameters=parameters).hash_list
    #                 response_collector_list = self._unique(response_collector_list)
    #                 response = {
    #                     'base_mime_type': self.base_content_type,
    #                     'id': interpretation.id,
    #                     'string': string,
    #                     'structure': structure,
    #                     'response': response_collector_list,
    #                     'index': index,
    #                 }
    #                 self.response_list.append(response)
    #                 index += 1
    #             else:
    #                 pass
    #     if self.output_format == 'plain':
    #         if structure_index:
    #             i = int(structure_index)
    #             ens_list = [full_ensemble_list[i], ]
    #         elif len(full_ensemble_list) == 1:
    #             ens_list = [full_ensemble_list[0], ]
    #         else:
    #             ens_list = full_ensemble_list
    #         if columns and rows and page:
    #             #user_page_num = int(page)
    #             user_columns, columns = int(columns), int(columns)
    #             user_rows = int(rows)
    #             dataset_size = len(ens_list)
    #             rows = dataset_size / user_columns
    #             if dataset_size % user_columns:
    #                 rows += 1
    #             parameters.update({'rows': rows, 'columns': columns})
    #             if not user_rows == rows:
    #                 rows = user_rows
    #                 if rows > 25:
    #                     rows = 25
    #                 parameters.update({'rows': rows, })
    #                 page_size = rows * columns
    #                 paginator = Paginator(ens_list, page_size)
    #                 ens_list = paginator.page(page).object_list
    #         dataset = Dataset(ens_list)
    #         if base_content_type == 'text':
    #             self.content_type = "text/plain"
    #             response_collector_list = dataset.get(propname)
    #             response_collector_list = self._unique(response_collector_list)
    #         elif base_content_type == 'image':
    #             # unique for structures that come from different resolvers:
    #             # dataset.unique()
    #             image = dataset.get_image(parameters=parameters, www_media_path=settings.MEDIA_ROOT + 'tmp')
    #             f = open(image.file, 'r')
    #             image_file = File(f)
    #             image_file.url = image.file
    #             image_file.image = f.read()
    #             response_collector_list = image_file.image
    #             self.content_type = "image/gif"
    #         else:
    #             pass
    #         self.response_list = response_collector_list
    #     else:
    #         pass
    #     return self.response_list

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
        parameters = self.url_parameters.copy()
        resolver_list = parameters.get('resolver', None)
        structure_index = parameters.get('structure_index', None)
        response_index = parameters.get('index', None)
        filter_parameter = parameters.get('filter', None)
        if filter_parameter:
            filter_parameter = filter_parameter.lower()
        mode = parameters.get('mode', 'simple')
        if resolver_list:
            resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._interpretations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        representation_list = []
        names_list = []
        for interpretation in interpretations:
            for structure in interpretation.structures:
                name_sets = NameCache(structure=structure.object)['classified_name_object_sets']
                names = []
                classification_strings = NameType.objects.all()
                for key, value in name_sets.items():
                    key_string = classification_strings.filter(id=key)[0].string.lower()
                    for n in list(value):
                        if filter_parameter and not filter_parameter == key_string.lower():
                            continue
                        names.append({'class': key_string, 'name': n.name})
                names_list.append(names)
                if self.output_format == 'xml':
                    representation = {
                        'base_mime_type': self.base_content_type,
                        'id': interpretation.id,
                        'string': string,
                        'structure': structure,
                        'names': names,
                        'index': index,
                    }
                    representation_list.append(representation)
                    index += 1
                else:
                    pass
        if self.output_format == 'plain':
            if structure_index:
                i = int(structure_index)
                names_list = [names_list[i], ]
            response_list = []
            for names in names_list:
                for n in names:
                    if filter_parameter:
                        if not n['class'] == str(filter_parameter):
                            continue
                    response_list.append(str(n['name']))
            self.content_type = "text/plain"
            self.response_list = self._unique(response_list)
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

    @staticmethod
    def _unique(input_list):
        # creates a unique list without changing the order of the remaining list elements
        unique_set = {}
        return [unique_set.setdefault(element, element) for element in input_list if element not in unique_set]


class Resolver(object):
    def __init__(self):
        self.identifier = None
        self.representation = None
        # dirty, but a fake request is needed to get use the resolver without http
        request = HttpRequest()
        request.GET = QueryDict('')
        self.request = request

    def resolve(self, identifier, representation):
        url_method = Dispatcher(representation, self.request)
        url_method.parse(identifier)
        return url_method.response_list


