from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, CustomUserSettings, ExpandedView


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ['alias','email','first_name', 'last_name', 'subscription']
    list_display = ['display_text', 'alias']
    list_filter = ['subscription']

@admin.register(CustomUserSettings)
class CustomUserSettingsAdmin(admin.ModelAdmin):
    search_fields = ['talent']

@admin.register(ExpandedView)
class ExpandedViewAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias']
