from django.contrib import admin

from .models import (
    FeedBack, FeedBackActions
    )


@admin.register(FeedBack)
class FeedBackAdmin(admin.ModelAdmin):
    pass


@admin.register(FeedBackActions)
class FeedBackActionsAdmin(admin.ModelAdmin):
    pass
