import graphene
from django_countries import countries
from graphene_django import DjangoObjectType

from ..models import Region, City, Suburb, Currency


class CountryFieldType(graphene.Scalar):
    @staticmethod
    def serialize(country_code):
        if country_code:
            return countries.name(country_code)
        return None

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return countries.alpha2(node.value)

    @staticmethod
    def parse_value(value):
        return countries.alpha2(value)
    
    
class RegionOutputType(DjangoObjectType):
    class Meta:
        model = Region
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'country',
            'region'
        }
        ordering = [
            'country',
            '-country',
            'region'
        ]
        
        
class CityOutputType(DjangoObjectType):
    class Meta:
        model = City
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        flter_fields = [
            'region',
            'city'
        ]
        ordering = [
            'region__region',
            'city'
        ]
        
        
class SuburbOutputType(DjangoObjectType):
    class Meta:
        model = Suburb
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = [
            'city',
            'suburb'
        ]
        ordering = [
            'city__city',
            'suburb'
        ]
        
        
class CurrencyOutputType(DjangoObjectType):
    class Meta:
        model = Currency
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = [
            'country',
            'currency_name',
            'currency_abv'
        ]
        ordering = [
            'country__country',
            'currency_name',
            'currency_abv'
        ]