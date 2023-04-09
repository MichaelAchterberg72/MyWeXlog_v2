from django.contrib import admin

from .models import (
    ProjectData, ProjectPersonalDetails, ProjectPersonalDetailsTask, ProjectTaskBilling
    )


@admin.register(ProjectPersonalDetails)
class ProjectPersonalDetailsAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'project__name', 'project__company__ename']

@admin.register(ProjectData)
class ProjectDataAdmin(admin.ModelAdmin):
    search_fields = ['name', 'company__ename']

@admin.register(ProjectPersonalDetailsTask)
class ProjectPersonalDetailsTaskAdmin(admin.ModelAdmin):
    pass

@admin.register(ProjectTaskBilling)
class ProjectTaskBillingAdmin(admin.ModelAdmin):
    pass
