import django_filters

from ..models import Timesheet


class TimesheetFilter(django_filters.FilterSet):
    class Meta:
        model = Timesheet
        fields = [
            'talent',
            'work_experience',
            'date_captured',
            'date',
            'client',
            'project',
            'task',
            'details',
            'time_from',
            'time_to',
            'location',
            'out_of_office',
            'notification',
            'notification_time',
            'notification_duration',
            'busy',
            'repeat',
            'include_for_certificate',
            'include_for_invoice',
        ]