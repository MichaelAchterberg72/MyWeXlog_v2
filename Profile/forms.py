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
            Profile, Email, PhysicalAddress, PostalAddress
          )
from enterprises.models import Enterprise

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('synonym', 'birth_date', 'background', 'mentor',)

#>>> Select2 Company Field in email
class CompanySearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
    ]


class CompanySelect2Widget(CompanySearchFieldMixin, ModelSelect2Widget):
    model = Enterprise

    def create_value(self, value):
        self.get_queryset().create(name=value)
#<<< Select2 Company Field

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ('email', 'active', 'company',)
        widgets={
            'company': CompanySelect2Widget(),
        }

class EmailStatusForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ('active',)

class PhysicalAddressForm(forms.ModelForm):
    class Meta:
        model = PhysicalAddress
        exclude = ['talent']
