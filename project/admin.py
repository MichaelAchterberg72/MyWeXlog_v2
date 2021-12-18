from django.contrib import admin

from .models import ProjectData, ProjectPersonalDetails


@admin.register(ProjectPersonalDetails)
class ProjectPersonalDetailsAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'project__name', 'project__company__ename']

@admin.register(ProjectData)
class ProjectDataAdmin(admin.ModelAdmin):
    search_fields = ['name', 'company__ename']
