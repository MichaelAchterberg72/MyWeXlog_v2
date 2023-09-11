import django_filters

from ..models import (
    CorporateHR
)


class CorporateHRFilter(django_filters.FilterSet):
    companybranch__name__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='companybranch__name')
    companybranch__name__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='companybranch__name')
    companybranch__name__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='companybranch__name')
    
    company__ename__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='company__ename')
    company__ename__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='company__ename')
    company__ename__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='company__ename')

    subscription__iexact = django_filters.ChoiceFilter(lookup_expr='iexact', field_name='subscription')

    date_created__lt = django_filters.DateFilter(lookup_expr='lt', field_name='date_created')
    date_created__lte = django_filters.DateFilter(lookup_expr='lte', field_name='date_created')
    date_created__gt = django_filters.DateFilter(lookup_expr='gt', field_name='date_created')
    date_created__gte = django_filters.DateFilter(lookup_expr='gte', field_name='date_created')
    
    expiry__lt = django_filters.DateFilter(lookup_expr='lt', field_name='expiry')
    expiry__lte = django_filters.DateFilter(lookup_expr='lte', field_name='expiry')
    expiry__gt = django_filters.DateFilter(lookup_expr='gt', field_name='expiry')
    expiry__gte = django_filters.DateFilter(lookup_expr='gte', field_name='expiry')
    
    slug__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='slug')

    order_by = django_filters.OrderingFilter(
            fields=(
                'companybranch',
                'company',
                'subscription',
                'date_created',
                'expiry',
                'slug',
            )
        )
    
    class Meta:
        model = CorporateHR
        fields = [
            'companybranch',
            'company',
            'subscription',
            'date_created',
            'expiry',
            'slug',
        ]