from rest_framework import routers

from .views import ResolverApiView


class ResolverApiRouter(routers.DefaultRouter):
    APIRootView = ResolverApiView
