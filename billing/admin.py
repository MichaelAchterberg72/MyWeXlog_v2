from django.contrib import admin

#from .models import Timesheet
from .models import Timesheet


@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    pass
