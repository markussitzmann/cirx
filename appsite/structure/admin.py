from django.contrib import admin

from structure.models import ResponseType, Structure2


@admin.register(Structure2)
class StructureAdmin(admin.ModelAdmin):
    pass


@admin.register(ResponseType)
class ResponseTypeAdmin(admin.ModelAdmin):
    pass