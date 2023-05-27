import graphene
from graphene_django import DjangoObjectType

from ..models import (
    FeedBack,
    FeedBackActions,
    Notices,
    NoticeRead
)


class FeedbackOutputType(DjangoObjectType):
    id_int = graphene.Int(description="The integer representation of the ID")

    @staticmethod
    def resolve_id_int(root, info):
        return int(root.pk)
    
    class Meta:
        model = FeedBack
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'talent': ['iexact', 'icontains', 'istartswith'],
            'date_captured': ['iexact', 'lt', 'lte', 'gt', 'gte'],
            'type': ['iexact', 'icontains', 'istartswith'],
            'details': ['iexact', 'icontains'],
            'optional_1':['iexact', 'icontains'],
            'optional_2': ['iexact', 'icontains'],
            'responded': ['iexact'],
            'slug': ['iexact']
        }
        
        
class FeedBackActionsOutputType(DjangoObjectType):
    id_int = graphene.Int(description="The integer representation of the ID")

    @staticmethod
    def resolve_id_int(root, info):
        return int(root.pk)
    
    class Meta:
        model = FeedBackActions
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        
        
class NoticesOutputType(DjangoObjectType):
    id_int = graphene.Int(description="The integer representation of the ID")

    @staticmethod
    def resolve_id_int(root, info):
        return int(root.pk)
    
    class Meta:
        model = Notices
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        
        
class NoticeReadOutputType(DjangoObjectType):
    id_int = graphene.Int(description="The integer representation of the ID")

    @staticmethod
    def resolve_id_int(root, info):
        return int(root.pk)
    
    class Meta:
        model = NoticeRead
        fields = '__all__'
        interfaces = (graphene.relay.Node,)