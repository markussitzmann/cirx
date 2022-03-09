from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('chemical/', include('structure.urls')),
    path('simple/', include('simple.urls')),
    path('admin/', admin.site.urls),
    re_path('^api-auth', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include('resolver.urls')),
]
