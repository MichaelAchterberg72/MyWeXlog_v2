import graphene
from graphene_django.filter import DjangoFilterConnectionField
from ..models import (
    Author,
    Publisher,
    Genre,
    BookList,
    Format,
    ReadBy
)
from .output_types import AuthorOutputType
from .filters import AuthorFilter


class Query(graphene.ObjectType):
    author = graphene.Field(AuthorOutputType, id=graphene.ID())
    authors = DjangoFilterConnectionField(
            AuthorOutputType, 
            filterset_class=AuthorFilter
        )

    def resolve_author(self, info, id):
        try:
            return Author.objects.get(pk=id)
        except Author.DoesNotExist:
            return None