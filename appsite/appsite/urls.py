from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include, re_path
from django.conf import settings

urlpatterns = [
    path('apps/', include('neon.urls')),
    path('chemical/', include('structure.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('resolver.urls')),
    re_path('^api-auth', include('rest_framework.urls', namespace='rest_framework')),
    # path('__debug__/', include('debug_toolbar.urls')),
    path('', lambda request: redirect('apps/', permanent=False)),
]

if not settings.TESTING:
    urlpatterns = [
        *urlpatterns,
        path("__debug__/", include("debug_toolbar.urls")),
    ]