from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, CustomUserSettings, ExpandedView

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ['alias','email']

@admin.register(CustomUserSettings)
class CustomUserSettingsAdmin(admin.ModelAdmin):
    pass

@admin.register(ExpandedView)
class ExpandedViewAdmin(admin.ModelAdmin):
    pass
