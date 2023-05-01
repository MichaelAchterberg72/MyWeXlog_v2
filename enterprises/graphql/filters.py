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
        fields = '__all__'
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