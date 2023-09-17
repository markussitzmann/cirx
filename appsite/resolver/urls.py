from django.urls import include, path, re_path

from rest_framework.routers import DefaultRouter
from rest_framework.settings import api_settings

from . import views
from . import routers

router = routers.ResolverApiRouter(trailing_slash=False)
router.register('inchis', views.InChIViewSet)
router.register('inchitypes', views.InChITypeViewSet)
router.register('organizations', views.OrganizationViewSet)
router.register('publishers', views.PublisherViewSet)
router.register('structures', views.StructureViewSet)
router.register('structureparents', views.StructureParentStructureViewSet)
router.register('structureinchiassociations', views.StructureInChIAssociationViewSet)
router.register('entrypoints', views.EntryPointViewSet)
router.register('endpoints', views.EndPointViewSet)
router.register('mediatypes', views.MediaTypeViewSet)



urlpatterns = [

    re_path(r'', include(router.urls)),

    path('_self',
        views.EntryPointViewSet.as_view({'get': 'get_self_entrypoint'}),
        name='entrypoints-self'),

    path('structures/<pk>/relationships/<related_field>',
         views.StructureRelationshipView.as_view(), {'source': 'relationships'},
         name='structures-relationships'),
    path('structures/<pk>/<related_field>',
         views.StructureViewSet.as_view({'get': 'retrieve_related'}), {'source': 'field'},
         name='structures-related'),

    path('structureparents/<pk>/relationships/<related_field>',
         views.StructureParentStructureRelationshipView.as_view(), {'source': 'relationships'},
         name='structureparents-relationships'),
    path('structureparents/<pk>/<related_field>',
         views.StructureParentStructureViewSet.as_view({'get': 'retrieve_related'}), {'source': 'field'},
         name='structureparents-related'),

    path('inchis/<pk>/relationships/<related_field>',
         views.InChIRelationshipView.as_view(), {'source': 'relationships'},
         name='inchis-relationships'),
    path('inchis/<pk>/<related_field>',
         views.InChIViewSet.as_view({'get': 'retrieve_related'}), {'source': 'field'},
         name='inchis-related'),

    path('structureinchiassociations/<pk>/relationships/<related_field>',
        views.StructureInChIAssociationRelationshipView.as_view(), {'source': 'relationships'},
        name='structureinchiassociations-relationships'),
    path('structureinchiassociations/<pk>/<related_field>',
        views.StructureInChIAssociationViewSet.as_view({'get': 'retrieve_related'}), {'source': 'field'},
        name='structureinchiassociations-related'),

    path('inchitypes/<pk>/relationships/<related_field>',
         views.InChITypeRelationshipView.as_view(), {'source': 'relationships'},
         name='inchitypes-relationships'),
    path('inchitypes/<pk>/<related_field>',
         views.InChITypeViewSet.as_view({'get': 'retrieve_related'}), {'source': 'field'},
         name='inchitypes-related'),

    path('publishers/<pk>/relationships/<related_field>',
        views.PublisherRelationshipView.as_view(), {'source': 'relationships'},
        name='publishers-relationships'),
    path('publishers/<pk>/<related_field>',
        views.PublisherViewSet.as_view({'get': 'retrieve_related'}), {'source': 'field'},
        name='publishers-related'),

    path('entrypoints/<pk>/relationships/<related_field>',
        views.EntryPointRelationshipView.as_view(), {'source': 'relationships'},
        name='entrypoints-relationships'),
    path('entrypoints/<pk>/<related_field>',
        views.EntryPointViewSet.as_view({'get': 'retrieve_related'}), {'source': 'field'},
        name='entrypoints-related'),

    path('organizations/<pk>/relationships/<related_field>',
        views.OrganizationRelationshipView.as_view(), {'source': 'relationships'},
        name='organizations-relationships'),
    path('organizations/<pk>/<related_field>',
        views.OrganizationViewSet.as_view({'get': 'retrieve_related'}), {'source': 'field'},
        name='organizations-related'),

    path('endpoints/<pk>/relationships/<related_field>',
        views.EndPointRelationshipView.as_view(), {'source': 'relationships'},
        name='endpoints-relationships'),
    path('endpoints/<pk>/<related_field>',
        views.EndPointViewSet.as_view({'get': 'retrieve_related'}), {'source': 'field'},
        name='endpoints-related'),

    path('mediatypes/<pk>/relationships/<related_field>',
        views.MediaTypeRelationshipView.as_view(), {'source': 'relationships'},
        name='mediatypes-relationships'),
    path('mediatypes/<pk>/<related_field>',
        views.MediaTypeViewSet.as_view({'get': 'retrieve_related'}), {'source': 'field'},
        name='mediatypes-related'),

]
