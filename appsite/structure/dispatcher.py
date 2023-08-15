import functools
import io
import logging
from collections import namedtuple
from distutils.util import strtobool
from typing import List, Dict, Tuple

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpRequest
from pycactvs import Dataset as CsDataset
from pycactvs import Ens, Molfile, Prop

from resolver.models import Record, StructureNameAssociation, NameAffinityClass
from structure.models import ResponseType
from structure.string_resolver import ChemicalString, ChemicalStructure, ResolverData, ResolverParams

logger = logging.getLogger('cirx')

DispatcherData = namedtuple("DispatcherData", "identifier representation response")
DispatcherResponse = namedtuple("DispatcherResponse", "full simple content_type")
DispatcherMethodResponse = namedtuple("DispatcherMethodResponse", "content content_type")

try:
    ens_image_prop: Prop = Prop.Ref("E_SVG_IMAGE")
    ens_image_parameters = ens_image_prop.parameters
    ens_image_prop.datatype = "xmlstring"
except Exception as e:
    logger.warning(e)


try:
    dataset_image_prop: Prop = Prop.Ref("D_SVG_IMAGE")
    dataset_image_parameters = dataset_image_prop.parameters
    dataset_image_prop.datatype = "xmlstring"
except Exception as e:
    logger.warning(e)


def dispatcher_method(_func=None, *, as_list=False):
    def dispatcher_method_decorator(func):
        @functools.wraps(func)
        def dispatcher_method_wrapper(self, string, *args, **kwargs):
            params: ResolverParams = self._params
            chemical_string: ChemicalString = ChemicalString(string=string, resolver_list=params.resolver_list)
            resolver_data = [data for data in chemical_string.resolver_data.values() if data.resolved]
            index = 1
            if not self.output_format == 'xml' and len(resolver_data) and params.mode == 'simple':
                resolver_data = [resolver_data[0], ]
            representation_list = []
            data: ResolverData
            for data in resolver_data:
                #response_list = []
                if as_list:
                    try:
                        response: DispatcherMethodResponse = func(self, data.resolved, self.representation_param)
                        representation = {
                            'id': index,
                            'string': string,
                            'structure': data.resolved,
                            'response': response,
                            'index': index,
                            'base_content_type': self.base_content_type,
                            'content_type': response.content_type,
                        }
                        representation_list.append(representation)
                        index += 1
                    except Exception as msg:
                        pass
                else:
                    for resolved in data.resolved:
                        try:
                            response: DispatcherMethodResponse = func(self, resolved, self.representation_param)
                            #response_list.append(response)
                            representation = {
                                'id': index,
                                'string': string,
                                'structure': resolved,
                                'response': response,
                                'index': index,
                                'base_content_type': self.base_content_type,
                                'content_type': response.content_type,
                            }
                            representation_list.append(representation)
                            index += 1
                        except Exception as msg:
                            pass
            if len(representation_list) == 0:
                raise ValueError("no representation available for {}".format(string))
            content_type = list(set([representation['content_type'] for representation in representation_list]))
            if len(content_type) != 1:
                raise ValueError("content type not unique")
            return DispatcherResponse(
                full=representation_list,
                simple=[representation['response'] for representation in representation_list],
                content_type=content_type[0]
            )
        return dispatcher_method_wrapper

    if _func is None:
        return dispatcher_method_decorator
    else:
        return dispatcher_method_decorator(_func)


class Dispatcher:

    def __init__(self, request, representation_type, representation_param=None, output_format='plain'):
        response_type = ResponseType.objects.get(url=representation_type)
        self.base_content_type = response_type.base_mime_type
        self.url_parameters: HttpRequest.GET = request.GET.copy() if request else None
        self.representation_type = representation_type
        self.output_format = output_format
        #self.simple_mode: bool = self._use_simple_mode(output_format)

        if not representation_param:
            self.representation_param = response_type.parameter
        else:
            self.representation_param = representation_param

        self.method = getattr(self, response_type.method, self.representation_param)

    def parse(self, string) -> DispatcherData:
        response: DispatcherResponse = self.method(string)
        representation = self.representation_type
        return DispatcherData(
            identifier=string,
            representation=representation,
            response=response
        )

    def urls(self, string):
        parameters = self.url_parameters.copy()
        resolver_list = self._get_resolver_list()
        filter = parameters.get('filter', None)
        mode = parameters.get('mode', 'simple')
        # if resolver_list:
        #     resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._representations
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
        resolver_list = self._get_resolver_list()
        mode = parameters.get('mode', 'simple')
        # if resolver_list:
        #     resolver_list = resolver_list.split(',')
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._representations
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
                    #compound = None
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
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._representations
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
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._representations
        index = 1
        if not self.output_format == 'xml' and mode == 'simple':
            interpretations = [interpretations[0], ]
        representation_list = []
        all_interpretation_response_list = []
        for interpretation in interpretations:
            for structure in interpretation.with_related_objects:
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
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._representations
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
        interpretations = ChemicalString(string=string, resolver_list=resolver_list)._representations
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

    @dispatcher_method
    def ncicadd_compound_id(self, resolved: ChemicalStructure, *args, **kwargs) -> DispatcherMethodResponse:
        if not resolved.structure or not resolved.structure.compound:
            raise ValueError("no compound found")
        return DispatcherMethodResponse(
            content=[repr(resolved.structure.compound), ],
            content_type="text/plain"
        )

    @dispatcher_method
    def ncicadd_structure_id(self, resolved: ChemicalStructure, *args, **kwargs) -> DispatcherMethodResponse:
        if not resolved.structure:
            raise ValueError("no structure found")
        return DispatcherMethodResponse(
            content=[repr(resolved.structure), ],
            content_type="text/plain"
        )

    @dispatcher_method
    def ncicadd_record_id(self, resolved: ChemicalStructure, *args, **kwargs) -> DispatcherMethodResponse:
        records = Record.with_related_objects.by_structure_ids([resolved.structure.id, ])
        if len(records) == 0:
            raise ValueError("no records found")
        return DispatcherMethodResponse(
            content=[repr(record) for record in records],
            content_type="text/plain"
        )

    @dispatcher_method
    def names(self, resolved: ChemicalStructure, *args, **kwargs) -> DispatcherMethodResponse:
        affinity = {a.title: a for a in NameAffinityClass.objects.all()}

        compounds = []
        ficts_parent = resolved.ficts_parent(only_lookup=False)
        if ficts_parent and ficts_parent.structure:
            compounds.append(ficts_parent.structure.compound)
        ficus_parent = resolved.ficus_parent(only_lookup=False)
        if not len(compounds) and ficus_parent and ficus_parent.structure:
            compounds.append(ficus_parent.structure.compound)

        associations = StructureNameAssociation.with_related_objects.by_compound(
            compounds,
            affinity_classes = [affinity['exact'], affinity['narrow']]
        ).filter(name_type__parent__title='NAME').all().order_by('name__name')
        association: StructureNameAssociation
        names = [association.name.name for association in associations]
        if len(names) == 0:
            raise ValueError("no names available")
        return DispatcherMethodResponse(
            content=names,
            content_type="text/plain"
        )

    @dispatcher_method
    def prop(self, resolved: ChemicalStructure, representation_param: str, *args, **kwargs) -> DispatcherMethodResponse:
        params = self._params
        prop_name = representation_param
        prop_val = resolved.ens.get(prop_name, parameters=params.url_params)
        return DispatcherMethodResponse(
            content=[prop_val, ],
            content_type="text/plain"
        )

    @dispatcher_method(as_list=True)
    def structure_image(self, resolved: List[ChemicalStructure], *args, **kwargs) -> DispatcherMethodResponse:
        url_params = self._params.url_params
        preset_svg_parameters = {
            'width': '250',
            'height': '250',
            'bgcolor': 'white',
            'atomcolor': 'element',
            'bonds': '10',
            'framecolor': 'transparent',
        }
        if url_params:
            svg_parameters = {k: v for k, v in url_params.items()}
        else:
            svg_parameters = {}

        for k, v in preset_svg_parameters.items():
            if k not in svg_parameters:
                svg_parameters[k] = v

        ens_params = {k: (int(v) if v.isnumeric() else v) for k, v in svg_parameters.items() if
                      k in ens_image_parameters}
        dataset_params = {k: (int(v) if v.isnumeric() else v) for k, v in svg_parameters.items() if
                          k in dataset_image_parameters}

        if len(resolved) > 1:
            dataset: CsDataset = CsDataset([structure.ens for structure in resolved])
            if url_params:
                rows, columns, page = \
                    int(url_params.get('rows', 3)), \
                    int(url_params.get('columns', 3)), \
                    int(url_params.get('page', 1))
                image_dataset = Dispatcher._create_dataset_page(dataset, rows=rows, columns=columns, page=page)
                dataset_params.update({"nrows": int(rows), "ncols": int(columns)})
            else:
                image_dataset = Dispatcher._create_dataset_page(dataset, rows=3, columns=3, page=1)
                dataset_params.update({"nrows": 3, "ncols": 3})
            #TODO: this might create thread problems:
            ens_image_prop.setparameter(ens_params)
            image = image_dataset.get(dataset_image_prop, parameters=dataset_params)
            del image_dataset
        else:
            image = resolved[0].ens.get(ens_image_prop, parameters=ens_params)
        return DispatcherMethodResponse(
            content=image,
            content_type="image/svg+xml"
        )

    @dispatcher_method(as_list=True)
    def molfile(self, resolved: List[ChemicalStructure], *args, **kwargs) -> DispatcherMethodResponse:
        url_params = self._params.url_params
        if url_params:
            molfile_parameters = {k: v for k, v in url_params.items()}
        else:
            molfile_parameters = {}
        #TODO: dirty hack for Twirly mol
        if 'dom_id' in molfile_parameters:
            del molfile_parameters['dom_id']
            #molfile_parameters['write3d'] = True
        dataset: CsDataset = CsDataset([structure.ens for structure in resolved])
        molfile_string: bytes = Molfile.String(dataset, molfile_parameters)
        try:
            content = molfile_string.decode(encoding='utf-8')
            content_type = "text/plain"
        except UnicodeDecodeError:
            content = io.BytesIO(molfile_string).getvalue()
            content_type = "application/octet-stream"
        except Exception as msg:
            raise ValueError("creating molfile representation failed", msg)
        return DispatcherMethodResponse(
            content=[content, ],
            content_type=content_type
        )

    @staticmethod
    def _create_dataset_from_resolver_string(string: str, resolver_list: List[str], simple: bool, index: int = -1) -> CsDataset:
        resolver_data: Dict[str, ResolverData] = ChemicalString(string=string, resolver_list=resolver_list).resolver_data
        return Dispatcher._create_dataset(resolver_data, simple, index)

    @staticmethod
    def _create_dataset(resolver_data: Dict[str, ResolverData], simple: bool, structure_index: int = -1) -> CsDataset:
        ens_list: List[Ens] = [structure.ens for data in resolver_data.values() if data.resolved for structure in data.resolved]
        # structure_list = []
        # for data in resolver_data.values():
        #      if data.resolved:
        #         structure_list.extend(data.resolved)
        #
        # structure_lists: List[List[ChemicalStructure]] = [
        #     resolver_data.resolved for resolver_data.values() in ([interpretations[0]] if simple else resolver_data.values())
        # ]
        # ens_list: List[Ens] = [
        #     structure.ens for structure in structure_list
        # ]
        dataset: CsDataset
        if structure_index > 0:
            dataset = CsDataset(ens_list[structure_index])
        else:
            dataset = CsDataset(ens_list)
        return dataset

    @staticmethod
    def _create_dataset_page(dataset: CsDataset, rows: int, columns: int, page: int) -> CsDataset:
        if rows and columns and page:
            try:
                page_size: int = rows * columns
                paginator: Paginator = Paginator(dataset.ens(), page_size)
                return CsDataset(paginator.page(page).object_list)
            except (EmptyPage, ZeroDivisionError) as msg:
                raise ValueError("no dataset available", msg)
        else:
            raise ValueError("no valid parameters for dataset page creation")

    @staticmethod
    def _use_simple_mode(output_format: str, simple_mode: bool) -> bool:
        if output_format == 'xml' and not simple_mode:
            return False
        return True

    @property
    def _params(self) -> ResolverParams:
        if self.url_parameters:
            params = self.url_parameters.copy()
            raw_resolver_str = params.get("resolver", [])
            if raw_resolver_str:
                resolver_list = raw_resolver_str.split(',')
            else:
                resolver_list = []

            structure_index = -1
            writeflags = params.get('writeflags', [])
            if 'structure_index' in params:
                structure_index = int(params.get('structure_index', -1))
                del params['structure_index']
            if 'get3d' in params:
                if 'write3d' not in writeflags and strtobool(params['get3d']):
                    writeflags.append('write3d')
                del params['get3d']
            if 'dom_id' in params and 'write3d' not in writeflags:
                writeflags.append('write3d')
            params['writeflags'] = writeflags

            filter = params.get("filter", None)
            mode = params.get("mode", "simple")
            structure_index = structure_index
            page = int(params.get('page', -1))
            columns = int(params.get('columns', -1))
            rows = int(params.get('rows', -1))

            return ResolverParams(
                url_params=params,
                resolver_list=resolver_list,
                filter=filter,
                mode=mode,
                structure_index=structure_index,
                page=page,
                columns=columns,
                rows=rows
            )
        return ResolverParams(
            url_params=None,
            resolver_list=[],
            filter=None,
            mode="simple",
            structure_index=-1,
            page=-1,
            columns=-1,
            rows=-1
        )

    # @staticmethod
    # def _prepare_params(query_dict: QueryDict) -> Tuple[Dict, int]:
    #     url_param_dict = query_dict.copy().dict()
    #     structure_index: int = -1
    #     if 'structure_index' in url_param_dict:
    #         structure_index = int(url_param_dict.get('structure_index', -1))
    #         del url_param_dict['structure_index']
    #     if 'get3d' in url_param_dict:
    #         writeflags = url_param_dict.get('writeflags', [])
    #         if 'write3d' not in writeflags and strtobool(url_param_dict['get3d']):
    #             writeflags.append('write3d')
    #             url_param_dict['writeflags'] = writeflags
    #         del url_param_dict['get3d']
    #     return url_param_dict, structure_index

    def _interpretations(self, string: str, structure_index: int = -1) -> Tuple[List[ChemicalString], bool]:
        url_params = self.url_parameters.copy()
        if 'resolver' in url_params:
            resolver_list = url_params.get('resolver').split(',')
        else:
            resolver_list = settings.CIR_AVAILABLE_RESOLVERS
        simple: bool = self._use_simple_mode(
            output_format=self.output_format,
            simple_mode=('mode' in url_params and url_params == 'simple')
        )
        interpretations = ChemicalString(string=string, resolver_list=resolver_list, simple=simple).representations
        if structure_index > 0:
            interpretations = [interpretations[structure_index], ]
        return interpretations, simple



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

    # def names(self, string):
    #     parameters = self.url_parameters.copy()
    #     resolver_list = parameters.get('resolver', None)
    #     structure_index = parameters.get('structure_index', None)
    #     response_index = parameters.get('index', None)
    #     filter_parameter = parameters.get('filter', None)
    #     if filter_parameter:
    #         filter_parameter = filter_parameter.lower()
    #     mode = parameters.get('mode', 'simple')
    #     if resolver_list:
    #         resolver_list = resolver_list.split(',')
    #     interpretations = ChemicalString(string=string, resolver_list=resolver_list)._representations
    #     index = 1
    #     if not self.output_format == 'xml' and mode == 'simple':
    #         interpretations = [interpretations[0], ]
    #     representation_list = []
    #     names_list = []
    #     for interpretation in interpretations:
    #         for structure in interpretation.with_related_objects:
    #             name_sets = NameCache(structure=structure.object)['classified_name_object_sets']
    #             names = []
    #             classification_strings = NameType.objects.all()
    #             for key, value in name_sets.items():
    #                 key_string = classification_strings.filter(id=key)[0].string.lower()
    #                 for n in list(value):
    #                     if filter_parameter and not filter_parameter == key_string.lower():
    #                         continue
    #                     names.append({'class': key_string, 'name': n.name})
    #             names_list.append(names)
    #             if self.output_format == 'xml':
    #                 representation = {
    #                     'base_mime_type': self.base_content_type,
    #                     'id': interpretation.id,
    #                     'string': string,
    #                     'structure': structure,
    #                     'names': names,
    #                     'index': index,
    #                 }
    #                 representation_list.append(representation)
    #                 index += 1
    #             else:
    #                 pass
    #     if self.output_format == 'plain':
    #         if structure_index:
    #             i = int(structure_index)
    #             names_list = [names_list[i], ]
    #         response_list = []
    #         for names in names_list:
    #             for n in names:
    #                 if filter_parameter:
    #                     if not n['class'] == str(filter_parameter):
    #                         continue
    #                 response_list.append(str(n['name']))
    #         self.content_type = "text/plain"
    #         self.response_list = self._unique(response_list)
    #         if response_index:
    #             i = int(response_index)
    #             self.response_list = [self.response_list[i], ]
    #     return representation_list

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


# class Resolver(object):
#     def __init__(self):
#         self.identifier = None
#         self.representation = None
#         # dirty, but a fake request is needed to get use the resolver without http
#         request = HttpRequest()
#         request.GET = QueryDict('')
#         self.request = request
#
#     def resolve(self, identifier, representation):
#         url_method = Dispatcher(representation, self.request)
#         url_method.parse(identifier)
#         return url_method.response_list


