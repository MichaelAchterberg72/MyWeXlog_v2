from django import forms
from django.contrib.auth.models import User
from django.utils.encoding import force_text

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


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        fields = ('branch', 'phone', 'type', 'existing')


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ('enterprise', 'name', 'type', 'phy_address_line1', 'phy_address_line2', 'country', 'region', 'city', 'suburb', 'code', 'industry')


class IndustryPopUpForm(forms.ModelForm):
    class Meta:
        model = Industry
        fields = ('industry',)


class BranchTypePopUpForm(forms.ModelForm):
    class Meta:
        model = BranchType
        fields = ('type',)


class EnterprisePopupForm(forms.ModelForm):
    class Meta:
        model = Enterprise
        fields = ('name', 'description', 'website')
