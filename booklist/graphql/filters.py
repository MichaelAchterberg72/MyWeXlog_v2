import graphene
import django_filters

from utils.graphql.filters import MultipleLookupFilter, multiple_char_lookup_filter

from ..models import (
    Author,
    Publisher,
    Genre,
    BookList,
    Format,
    ReadBy
)


class AuthorFilter(django_filters.FilterSet):
    # name = MultipleLookupFilter(lookups=['icontains', 'iexact'], field_name='name')
    name__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='name')
    name__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='name')
    name__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='name')
    # name_Iexact = django_filters.CharFilter(method=multiple_char_lookup_filter)
    order_by = django_filters.OrderingFilter(
            fields=(
                ('name'),
            )
        )
    
    class Meta:
        model = Author
        fields = ['name']
        


class PublisherFilter(django_filters.FilterSet):
    publisher__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='publisher')
    publisher__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='publisher')
    publisher__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='publisher')
    
    link__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='link')
    link__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='link')
    link__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='link')
    
    order_by = django_filters.OrderingFilter(
            fields=(
                'publisher', 'link'
            )
        )
     
    class Meta:
        model = Publisher
        fields = ['publisher', 'link']


class GenreFilter(django_filters.FilterSet):
    name__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='name')
    name__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='name')
    name__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='name')
    
    order_by = django_filters.OrderingFilter(
            fields=(
                ('name'),
            )
        )
    
    class Meta:
        model = Genre
        fields = ['name']


class BookListFilter(django_filters.FilterSet):
    title__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='title')
    title__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='title')
    title__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='title')
    
    link__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='link')
    link__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='link')
    link__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='link')
    
    order_by = django_filters.OrderingFilter(
        fields=(
            'title',
            'type',
            'publisher__publisher',
            'link',
            'author__name',
            'tag__skill',
            'tag__code',
            'genre__name',
        ),
    )
    
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
    format__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='format')
    format__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='format')
    format__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='format')
    
    order_by = django_filters.OrderingFilter(
            fields=(
                ('format'),
            )
        )
    
    class Meta:
        model = Format
        fields = ['format']
        

class ReadByFilter(django_filters.FilterSet):
    date_captured__lt = django_filters.DateFilter(lookup_expr='lt', field_name='date_captured')
    date_captured__lte = django_filters.DateFilter(lookup_expr='lte', field_name='date_captured')
    date_captured__gt = django_filters.DateFilter(lookup_expr='gt', field_name='date_captured')
    date_captured__gte = django_filters.DateFilter(lookup_expr='gte', field_name='date_captured')
    
    review__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='review')
    
    order_by = django_filters.OrderingFilter(
        fields=(
                'talent__alias',
                'book__title',
                'book__type',
                'book__author__name',
                'type__format',
                'date',
                'review'
            ),
        )
     
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