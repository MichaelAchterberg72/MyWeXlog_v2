from django.contrib import admin

from .models import LanguageList, PhoneNumberType, SkillTag


@admin.register(PhoneNumberType)
class PhoneNumberTypeAdmin(admin.ModelAdmin):
    search_fields = ['type']


@admin.register(SkillTag)
class SkillTagAdmin(admin.ModelAdmin):
    search_fields = ['skill']


@admin.register(LanguageList)
class LanguageListAdmin(admin.ModelAdmin):
    search_fields = ['language']
