import django_filters

from ..models import PhoneNumberType, SkillTag, LanguageList


class PhoneNumberTypeFilter(django_filters.FilterSet):
    class Meta:
        model = PhoneNumberType
        fields = [
            'type'
        ]


class SkillTagFilter(django_filters.FilterSet):
    class Meta:
        model = SkillTag
        fields = [
            'skill',
            'code'
        ]


class LanguageListFilter(django_filters.FilterSet):
    class Meta:
        model = LanguageList
        fields = [
            'language'
        ]