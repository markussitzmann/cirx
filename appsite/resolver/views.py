from django.db.models import Prefetch
from django.utils.safestring import mark_safe
from rest_framework import permissions, routers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_json_api.views import RelationshipView, ModelViewSet

from resolver.models import InChI, Structure, Organization, Publisher, EntryPoint, EndPoint, MediaType, InChIType, \
    StructureInChIAssociation
from resolver.serializers import (
    InChISerializer,
    OrganizationSerializer,
    PublisherSerializer,
    EntryPointSerializer,
    EndPointSerializer,
    MediaTypeSerializer,
    StructureSerializer,
    InChITypeSerializer,
    StructureInChIAssociationSerializer
)


class ResolverApiView(routers.APIRootView):
    """
    Wrapper class for setting API root view name and description
    """
    def get_view_name(self):
        return "API Root Resource"

    def get_view_description(self, html=False):
        #if os.environ['INCHI_RESOLVER_TITLE'] == '':
        #    title = 'InChI Resolver'
        #else:
        #    title = os.environ.get('INCHI_RESOLVER_TITLE', 'InChI Resolver')
        title = "CIRX API"
        text = "API Root resource of the Chemical Identifier Resolver X2"
        if html:
            return mark_safe(f"<p>{text}</p>")
        else:
            return text



class ResourceModelViewSet(ModelViewSet):

    def get_view_name(self, *args, **kwargs):
        text = self.name
        if hasattr(self, 'suffix') and self.suffix:
            text += ' ' + self.suffix
        if hasattr(self, 'kwargs'):
            if 'related_field' in self.kwargs:
                text += " Instance: Related " + str(self.kwargs['related_field']).capitalize()
        return text


class ResourceRelationshipView(RelationshipView):

    def get_view_name(self, *args, **kwargs):
        text = self.name
        if hasattr(self, 'kwargs'):
            if 'related_field' in self.kwargs:
                if str(self.kwargs['related_field'])[-1] == "s":
                    field = str(self.kwargs['related_field'])[0:-1]
                else:
                    field = str(self.kwargs['related_field'])
                text += " Instance: " + field.capitalize() + " Relationship"
        return text

    def get_view_description(self, html=False):
        text = """
            This resource provides a relationship link which allows for the manipulation (creation, deletion) of this
            relationship by a client.
        """
        if html:
            return mark_safe(f"<p>{text}</p>")
        else:
            return text


### STRUCTURE ###
class StructureViewSet(ResourceModelViewSet):
    """
        The **Stucture resource** of the Chemical Identifier Resolver X2 API
    """
    def __init__(self, *args, **kwargs):
        self.name = "Structure"
        super().__init__(*args, **kwargs)

    queryset = Structure.objects.filter(compound__isnull=False, blocked__isnull=True)\
        .select_related('ficts_parent', 'ficus_parent', 'uuuuu_parent', 'compound')\
        .prefetch_related('inchis', 'inchis__inchitype', 'inchis__inchi', 'entrypoints', 'ficts_children',
                          'ficus_children', 'uuuuu_children')
    # select_for_includes = {
    #     'ficts_parent': ['ficts_parent'],
    #     'ficus_parent': ['ficus_parent'],
    #     'uuuuu_parent': ['uuuuu_parent'],
    # }
    prefetch_for_includes = {
        '__all__': [],
        'inchis': ['inchis__structure', 'inchis__inchi'],
        #'all_parents': [Prefetch('all_parents', queryset=Structure.objects
        #                         .select_related('ficts_parent', 'ficus_parent', 'uuuuu_parent'))],
        #'category.section': ['category']
    }
    serializer_class = StructureSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filterset_fields = {
        'id': ('exact', 'in'),
        'ficts_parent': ('exact', 'in'),
        'ficus_parent': ('exact', 'in'),
        'uuuuu_parent': ('exact', 'in'),
        # 'ficts_children': ('exact', 'in'),
        # 'ficus_children': ('exact', 'in'),
        # 'uuuuu_children': ('exact', 'in'),
        'hashisy': ('icontains', 'iexact', 'contains', 'exact'),
        'inchis__inchitype': ('exact', 'in'),
        'inchis__inchi__key': ('icontains', 'iexact', 'contains', 'exact'),
        'inchis__inchi__string': ('icontains', 'iexact', 'contains', 'exact'),
    }
    search_fields = (
        'id',
        'hashisy',
        'ficts_parent',
        'ficus_parent',
        'uuuuu_parent',
        'ficts_children',
        'ficus_children',
        'uuuuu_children',
    )


class StructureRelationshipView(ResourceRelationshipView):

    def __init__(self, *args, **kwargs):
        self.name = "Structure"
        super().__init__(*args, **kwargs)

    queryset = Structure.objects
    self_link_view_name = 'structure-relationships'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


### INCHI ###

class InChIViewSet(ResourceModelViewSet):
    """
        The **InChI resource** of the Chemical Identifier Resolver X2 API
    """
    def __init__(self, *args, **kwargs):
        self.name = "InChI"
        super().__init__(*args, **kwargs)

    queryset = InChI.objects.all()
    serializer_class = InChISerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filterset_fields = {
        'id': ('exact', 'in'),
        'key': ('icontains', 'iexact', 'contains', 'exact'),
        'string': ('icontains', 'iexact', 'contains', 'exact'),
        'version': ('exact', 'in', 'gt', 'gte', 'lt', 'lte',),
        'entrypoints__category': ('exact', 'in'),
    }
    search_fields = ('string', 'key',)


class InChIRelationshipView(ResourceRelationshipView):

    def __init__(self, *args, **kwargs):
        self.name = "InChI"
        super().__init__(*args, **kwargs)

    queryset = InChI.objects.all()
    self_link_view_name = 'inchi-relationships'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class StructureInChIAssociationViewSet(ResourceModelViewSet):
    """
    """
    def __init__(self, *args, **kwargs):
        self.name = "StructureInChIAssociation"
        super().__init__(*args, **kwargs)

    queryset = StructureInChIAssociation.objects.all()
    serializer_class = StructureInChIAssociationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filterset_fields = {
        'id': ('exact', 'in'),
        #'inchikey': ('icontains', 'iexact', 'contains', 'exact'),
        'inchi__key': ('icontains', 'iexact', 'contains', 'exact'),

        #'string': ('icontains', 'iexact', 'contains', 'exact'),
        #'version': ('exact', 'in', 'gt', 'gte', 'lt', 'lte',),
        #'entrypoints__category': ('exact', 'in'),
    }
    search_fields = ('string', 'key',)


class StructureInChIAssociationRelationshipView(ResourceRelationshipView):

    def __init__(self, *args, **kwargs):
        self.name = "StructureInChIAssociation"
        super().__init__(*args, **kwargs)

    queryset = StructureInChIAssociation.objects.all()
    self_link_view_name = 'structureinchiassociation-relationships'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class InChITypeViewSet(ResourceModelViewSet):
    """
        The **InChI resource** of the Chemical Identifier Resolver X2 API
    """
    def __init__(self, *args, **kwargs):
        self.name = "InChI Type"
        super().__init__(*args, **kwargs)

    queryset = InChIType.objects.all()
    serializer_class = InChITypeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filterset_fields = {
        'id': ('exact', 'in'),
        #'version': ('exact', 'in', 'gt', 'gte', 'lt', 'lte',),
    }


class InChITypeRelationshipView(ResourceRelationshipView):

    def __init__(self, *args, **kwargs):
        self.name = "InChI Type"
        super().__init__(*args, **kwargs)

    queryset = InChIType.objects.all()
    self_link_view_name = 'inchitype-relationships'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)



### ORGANZATION ###

class OrganizationViewSet(ResourceModelViewSet):
    """
        The **organization resource** of the Chemical Identifier Resolver X2 API
    """
    def __init__(self, *args, **kwargs):
        self.name = "Organization"
        super().__init__(*args, **kwargs)

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filterset_fields = {
        'id': ('exact', 'in'),
        'name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'abbreviation': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'category': ('exact', 'in'),
        'href': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'parent': ('exact', 'in'),
        'parent__name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'parent__abbreviation': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'children': ('exact', 'in'),
        'children__name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'children__abbreviation': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'publishers__name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'publishers__category': ('icontains', 'iexact', 'contains', 'exact', 'in'),
    }
    search_fields = ('name', 'abbreviation', 'category', 'href')


class OrganizationRelationshipView(ResourceRelationshipView):
    """
    """

    def __init__(self, *args, **kwargs):
        self.name = "Organization"
        super().__init__(*args, **kwargs)

    queryset = Organization.objects.all()
    self_link_view_name = 'organization-relationships'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


### PUBLISHER ###

class PublisherViewSet(ResourceModelViewSet):
    """
        The **publisher resource** of the Chemical Identifier Resolver X2 API
    """
    def __init__(self, *args, **kwargs):
        self.name = "Publisher"
        super().__init__(*args, **kwargs)

    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filterset_fields = {
        'id': ('exact', 'in'),
        'name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'category': ('exact', 'in'),
        'email': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'address': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'href': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'orcid': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'parent__name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'parent__category': ('exact', 'in'),
        'parent__email': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'parent__address': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'parent__href': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'parent__orcid': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'children__name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'children__category': ('exact', 'in'),
        'children__email': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'children__address': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'children__href': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'children__orcid': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'organizations__name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'organizations__abbreviation': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'organizations__category': ('icontains', 'iexact', 'contains', 'exact', 'in'),
    }
    search_fields = ('name', 'category', 'email', 'address', 'href', 'orcid')


class PublisherRelationshipView(ResourceRelationshipView):
    """
    """
    def __init__(self, *args, **kwargs):
        self.name = "Publisher"
        super().__init__(*args, **kwargs)

    queryset = Publisher.objects.all()
    self_link_view_name = 'publisher-relationships'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


### ENTRYPOINT ###

class EntryPointViewSet(ResourceModelViewSet):
    """
        The **entrypoint resource** of the Chemical Identifier Resolver X2 API
    """
    def __init__(self, *args, **kwargs):
        self.name = "Entrypoint"
        super().__init__(*args, **kwargs)

    queryset = EntryPoint.objects.all()
    serializer_class = EntryPointSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @action(detail=False)
    def get_self_entrypoint(self, request, pk=None):
        queryset = EntryPoint.objects.filter(category='self').get()
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)

    filterset_fields = {
        'id': ('exact', 'in'),
        'category': ('exact', 'in'),
        'href': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'description': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'publisher__name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'publisher__category': ('exact', 'in'),
        'publisher__email': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'publisher__address': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'publisher__href': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'publisher__orcid': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'endpoints__description': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'endpoints__category': ('exact', 'in'),
        'endpoints__uri': ('icontains', 'iexact', 'contains', 'exact', 'in'),
    }
    search_fields = ('category', 'href', 'name', 'description')


class EntryPointRelationshipView(ResourceRelationshipView):
    """
    """
    def __init__(self, *args, **kwargs):
        self.name = "Entrypoint"
        super().__init__(*args, **kwargs)

    queryset = EntryPoint.objects.all()
    self_link_view_name = 'entrypoint-relationships'


### ENDPOINT ###

class EndPointViewSet(ResourceModelViewSet):
    """
        The **endpoint resource** of the Chemical Identifier Resolver X2 API
    """
    def __init__(self, *args, **kwargs):
        self.name = "Endpoint"
        super().__init__(*args, **kwargs)

    queryset = EndPoint.objects.all()
    serializer_class = EndPointSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filterset_fields = {
        'id': ('exact', 'in'),
        'description': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'category': ('exact', 'in'),
        'uri': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'entrypoint__name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'entrypoint__category': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'accept_header_media_types__name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'content_media_types__name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'request_schema_endpoint__description': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'request_schema_endpoint__category': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'request_schema_endpoint__uri': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'response_schema_endpoint__description': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'response_schema_endpoint__category': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'response_schema_endpoint__uri': ('icontains', 'iexact', 'contains', 'exact', 'in'),
    }
    search_fields = ('category', 'uri', 'description',)


class EndPointRelationshipView(ResourceRelationshipView):
    """
    """
    def __init__(self, *args, **kwargs):
        self.name = "Endpoint"
        super().__init__(*args, **kwargs)

    queryset = EndPoint.objects.all()
    self_link_view_name = 'endpoint-relationships'


### MEDIA  TYPE ###

class MediaTypeViewSet(ResourceModelViewSet):
    """
        The **mediatype resource** of the Chemical Identifier Resolver X2 API
    """
    def __init__(self, *args, **kwargs):
        self.name = "Mediatype"
        super().__init__(*args, **kwargs)

    queryset = MediaType.objects.all()
    serializer_class = MediaTypeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filterset_fields = {
        'id': ('exact', 'in'),
        'name': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'description': ('icontains', 'iexact', 'contains', 'exact', 'in'),
        'accepting_endpoints': ('exact', 'in'),
        'delivering_endpoints': ('exact', 'in'),
    }
    search_fields = ('name', 'description',)


class MediaTypeRelationshipView(ResourceRelationshipView):
    """
    """
    def __init__(self, *args, **kwargs):
        self.name = "Mediatype"
        super().__init__(*args, **kwargs)

    queryset = MediaType.objects.all()
    self_link_view_name = 'mediatype-relationships'

