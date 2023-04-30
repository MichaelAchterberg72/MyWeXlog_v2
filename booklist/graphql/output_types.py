import graphene
from graphene_django import DjangoObjectType

from ..models import (
    Author,
    Publisher,
    Genre,
    BookList,
    Format,
    ReadBy
)


class AuthorOutputType(DjangoObjectType):
    class Meta:
        model = Author
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains', 'startswith'],
        }
        ordering = ['name']


class PublisherOutputType(DjangoObjectType):
    class Meta:
        model = Publisher
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains', 'istartswith'],
            'link': ['exact'],
        }
        ordering = ['publisher', 'link']
        
        
class GenreOutputType(DjangoObjectType):
    class Meta:
        model = Genre
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains', 'istartswith'],
        }
        ordering = ['name']
        
        
class BookListOutputType(DjangoObjectType):
    class Meta:
        model = BookList
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains', 'istartswith'],
            'type': ['exact', 'icontains', 'istartswith'],
            'publisher__publisher': ['exact', 'icontains', 'istartswith'],
            'link': ['exact', 'icontains'],
            'author__name': ['exact', 'icontains', 'istartswith'],
            'tag__skill': ['exact', 'icontains', 'istartswith'],
            'genre__name': ['exact', 'icontains', 'istartswith'],
            'slug': ['exact'],
        }
        ordering = [
            'name', 
            'type', 
            'publisher__publisher', 
            'link', 
            'author__name', 
            'tag__skill',
            'genre__name'
        ]
        
        
class FormatOutputType(DjangoObjectType):
    class Meta:
        model = Format
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'format': ['exact', 'icontains', 'istartswith'],
        }
        ordering = [
            'format'
        ]
        
        
class ReadByOutputType(DjangoObjectType):
    class Meta:
        model = ReadBy
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'talent__alias': ['exact', 'icontains', 'istartswith'],
            'book__title': ['iexact', 'icontains', 'istartswith'],
            'type': ['iexact', 'icontains', 'istartswith'],
            'date': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'review': ['icontains'],
        }
        ordering = [
            'talent__alias'
            'book__title'
            'type',
            'date',
            '-date',
        ]