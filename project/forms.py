from django import forms
from django.contrib.auth.models import User


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

from django_select2.forms import (
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)

from .models import ProjectData
from enterprises.models import Enterprise
from locations.models import Region, City, Suburb

class ProjectAddForm(forms.ModelForm):
    class Meta:
        model = ProjectData
        fields = ('name','owner','country','region','city', 'industry')

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

class ProjectSearchForm(forms.Form):
    query = forms.CharField()
