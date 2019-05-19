from django.contrib import admin

from .models import (
    Email, SiteName, OnlineRegistrations, Profile, PhysicalAddress
    )

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    pass

@admin.register(SiteName)
class SiteNameAdmin(admin.ModelAdmin):
    pass

@admin.register(OnlineRegistrations)
class OnlineRegistrationsAdmin(admin.ModelAdmin):
    pass

@admin.register(PhysicalAddress)
class PhysicalAddressAdmin(admin.ModelAdmin):
    pass

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
