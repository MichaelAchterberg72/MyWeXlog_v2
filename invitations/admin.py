from django.contrib import admin

from .models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    search_fields = ['invited_by__alias', 'name', 'surname']
