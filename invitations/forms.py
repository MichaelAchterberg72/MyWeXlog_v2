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
    class Meta:
        model = Invitation
        fields = ('name', 'surname', 'worked_for', 'email')
        widgets = {
            'worked_for':  BranchSelect2Widget(),
        }
