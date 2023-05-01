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
        order_by = '__all__'


class PublisherFilter(django_filters.FilterSet):
    class Meta:
        model = Publisher
        fields = ['publisher', 'link']
        order_by = '__all__'


class GenreFilter(django_filters.FilterSet):
    class Meta:
        model = Genre
        fields = ['name']
        order_by = '__all__'


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
        order_by = '__all__'


class FormatFilter(django_filters.FilterSet):
    class Meta:
        model = Format
        fields = ['format']
        order_by = '__all__'
        

class ReadByFilter(django_filters.FilterSet):
    class Meta:
        model = ReadBy
        fields = [
            'talent__alias',
            'book__title',
            'book__type',
            'book__author__name',
            'type__format',
            'date',
            'review'
        ]
        order_by = '__all__'