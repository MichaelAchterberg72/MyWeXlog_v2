import django_filters

from ..models import (
    FeedBack,
    FeedBackActions,
    Notices,
    NoticeRead                      
)


class FeedbackFilter(django_filters.FilterSet):
    # talent__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='talent')
    # # talent__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='talent')
    # talent__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='talent')

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
            "date_captured",
            "type",
            "details",
            "optional_1",
            "optional_2",
            "responded",
            "slug",
    ]
        
        
class FeedBackActionsFilter(django_filters.FilterSet):
    review_by__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='review_by')
    review_by__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='review_by')
    review_by__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='review_by')

    date_reviewed__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='date_reviewed')
    date_reviewed__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='date_reviewed')
    date_reviewed__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='date_reviewed')
    date_reviewed__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='date_reviewed')

    actions__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='actions')
    
    order_by = django_filters.OrderingFilter(
            fields=(
                "review_by",
                "date_reviewed",
                "actions"
            )
        )
    
    class Meta:
        model = FeedBackActions
        fields = [
            "review_by",
            "date_reviewed",
            "actions"
    ]
        
        
class NoticesFilter(django_filters.FilterSet):
    notice_date__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='notice_date')
    notice_date__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='notice_date')
    notice_date__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='notice_date')
    notice_date__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='notice_date')
    
    subject__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='subject')
    subject__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='subject')
    subject__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='subject')

    notice__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='notice')
    notice__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='notice')

    slug__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='slug')
    
    order_by = django_filters.OrderingFilter(
            fields=(
                "notice_date",
                "subject",
                "notice",
                "slug"
            )
        )
    
    class Meta:
        model = Notices
        fields = [
            "notice_date",
            "subject",
            "notice",
            "slug"
    ]
        
        
class NoticesReadFilter(django_filters.FilterSet):
    date_read__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='date_read')
    date_read__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='date_read')
    date_read__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='date_read')
    date_read__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='date_read')

    notice_read__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='notice_read')
    
    order_by = django_filters.OrderingFilter(
            fields=(
                "date_read",
                "notice_read"
            )
        )
    
    class Meta:
        model = NoticeRead
        fields = [
            "date_read",
            "notice_read"
    ]