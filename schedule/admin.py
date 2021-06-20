from django.contrib import admin

from schedule.forms import EventAdminForm
from schedule.models import (
    Calendar,
    CalendarRelation,
    Event,
    EventRelation,
    Occurrence,
    Rule,
    NotePad,
    NotePadRelatedProject,
    NotePadRelatedTask,
    NotePadRelatedEvent,
    NotePadRelatedOccurrence,
)


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ("talent", "name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    fieldsets = ((None, {"fields": [("talent", "name", "slug")]}),)


@admin.register(CalendarRelation)
class CalendarRelationAdmin(admin.ModelAdmin):
    list_display = ("calendar", "content_object")
    list_filter = ("inheritable",)
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "calendar",
                    ("content_type", "object_id", "distinction"),
                    "inheritable",
                ]
            },
        ),
    )


@admin.register(EventRelation)
class EventRelationAdmin(admin.ModelAdmin):
    list_display = ("event", "content_object", "distinction")
    fieldsets = (
        (None, {"fields": ["event", ("content_type", "object_id", "distinction")]}),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start", "end")
    list_filter = ("start",)
    ordering = ("-start",)
    date_hierarchy = "start"
    search_fields = ("title", "description")
    fieldsets = (
        (
            None,
            {
                "fields": [
                    ("title", "color_event"),
                    ("description",),
                    ("start", "end"),
                    ("creator", "calendar"),
                    ("companybranch", "task"),
                    ("skills",),
                    ("rule", "end_recurring_period"),
                ]
            },
        ),
    )
    form = EventAdminForm


admin.site.register(Occurrence, admin.ModelAdmin)


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ("frequency",)
    search_fields = ("name", "description")

@admin.register(NotePad)
class NotePadAdmin(admin.ModelAdmin):
    list_display = ("talent",)
    list_filter = ("talent",)
    search_fields = ("talent", "heading")

@admin.register(NotePadRelatedProject)
class NotePadRelatedProjectAdmin(admin.ModelAdmin):
    list_display = ("talent",)
    list_filter = ("talent",)
    search_fields = ("talent", "notepad_id__heading")

@admin.register(NotePadRelatedTask)
class NotePadRelatedTaskAdmin(admin.ModelAdmin):
    list_display = ("talent",)
    list_filter = ("talent",)
    search_fields = ("talent", "notepad_id__heading")

@admin.register(NotePadRelatedEvent)
class NotePadRelatedEventAdmin(admin.ModelAdmin):
    list_display = ("talent",)
    list_filter = ("talent",)
    search_fields = ("talent", "notepad_id__heading")

@admin.register(NotePadRelatedOccurrence)
class NotePadRelatedOccurrenceAdmin(admin.ModelAdmin):
    list_display = ("talent",)
    list_filter = ("talent",)
    search_fields = ("talent", "notepad_id__heading")
