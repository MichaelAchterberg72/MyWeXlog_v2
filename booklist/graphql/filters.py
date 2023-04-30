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