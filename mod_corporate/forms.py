from django import forms
from django.contrib.auth.models import User

from .models import (
    CorporateStaff, OrgStructure
)

class OrgStructureForm(forms.ModelForm):
    level = forms.ModelChoiceField(queryset=None)
    def __init__(self, *args, **kwargs):
        self._corp=kwargs.pop('corp', None)
        super().__init__(*args, **kwargs)
        self.fields['level'].queryset = OrgStructure.objects.filter(corporate=self._corp)
    class Meta:
        model = OrgStructure
        fields = ('level_name', 'level')
        labels = {
            'level':'Parent Department',
            'level_name':'Department Name'
        }
