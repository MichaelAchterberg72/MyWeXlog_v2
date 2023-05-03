import django_filters

from ..models import (
    Industry,
    Enterprise,
    BranchType,
    Branch,
    PhoneNumber
)


class IndustryFilter(django_filters.FilterSet):
    class Meta:
        model = Industry
        fields = [
            'industry'
        ]
        order_by = '__all__'
        
        
class EnterpriseFilter(django_filters.FilterSet):
    class Meta:
        model = Enterprise
        fields = [
            'ename',
            'slug',
            'description',
            'website',
            'filter_class',
            'rate_1',
            'rate_2',
            'rate_3',
            'rate_4',
            'rate_count',
        ]
        order_by = '__all__'
        
        
class BranchTypeFilter(django_filters.FilterSet):
    class Meta:
        model = BranchType
        fields = [
            'type'
        ]
        order_by = '__all__'
        
        
class BranchFilter(django_filters.FilterSet):
    class Meta:
        model = Branch
        fields = '__all__'
        order_by = '__all__'
        
        
class PhoneNumberFilter(django_filters.FilterSet):
    class Meta:
        model = PhoneNumber
        fields = '__all__'
        order_by = '__all__'