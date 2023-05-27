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
)


class Query(graphene.ObjectType):
    feedback = graphene.Field(FeedbackOutputType, id=graphene.ID())
    feedbacks = DjangoFilterConnectionField(
            FeedbackOutputType, 
            filterset_class=FeedbackFilter
        )
    
    def resolve_feedback(self, info, id):
        try:
            return FeedBack.objects.get(pk=id)
        except FeedBack.DoesNotExist:
            return None