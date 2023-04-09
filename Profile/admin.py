from django.contrib import admin

from .models import (BriefCareerHistory, Email, FileUpload,
                     IdentificationDetail, IdType, LanguageTrack,
                     OnlineRegistrations, PassportDetail, PhoneNumber,
                     PhysicalAddress, PostalAddress, Profile, ProfileImages,
                     SiteName, WillingToRelocate)


@admin.register(ProfileImages)
class  ProfileImagesAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']


@admin.register(WillingToRelocate)
class  WillingToRelocateAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']


@admin.register(BriefCareerHistory)
class  BriefCareerHistoryAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']


@admin.register(LanguageTrack)
class LanguageTrackAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'language__language']


@admin.register(PassportDetail)
class PassportDetailAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']

@admin.register(IdType)
class IdTypeAdmin(admin.ModelAdmin):
    search_fields = ['type']

@admin.register(IdentificationDetail)
class IdentificationDetailAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'id_type__type']

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'email']

@admin.register(SiteName)
class SiteNameAdmin(admin.ModelAdmin):
    search_fields = ['site']

@admin.register(OnlineRegistrations)
class OnlineRegistrationsAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'sitename__site']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'f_name', 'l_name']


@admin.register(PhysicalAddress)
class PhysicalAddressAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']

@admin.register(PostalAddress)
class PostalAddressAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']

@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']
