import graphene
from graphene_django.filter import DjangoFilterConnectionField
from ..models import (
    Industry,
    Enterprise,
    BranchType,
    Branch,
    PhoneNumber
)
from .output_types import (
    IndustryOutputType,
    EnterpriseOutputType,
    BranchOutputType,
    BranchTypeOutputType,
    PhoneNumberOutputType
)
from .filters import (
    IndustryFilter,
    EnterpriseFilter,
    BranchTypeFilter,
    BranchFilter,
    PhoneNumberFilter
)

class Query(graphene.ObjectType):
    industry = graphene.Field(IndustryOutputType, id=graphene.ID())
    industrys = DjangoFilterConnectionField(
            IndustryOutputType, 
            filterset_class=IndustryFilter
        )
    enterprise = graphene.Field(EnterpriseOutputType, id=graphene.ID())
    enterprises = DjangoFilterConnectionField(
            EnterpriseOutputType, 
            filterset_class=EnterpriseFilter
        )
    branch_type = graphene.Field(BranchTypeOutputType, id=graphene.ID())
    branch_types = DjangoFilterConnectionField(
            BranchTypeOutputType, 
            filterset_class=BranchTypeFilter
        )
    branch = graphene.Field(BranchOutputType, id=graphene.ID())
    branchs = DjangoFilterConnectionField(
            BranchOutputType, 
            filterset_class=BranchFilter
        )
    phone_number = graphene.Field(PhoneNumberOutputType, id=graphene.ID())
    phone_numbers = DjangoFilterConnectionField(
            PhoneNumberOutputType, 
            filterset_class=PhoneNumberFilter
        )
    
    def resolve_phone_number(self, info, id):
        try:
            return PhoneNumber.objects.get(pk=id)
        except PhoneNumber.DoesNotExist:
            return None
        
    def resolve_branch(self, info, id):
        try:
            return Branch.objects.get(pk=id)
        except Branch.DoesNotExist:
            return None
        
    def resolve_branch_type(self, info, id):
        try:
            return BranchType.objects.get(pk=id)
        except BranchType.DoesNotExist:
            return None
        
    def resolve_enterprise(self, info, id):
        try:
            return Enterprise.objects.get(pk=id)
        except Enterprise.DoesNotExist:
            return None
        
    def resolve_industry(self, info, id):
        try:
            return Industry.objects.get(pk=id)
        except Industry.DoesNotExist:
            return None