import graphene
from django.db import transaction

from utils.graphql.output_types import SuccessMessage, FailureMessage, SuccessMutationResult

from .input_types import (
    CorporateHRInputType
)

from ..models import (
    CorporateHR,
)


class CorporateHRpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = CorporateHRInputType.id
        companybranch = CorporateHRInputType.companybranch
        company = CorporateHRInputType.company
        subscription = CorporateHRInputType.subscription
        date_created = CorporateHRInputType.date_created
        expiry = CorporateHRInputType.expiry
        slug = CorporateHRInputType.slug
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        errors = []
        if errors:
            return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
        
        try:
            with transaction.atomic():
                corporatehr_id = kwargs.pop('slug', None)
                corporatehr = CorporateHR.update_or_create_object(id=corporatehr_id, **kwargs)
                message = "CorporateHR updated successfully" if corporatehr_id else "CorporateHR created successfully"
                return SuccessMessage(success=True, id=corporatehr.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding corporatehr", errors=[str(e)])


class CorporateHRDelete(graphene.Mutation):
    class Arguments:
        id = CorporateHRInputType.id
        
    Output = SuccessMutationResult
    
    @classmethod
    def mutate(cls, root, info, **kwargs):
        errors = []
        if errors:
            return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
        
        try:
            with transaction.atomic():
                corporatehr = CorporateHR.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="CorporateHR deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting corporatehr", errors=[str(e)])


class Mutation(graphene.ObjectType):
    corporatehr_update_or_create = CorporateHRpdateOrCreate.Field()
    corporatehr_delete = CorporateHRDelete.Field()