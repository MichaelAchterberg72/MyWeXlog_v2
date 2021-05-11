from django.contrib import admin

from .models import (
    ProjectData, ProjectPersonalDetails, ProjectPersonalDetailsTask, ProjectTaskBilling
    )


@admin.register(ProjectPersonalDetails)
class ProjectPersonalDetailsAdmin(admin.ModelAdmin):
    pass

@admin.register(ProjectData)
class ProjectDataAdmin(admin.ModelAdmin):
    pass

@admin.register(ProjectPersonalDetailsTask)
class ProjectPersonalDetailsTaskAdmin(admin.ModelAdmin):
    pass

@admin.register(ProjectTaskBilling)
class ProjectTaskBillingAdmin(admin.ModelAdmin):
    pass
