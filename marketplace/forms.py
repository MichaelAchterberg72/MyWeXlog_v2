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
            WorkLocation, TalentRequired, Deliverables, SkillLevel, SkillRequired, TalentAvailabillity
)


from locations.models import Currency, City
from enterprises.models import Branch

#>>> Select 2
class BranchSearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
    ]

class BranchSelect2Widget(BranchSearchFieldMixin, ModelSelect2Widget):
    model = Branch

    def create_value(self, value):
        self.get_queryset().create(name=value)

class CurrencySearchFieldMixin:
    search_fields = [
        'currency_name__icontains', 'pk__startswith'
    ]

class CurrencySelect2Widget(CurrencySearchFieldMixin, ModelSelect2Widget):
    model = Currency

    def create_value(self, value):
        self.get_queryset().create(currency=value)

class CitySearchFieldMixin:
    search_fields = [
        'city__icontains', 'pk__startswith'
    ]
class CitySelect2Widget(CitySearchFieldMixin, ModelSelect2Widget):
    model = City

    def create_value(self, value):
        self.get_queryset().create(city=value)
#Select2<<<


class TalentAvailabillityForm(forms.ModelForm):
    class Meta:
        model = TalentAvailabillity
        fields = ('date_from', 'date_to', 'hours_available', 'unit')


class SkillRequiredForm(forms.ModelForm):
    class Meta:
        model = SkillRequired
        fields = ('skill', 'experience_level')


class SkillLevelForm(forms.ModelForm):
    class Meta:
        model = SkillLevel
        fields = ('level', 'description', 'min_hours')


class DeliverablesForm(forms.ModelForm):
    class Meta:
        model = Deliverables
        fields = ('deliverable',)
        widgets = {
            'deliverable': forms.Textarea(),
        }


class TalentRequiredForm(forms.ModelForm):
    class Meta:
        model = TalentRequired
        fields = ('title', 'enterprise', 'date_deadline', 'hours_required', 'unit', 'worklocation', 'rate_offered', 'rate_unit', 'currency', 'rate_unit', 'offer_status', 'certification', 'scope', 'expectations', 'terms', 'city')
        widgets={
            'city': CitySelect2Widget(),
            'currency': CurrencySelect2Widget(),
            'enterprise': BranchSelect2Widget(),

        }


class WorkLocationForm(forms.ModelForm):
    class Meta:
        model = WorkLocation
        fields = ('type', 'description')
