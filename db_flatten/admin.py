from django.contrib import admin

from .models import LanguageList, PhoneNumberType, SkillTag


@admin.register(PhoneNumberType)
class PhoneNumberTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(SkillTag)
class SkillTagAdmin(admin.ModelAdmin):
    pass


@admin.register(LanguageList)
class LanguageListAdmin(admin.ModelAdmin):
    pass
