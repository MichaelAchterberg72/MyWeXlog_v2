from django.contrib import admin

from .models import (
    PhoneNumberType, SkillTag, LanguageList
    )


@admin.register(PhoneNumberType)
class PhoneNumberTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(SkillTag)
class SkillTagAdmin(admin.ModelAdmin):
    pass


@admin.register(LanguageList)
class LanguageListAdmin(admin.ModelAdmin):
    pass
