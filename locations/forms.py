from django import forms
from django.contrib.auth.models import User


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


from . models import (
        Region, City, Suburb, Currency
)


class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ('country', 'region',)


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ('city', 'region',)


class SuburbForm(forms.ModelForm):
    class Meta:
        model = Suburb
        fields = ('city', 'suburb',)
