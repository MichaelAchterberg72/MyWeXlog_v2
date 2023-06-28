import graphene
from graphene_django.filter import DjangoFilterConnectionField
from ..models import (
    FeedBack,
    FeedBackActions,
    Notices,
    NoticeRead,
)
from .output_types import (
    FeedbackOutputType,
    FeedBackActionsOutputType,
    NoticesOutputType,
    NoticeReadOutputType,
)
from .filters import (
    FeedbackFilter,
    FeedBackActionsFilter,
    NoticesFilter,
    NoticesReadFilter
)


class Query(graphene.ObjectType):
    feedback = graphene.Field(FeedbackOutputType, id=graphene.ID())
    feedbacks = DjangoFilterConnectionField(
            FeedbackOutputType, 
            filterset_class=FeedbackFilter
        )
    
    feedback_action = graphene.Field(FeedBackActionsOutputType, id=graphene.ID())
    feedback_actions = DjangoFilterConnectionField(
            FeedBackActionsOutputType, 
            filterset_class=FeedBackActionsFilter
        )
    
    notices = graphene.Field(NoticesOutputType, id=graphene.ID())
    noticess = DjangoFilterConnectionField(
            NoticesOutputType, 
            filterset_class=NoticesFilter
        )
    
    notices_read = graphene.Field(NoticeReadOutputType, id=graphene.ID())
    notices_reads = DjangoFilterConnectionField(
            NoticeReadOutputType, 
            filterset_class=NoticesReadFilter
        )
    
    def resolve_notices_read(self, info, id):
        try:
            return NoticeRead.objects.get(pk=id)
        except NoticeRead.DoesNotExist:
            return None
    
    def resolve_notices(self, info, id):
        try:
            return Notices.objects.get(pk=id)
        except Notices.DoesNotExist:
            return None
    
    def resolve_feedback_action(self, info, id):
        try:
            return FeedBackAction.objects.get(pk=id)
        except FeedBackAction.DoesNotExist:
            return None
        
    def resolve_feedback(self, info, id):
        try:
            return FeedBack.objects.get(pk=id)
        except FeedBack.DoesNotExist:
            return None