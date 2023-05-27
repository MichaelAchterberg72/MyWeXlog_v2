import django_filters

from ..models import (
    FeedBack,
    FeedBackActions,
    Notices,
    NoticeRead                      
)


class FeedbackFilter(django_filters.FilterSet):
    talent__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='talent')
    # talent__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='talent')
    talent__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='talent')

    date_captured__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='date_captured')
    date_captured__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='date_captured')
    date_captured__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='date_captured')
    date_captured__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='date_captured')

    type__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='type')
    
    details__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='details')
    details__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='details')
    details__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='details')

    optional_1__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='optional_1')
    optional_1__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='optional_1')
    optional_1__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='optional_1')

    optional_2__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='optional_2')
    optional_2__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='optional_2')
    optional_2__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='optional_2')

    slug__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='slug')
    slug__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='slug')
    slug__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='slug')
    
    order_by = django_filters.OrderingFilter(
            fields=(
                "talent",
                "date_captured",
                "type",
                "details",
                "optional_1",
                "optional_2",
                "responded",
                "slug",
            )
        )
    
    class Meta:
        model = FeedBack
        fields = [
            "talent",
            "date_captured",
            "type",
            "details",
            "optional_1",
            "optional_2",
            "responded",
            "slug",
    ]