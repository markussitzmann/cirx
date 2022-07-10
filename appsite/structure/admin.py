from django.contrib import admin

from structure.models import ResponseType
from resolver.models import Structure


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    pass


@admin.register(ResponseType)
class ResponseTypeAdmin(admin.ModelAdmin):
    pass