from typing import Dict

from django.db import IntegrityError
from rest_framework.fields import MultipleChoiceField
from rest_framework_json_api import relations
from rest_framework_json_api import serializers

import resolver.serializers
from structure.ncicadd.identifier import Identifier as NCICADDIdentifier
from resolver import defaults
from resolver.exceptions import ResourceExistsError
from resolver.models import InChI, Structure, Organization, Publisher, EntryPoint, EndPoint, MediaType, InChIType, \
    StructureInChIAssociation, StructureParentStructure


class StructureParentStructureSerializer(serializers.HyperlinkedModelSerializer):

    structure = relations.ResourceRelatedField(
        queryset=Structure.objects,
        many=False,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='structureparents-related',
        related_link_url_kwarg='pk',
        self_link_view_name='structureparents-relationships',
    )

    fictsparent = relations.ResourceRelatedField(
        source='ficts_parent',
        queryset=Structure.objects,
        many=False,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='structureparents-related',
        related_link_url_kwarg='pk',
        self_link_view_name='structureparents-relationships',
    )

    ficts_children = relations.ResourceRelatedField(
        queryset=Structure.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='structureparents-related',
        related_link_url_kwarg='pk',
        self_link_view_name='structureparents-relationships',
    )

    ficusparent = relations.ResourceRelatedField(
        source='ficus_parent',
        queryset=Structure.objects,
        many=False,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='structureparents-related',
        related_link_url_kwarg='pk',
        self_link_view_name='structureparents-relationships',
    )

    ficus_children = relations.ResourceRelatedField(
        queryset=Structure.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='structureparents-related',
        related_link_url_kwarg='pk',
        self_link_view_name='structureparents-relationships',
    )

    uuuuuparent = relations.ResourceRelatedField(
        source='uuuuu_parent',
        queryset=Structure.objects,
        many=False,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='structureparents-related',
        related_link_url_kwarg='pk',
        self_link_view_name='structureparents-relationships',
    )

    uuuuu_children = relations.ResourceRelatedField(
        queryset=Structure.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='structureparents-related',
        related_link_url_kwarg='pk',
        self_link_view_name='structureparents-relationships',
    )

    included_serializers = {
        'structure': 'resolver.serializers.StructureSerializer',
        'fictsparent': 'resolver.serializers.StructureSerializer',
        'ficusparent': 'resolver.serializers.StructureSerializer',
        'uuuuuparent': 'resolver.serializers.StructureSerializer',
        'ficts_children': 'resolver.serializers.StructureSerializer',
        'ficus_children': 'resolver.serializers.StructureSerializer',
        'uuuuu_children': 'resolver.serializers.StructureSerializer',
        #'entrypoints': 'resolver.serializers.EntryPointSerializer',
        #'inchis': 'resolver.serializers.StructureInChIAssociationSerializer',
    }

    #smiles = serializers.SerializerMethodField('serialize_minimol')
    ficts = serializers.SerializerMethodField('get_ficts')
    ficus = serializers.SerializerMethodField('get_ficus')
    uuuuu = serializers.SerializerMethodField('get_uuuuu')

    def get_ficts(self, obj: StructureParentStructure):
        if obj.ficts_parent:
            return NCICADDIdentifier(hashcode=obj.ficts_parent.hashisy.hashisy, identifier_type='FICTS').string
        else:
            None

    def get_ficus(self, obj: StructureParentStructure):
        if obj.ficus_parent:
            return NCICADDIdentifier(hashcode=obj.ficus_parent.hashisy.hashisy, identifier_type='FICuS').string
        else:
            None

    def get_uuuuu(self, obj: StructureParentStructure):
        if obj.uuuuu_parent:
            return NCICADDIdentifier(hashcode=obj.uuuuu_parent.hashisy.hashisy, identifier_type='uuuuu').string
        else:
            None

    class Meta:
        model = Structure
        fields = (
            'id',
            #'url',
            #'hashisy',
            #'smiles',
            'structure',
            'fictsparent',
            'ficusparent',
            'uuuuuparent',
            'ficts_children',
            'ficus_children',
            'uuuuu_children',
            #'structureinchiassociations',
            #'entrypoints',
            'ficts',
            'ficus',
            'uuuuu',
            'added',
        )
        read_only_fields = ('id',)
        #meta_fields = ('added',)


class StructureSerializer(serializers.HyperlinkedModelSerializer):

    entrypoints = relations.ResourceRelatedField(
        queryset=EntryPoint.objects,
        many=True,
        read_only=False,
        required=False,
        related_link_view_name='structures-related',
        related_link_url_kwarg='pk',
        self_link_view_name='structures-relationships',
    )

    structureparents = relations.ResourceRelatedField(
        source='parents',
        queryset=StructureParentStructure.objects,
        many=False,
        read_only=False,
        required=False,
        related_link_view_name='structures-related',
        related_link_url_kwarg='pk',
        self_link_view_name='structures-relationships',
    )


    structureinchiassociations = relations.ResourceRelatedField(
        source='inchis',
        queryset=StructureInChIAssociation.objects,
        many=True,
        read_only=False,
        required=False,
        related_link_view_name='structures-related',
        related_link_url_kwarg='pk',
        self_link_view_name='structures-relationships',
    )

    included_serializers = {
        'parents': 'resolver.serializers.StructureParentStructureSerializer',
        'entrypoints': 'resolver.serializers.EntryPointSerializer',
        'structureparents': 'resolver.serializers.StructureParentStructureSerializer',
        'structureinchiassociations': 'resolver.serializers.StructureInChIAssociationSerializer',
    }

    smiles = serializers.SerializerMethodField('serialize_minimol')
    hashisy = serializers.SerializerMethodField('serialize_hashisy')

    def serialize_minimol(self, obj):
        return obj.to_ens.get("E_SMILES")

    def serialize_hashisy(self, obj):
        return obj.hash.padded

    class Meta:
        model = Structure
        fields = (
            'url',
            'hashisy',
            'smiles',
            'structureparents',
            'structureinchiassociations',
            'entrypoints',
            'added',
        )
        read_only_fields = ('id',)
        meta_fields = ('added',)

    def create(self, validated_data: Dict):
        # not implemented yet
        pass

    def update(self, instance: Structure, validated_data: Dict):
        # not implemented yet
        pass


class InChITypeSerializer(serializers.HyperlinkedModelSerializer):

    associations = relations.HyperlinkedRelatedField(
        queryset=StructureInChIAssociation.objects,
        many=True,
        read_only=False,
        required=False,
        related_link_view_name='inchitypes-related',
        related_link_url_kwarg='pk',
        self_link_view_name='inchitypes-relationships',
    )

    included_serializers = {
        'structureinchiassociations': 'resolver.serializers.StructureInChIAssociationSerializer',
    }

    class Meta:
        model = InChIType
        fields = (
            'url',
            'associations',
            'software_version',
            'description',
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
            'added',
            'modified'
        )
        #read_only_fields = ('key', 'version')
        meta_fields = ('added', 'modified')


class InChISerializer(serializers.HyperlinkedModelSerializer):

    entrypoints = relations.ResourceRelatedField(
        queryset=EntryPoint.objects,
        many=True,
        read_only=False,
        required=False,
        related_link_view_name='inchis-related',
        related_link_url_kwarg='pk',
        self_link_view_name='inchis-relationships',
    )

    structures = relations.ResourceRelatedField(
        queryset=StructureInChIAssociation.objects,
        many=True,
        read_only=False,
        required=False,
        related_link_view_name='inchis-related',
        related_link_url_kwarg='pk',
        self_link_view_name='inchis-relationships',
    )

    included_serializers = {
        'entrypoints': 'resolver.serializers.EntryPointSerializer',
        'structures': 'resolver.serializers.StructureInChIAssociationSerializer'
    }

    class Meta:
        model = InChI
        fields = (
            'url',
            'key',
            'string',
            'version',
            'entrypoints',
            'structures',
            'added',
            'modified'
        )
        read_only_fields = ('key', 'version')
        meta_fields = ('added', 'modified')

    def create(self, validated_data: Dict):
        entrypoints = validated_data.pop('entrypoints', None)

        self.is_valid(raise_exception=True)

        try:
            inchi = InChI.objects.get(**validated_data)
        except InChI.DoesNotExist:
            inchi = InChI.create(**validated_data)
            try:
                inchi.save()
            except IntegrityError as e:
                raise ResourceExistsError("inchi resource already exists", code=409)
            if entrypoints:
                inchi.entrypoints.add(*entrypoints, bulk=True)
        return inchi

    def update(self, instance: InChI, validated_data: Dict):
        if 'string' in validated_data or 'key' in validated_data or 'version' in validated_data or \
                'is_standard' in validated_data:
            raise IntegrityError("fields 'string', 'key', 'version', and 'is_standard'"
                                 "are immutable for the inchis resource")

        entrypoints = validated_data.pop('entrypoints', None)

        instance.save()

        if entrypoints:
            instance.entrypoints.bulk_update(entrypoints, bulk=True, clear=True)
        else:
            instance.entrypoints.clear(bulk=True)

        return instance


class StructureInChIAssociationSerializer(serializers.HyperlinkedModelSerializer):

    structure = relations.ResourceRelatedField(
        queryset=Structure.objects,
        many=False,
        read_only=False,
        required=True,
        related_link_view_name='structureinchiassociations-related',
        related_link_url_kwarg='pk',
        self_link_view_name='structureinchiassociations-relationships',
    )

    inchi = relations.ResourceRelatedField(
        queryset=InChI.objects,
        many=False,
        read_only=False,
        required=True,
        related_link_view_name='structureinchiassociations-related',
        related_link_url_kwarg='pk',
        self_link_view_name='structureinchiassociations-relationships',
    )

    inchitype = relations.ResourceRelatedField(
        source='inchi_type',
        queryset=InChIType.objects,
        many=False,
        read_only=False,
        required=True,
        related_link_view_name='structureinchiassociations-related',
        related_link_url_kwarg='pk',
        self_link_view_name='structureinchiassociations-relationships',
    )

    included_serializers = {
        'inchi': 'resolver.serializers.InChISerializer',
        'inchitype': 'resolver.serializers.InChITypeSerializer',
        'structure': 'resolver.serializers.StructureSerializer'
    }

    class Meta:
        model = StructureInChIAssociation
        fields = (
            'url',
            'save_opt',
            'software_version',
            'structure',
            'inchi',
            'inchitype',
            'added',
            'modified'
        )
        read_only_fields = ('added', 'modified')
        meta_fields = ('added', 'modified')
        ordering = ['structure', 'inchi']

    def get_inchikey(self, obj):
        return obj.inchi.key

    def get_smiles(self, obj):
        return obj.structure.to_ens.get("E_SMILES")


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):

    parent = relations.ResourceRelatedField(
        queryset=Organization.objects,
        many=False,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='organizations-related',
        related_link_url_kwarg='pk',
        self_link_view_name='organizations-relationships',
    )

    children = relations.ResourceRelatedField(
        queryset=Organization.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='organizations-related',
        related_link_url_kwarg='pk',
        self_link_view_name='organizations-relationships',
    )

    publishers = relations.ResourceRelatedField(
        queryset=Publisher.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='organizations-related',
        related_link_url_kwarg='pk',
        self_link_view_name='organizations-relationships',
    )

    included_serializers = {
        'parent': 'resolver.serializers.OrganizationSerializer',
        'children': 'resolver.serializers.OrganizationSerializer',
        'publishers': 'resolver.serializers.PublisherSerializer',
    }

    class Meta:
        model = Organization
        fields = (
            'url',
            'parent',
            'children',
            'name',
            'abbreviation',
            'category',
            'href',
            'publishers',
            'added',
            'modified'
        )
        read_only_fields = ('added', 'modified')
        meta_fields = ('added', 'modified')

    def create(self, validated_data: Dict):
        children = validated_data.pop('children', None)
        publishers = validated_data.pop('publishers', None)

        self.is_valid(raise_exception=True)

        try:
            organization = Organization.objects.get(**validated_data)
        except Organization.DoesNotExist:
            organization = Organization.create(**validated_data)
            try:
                organization.save()
            except IntegrityError as e:
                raise ResourceExistsError("organization resource already exists", code=409)
            if children:
                organization.children.add(*children, bulk=True)
            if publishers:
                organization.publishers.add(*publishers, bulk=True)
        return organization

    def update(self, instance: Organization, validated_data: Dict):
        if 'name' in validated_data or 'parent' in validated_data:
            raise IntegrityError("fields 'name' and 'parent' are immutable for the organizations resource")

        children = validated_data.pop('children', None)
        publishers = validated_data.pop('publishers', None)

        instance.abbreviation = validated_data.get('abbreviation', instance.abbreviation)
        instance.category = validated_data.get('category', instance.category)
        instance.href = validated_data.get('href', instance.href)

        instance.save()

        if children:
            instance.children.bulk_update(children, bulk=True, clear=True)
        else:
            instance.children.clear(bulk=True)
        if publishers:
            instance.publishers.bulk_update(publishers, bulk=True, clear=True)
        else:
            instance.publishers.clear(bulk=True)

        return instance


class PublisherSerializer(serializers.HyperlinkedModelSerializer):

    parent = relations.ResourceRelatedField(
        queryset=Publisher.objects,
        many=False,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='publishers-related',
        related_link_url_kwarg='pk',
        self_link_view_name='publishers-relationships',
    )

    organizations = relations.ResourceRelatedField(
        queryset=Organization.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='publishers-related',
        related_link_url_kwarg='pk',
        self_link_view_name='publishers-relationships',
    )

    children = relations.ResourceRelatedField(
        queryset=Publisher.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='publishers-related',
        related_link_url_kwarg='pk',
        self_link_view_name='publishers-relationships',
    )

    entrypoints = relations.ResourceRelatedField(
        queryset=EntryPoint.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='publishers-related',
        related_link_url_kwarg='pk',
        self_link_view_name='publishers-relationships',
    )

    included_serializers = {
        'organizations': 'resolver.serializers.OrganizationSerializer',
        'entrypoints': 'resolver.serializers.EntryPointSerializer',
        'parent': 'resolver.serializers.PublisherSerializer',
        'children': 'resolver.serializers.PublisherSerializer',
    }

    class Meta:
        model = Publisher
        fields = (
            'url',
            'parent',
            'children',
            'organizations',
            'entrypoints',
            'name',
            'category',
            'email',
            'address',
            'href',
            'orcid',
            'added',
            'modified'
        )
        read_only_fields = ('added', 'modified')
        meta_fields = ('added', 'modified')

    def create(self, validated_data: Dict):
        children = validated_data.pop('children', None)
        entrypoints = validated_data.pop('entrypoints', None)
        organizations = validated_data.pop('organizations', None)

        self.is_valid(raise_exception=True)

        try:
            publisher = Publisher.objects.get(**validated_data)
        except Publisher.DoesNotExist:
            publisher = Publisher.create(**validated_data)
            try:
                publisher.save()
            except IntegrityError as e:
                raise ResourceExistsError("organization resource already exists", code=409)
            if children:
                publisher.children.add(*children, bulk=True)
            if entrypoints:
                publisher.entrypoints.add(*entrypoints, bulk=True)
            if organizations:
                publisher.organizations.add(*organizations, bulk=True)
        return publisher

    def update(self, instance: Publisher, validated_data: Dict):
        if 'parent' in validated_data or 'name' in validated_data:
            raise IntegrityError("fields 'parent', and 'name' are immutable for the publishers resource")

        children = validated_data.pop('children', None)
        entrypoints = validated_data.pop('entrypoints', None)
        organizations = validated_data.pop('organizations', None)

        instance.category = validated_data.get('category', instance.category)
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.address = validated_data.get('address', instance.address)
        instance.href = validated_data.get('href', instance.href)
        instance.orcid = validated_data.get('orcid', instance.orcid)

        instance.save()

        if children:
            instance.children.bulk_update(children, bulk=True, clear=True)
        else:
            instance.children.clear(bulk=True)
        if entrypoints:
            instance.entrypoints.bulk_update(entrypoints, bulk=True, clear=True)
        else:
            instance.entrypoints.clear(bulk=True)
        if organizations:
            instance.organizations.bulk_update(organizations, bulk=True, clear=True)
        else:
            instance.organizations.clear(bulk=True)

        return instance


class EntryPointSerializer(serializers.HyperlinkedModelSerializer):

    parent = relations.ResourceRelatedField(
        queryset=EntryPoint.objects,
        many=False,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='entrypoints-related',
        related_link_url_kwarg='pk',
        self_link_view_name='entrypoints-relationships',
    )

    publisher = relations.ResourceRelatedField(
        queryset=Publisher.objects,
        many=False,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='entrypoints-related',
        related_link_url_kwarg='pk',
        self_link_view_name='entrypoints-relationships',
    )

    children = relations.ResourceRelatedField(
        queryset=EntryPoint.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='entrypoints-related',
        related_link_url_kwarg='pk',
        self_link_view_name='entrypoints-relationships',
    )

    endpoints = relations.ResourceRelatedField(
        queryset=EndPoint.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='entrypoints-related',
        related_link_url_kwarg='pk',
        self_link_view_name='entrypoints-relationships',
    )

    included_serializers = {
        'publisher': 'resolver.serializers.PublisherSerializer',
        'endpoints': 'resolver.serializers.EndPointSerializer',
        'parent': 'resolver.serializers.EntryPointSerializer',
        'children': 'resolver.serializers.EntryPointSerializer',
    }

    class Meta:
        model = EntryPoint
        fields = (
            'url',
            'parent',
            'children',
            'publisher',
            'name',
            'description',
            'category',
            'href',
            'entrypoint_href',
            'endpoints',
            'added',
            'modified'
        )
        read_only_fields = ('added', 'modified')
        meta_fields = ('added', 'modified')

    def create(self, validated_data: Dict):
        children = validated_data.pop('children', None)
        publishers = validated_data.pop('publishers', None)
        endpoints = validated_data.pop('endpoints', None)

        self.is_valid(raise_exception=True)

        try:
            entrypoint = EntryPoint.objects.get(**validated_data)
        except EntryPoint.DoesNotExist:
            entrypoint = EntryPoint.create(**validated_data)
            try:
                entrypoint.save()
            except IntegrityError as e:
                raise ResourceExistsError("entrypoint resource already exists", code=409)
            if children:
                entrypoint.children.add(*children, bulk=True)
            if publishers:
                entrypoint.publishers.add(*publishers, bulk=True)
            if endpoints:
                entrypoint.endpoints.add(*endpoints, bulk=True)

        return entrypoint

    def update(self, instance: EntryPoint, validated_data: Dict):
        if 'parent' in validated_data \
                or 'publisher' in validated_data \
                or 'href' in validated_data:
            raise IntegrityError("fields 'parent', 'publisher', 'href' are immutable \
            for the entrypoints resource")

        children = validated_data.pop('children', None)
        endpoints = validated_data.pop('endpoints', None)

        instance.publisher = validated_data.get('publisher', instance.publisher)
        instance.entrypoint_href = validated_data.get('entrypoint_href', instance.entrypoint_href)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.category = validated_data.get('category', instance.category)

        instance.save()

        if children:
            instance.children.bulk_update(children, bulk=True, clear=True)
        else:
            instance.children.clear(bulk=True)
        if endpoints:
            instance.children.bulk_update(endpoints, bulk=True, clear=True)
        else:
            instance.endpoints.clear(bulk=True)

        return instance


class EndPointSerializer(serializers.HyperlinkedModelSerializer):

    accept_header_media_types = relations.ResourceRelatedField(
        queryset=MediaType.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='endpoints-related',
        related_link_url_kwarg='pk',
        self_link_view_name='endpoints-relationships',
    )

    content_media_types = relations.ResourceRelatedField(
        queryset=MediaType.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='endpoints-related',
        related_link_url_kwarg='pk',
        self_link_view_name='endpoints-relationships',
    )

    request_schema_endpoint = relations.ResourceRelatedField(
        queryset=MediaType.objects,
        many=False,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='endpoints-related',
        related_link_url_kwarg='pk',
        self_link_view_name='endpoints-relationships',
    )

    response_schema_endpoint = relations.ResourceRelatedField(
        queryset=MediaType.objects,
        many=False,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='endpoints-related',
        related_link_url_kwarg='pk',
        self_link_view_name='endpoints-relationships',
    )

    full_path_uri = serializers.CharField()

    included_serializers = {
        'entrypoint': 'resolver.serializers.EntryPointSerializer',
        'accept_header_media_types': 'resolver.serializers.MediaTypeSerializer',
        'content_media_types': 'resolver.serializers.MediaTypeSerializer',
        'request_schema_endpoint': 'resolver.serializers.EndPointSerializer',
        'response_schema_endpoint': 'resolver.serializers.EndPointSerializer',
    }

    request_methods = MultipleChoiceField(choices=defaults.http_verbs, default=['GET'])

    class Meta:
        model = EndPoint
        fields = (
            'url',
            'entrypoint',
            'uri',
            'full_path_uri',
            'description',
            'category',
            'request_methods',
            'accept_header_media_types',
            'content_media_types',
            'request_schema_endpoint',
            'response_schema_endpoint',
            'full_path_uri',
            'added',
            'modified'
        )
        read_only_fields = ('full_path_uri', 'added', 'modified')
        meta_fields = ('added', 'modified')

    def create(self, validated_data: Dict):
        accept_header_mediatypes = validated_data.pop('accept_header_mediatypes', None)
        content_mediatypes = validated_data.pop('content_mediatypes', None)
        request_schema_endpoint = validated_data.pop('request_schema_endpoint', None)
        response_schema_endpoint = validated_data.pop('response_schema_endpoint', None)

        self.is_valid(raise_exception=True)

        try:
            endpoint = EndPoint.objects.get(**validated_data)
        except EndPoint.DoesNotExist:
            endpoint = EndPoint.create(**validated_data)
            try:
                endpoint.save()
            except IntegrityError as e:
                raise ResourceExistsError("endpoint resource already exists", code=409)
            if accept_header_mediatypes:
                endpoint.accept_header_mediatypes.add(*accept_header_mediatypes, bulk=True)
            if content_mediatypes:
                endpoint.content_mediatypes.add(*content_mediatypes, bulk=True)
            if request_schema_endpoint:
                endpoint.request_schema_endpoint.add(*request_schema_endpoint, bulk=True)
            if response_schema_endpoint:
                endpoint.response_schema_endpoint.add(*response_schema_endpoint, bulk=True)
        return endpoint

    def update(self, instance: EndPoint, validated_data: Dict):
        if 'entrypoint' in validated_data or 'uri' in validated_data:
            raise IntegrityError("fields 'entrypoint', and 'uri' are immutable \
            for the endpoints resource")

        accept_header_media_types = validated_data.pop('accept_header_mediatypes', None)
        content_media_types = validated_data.pop('content_mediatypes', None)
        request_schema_endpoint = validated_data.pop('request_schema_endpoint', None)
        response_schema_endpoint = validated_data.pop('response_schema_endpoint', None)

        instance.category = validated_data.get('category', instance.category)
        instance.request_methods = validated_data.get('request_methods', instance.request_methods)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        if accept_header_media_types:
            instance.accept_header_media_types.bulk_update(accept_header_media_types, bulk=True, clear=True)
        else:
            instance.accept_header_media_types.clear(bulk=True)

        if content_media_types:
            instance.content_media_types.bulk_update(content_media_types, bulk=True, clear=True)
        else:
            instance.content_media_types.clear(bulk=True)

        if request_schema_endpoint:
            instance.request_schema_endpoint.bulk_update(request_schema_endpoint, bulk=True, clear=True)
        else:
            instance.request_schema_endpoint.clear(bulk=True)

        if content_media_types:
            instance.response_schema_endpoint.bulk_update(response_schema_endpoint, bulk=True, clear=True)
        else:
            instance.response_schema_endpoint.clear(bulk=True)

        return instance


class MediaTypeSerializer(serializers.HyperlinkedModelSerializer):

    accepting_endpoints = relations.ResourceRelatedField(
        queryset=EndPoint.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='mediatypes-related',
        related_link_url_kwarg='pk',
        self_link_view_name='mediatypes-relationships',
    )

    delivering_endpoints = relations.ResourceRelatedField(
        queryset=EndPoint.objects,
        many=True,
        read_only=False,
        required=False,
        default=None,
        related_link_view_name='mediatypes-related',
        related_link_url_kwarg='pk',
        self_link_view_name='mediatypes-relationships',
    )

    included_serializers = {
        'accepting_endpoints': 'resolver.serializers.EndPointSerializer',
        'delivering_endpoints': 'resolver.serializers.EndPointSerializer',
    }

    class Meta:
        model = MediaType
        fields = ('url', 'name', 'description', 'accepting_endpoints', 'delivering_endpoints', 'added', 'modified')
        read_only_fields = ('added', 'modified')
        meta_fields = ('added', 'modified')

    def create(self, validated_data: Dict):
        accepting_endpoints = validated_data.pop('accepting_endpoints', None)
        delivering_endpoints = validated_data.pop('delivering_endpoints', None)

        self.is_valid(raise_exception=True)

        try:
            mediatype = MediaType.objects.get(**validated_data)
        except MediaType.DoesNotExist:
            mediatype = MediaType.create(**validated_data)
            try:
                mediatype.save()
            except IntegrityError as e:
                raise ResourceExistsError("mediatype resource already exists", code=409)
            if accepting_endpoints:
                mediatype.accepting_endpoints.add(*accepting_endpoints, bulk=True)
            if delivering_endpoints:
                mediatype.delivering_endpoints.add(*delivering_endpoints, bulk=True)
        return mediatype

    def update(self, instance: MediaType, validated_data: Dict):
        if 'name' in validated_data:
            raise IntegrityError("field 'name', is immutable for the mediatypes resource")

        accepting_endpoints = validated_data.pop('accepting_endpoints', None)
        delivering_endpoints = validated_data.pop('delivering_endpoints', None)

        instance.description = validated_data.get('description', instance.description)

        instance.save()

        if accepting_endpoints:
            instance.accepting_endpoints.bulk_update(accepting_endpoints, bulk=True, clear=True)
        else:
            instance.accepting_endpoints.clear(bulk=True)
        if delivering_endpoints:
            instance.delivering_endpoints.bulk_update(delivering_endpoints, bulk=True, clear=True)
        else:
            instance.delivering_endpoints.clear(bulk=True)

        return instance
