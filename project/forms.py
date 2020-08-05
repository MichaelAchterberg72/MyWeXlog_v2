from django import forms
from django.contrib.auth.models import User


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

from django_select2.forms import (
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)

from .models import ProjectData
from enterprises.models import Enterprise, Industry, Branch
from locations.models import Region, City, Suburb



class BranchSearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith', 'company__ename__icontains', 'city__city__icontains', 'region__region__icontains',
        ]
    dependent_fields = {'company': 'company'}

class BranchSelect2Widget(BranchSearchFieldMixin, ModelSelect2Widget):
    model = Branch

    def create_value(self, value):
        self.get_queryset().create(name=value)


class CompanySearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
    ]
class CompanySelect2Widget(CompanySearchFieldMixin, ModelSelect2Widget):
    model = Enterprise

    def create_value(self, value):
        self.get_queryset().create(name=value)

class IndustrySearchFieldMixin:
    search_fields = [
        'industry__icontains', 'pk__startswith'
    ]
class IndustrySelect2Widget(IndustrySearchFieldMixin, ModelSelect2Widget):
    model = Industry

    def create_value(self, value):
        self.get_queryset().create(industry=value)

class CitySearchFieldMixin:
    search_fields = [
        'city__icontains', 'pk__startswith'
    ]
    dependent_fields={'region': 'region'}

class RegionSearchFieldMixin:
    search_fields = [
        'region__icontains', 'pk__startswith'
    ]
    dependent_fields={'country': 'country'}

class CitySelect2Widget(CitySearchFieldMixin, ModelSelect2Widget):
    model = City

    def create_value(self, value):
        self.get_queryset().create(city=value)

class RegionSelect2Widget(RegionSearchFieldMixin, ModelSelect2Widget):
    model = Region

    def create_value(self, value):
        self.get_queryset().create(region=value)


class ProjectAddForm(forms.ModelForm):

    '''
    #removed this validation for now.
    pwd = None
    def __init__(self, *args, **kwargs):
        global pwd
        pwd = kwargs.pop('pwd')
        super().__init__(*args, **kwargs)
    '''

    class Meta:
        model = ProjectData
        fields = ('name', 'company', 'country', 'companybranch', 'region', 'city', 'industry')
        widgets = {
            'company': CompanySelect2Widget(),
            'industry': IndustrySelect2Widget(),
            'region': RegionSelect2Widget(),
            'city': CitySelect2Widget(),
            'companybranch': BranchSelect2Widget(),
        }
    '''
    def clean_project(self):
        project_passed = self.cleaned_data.get("name")
        als = project_passed

        if als in pwd:
            raise forms.ValidationError("A project with this name already exists! Please enter another name.")
        return project_passed
    '''

class ProjectSearchForm(forms.Form):
    query = forms.CharField()

class ProjectForm(forms.ModelForm):
    class Meta:
        model = ProjectData
        fields = ('name', 'company', 'companybranch', 'industry', 'country', 'region', 'city')
        widgets = {
            'company': CompanySelect2Widget(),
            'industry': IndustrySelect2Widget(),
            'region': RegionSelect2Widget(),
            'city': CitySelect2Widget(),
            'companybranch': BranchSelect2Widget(),
        }
