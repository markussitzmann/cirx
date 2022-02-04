from django.contrib import admin

from etl.models import StructureFile, FileCollection


@admin.register(StructureFile)
class StructureFileAdmin(admin.ModelAdmin):
    pass


@admin.register(FileCollection)
class FileCollectionAdmin(admin.ModelAdmin):
    pass
