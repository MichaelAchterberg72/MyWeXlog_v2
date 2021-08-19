from django.contrib import admin

from .models import Branch, BranchType, Enterprise, Industry, PhoneNumber


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    pass

@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):
    pass

@admin.register(BranchType)
class BranchTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    pass

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    pass
