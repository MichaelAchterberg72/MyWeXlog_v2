import graphene
import django_filters

from ..models import (
    Author,
    Publisher,
    Genre,
    BookList,
    Format,
    ReadBy
)


class AuthorFilter(django_filters.FilterSet):
    class Meta:
        model = Author
        fields = ['name']


class PublisherFilter(django_filters.FilterSet):
    class Meta:
        model = Publisher
        fields = ['publisher', 'link']


class GenreFilter(django_filters.FilterSet):
    class Meta:
        model = Genre
        fields = ['name']


class BookListFilter(django_filters.FilterSet):
    class Meta:
        model = BookList
        fields = [
            'title',
            'type',
            'publisher__publisher',
            'link',
            'author__name',
            'tag__skill',
            'tag__code',
            'genre__name'
        ]


class FormatFilter(django_filters.FilterSet):
    class Meta:
        model = Format
        fields = ['name']
        

class ReadByFilter(django_filters.FilterSet):
    class Meta:
        model = ReadBy
        fields = [
            'talent__alias',
            'book__title',
            'book__type',
            'book__author__name',
            'type__tag__skill',
            'type__tag__code',
            'date',
            'review'
        ]