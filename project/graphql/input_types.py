import graphene

from users.graphql.input_types import UserInputType
from locations.graphql.input_types import CurrencyInputType
from db_flatten.graphql.input_types import SkillTagInputType
from enterprises.graphql.input_types import (
    EnterpriseInputType, 
    BranchInputType, 
    IndustryInputType
)
from locations.graphql.input_types import (
    CountryFieldInputType, 
    RegionInputType,
    CityInputType,
)


class ProjectDataInputType(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()
    company = graphene.Argument(EnterpriseInputType)
    companybranch = graphene.Argument(BranchInputType)
    description = graphene.String()
    country = CountryFieldInputType(required=True)
    region = graphene.Argument(RegionInputType)
    city = graphene.Argument(CityInputType)
    industry = graphene.Argument(IndustryInputType)
    slug = graphene.String()
    
    
class ProjectPersonalDetailsInputType(graphene.InputObjectType):
    id = graphene.ID()
    talent = graphene.Argument(UserInputType)
    project = graphene.Argument(ProjectDataInputType)
    company = graphene.Argument(EnterpriseInputType)
    companybranch = graphene.Argument(BranchInputType)
    description = graphene.String()
    slug = graphene.String()
    
    
class ProjectPersonalDetailsTaskInputType(graphene.InputObjectType):
    id = graphene.ID()
    talent = graphene.Argument(UserInputType)
    ppd = graphene.Argument(ProjectPersonalDetailsInputType)
    company = graphene.Argument(BranchInputType)
    client = graphene.Argument(BranchInputType)
    task = graphene.String()
    description = graphene.String()
    skills = graphene.Argument(SkillTagInputType)
    date_create = graphene.Date()
    date_start = graphene.Date()
    date_end = graphene.Date()
    task_status = graphene.Int()
    date_due = graphene.DateTime()
    date_complete = graphene.DateTime()
    slug = graphene.String()
    
    
class ProjectTaskBillingInputType(graphene.InputObjectType):
    id = graphene.ID()
    talent = graphene.Argument(UserInputType)
    ppdt = graphene.Argument(ProjectPersonalDetailsTaskInputType)
    billing_rate = graphene.Decimal()
    currency = graphene.Argument(CurrencyInputType)
    rate_unit = graphene.String()
    date_start = graphene.Date()
    date_end = graphene.Date()
    current = graphene.Boolean()