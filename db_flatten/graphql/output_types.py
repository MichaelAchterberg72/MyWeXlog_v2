import graphene
from graphene_django import DjangoObjectType

from ..models import (
    PhoneNumberType,
    SkillTag,
    LanguageList
)


class PhoneNumberTypeOutputType(DjangoObjectType):
    id_int = graphene.Int(description="The integer representation of the ID")

    @staticmethod
    def resolve_id_int(root, info):
        return int(root.pk)
    
    class Meta:
        model = PhoneNumberType
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'type': ['exact', 'icontaints', 'istartswith'],
        }
        ordering = ['type']
        
        
class SkillTagOutputType(DjangoObjectType):
    id_int = graphene.Int(description="The integer representation of the ID")

    @staticmethod
    def resolve_id_int(root, info):
        return int(root.pk)
    
    class Meta:
        model = SkillTag
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'skill': ['exact', 'iexact', 'icontains', 'istartswith'],
            'code': ['exact', 'iexact', 'icontains', 'istartswith'],
        }
        ordering = ['skill', 'code']
        
        
class LanguageListOutputType(DjangoObjectType):
    id_int = graphene.Int(description="The integer representation of the ID")

    @staticmethod
    def resolve_id_int(root, info):
        return int(root.pk)
    
    class Meta:
        model = LanguageList
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'language': ['exact', 'iexact', 'icontains', 'istartswith'],
        }
        ordering = ['language']
