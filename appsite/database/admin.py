from django.contrib import admin

from database.models import DatabaseContext


@admin.register(DatabaseContext)
class DatabaseContextAdmin(admin.ModelAdmin):
    pass

