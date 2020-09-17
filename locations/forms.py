from django import forms
from django.contrib.auth.models import User


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django_select2.forms import (
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)

from . models import (
        Region, City, Suburb, Currency
)


#>>> Select 2
class RegionSearchFieldMixin:
    search_fields = [
        'region__icontains', 'pk__startswith'
    ]
    dependent_fields={'country': 'country'}

class RegionSelect2Widget(RegionSearchFieldMixin, ModelSelect2Widget):
    model = Region

    def create_value(self, value):
        self.get_queryset().create(region=value)


class SuburbSearchFieldMixin:
    search_fields = [
        'suburb__icontains', 'pk__startswith',
    ]
    dependent_fields={'city': 'city'}

class SuburbSelect2Widget(SuburbSearchFieldMixin, ModelSelect2Widget):
    model = Suburb

    def create_value(self, value):
        self.get_queryset().create(suburb=value)


class CitySearchFieldMixin:
    search_fields = [
        'city__icontains', 'pk__startswith'
    ]
    dependent_fields={'region': 'region'}

class CitySelect2Widget(CitySearchFieldMixin, ModelSelect2Widget):
    model = City

    def create_value(self, value):
        self.get_queryset().create(city=value)
#Select2<<<


class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ('country', 'region',)


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ('city', 'region',)
        widgets={
            'region': RegionSelect2Widget(),
        }


class SuburbForm(forms.ModelForm):
    class Meta:
        model = Suburb
        fields = ('suburb',)
        '''
        widgets={
            'city': CitySelect2Widget(),
        }
        '''

class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ('country', 'currency_name', 'currency_abv')
