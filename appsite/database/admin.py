# from django.contrib import admin
#
# from database.models import ContextTag, Database, Release, URIPattern
#
#
# class ReleaseInline(admin.StackedInline):
#     model = Release
#     extra = 0
#
#
# @admin.register(Database)
# class DatabaseAdmin(admin.ModelAdmin):
#     inlines = [
#         ReleaseInline
#     ]
#
#
# @admin.register(Release)
# class ReleaseAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(ContextTag)
# class ContextTagAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(URIPattern)
# class URIPatternAdmin(admin.ModelAdmin):
#     pass
