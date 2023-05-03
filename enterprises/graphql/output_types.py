import graphene
from graphene_django import DjangoObjectType

from ..models import (
    Industry,
    Enterprise,
    BranchType,
    Branch,
    PhoneNumber
)


class IndustryOutputType(DjangoObjectType):
    class Meta:
        model = Industry
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'industry': ['exact', 'icontains', 'istartswith']
        }


class EnterpriseOutputType(DjangoObjectType):
    class Meta:
        model = Enterprise
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enums = True
        filter_fields = {
            'ename': ['exact', 'icontains', 'istartswith'],
            'slug': ['exact'],
            'description': ['icontains', 'istartswith'],
            'website': ['exact', 'icontains', 'istartswith'],
            'filter_class': ['exact'],
            'rate_1': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rate_2': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rate_3': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rate_4': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rate_count': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
        
        
class BranchTypeOutputType(DjangoObjectType):
    class Meta:
        model = BranchType
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'type': ['exact', 'icontains', 'istartswith']
        }
        
        
class BranchOutputType(DjangoObjectType):
    class Meta:
        model = Branch
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enums = True
        filter_fields = {
            'company__ename': ['exact', 'icontains', 'istartswith'],
            'name': ['exact', 'icontains', 'istartswith'],
            'type__type': ['exact', 'icontains', 'istartswith'],
            'size': ['exact', 'icontains', 'istartswith'],
            'phy_address_line1': ['exact', 'icontains', 'istartswith'],
            'phy_address_line2': ['exact', 'icontains', 'istartswith'],
            'country': ['exact', 'icontains', 'istartswith'],
            'region__region': ['exact', 'icontains', 'istartswith'],
            'city__city': ['exact', 'icontains', 'istartswith'],
            'suburb__suburb': ['exact', 'icontains', 'istartswith'],
            'code': ['exact', 'icontains', 'istartswith'],
            'industry__industry': ['exact', 'icontains', 'istartswith'],
            'slug': ['exact'],
            'rate_1': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rate_2': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rate_3': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rate_4': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rate_count': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
        
        
class PhoneNumberOutputType(DjangoObjectType):
    class Meta:
        model = PhoneNumber
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'branch__name': ['exact', 'icontains', 'istartswith'],
            'phone': ['exact', 'icontains', 'istartswith'],
            'type__type': ['exact', 'icontains', 'istartswith'],
            'existing': ['exact'],
        }