from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('chemical/', include('structure.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('resolver.urls')),
    re_path('^api-auth', include('rest_framework.urls', namespace='rest_framework')),
    path('__debug__/', include('debug_toolbar.urls')),
    path('', include('neon.urls')),
]
