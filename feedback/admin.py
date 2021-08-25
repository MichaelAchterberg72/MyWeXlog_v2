from django.contrib import admin

from .models import FeedBack, FeedBackActions, NoticeRead, Notices


@admin.register(FeedBack)
class FeedBackAdmin(admin.ModelAdmin):
    pass


@admin.register(FeedBackActions)
class FeedBackActionsAdmin(admin.ModelAdmin):
    pass


@admin.register(Notices)
class NoticesAdmin(admin.ModelAdmin):
    pass


@admin.register(NoticeRead)
class NoticeReadAdmin(admin.ModelAdmin):
    pass
