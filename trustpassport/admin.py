from django.contrib import admin

from .models import (
    TalentPassport, EnterprisePassport
    )

@admin.register(TalentPassport)
class TalentPassportAdmin(admin.ModelAdmin):
    pass

@admin.register(EnterprisePassport)
class EnterprisePassportAdmin(admin.ModelAdmin):
    pass
