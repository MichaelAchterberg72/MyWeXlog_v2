import graphene

from .types import UserOutputType


class Query(graphene.ObjectType):
    me = graphene.Field(UserOutputType)

    def resolve_me(self, info):
        user = info.context.user
        if user.is_authenticated:
            return user
        return None