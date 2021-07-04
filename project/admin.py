from django.contrib import admin

from .models import (
    ProjectData, ProjectPersonalDetails
    )

@admin.register(ProjectPersonalDetails)
class ProjectPersonalDetailsAdmin(admin.ModelAdmin):
    pass

@admin.register(ProjectData)
class ProjectDataAdmin(admin.ModelAdmin):
    pass
