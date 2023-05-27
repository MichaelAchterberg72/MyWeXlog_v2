import graphene
from graphene_django.filter import DjangoFilterConnectionField

from .output_types import UserOutputType
from .filters import UserFilter

from ..models import CustomUser


class Query(graphene.ObjectType):
    user = graphene.Field(UserOutputType, id=graphene.ID())
    users = DjangoFilterConnectionField(
            UserOutputType, 
            filterset_class=UserFilter
        )
    
    def resolve_user(self, info, id):
        try:
            return CustomUser.objects.get(pk=id)
        except CustomUser.DoesNotExist:
            return None