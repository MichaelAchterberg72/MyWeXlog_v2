import graphene

from users.graphql.input_types import UserInputType


class TimesheetInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    
    talent = graphene.Field(UserInputType)
    work_experience = graphene.Field()
    date_captured = graphene.Date()
    date = graphene.Date()
    client = graphene.Field()
    project = graphene.Field()
    task = graphene.Field()
    details = graphene.String()
    time_from = graphene.DateTime()
    time_to = graphene.DateTime()
    location = graphene.String()
    out_of_office = graphene.Boolean()
    notification = graphene.String()
    notification_time = graphene.String()
    notification_duration = graphene.String()
    busy = graphene.String()
    repeat = graphene.String()
    include_for_certificate = graphene.Boolean()
    include_for_invoice = graphene.Boolean()