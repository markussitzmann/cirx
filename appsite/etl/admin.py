from django.contrib import admin

from etl.models import StructureFile, StructureFileCollection


@admin.register(StructureFile)
class StructureFileAdmin(admin.ModelAdmin):
   pass


class StructureFileInline(admin.StackedInline):
    model = StructureFile
    extra = 0


@admin.register(StructureFileCollection)
class FileCollectionAdmin(admin.ModelAdmin):
    inlines = [
        StructureFileInline
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['file_location_pattern_string', 'release']
        else:
            return ['file_location_pattern_string']
