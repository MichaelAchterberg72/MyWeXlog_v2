import django_filters

from ..models import (
    Industry,
    Enterprise,
    BranchType,
    Branch,
    PhoneNumber
)


class IndustryFilter(django_filters.FilterSet):
    industry__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='industry')
    industry__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='industry')
    industry__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='industry')
    
    class Meta:
        model = Industry
        fields = [
            'industry'
        ]
        order_by = '__all__'
        
        
class EnterpriseFilter(django_filters.FilterSet):
    ename__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='ename')
    ename__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='ename')
    ename__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='ename')
    
    description__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='description')
    
    website__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='website')
    website__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='website')
    website__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='website')
    
    rate_1__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='rate_1')
    rate_1__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='rate_1')
    rate_1__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='rate_1')
    rate_1__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='rate_1')
    
    rate_2__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='rate_2')
    rate_2__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='rate_2')
    rate_2__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='rate_2')
    rate_2__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='rate_2')
    
    rate_3__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='rate_3')
    rate_3__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='rate_3')
    rate_3__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='rate_3')
    rate_3__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='rate_3')
    
    rate_4__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='rate_4')
    rate_4__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='rate_4')
    rate_4__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='rate_4')
    rate_4__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='rate_4')
    
    rate_count__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='rate_count')
    rate_count__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='rate_count')
    rate_count__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='rate_count')
    rate_count__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='rate_count')
    
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
    type__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='type')
    type__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='type')
    type__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='type')
    
    class Meta:
        model = BranchType
        fields = [
            'type'
        ]
        order_by = '__all__'
        
        
class BranchFilter(django_filters.FilterSet):
    name__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='name')
    name__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='name')
    name__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='name')
    
    phy_address_line1__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='phy_address_line1')
    phy_address_line1__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='phy_address_line1')
    phy_address_line1__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='phy_address_line1')
    
    phy_address_line2__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='phy_address_line2')
    phy_address_line2__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='phy_address_line2')
    phy_address_line2__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='phy_address_line2')
    
    code__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='code')
    code__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='code')
    code__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='name')
    
    rate_1__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='rate_1')
    rate_1__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='rate_1')
    rate_1__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='rate_1')
    rate_1__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='rate_1')
    
    rate_2__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='rate_2')
    rate_2__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='rate_2')
    rate_2__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='rate_2')
    rate_2__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='rate_2')
    
    rate_3__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='rate_3')
    rate_3__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='rate_3')
    rate_3__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='rate_3')
    rate_3__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='rate_3')
    
    rate_4__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='rate_4')
    rate_4__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='rate_4')
    rate_4__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='rate_4')
    rate_4__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='rate_4')
    
    rate_count__lt = django_filters.NumberFilter(lookup_expr='lt', field_name='rate_count')
    rate_count__lte = django_filters.NumberFilter(lookup_expr='lte', field_name='rate_count')
    rate_count__gt = django_filters.NumberFilter(lookup_expr='gt', field_name='rate_count')
    rate_count__gte = django_filters.NumberFilter(lookup_expr='gte', field_name='rate_count')

    class Meta:
        model = Branch
        fields = '__all__'
        order_by = '__all__'
        
        
class PhoneNumberFilter(django_filters.FilterSet):
    phone = django_filters.CharFilter(field_name='phone', lookup_expr='exact')
    phone_contains = django_filters.CharFilter(field_name='phone', lookup_expr='icontains')
    
    existing = django_filters.BooleanFilter(field_name='existing')
    
    class Meta:
        model = PhoneNumber
        fields = '__all__'
        order_by = '__all__'