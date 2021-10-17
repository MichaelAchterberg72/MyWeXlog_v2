from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django_select2.forms import (ModelSelect2TagWidget, ModelSelect2Widget,
                                  Select2MultipleWidget, Select2Widget)

from enterprises.models import Branch, Enterprise, Industry
from locations.models import City, Region, Suburb

from .models import ProjectData, ProjectPersonalDetails


class ProjectSearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith', 'company__ename__icontains', 'region__region__icontains', 'city__city__icontains',
    ]

#    dependent_fields = {'companybranch': 'companybranch'}

class ProjectSelect2Widget(ProjectSearchFieldMixin, ModelSelect2Widget):
    model = ProjectData

    def create_value(self, value):
        self.get_queryset().create(name=value)


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
        'ename__icontains', 'pk__startswith'
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
    '''This form is used when adding aproject from talenttrack app'''
    '''
    #removed this validation for now...
    pwd = None
    def __init__(self, *args, **kwargs):
        global pwd
        pwd = kwargs.pop('pwd')
        super().__init__(*args, **kwargs)
    '''

    class Meta:
        model = ProjectData
        fields = ('name', 'country', 'region', 'city', 'industry')
        widgets = {
            #'company': CompanySelect2Widget(),
            'industry': IndustrySelect2Widget(),
            'region': RegionSelect2Widget(),
            'city': CitySelect2Widget(),
            #'companybranch': BranchSelect2Widget(),
        }
        labels = {
            'city' : 'Closest City / Town / Village',
        }

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        name = cleaned_data.get("name")
        companybranch = cleaned_data.get("companybranch")

        if ProjectData.objects.filter(name = name, companybranch = companybranch).count() > 0:
            del cleaned_data["name"]
            del cleaned_data["companybranch"]
            raise ValidationError("This combination of Company and Branch already exist! Please enter another combination or select the existing combination.")

        return cleaned_data

    '''
    def clean_project(self):
        project_passed = self.cleaned_data.get("name")
        als = project_passed

        if als in pwd:
            raise ValidationError("A project with this name already exists! Please enter another name.")
        return project_passed
    '''

class ProjectFullAddForm(forms.ModelForm):
    '''This form is used when adding a full project'''
    class Meta:
        model = ProjectData
        fields = ('name', 'company', 'companybranch', 'country', 'region', 'city', 'industry')
        widgets = {
            'company': CompanySelect2Widget(),
            'industry': IndustrySelect2Widget(),
            'region': RegionSelect2Widget(),
            'city': CitySelect2Widget(),
            'companybranch': BranchSelect2Widget(),
        }
        labels = {
            'city' : 'Closest City / Town / Village',
            'company' : 'The company that owns the project'
        }

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        name = cleaned_data.get("name")
        companybranch = cleaned_data.get("companybranch")

        if ProjectData.objects.filter(name = name, companybranch = companybranch).count() > 0:
            del cleaned_data["name"]
            del cleaned_data["companybranch"]
            raise ValidationError("This combination of Company and Branch already exist! Please enter another combination or select the existing combination.")

        return cleaned_data

class ProjectAddHome(forms.ModelForm):
    '''This form is used when adding aproject from talenttrack app'''
    class Meta:
        model = ProjectData
        fields = ('company', 'companybranch', 'name', 'country', 'region', 'city', 'industry')
        widgets = {
            'company': CompanySelect2Widget(),
            'industry': IndustrySelect2Widget(),
            'region': RegionSelect2Widget(),
            'city': CitySelect2Widget(),
            'companybranch': BranchSelect2Widget(),
        }
        labels = {
            'city' : 'Closest City / Town / Village',
        }

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        name = cleaned_data.get("name")
        companybranch = cleaned_data.get("companybranch")

        if ProjectData.objects.filter(name = name, companybranch = companybranch).count() > 0:
            del cleaned_data["name"]
            del cleaned_data["companybranch"]
            raise ValidationError("This combination of Company and Branch already exist! Please enter another combination or select the existing combination.")

        return cleaned_data


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

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        name = cleaned_data.get("name")
        companybranch = cleaned_data.get("companybranch")

        if ProjectData.objects.filter(name = name, companybranch = companybranch).count() > 0:
            del cleaned_data["name"]
            del cleaned_data["companybranch"]
            raise ValidationError("This combination of Company and Branch already exist! Please enter another combination or select the existing combination.")

        return cleaned_data


class ProjectPersonalDetailsForm(forms.ModelForm):
    class Meta:
        model = ProjectPersonalDetails
        fields = ('description',)
        widgets = {
            'companybranch': BranchSelect2Widget(),
        }


class AddProjectPersonalDetailsForm(forms.ModelForm):
    class Meta:
        model = ProjectPersonalDetails
        fields = ('project', 'company', 'companybranch', 'description',)
        widgets = {
            'company': CompanySelect2Widget(),
            'companybranch': BranchSelect2Widget(),
            'project': ProjectSelect2Widget(),
        }
        labels = {
            'company' : 'Company you are working for on the project',
        }
        help_texts = {
            'project' : '*Enter either the project owner, project name, region or city of the project',
        }

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        talent = cleaned_data.get("talent")
        companybranch = cleaned_data.get("companybranch")
        company = cleaned_data.get("company")
        project = cleaned_data.get("project")

        if ProjectPersonalDetails.objects.filter(talent = talent, project = project, company = company, companybranch = companybranch).count() > 0:
            del cleaned_data["talent"]
            del cleaned_data["companybranch"]
            del cleaned_data["company"]
            del cleaned_data["project"]
            raise ValidationError("This combination of Project, Company and Branch already exist in your profile! Please enter another combination or select the existing combination.")

        return cleaned_data
