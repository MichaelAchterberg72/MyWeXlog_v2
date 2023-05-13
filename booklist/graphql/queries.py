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
from .output_types import (
    AuthorOutputType,
    PublisherOutputType,
    GenreOutputType,
    BookListOutputType,
    FormatOutputType,
    ReadByOutputType
)
from .filters import (
    AuthorFilter,
    PublisherFilter,
    GenreFilter,
    BookListFilter,
    FormatFilter,
    ReadByFilter
)


class Query(graphene.ObjectType):
    author = graphene.Field(AuthorOutputType, id=graphene.ID())
    authors = DjangoFilterConnectionField(
            AuthorOutputType, 
            filterset_class=AuthorFilter,
        )
    publisher = graphene.Field(PublisherOutputType, id=graphene.ID())
    publishers = DjangoFilterConnectionField(
            PublisherOutputType, 
            filterset_class=PublisherFilter
        )
    genre = graphene.Field(GenreOutputType, id=graphene.ID())
    genres = DjangoFilterConnectionField(
            GenreOutputType, 
            filterset_class=GenreFilter
        )
    booklist = graphene.Field(BookListOutputType, slug=graphene.String())
    booklists = DjangoFilterConnectionField(
            BookListOutputType, 
            filterset_class=BookListFilter
        )
    format = graphene.Field(FormatOutputType, slug=graphene.String())
    formats = DjangoFilterConnectionField(
            FormatOutputType, 
            filterset_class=FormatFilter
        )
    readby = graphene.Field(ReadByOutputType, slug=graphene.String())
    readbys = DjangoFilterConnectionField(
            ReadByOutputType, 
            filterset_class=ReadByFilter
        )

    def resolve_author(self, info, id):
        try:
            return Author.objects.get(pk=id)
        except Author.DoesNotExist:
            return None

    def resolve_publisher(self, info, id):
        try:
            return Publisher.objects.get(pk=id)
        except Publisher.DoesNotExist:
            return None

    def resolve_genre(self, info, id):
        try:
            return Genre.objects.get(pk=id)
        except Genre.DoesNotExist:
            return None

    def resolve_booklist(self, info, id):
        try:
            return BookList.objects.get(pk=id)
        except BookList.DoesNotExist:
            return None

    def resolve_format(self, info, id):
        try:
            return Format.objects.get(pk=id)
        except Format.DoesNotExist:
            return None

    def resolve_readby(self, info, id):
        try:
            return ReadBy.objects.get(pk=id)
        except ReadBy.DoesNotExist:
            return None