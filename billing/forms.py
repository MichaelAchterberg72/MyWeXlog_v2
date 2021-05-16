from django import forms


from .models import Timesheet


class DateInput(forms.DateInput):
    input_type = 'date'
    
class CalendarDetailForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = (
            'date',
            'client',
            'project',
            'task',
            'details',
            'time_from', 'time_to',
            'location',
            'out_of_office',
            'notification',
            'notification_time',
            'notification_duration',
            'busy',
            'repeat',
        )
        widgets = {
            'date': DateInput(),
        }
