import graphene
from graphene_django import DjangoObjectType

from ..models import PhoneNumberType, PhoneNumberType, LanguageList


class PhoneNumberTypeOutputType(DjangoObjectType):
    class Meta:
        model = PhoneNumberType
        fields = '__all__'
        
        
class SkillTagOutputType(DjangoObjectType):
    class Meta:
        model = PhoneNumberType
        fields = '__all__'
        
        
class LanguageListOutputType(DjangoObjectType):
    class Meta:
        model = LanguageList
        fields = '__all__'