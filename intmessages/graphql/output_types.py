import graphene
from graphene_django import DjangoObjectType

from ..models import (
    ChatGroup,
    ChatRoomMembers,
    Message,
    MessageRead,
)


class ChatGroupOutputType(DjangoObjectType):
    id_int = graphene.Int(description="The integer representation of the ID")

    @staticmethod
    def resolve_id_int(root, info):
        return int(root.pk)
    
    class Meta:
        model = ChatGroup
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'room_name': ['iexact', 'icontains', 'istartswith'],
            'description': ['iexact', 'icontains', 'istartswith'],
            'date_created': ['iexact', 'lt', 'lte', 'gt', 'gte'],
            'slug': ['iexact']
        }


class ChatRoomMembersOutputType(DjangoObjectType):
    id_int = graphene.Int(description="The integer representation of the ID")

    @staticmethod
    def resolve_id_int(root, info):
        return int(root.pk)
    
    class Meta:
        model = ChatRoomMembers
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'room_name': ['iexact', 'icontains', 'istartswith'],
            'description': ['iexact', 'icontains', 'istartswith'],
            'date_created': ['iexact', 'lt', 'lte', 'gt', 'gte'],
            'slug': ['iexact']
        }