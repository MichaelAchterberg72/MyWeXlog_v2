from django import forms

from .models import Invitation
from enterprises.models import Branch


from django_select2.forms import (
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget, ModelSelect2MultipleWidget, Select2MultipleWidget
)


class BranchSearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
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
        fields = ('name', 'surname', 'worked_for', 'email')
        widgets = {
            'worked_for':  BranchSelect2Widget(),
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
        fields = ('name', 'surname', 'email')

    def clean_email(self):
        email_passed = self.cleaned_data.get("email")
        als = email_passed

        if als in pwd:
            raise forms.ValidationError("A person with this email address has already been invited! Please Choose another email.")
        return email_passed
