from django.contrib import admin

from database.models import ContextTag, Database, Release, URIPattern


@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    pass


@admin.register(Release)
class DatabaseAdmin(admin.ModelAdmin):
    pass


@admin.register(ContextTag)
class ContextTagAdmin(admin.ModelAdmin):
    pass


@admin.register(URIPattern)
class URIPatternAdmin(admin.ModelAdmin):
    pass
