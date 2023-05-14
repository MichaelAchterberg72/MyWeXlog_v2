import graphene
from graphene_file_upload.scalars import Upload

from .enums import EnterpriseFCEnum, BranchSizeEnum

from locations.graphql.input_types import (
    CountryFieldInputType, 
    RegionInputType,
    CityInputType,
    SuburbInputType
)
from db_flatten.graphql.input_types import PhoneNumberTypeInputType


class IndustryInputType(graphene.InputObjectType):
    id = graphene.ID()
    industry = graphene.String()
    
    
class EnterpriseInputType(graphene.InputObjectType):
    id = graphene.ID()
    ename = graphene.String()
    slug = graphene.String()
    description = graphene.String()
    logo = Upload()
    website = graphene.String()
    filter_class = EnterpriseFCEnum()
    rate_1 = graphene.Float()
    rate_2 = graphene.Float()
    rate_3 = graphene.Float()
    rate_4 = graphene.Float()
    rate_count = graphene.Int()


class BranchTypeInputType(graphene.InputObjectType):
    id = graphene.ID()
    type = graphene.String()
    
    
class BranchInputType(graphene.InputObjectType):
    id = graphene.ID()
    company = graphene.Argument(EnterpriseInputType)
    name = graphene.String()
    type = graphene.Argument(BranchTypeInputType)
    size = BranchSizeEnum()
    phy_address_line1 = graphene.String()
    phy_address_line2 = graphene.String()
    country = CountryFieldInputType(required=True)
    region = graphene.Argument(RegionInputType)
    city = graphene.Argument(CityInputType)
    suburb = graphene.Argument(SuburbInputType)
    code = graphene.String()
    industry = graphene.List(IndustryInputType)
    slug = graphene.String()
    rate_1 = graphene.Float()
    rate_2 = graphene.Float()
    rate_3 = graphene.Float()
    rate_4 = graphene.Float()
    rate_count = graphene.Int()
    
    
class PhoneNumberInputType(graphene.InputObjectType):
    id = graphene.ID()
    branch = graphene.Argument(BranchInputType)
    phone = graphene.String()
    type = graphene.Argument(PhoneNumberTypeInputType)
    existing = graphene.Boolean()