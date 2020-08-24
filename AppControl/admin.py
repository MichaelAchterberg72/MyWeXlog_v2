from django.contrib import admin

from .models import (
    CorporateStaff, CorporateHR
    )


@admin.register(CorporateStaff)
class CorporateStaffAdmin(admin.ModelAdmin):
    pass


@admin.register(CorporateHR)
class CorporateHRAdmin(admin.ModelAdmin):
    pass
