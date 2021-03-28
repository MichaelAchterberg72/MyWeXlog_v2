from django import forms
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django.forms.widgets import TextInput

from django.contrib.admin.widgets import FilteredSelectMultiple
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


from django_select2.forms import (
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)


from .models import (
            Industry, Enterprise, BranchType, Branch, PhoneNumber,
            )

from locations.models import (
            Region, City, Suburb
)


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        fields = ('branch', 'phone', 'type', 'existing')

#>>> Select 2
class RegionSearchFieldMixin:
    search_fields = [
        'region__icontains', 'pk__startswith'
    ]
    dependent_fields = {'country': 'country'}


class RegionSelect2Widget(RegionSearchFieldMixin, ModelSelect2Widget):
    model = Region

    def create_value(self, value):
        self.get_queryset().create(region=value)


class SuburbSearchFieldMixin:
    search_fields = [
        'suburb__icontains', 'pk__startswith'
    ]
    dependent_fields = {'city': 'city'}


class SuburbSelect2Widget(SuburbSearchFieldMixin, ModelSelect2Widget):
    model = Suburb

    def create_value(self, value):
        self.get_queryset().create(suburb=value)


class CitySearchFieldMixin:
    search_fields = [
        'city__icontains', 'pk__startswith'
    ]
    dependent_fields = {'region': 'region'}

class CitySelect2Widget(CitySearchFieldMixin, ModelSelect2Widget):
    model = City

    def create_value(self, value):
        self.get_queryset().create(city=value)


class CompanySearchFieldMixin:
    search_fields = [
        'ename__icontains', 'pk__startswith'
    ]

class CompanySelect2Widget(CompanySearchFieldMixin, ModelSelect2Widget):
    model = Enterprise

    def create_value(self, value):
        self.get_queryset().create(ename=value)

class IndSearchFieldMixin:
    search_fields = [
        'industry__icontains', 'pk__startswith'
    ]

class IndSelect2Widget(IndSearchFieldMixin, Select2MultipleWidget):
    model = Industry

    def create_value(self, value):
        self.get_queryset().create(industry=value)
#Select2<<<

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ('name', 'type', 'size', 'phy_address_line1', 'phy_address_line2', 'country', 'region', 'city', 'suburb', 'code', 'industry',)

        widgets={
            'region': RegionSelect2Widget(),
            'city': CitySelect2Widget(),
            'suburb': SuburbSelect2Widget(),
            'industry': IndSelect2Widget(),
        }


class FullBranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ('name', 'type', 'size', 'phy_address_line1', 'phy_address_line2', 'country', 'region', 'city', 'suburb', 'code', 'industry',)
        widgets={
            'region': RegionSelect2Widget(),
            'city': CitySelect2Widget(),
            'suburb': SuburbSelect2Widget(),
            #'company': CompanySelect2Widget(),
            'industry': IndSelect2Widget(),
        }


class IndustryPopUpForm(forms.ModelForm):
    class Meta:
        model = Industry
        fields = ('industry',)


class BranchTypePopUpForm(forms.ModelForm):
    class Meta:
        model = BranchType
        fields = ('type',)


class EnterprisePopupForm(forms.ModelForm):
    pwd = None
    def __init__(self, *args, **kwargs):
        global pwd
        pwd = kwargs.pop('pwd')
        super().__init__(*args, **kwargs)

    class Meta:
        model = Enterprise
        fields = ('ename', 'description', 'website')

    def clean_company(self):
        company_passed = self.cleaned_data.get("name")
        als = company_passed

        if als in pwd:
            raise forms.ValidationError("A company with this name already exists! Please enter another name.")
        return company_passed


class EnterpriseBranchPopupForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ('company', 'name', 'type', 'size', 'phy_address_line1', 'phy_address_line2', 'country', 'region', 'city', 'suburb', 'code', 'industry',)
        widgets={
            'region': RegionSelect2Widget(),
            'city': CitySelect2Widget(),
            'suburb': SuburbSelect2Widget(),
            'company': CompanySelect2Widget(),
            'industry': IndSelect2Widget(),
        }
