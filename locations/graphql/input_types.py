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