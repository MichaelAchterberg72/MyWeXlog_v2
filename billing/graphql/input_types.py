import graphene

from .enums import TimesheetBusyEnum, TimesheetDurationEnum, TimesheetNotificationEnum, TimesheetRepeatEnum
from users.graphql.input_types import UserInputType
from talenttrack.graphql.input_types import WorkExperienceInputType
from enterprises.graphql.input_types import BranchInputType
from project.graphql.input_types import ProjectPersonalDetailsInputType, ProjectPersonalDetailsTaskInputType


class TimesheetInputType(graphene.InputObjectType):
    id = graphene.ID()
    talent = graphene.Argument(UserInputType)
    work_experience = graphene.Argument(WorkExperienceInputType)
    date_captured = graphene.Date()
    date = graphene.Date()
    client = graphene.Argument(BranchInputType)
    project = graphene.Argument(ProjectPersonalDetailsInputType)
    task = graphene.Argument(ProjectPersonalDetailsTaskInputType)
    details = graphene.String()
    time_from = graphene.DateTime()
    time_to = graphene.DateTime()
    location = graphene.String()
    out_of_office = graphene.Boolean()
    notification = graphene.String()
    notification_time = TimesheetNotificationEnum()
    notification_duration = TimesheetDurationEnum()
    busy = TimesheetBusyEnum()
    repeat = TimesheetRepeatEnum()
    include_for_certificate = graphene.Boolean()
    include_for_invoice = graphene.Boolean()