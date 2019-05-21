from django.contrib import admin

from .models import (
    ProjectData
    )

@admin.register(ProjectData)
class ProjectDataAdmin(admin.ModelAdmin):
    pass
