from django.contrib import admin

from resolver.models import Structure, ResponseType


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    pass


@admin.register(ResponseType)
class ResponseTypeAdmin(admin.ModelAdmin):
    pass