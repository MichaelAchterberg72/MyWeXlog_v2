from django import forms
from django.contrib.auth.models import User

from .models import (
    CorporateStaff, OrgStructure, CorporateHR
)

class OrgStructureForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=None)
    def __init__(self, *args, **kwargs):
        self._fil=kwargs.pop('fil', None)
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = OrgStructure.objects.filter(corporate=self._fil)
    class Meta:
        model = OrgStructure
        fields = ('level_name', 'parent',)
        labels = {
            'level_name':'Department Name',
        }


class StaffSearchForm(forms.Form):
    query = forms.CharField()
    class Meta:
        labels = {
            'query': 'Search by Name',
        }


class AddStaffForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'format_chkbox'})

    class Meta:
        model = CorporateStaff
        fields = ('type', 'department', 'status')
        labels = {
            'type':'Form of Relationship',
            'department':'Department',
            'status':'Grant Administrator Access',
        }


class AdminTypeForm(forms.ModelForm):
    class Meta:
        model = CorporateStaff
        fields = ('corp_access',)
        labels = {
            'corp_access':'Access Level',
        }
