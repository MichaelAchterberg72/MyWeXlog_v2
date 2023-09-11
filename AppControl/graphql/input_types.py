import graphene
from .enums import (
    SubChoices
)

from enterprises.graphql.input_types import (
    BranchInputType, 
    EnterpriseInputType,
)


class CorporateHRInputType(graphene.InputObjectType):
    id = graphene.ID()
    companybranch = graphene.ID(BranchInputType)
    company = graphene.Argument(EnterpriseInputType)
    subscription = SubChoices()
    date_created = graphene.Date()
    expiry = graphene.Date()
    slug = graphene.String()