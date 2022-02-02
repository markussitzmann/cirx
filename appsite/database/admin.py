from django.contrib import admin

from database.models import DatabaseContext, ContextTag


@admin.register(DatabaseContext)
class DatabaseContextAdmin(admin.ModelAdmin):
    pass


@admin.register(ContextTag)
class ContextTagAdmin(admin.ModelAdmin):
    pass

