from django.contrib import admin
from resolver.models import InChI, Organization, Publisher, EntryPoint, EndPoint, Release, Dataset, ContextTag, \
    URIPattern


@admin.register(InChI)
class InchiAdmin(admin.ModelAdmin):
    pass


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    pass


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    pass


@admin.register(EntryPoint)
class EntryPointAdmin(admin.ModelAdmin):
    pass


@admin.register(EndPoint)
class EndPointAdmin(admin.ModelAdmin):
    pass


class ReleaseInline(admin.StackedInline):
    model = Release
    extra = 0


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    inlines = [
        ReleaseInline
    ]


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    pass


@admin.register(ContextTag)
class ContextTagAdmin(admin.ModelAdmin):
    pass


@admin.register(URIPattern)
class URIPatternAdmin(admin.ModelAdmin):
    pass