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

class EnterprisePopupForm(forms.ModelForm):
    class Meta:
        model = Enterprise
        fields = ('name', 'description', 'website')
