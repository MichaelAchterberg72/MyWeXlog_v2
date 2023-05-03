import graphene
from graphene_django.filter import DjangoFilterConnectionField
from ..models import (
    Industry,
    Enterprise,
    BranchType,
    Branch,
    PhoneNumber
)
from .output_types import (
    IndustryOutputType
)
from .filters import IndustryFilter


class Query(graphene.ObjectType):
    industry = graphene.Field(IndustryOutputType, id=graphene.ID())
    industrys = DjangoFilterConnectionField(
            IndustryOutputType, 
            filterset_class=IndustryFilter
        )
    
    def resolve_industry(self, info, id):
        try:
            return Industry.objects.get(pk=id)
        except Industry.DoesNotExist:
            return None