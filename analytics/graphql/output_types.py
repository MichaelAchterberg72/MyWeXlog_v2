import graphene
from graphene_django import DjangoObjectType

from ..models import ObjectViewed


class ObjectViewedOutputType(DjangoObjectType):
    class Meta:
        model = ObjectViewed
        fields = '__all__'