from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import NON_FIELD_ERRORS


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
        fields = ('region','country')

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        country = cleaned_data.get("country")
        region = cleaned_data.get("region")

        if Region.objects.filter(country = country, region = region).count() > 0:
            del cleaned_data["country"]
            del cleaned_data["region"]
            raise ValidationError("This combination of Country and Region already exists! Please enter another combination or select the existing combination.")

        return cleaned_data


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ('city', )

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        region = cleaned_data.get("region")
        city = cleaned_data.get("city")

        if City.objects.filter(region = region, city = city).count() > 0:
            del cleaned_data["region"]
            del cleaned_data["city"]
            raise ValidationError("This combination of Region and City already exists! Please enter another combination or select the existing combination.")

        return cleaned_data


class VacCityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ('city', 'region' )

        widgets = {
            'region': RegionSelect2Widget(),
        }

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        region = cleaned_data.get("region")
        city = cleaned_data.get("city")

        if City.objects.filter(region = region, city = city).count() > 0:
            del cleaned_data["region"]
            del cleaned_data["city"]
            raise ValidationError("This combination of Region and City already exists! Please enter another combination or select the existing combination.")

        return cleaned_data


class SuburbForm(forms.ModelForm):
    class Meta:
        model = Suburb
        fields = ('suburb',)

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        suburb = cleaned_data.get("suburb")
        city = cleaned_data.get("city")

        if Suburb.objects.filter(suburb = suburb, city = city).count() > 0:
            del cleaned_data["suburb"]
            del cleaned_data["city"]
            raise ValidationError("This combination of City and Suburb already exists! Please enter another combination or select the existing combination.")

        return cleaned_data


class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ('country', 'currency_name', 'currency_abv')

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        country = cleaned_data.get("country")
        currency_name = cleaned_data.get("currency_name")

        if Currency.objects.filter(country = country, currency_name = currency_name).count() > 0:
            del cleaned_data["country"]
            del cleaned_data["currency_name"]
            raise ValidationError("This combination of Country and Currency Namealready exists! Please enter another combination or select the existing combination.")

        return cleaned_data
