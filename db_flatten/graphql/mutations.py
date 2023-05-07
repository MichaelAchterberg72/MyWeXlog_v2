import graphene
from django.db import transaction

from utils.graphql.output_types import SuccessMessage, FailureMessage, SuccessMutationResult

from .input_types import PhoneNumberTypeInputType, SkillTagInputType, LanguageListInputType

from ..models import PhoneNumberType, SkillTag, LanguageList


class PhoneNumberTypeUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = PhoneNumberTypeInputType.id
        type = PhoneNumberTypeInputType.type
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                phone_number_type, created = PhoneNumberType.objects.update_or_create(**kwargs)
                message = "Phone Number Type updated successfully" if not created else "Phone Number Type created successfully"
                return SuccessMessage(success=True, id=phone_number_type.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding phone number type: {str(e)}")


class PhoneNumberTypeDelete(graphene.Mutation):
    class Arguments:
        id = PhoneNumberTypeInputType.id
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                phone_number_type = PhoneNumberType.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="Phone number type deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting phone number type: {str(e)}")


class SkillTagUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = SkillTagInputType.id
        skill = SkillTagInputType.skill
        code = SkillTagInputType.code
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                skill_tag, created = SkillTag.objects.update_or_create(**kwargs)
                message = "Skill tag updated successfully" if not created else "Skill tag created successfully"
                return SuccessMessage(success=True, id=skill_tag.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding skill tag: {str(e)}")


class SkillTagDelete(graphene.Mutation):
    class Arguments:
        id = SkillTagInputType.id
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                skill_tag = SkillTag.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="Skill tag deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting skill tag: {str(e)}")


class LanguageListUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = LanguageListInputType.id
        language = LanguageListInputType.language
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                language_list, created = LanguageList.objects.update_or_create(**kwargs)
                message = "Language item updated successfully" if not created else "Language item created successfully"
                return SuccessMessage(success=True, id=language_list.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding language item: {str(e)}")


class LanguageListDelete(graphene.Mutation):
    class Arguments:
        id = LanguageListInputType.id
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                language_list = LanguageList.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="Language item deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting language item: {str(e)}")


class Mutation(graphene.ObjectType):
    phone_number_type_update_or_create = PhoneNumberTypeUpdateOrCreate.Field()
    phone_number_type_delete = PhoneNumberTypeDelete.Field()
    skill_tag_update_or_create = SkillTagUpdateOrCreate.Field()
    skill_tag_delete = SkillTagDelete.Field()
    language_list_update_or_create = LanguageListUpdateOrCreate.Field()
    language_list_delete = LanguageListDelete.Field()