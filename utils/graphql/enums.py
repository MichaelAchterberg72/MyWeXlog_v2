import graphene
from django_countries import countries

class CountryEnum(graphene.Enum):
    class Meta:
        description = "List of countries"

    @classmethod
    def from_enum_value(cls, enum_value):
        return enum_value

    @classmethod
    def description(cls, enum_value):
        return countries[enum_value]

    @classmethod
    def get_names(cls):
        return countries