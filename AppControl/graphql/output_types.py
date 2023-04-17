import graphene
from graphene_django import DjangoObjectType

from ..models import CorporateHR


class CorporateHROutputType(DjangoObjectType):
    class Meta:
        model = CorporateHR
        fields = '__all__'