from django.contrib import admin

from .models import ObjectViewed


@admin.register(ObjectViewed)
class ObjectViewedAdmin(admin.ModelAdmin):
    pass
