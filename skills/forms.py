from django import forms


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django_countries.fields import CountryField
from django_select2.forms import ModelSelect2Widget


from locations.models import Region
from db_flatten.models import SkillTag

from .models import SkillFilter


#>>> Select 2
class SkillSearchFieldMixin:
    search_fields = [
        'skill__icontains', 'pk__startswith'
    ]

class SkillWidget(SkillSearchFieldMixin, ModelSelect2Widget):
    model = SkillTag

    def create_value(self, value):
        self.get_queryset().create(skill=value)

class RegionSearchFieldMixin:
    search_fields = [
        'region__icontains', 'pk__startswith'
    ]
    dependent_fields = {'country': 'country'}


class RegionWidget(RegionSearchFieldMixin, ModelSelect2Widget):
    model = Region

    def create_value(self, value):
        self.get_queryset().create(region=value)


#Select2 <<<
class SkillFilterInputForm(forms.Form):
    '''An input form for the multiple skill filter template '''
    country = CountryField(blank=True, blank_label='Country (Optional)').formfield()
