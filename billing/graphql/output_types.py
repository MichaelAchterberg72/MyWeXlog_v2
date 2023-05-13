import graphene
from graphene_django import DjangoObjectType

from ..models import Timesheet


class TimesheetOutputType(DjangoObjectType):
    class Meta:
        model = Timesheet
        fields = '__all__'
        convert_choices_to_enums = True
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'talent__alias': ['exact'],
            'date_captured': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'date': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'details': ['icontains'],
            'time_from': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'time_to': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'location': ['exact'],
            'out_of_office': ['exact'],
            'notification': ['exact'],
            'notification_time': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'notification_duration': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'busy': ['exact'],
            'repeat': ['exact'],
            'include_for_certificate': ['exact'],
            'include_for_invoice': ['exact'],
        }
        
    
            