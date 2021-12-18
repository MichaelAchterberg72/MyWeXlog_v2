from django.contrib import admin

from .models import Branch, BranchType, Enterprise, Industry, PhoneNumber


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    search_fields = ['industry']

@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):
    search_fields = ['ename']

@admin.register(BranchType)
class BranchTypeAdmin(admin.ModelAdmin):
    search_fields = ['type']

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    search_fields = ['company__ename', 'name']

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    search_fields = ['branch__company__ename', 'phone']
