from django.contrib import admin

from structure.models import ResponseType, Structure


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    pass


@admin.register(ResponseType)
class ResponseTypeAdmin(admin.ModelAdmin):
    pass