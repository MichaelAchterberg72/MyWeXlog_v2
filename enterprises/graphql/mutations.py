import graphene
from django.db import transaction

from utils.graphql.output_types import SuccessMessage, FailureMessage, SuccessMutationResult

from .input_types import (
    IndustryInputType,
    EnterpriseInputType,
    BranchTypeInputType,
    BranchInputType,
    PhoneNumberInputType,
    PhoneNumberTypeInputType
)

from ..models import (
    Industry,
    Enterprise,
    BranchType,
    Branch,
    PhoneNumber,
    PhoneNumberType
)


class IndustryUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = IndustryInputType.id
        industry = IndustryInputType.industry
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        errors = []
        if errors:
            return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
        
        try:
            with transaction.atomic():
                industry, created = Industry.objects.update_or_create(**kwargs)
                message = "Industry updated successfully" if not created else "Industry created successfully"
                return SuccessMessage(success=True, id=industry.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding industry", errors=[str(e)])


class IndustryDelete(graphene.Mutation):
    class Arguments:
        id = IndustryInputType.id
        
    Output = SuccessMutationResult
    
    @classmethod
    def mutate(cls, root, info, **kwargs):
        errors = []
        if errors:
            return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
        
        try:
            with transaction.atomic():
                industry = Industry.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="Industry deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting industry", errors=[str(e)])


class EnterpriseUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = EnterpriseInputType.id
        ename = EnterpriseInputType.ename
        slug = EnterpriseInputType.slug
        description = EnterpriseInputType.description
        logo = EnterpriseInputType.logo
        website = EnterpriseInputType.website
        filter_class = EnterpriseInputType.filter_class
        rate_1 = EnterpriseInputType.rate_1
        rate_2 = EnterpriseInputType.rate_2
        rate_3 = EnterpriseInputType.rate_3
        rate_4 = EnterpriseInputType.rate_4
        rate_count = EnterpriseInputType.rate_count
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        errors = []
        if errors:
            return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
        
        try:
            with transaction.atomic():
                enterprise, created = Enterprise.objects.update_or_create(**kwargs)
                message = "Enterprise updated successfully" if not created else "Enterprise created successfully"
                return SuccessMessage(success=True, id=enterprise.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding enterprise", errors=[str(e)])


class EnterpriseDelete(graphene.Mutation):
    class Arguments:
        id = EnterpriseInputType.id
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        errors = []
        if errors:
            return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
        
        try:
            with transaction.atomic():
                enterprise = Enterprise.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="Enterprise deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting enterprise", errors=[str(e)])


class BranchTypeUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = BranchTypeInputType.id
        type = BranchTypeInputType.type
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        errors = []
        if errors:
            return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
        
        try:
            with transaction.atomic():
                branch_type, created = BranchType.objects.update_or_create(**kwargs)
                message = "BranchType updated successfully" if not created else "BranchType created successfully"
                return SuccessMessage(success=True, id=branch_type.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding branch type", errors=[str(e)])


class BranchTypeDelete(graphene.Mutation):
    class Arguments:
        id = BranchTypeInputType.id
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        errors = []
        if errors:
            return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
        
        try:
            with transaction.atomic():
                branch_type = BranchType.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="BranchType deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting branch type", errors=[str(e)])


class BranchUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = BranchInputType.id
        company = BranchInputType.company
        name = BranchInputType.name
        type = BranchInputType.type
        size = BranchInputType.size
        phy_address_line1 = BranchInputType.phy_address_line1
        phy_address_line2 = BranchInputType.phy_address_line2
        country = BranchInputType.country
        region = BranchInputType.region
        city = BranchInputType.city
        suburb = BranchInputType.suburb
        code = BranchInputType.code
        industry = BranchInputType.industry
        slug = BranchInputType.slug
        rate_1 = BranchInputType.rate_1
        rate_2 = BranchInputType.rate_2
        rate_3 = BranchInputType.rate_3
        rate_4 = BranchInputType.rate_4
        rate_count = BranchInputType.rate_count
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                branch_id = kwargs.pop('id', None)
                branch = Branch.update_or_create(id=branch_id, **kwargs)
                message = "Branch updated successfully" if branch_id else "Branch created successfully"
                return SuccessMessage(success=True, id=branch.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding branch", errors=[str(e)])


class BranchDelete(graphene.Mutation):
    class Arguments:
        slug = BranchInputType.slug
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                branch = Branch.objects.get(kwargs['slug']).delete()
                return SuccessMessage(success=True, id=kwargs['slug'], message="Branch deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting branch", errors=[str(e)])


class PhoneNumberUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = PhoneNumberInputType.id
        type = PhoneNumberInputType.type
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                phone_number, created = PhoneNumber.objects.update_or_create(**kwargs)
                message = "PhoneNumber updated successfully" if not created else "PhoneNumber created successfully"
                return SuccessMessage(success=True, id=phone_number.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding phone number", errors=[str(e)])


class PhoneNumberDelete(graphene.Mutation):
    class Arguments:
        id = PhoneNumberInputType.id
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                phone_number = PhoneNumber.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="PhoneNumber deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting phone number", errors=[str(e)])



class Mutation(graphene.ObjectType):
    industry_update_or_create = IndustryUpdateOrCreate.Field()
    industry_delete = IndustryDelete.Field()
    
    enterprise_update_or_create = EnterpriseUpdateOrCreate.Field()
    enterprise_delete = EnterpriseDelete.Field()
    
    branch_type_update_or_create = BranchTypeUpdateOrCreate.Field()
    branch_type_delete = BranchTypeDelete.Field()
    
    branch_update_or_create = BranchUpdateOrCreate.Field()
    branch_delete = BranchDelete.Field()
    
    phone_numberupdate_or_create = PhoneNumberUpdateOrCreate.Field()
    phone_numberdelete = PhoneNumberDelete.Field()