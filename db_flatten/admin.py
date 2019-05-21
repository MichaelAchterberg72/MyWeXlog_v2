from django.contrib import admin

from .models import (
    PhoneNumberType
    )

@admin.register(PhoneNumberType)
class PhoneNumberTypeAdmin(admin.ModelAdmin):
    pass
