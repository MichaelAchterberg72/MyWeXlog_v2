from django.contrib import admin

from .models import (
    Email, SiteName, OnlineRegistrations, Profile, PhysicalAddress, PostalAddress, FileUpload, PhoneNumber, IdentificationDetail, IdType, PassportDetail, LanguageTrack, BriefCareerHistory, WillingToRelocate, ProfileImages
    )


@admin.register(ProfileImages)
class  ProfileImagesAdmin(admin.ModelAdmin):
    pass


@admin.register(WillingToRelocate)
class  WillingToRelocateAdmin(admin.ModelAdmin):
    pass


@admin.register(BriefCareerHistory)
class  BriefCareerHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(LanguageTrack)
class LanguageTrackAdmin(admin.ModelAdmin):
    pass


@admin.register(PassportDetail)
class PassportDetailAdmin(admin.ModelAdmin):
    pass

@admin.register(IdType)
class IdTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(IdentificationDetail)
class IdentificationDetailAdmin(admin.ModelAdmin):
    pass

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    pass

@admin.register(SiteName)
class SiteNameAdmin(admin.ModelAdmin):
    pass

@admin.register(OnlineRegistrations)
class OnlineRegistrationsAdmin(admin.ModelAdmin):
    pass

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(PhysicalAddress)
class PhysicalAddressAdmin(admin.ModelAdmin):
    pass

@admin.register(PostalAddress)
class PostalAddressAdmin(admin.ModelAdmin):
    pass

@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    pass

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    pass
