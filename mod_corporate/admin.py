from django.contrib import admin

from .models import CorporateStaff, OrgStructure


@admin.register(OrgStructure)
class OrgStructureAdmin(admin.ModelAdmin):
    pass


@admin.register(CorporateStaff)
class CorporateStaffAdmin(admin.ModelAdmin):
    pass
