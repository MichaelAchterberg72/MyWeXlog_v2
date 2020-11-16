from django.contrib import admin

from .models import (
    CorporateHR,
    )


@admin.register(CorporateHR)
class CorporateHRAdmin(admin.ModelAdmin):
    pass
