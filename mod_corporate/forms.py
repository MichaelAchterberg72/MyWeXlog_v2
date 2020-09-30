from django import forms
from django.contrib.auth.models import User

from .models import (
    CorporateStaff, OrgStructure
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
