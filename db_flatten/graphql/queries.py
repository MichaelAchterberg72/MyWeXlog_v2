import graphene
from graphene_django.filter import DjangoFilterConnectionField
from ..models import PhoneNumberType, SkillTag, LanguageList
from .output_types import PhoneNumberTypeOutputType, SkillTagOutputType, LanguageListOutputType
from .filters import PhoneNumberTypeFilter, SkillTagFilter, LanguageListFilter


class Query(graphene.ObjectType):
    phone_number_type = graphene.Field(PhoneNumberTypeOutputType, id=graphene.ID())
    phone_number_types = DjangoFilterConnectionField(
            PhoneNumberTypeOutputType, 
            filterset_class=PhoneNumberTypeFilter
        )
    skill_tag = graphene.Field(SkillTagOutputType, id=graphene.ID())
    skill_tags = DjangoFilterConnectionField(
            SkillTagOutputType, 
            filterset_class=SkillTagFilter
        )
    language_list = graphene.Field(LanguageListOutputType, id=graphene.ID())
    language_lists = DjangoFilterConnectionField(
            LanguageListOutputType, 
            filterset_class=LanguageListFilter
        )
    
    def resolve_language_list(self, info, id):
        try:
            return LanguageList.objects.get(pk=id)
        except LanguageList.DoesNotExist:
            return None
        
    def resolve_skill_tag(self, info, id):
        try:
            return SkillTag.objects.get(pk=id)
        except SkillTag.DoesNotExist:
            return None
        
    def resolve_phone_number_type(self, info, id):
        try:
            return PhoneNumberType.objects.get(pk=id)
        except PhoneNumberType.DoesNotExist:
            return None