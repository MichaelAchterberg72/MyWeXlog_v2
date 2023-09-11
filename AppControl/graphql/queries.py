import graphene
from graphene_django.filter import DjangoFilterConnectionField
from ..models import (
    CorporateHR,
)
from .output_types import (
    CorporateHROutputType,
)
from .filters import (
    CorporateHRFilter,
)

class Query(graphene.ObjectType):
    corporatehr = graphene.Field(CorporateHROutputType, id=graphene.ID())
    corporatehrs = DjangoFilterConnectionField(
            CorporateHROutputType, 
            filterset_class=CorporateHRFilter
        )
    
    def resolve_corporatehr(self, info, id):
        try:
            return CorporateHR.objects.get(pk=id)
        except CorporateHR.DoesNotExist:
            return None
        
    def resolve_corporatehrs(self, info, **kwargs):
        return CorporateHRFilter(kwargs).qs