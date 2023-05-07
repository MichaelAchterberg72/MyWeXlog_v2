from django_filters import CharFilter


class MultipleLookupFilter(CharFilter):
    def __init__(self, lookups, *args, **kwargs):
        super(MultipleLookupFilter, self).__init__(*args, **kwargs)
        self.lookups = lookups

    def filter(self, qs, value):
        if value:
            qs = qs.filter(**{f"{self.field_name}__{lookup}": value for lookup in self.lookups})
        return qs
    
    
def multiple_char_lookup_filter(field_name, queryset, name, value):
    query = {
        f"{field_name}__icontains": value,
        f"{field_name}__iexact": value,
    }
    return queryset.filter(**query)
