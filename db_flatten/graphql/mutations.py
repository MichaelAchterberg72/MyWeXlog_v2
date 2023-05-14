import graphene
from django.db import transaction

from utils.graphql.output_types import SuccessMessage, FailureMessage, SuccessMutationResult
from utils.utils import update_or_create_object
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
                phonenumber_id = kwargs.get('id')
                phonenumber = update_or_create_object(PhoneNumberType, kwargs)
                message = "Phone Number Type updated successfully" if phonenumber_id else "Phone Number Type created successfully"
                return SuccessMessage(success=True, id=phonenumber.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding phone number type", errors=[str(e)])


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
            return FailureMessage(success=False, message=f"Error deleting phone number type", errors=[str(e)])


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
                skill_tag_id = kwargs.get('id')
                skill_tag = update_or_create_object(SkillTag, kwargs)
                message = "Skill tag updated successfully" if skill_tag_id else "Skill tag created successfully"
                return SuccessMessage(success=True, id=skill_tag.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding skill tag", errors=[str(e)])


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
            return FailureMessage(success=False, message=f"Error deleting skill tag", errors=[str(e)])


class LanguageListUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = LanguageListInputType.id
        language = LanguageListInputType.language
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                language_list_id = kwargs.get('id')
                language_list = update_or_create_object(PhoneNumberType, kwargs)
                message = "Language item updated successfully" if language_list_id else "Language item created successfully"
                return SuccessMessage(success=True, id=language_list.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding language item", errors=[str(e)])


class LanguageListDelete(graphene.Mutation):
    class Arguments:
        id = LanguageListInputType.id
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        errors = []
        if errors:
            return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
        
        try:
            with transaction.atomic():
                language_list = LanguageList.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="Language item deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting language item", errors=[str(e)])


class Mutation(graphene.ObjectType):
    phone_number_type_update_or_create = PhoneNumberTypeUpdateOrCreate.Field()
    phone_number_type_delete = PhoneNumberTypeDelete.Field()
    skill_tag_update_or_create = SkillTagUpdateOrCreate.Field()
    skill_tag_delete = SkillTagDelete.Field()
    language_list_update_or_create = LanguageListUpdateOrCreate.Field()
    language_list_delete = LanguageListDelete.Field()