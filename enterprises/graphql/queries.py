import graphene
from graphene_django.filter import DjangoFilterConnectionField
from ..models import (
    Industry,
    Enterprise,
    BranchType,
    Branch,
    PhoneNumber
)
from .output_types import (
    indus
)
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