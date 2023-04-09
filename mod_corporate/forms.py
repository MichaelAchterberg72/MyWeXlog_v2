from django import forms
from django.contrib.auth.models import User

#>>>Select2
from talenttrack.forms import DesignationSelect2Widget
from users.models import CustomUser

from .models import CorporateHR, CorporateStaff, OrgStructure

#Select2<<<

class DateInput(forms.DateInput):
    input_type = 'date'


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
    '''Add a person that has listed the company as their current employer'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'format_chkbox'})

    class Meta:
        model = CorporateStaff
        fields = ('department', 'status')
        labels = {
            'department':'Department',
            'status':'Grant Administrator Access',
        }


class AddNewStaffForm(forms.ModelForm):
    '''Add a person that has not listed the company as their current employer'''
    department = forms.ModelChoiceField(queryset=None)
    def __init__(self, *args, **kwargs):
        self.cor_sg = kwargs.pop('cor_sg', None)
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = OrgStructure.objects.filter(corporate__slug=self.cor_sg)
        self.fields['status'].widget.attrs.update({'class': 'format_chkbox'})
        self.fields['talent'].queryset = CustomUser.objects.all()

    class Meta:
        model = CorporateStaff
        fields = ('talent', 'department', 'status', 'date_from', 'date_to', 'designation', 'type')
        widgets = {
            'date_from': DateInput(),
            'date_to': DateInput(),
            'designation': DesignationSelect2Widget(),
        }
        labels = {
            'talent':'Person',
            'type':'Relationship',
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
