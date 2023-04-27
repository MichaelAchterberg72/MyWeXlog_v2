import graphene
from django_countries import countries

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