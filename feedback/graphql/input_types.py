import graphene


class FeedbackInputType(graphene.InputObjectType):
    id = graphene.ID()
    talent = graphene.ID()
    date_captured = graphene.DateTime()
    type = graphene.String()
    details = graphene.String()
    optional_1 = graphene.String()
    optional_2 = graphene.String()
    responded = graphene.Boolean()
    slug = graphene.String()
    
    
class FeedBackActionsInputType(graphene.InputObjectType):
    id = graphene.ID()
    item = graphene.Argument(FeedbackInputType)
    review_by = graphene.Argument(Custom)
    date_reviewed = graphene.DateTime()
    actions = graphene.String()
    
    
class NoticesInputType(graphene.InputObjectType):
    id = graphene.ID()
    notice_date = graphene.DateTime()
    subject = graphene.String()
    notice = graphene.String()
    slug = graphene.String()
    
    
class NoticeReadInputType(graphene.InputObjectType):
    id = graphene.ID()
    talent = graphene.Argument()
    notice = graphene.Argument()
    date_read = graphene.DateTime()
    notice_read = graphene.Boolean()