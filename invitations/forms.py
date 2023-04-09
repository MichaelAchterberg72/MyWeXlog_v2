from django import forms
from django_select2.forms import (ModelSelect2MultipleWidget,
                                  ModelSelect2TagWidget, ModelSelect2Widget,
                                  Select2MultipleWidget, Select2Widget)

from enterprises.models import Branch

from .models import Invitation


class BranchSearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith', 'company__ename__icontains',
    ]

class BranchSelect2Widget(BranchSearchFieldMixin, ModelSelect2Widget):
    model = Branch

    def create_value(self, value):
        self.get_queryset().create(name=value)


class InvitationForm(forms.ModelForm):
    pwd = None
    def __init__(self, *args, **kwargs):
        global pwd
        pwd = kwargs.pop('pwd')
        super().__init__(*args, **kwargs)

    class Meta:
        model = Invitation
        fields = ('name', 'surname', 'companybranch', 'message', 'email')
        widgets = {
            'companybranch':  BranchSelect2Widget(),
        }

    def clean_email(self):
        email_passed = self.cleaned_data.get("email")
        als = email_passed

        if als in pwd:
            raise forms.ValidationError("A person with this email address has already been invited! Please Choose another email.")
        return email_passed


class InvitationLiteForm(forms.ModelForm):
    pwd = None
    def __init__(self, *args, **kwargs):
        global pwd
        pwd = kwargs.pop('pwd')
        super().__init__(*args, **kwargs)

    class Meta:
        model = Invitation
        fields = ('name', 'surname', 'message', 'email')

    def clean_email(self):
        email_passed = self.cleaned_data.get("email")
        als = email_passed

        if als in pwd:
            raise forms.ValidationError("A person with this email address has already been invited! Please Choose another email.")
        return email_passed
