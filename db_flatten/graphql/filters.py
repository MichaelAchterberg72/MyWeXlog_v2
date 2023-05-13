import django_filters

from ..models import PhoneNumberType, SkillTag, LanguageList


class PhoneNumberTypeFilter(django_filters.FilterSet):
    type__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='type')
    type__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='type')
    type__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='type')
    
    class Meta:
        model = PhoneNumberType
        fields = [
            'type'
        ]


class SkillTagFilter(django_filters.FilterSet):
    skill__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='skill')
    skill__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='skill')
    skill__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='skill')
    
    code__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='code')
    code__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='code')
    code__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='code')
    
    class Meta:
        model = SkillTag
        fields = [
            'skill',
            'code'
        ]
        order_by = django_filters.OrderingFilter(
            fields=(
                ('skill', 'code'),
            )
        )


class LanguageListFilter(django_filters.FilterSet):
    language__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='language')
    language__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='language')
    language__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='language')
    
    class Meta:
        model = LanguageList
        fields = [
            'language'
        ]
        order_by = django_filters.OrderingFilter(
            fields=(
                ('language')
            )
        )