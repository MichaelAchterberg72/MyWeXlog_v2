import graphene
from graphene_django import DjangoObjectType

from ..models import Timesheet


class TimesheetOutputType(DjangoObjectType):
    class Meta:
        model = Timesheet
        fields = '__all__'
        convert_choices_to_enums = ['notification', 'notification_duration', 'busy']
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'talent__alias': ['exact'],
            'date_captured': ['exact'],
            'date': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'client': ['exact', 'icontains', 'startswith'],
            'project': ['exact', 'icontains', 'startswith'],
            'task': ['exact', 'icontains', 'startswith'],
            'location': ['exact'],
            'include_for_certificate': ['exact'],
            'include_for_invoice': ['exact'],
        }
            