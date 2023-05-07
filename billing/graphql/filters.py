import django_filters

from utils.graphql.filters import MultipleLookupFilter

from ..models import Timesheet


class TimesheetFilter(django_filters.FilterSet):
     # name = MultipleLookupFilter(lookups=['icontains', 'iexact'], field_name='name')
    name__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='name')
    name__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='name')
    name__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='name')
    
    date_captured__lt = django_filters.DateFilter(lookup_expr='lt', field_name='date_captured')
    date_captured__lte = django_filters.DateFilter(lookup_expr='lte', field_name='date_captured')
    date_captured__gt = django_filters.DateFilter(lookup_expr='gt', field_name='date_captured')
    date_captured__gte = django_filters.DateFilter(lookup_expr='gte', field_name='date_captured')
    
    date__lt = django_filters.DateFilter(lookup_expr='lt', field_name='date')
    date__lte = django_filters.DateFilter(lookup_expr='lte', field_name='date')
    date__gt = django_filters.DateFilter(lookup_expr='gt', field_name='date')
    date__gte = django_filters.DateFilter(lookup_expr='gte', field_name='date')
    
    details__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='details')
    details__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='details')
    
    time_from__lt = django_filters.DateFilter(lookup_expr='lt', field_name='time_from')
    time_from__lte = django_filters.DateFilter(lookup_expr='lte', field_name='time_from')
    time_from__gt = django_filters.DateFilter(lookup_expr='gt', field_name='time_from')
    time_from__gte = django_filters.DateFilter(lookup_expr='gte', field_name='time_from')
    
    time_to__lt = django_filters.DateFilter(lookup_expr='lt', field_name='time_to')
    time_to__lte = django_filters.DateFilter(lookup_expr='lte', field_name='time_to')
    time_to__gt = django_filters.DateFilter(lookup_expr='gt', field_name='time_to')
    time_to__gte = django_filters.DateFilter(lookup_expr='gte', field_name='time_to')
    
    location__icontains = django_filters.CharFilter(lookup_expr='icontains', field_name='location')
    location__iexact = django_filters.CharFilter(lookup_expr='iexact', field_name='location')
    location__istartswith = django_filters.CharFilter(lookup_expr='istartswith', field_name='location')
    
    out_of_office = django_filters.BooleanFilter(field_name='out_of_office')
    
    notification = django_filters.CharFilter(field_name='notification')
    
    notification_duration = django_filters.CharFilter(field_name='notification_duration')
    
    busy = django_filters.CharFilter(field_name='busy')
    
    repeat = django_filters.CharFilter(field_name='repeat')
    
    include_for_certificate = django_filters.BooleanFilter(field_name='include_for_certificate')
    include_for_invoice = django_filters.BooleanFilter(field_name='include_for_invoice')

    
    class Meta:
        model = Timesheet
        fields = [
            'talent',
            'work_experience',
            'date_captured',
            'date',
            'client',
            'project',
            'task',
            'details',
            'time_from',
            'time_to',
            'location',
            'out_of_office',
            'notification',
            'notification_time',
            'notification_duration',
            'busy',
            'repeat',
            'include_for_certificate',
            'include_for_invoice',
        ]
        order_by = '__all__'