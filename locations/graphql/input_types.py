import graphene
from django_countries import countries

class CountryFieldInputType(graphene.InputObjectType):
    country_code = graphene.String(required=True)

    @staticmethod
    def is_valid_country_code(country_code):
        return country_code in dict(countries)

    @staticmethod
    def get_country_code(value):
        country_code = value.get('country_code')
        if CountryFieldInputType.is_valid_country_code(country_code):
            return country_code
        else:
            raise ValueError(f"Invalid country code: {country_code}")
        
        
class RegionInputType(graphene.InputObjectType):
    id = graphene.ID()
    country = CountryFieldInputType()
    region = graphene.String()
    
    
class CityInputType(graphene.InputObjectType):
    id = graphene.ID()
    region = graphene.Argument(RegionInputType)
    city = graphene.String()
    
    
class SuburbInputType(graphene.InputObjectType):
    id = graphene.ID()
    city = graphene.Argument(CityInputType)
    suburb = graphene.String()
    
    
class CurrencyInputType(graphene.InputObjectType):
    id = graphene.ID()
    country = CountryFieldInputType(required=True)
    currency_name = graphene.String()
    currency_abv = graphene.String()