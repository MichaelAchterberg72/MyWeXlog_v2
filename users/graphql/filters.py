import django_filters

from ..models import CustomUser


class UserFilter(django_filters.FilterSet):
    username__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='username')
    username__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='username')
    username__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='username')
    
    first_name__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='first_name')
    first_name__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='first_name')
    first_name__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='first_name')
    
    last_name__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='last_name')
    last_name__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='last_name')
    last_name__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='last_name')
    
    email__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='email')
    email__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='email')
    email__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='email')
    
    date_joined__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='date_joined')
    date_joined__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='date_joined')
    date_joined__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='date_joined')
    date_joined__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='date_joined')
    
    alias__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='alias')
    alias__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='alias')
    alias__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='alias')
    
    display_text__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='display_text')
    display_text__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='display_text')
    display_text__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='display_text')
    
    public_profile_name__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='public_profile_name')
    public_profile_name__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='public_profile_name')
    public_profile_name__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='public_profile_name')
    
    subscription__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='subscription')
    
    permission__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='permission')
    
    role__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='role')
    
    registered_date__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='registered_date')
    registered_date__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='registered_date')
    registered_date__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='registered_date')
    registered_date__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='registered_date')
    
    paid_date__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='paid_date')
    paid_date__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='paid_date')
    paid_date__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='paid_date')
    paid_date__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='paid_date')
    
    paid_type__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='paid_type')
    
    invite_code__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='invite_code')
    invite_code__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='invite_code')
    invite_code__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='invite_code')
    
    alphanum__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='alphanum')
    alphanum__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='alphanum')
    alphanum__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='alphanum')
    
    order_by = django_filters.OrderingFilter(
            fields=(
                "username",
                "first_name",
                "last_name",
                "email",
                "is_staff",
                "is_active",
                "date_joined",
                "alias",
                "display_text",
                "public_profile_name",
                "permit_viewing_of_profile_as_reference",
                "subscription",
                "permission",
                "role",
                "registered_date",
                "paid",
                "free_month",
                "paid_date",
                "paid_type",
                "invite_code",
                "alphanum",
            )
        )
    
    class Meta:
        model = CustomUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "date_joined",
            "alias",
            "display_text",
            "public_profile_name",
            "permit_viewing_of_profile_as_reference",
            "subscription",
            "permission",
            "role",
            "registered_date",
            "paid",
            "free_month",
            "paid_date",
            "paid_type",
            "invite_code",
            "alphanum",
    ]