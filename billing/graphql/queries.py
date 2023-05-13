import graphene
from graphene_django.filter import DjangoFilterConnectionField
from ..models import Timesheet
from .output_types import TimesheetOutputType
from .filters import TimesheetFilter


class Query(graphene.ObjectType):
    timesheet = graphene.Field(TimesheetOutputType, id=graphene.ID())
    timesheets = DjangoFilterConnectionField(
            TimesheetOutputType, 
            filterset_class=TimesheetFilter
        )
    
    def resolve_timesheet(self, info, id):
        try:
            return Timesheet.objects.get(pk=id)
        except Timesheet.DoesNotExist:
            return None
        
    def resolve_timesheets(self, info, **kwargs):
        return TimesheetFilter(kwargs).qs