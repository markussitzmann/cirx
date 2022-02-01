from django.contrib import admin
from resolver.models import InChI, Organization, Publisher, EntryPoint, EndPoint


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