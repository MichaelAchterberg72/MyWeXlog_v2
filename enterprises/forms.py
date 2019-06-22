from django import forms
from django.contrib.auth.models import User

from django_select2.forms import (
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
    )

from locations.models import Region, City, Suburb
from .models import *


class EnterpriseAddForm(forms.ModelForm):
    class Meta:
        model = Enterprise
        fields = ["name", "description", "website",]


class BranchTypeAddForm(forms.ModelForm):
    class Meta:
        model = BranchType
        fields = ["type",]


class IndustryAddForm(forms.ModelForm):
    class Meta:
        model = Industry
        fields = ["industry",]


class BranchAddForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ('enterprise','name','type','phy_address_line1','phy_address_line2','country','region','city', 'suburb', 'code', 'industry')


class CompanySearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
    ]


class CitySearchFieldMixin:
    search_fields = [
        'city__icontains', 'pk__startswith'
    ]


class RegionSearchFieldMixin:
    search_fields = [
        'region__icontains', 'pk__startswith'
    ]


class CompanySelect2Widget(CompanySearchFieldMixin, ModelSelect2Widget):
    model = Enterprise

    def create_value(self, value):
        self.get_queryset().create(name=value)


class CitySelect2Widget(CitySearchFieldMixin, ModelSelect2Widget):
    model = City

    def create_value(self, value):
        self.get_queryset().create(city=value)


class RegionSelect2Widget(RegionSearchFieldMixin, ModelSelect2Widget):
    model = Region

    def create_value(self, value):
        self.get_queryset().create(region=value)


class EnterpriseSearchForm(forms.Form):
    query = forms.CharField()


class BranchSearchForm(forms.Form):
    query = forms.CharField()
