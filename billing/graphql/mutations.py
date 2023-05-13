import graphene
from django.db import transaction

from utils.graphql.output_types import SuccessMessage, FailureMessage, SuccessMutationResult

from .input_types import TimesheetInputType

from ..models import Timesheet


class TimesheetUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = TimesheetInputType.id
        talent = TimesheetInputType.talent
        work_experience = TimesheetInputType.work_experience
        date_captured = TimesheetInputType.date_captured
        date = TimesheetInputType.date
        client = TimesheetInputType.client
        project = TimesheetInputType.project
        task = TimesheetInputType.task
        details = TimesheetInputType.details
        time_from = TimesheetInputType.time_from
        time_to = TimesheetInputType.time_to
        location = TimesheetInputType.location
        out_of_office = TimesheetInputType.out_of_office
        notification = TimesheetInputType.notification
        notification_time = TimesheetInputType.notification_time
        notification_duration = TimesheetInputType.notification_duration
        busy = TimesheetInputType.busy
        repeat = TimesheetInputType.repeat
        include_for_certificate = TimesheetInputType.include_for_certificate
        include_for_invoice = TimesheetInputType.include_for_invoice
        
    Output = SuccessMutationResult
    
    @classmethod
    def mutate(cls, root, info, **kwargs):
        errors = []
        if errors:
            return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
        
        try:
            with transaction.atomic():
                timesheet, created = Timesheet.objects.update_or_create(**kwargs)
                message = "Timesheet updated successfully" if not created else "Timesheet created successfully"
                return SuccessMessage(success=True, id=timesheet.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding timesheet", errors=[str(e)])


class TimesheetDelete(graphene.Mutation):
    class Arguments:
        id = TimesheetInputType.id
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        errors = []
        if errors:
            return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
        
        try:
            with transaction.atomic():
                timesheet = Timesheet.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="Timesheet deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting timesheet", errors=[str(e)])


class Mutation(graphene.ObjectType):
    timesheet_update_or_create = TimesheetUpdateOrCreate.Field()
    timesheet_delete = TimesheetDelete.Field()