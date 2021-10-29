from django import forms


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django_countries.fields import CountryField


from db_flatten.models import SkillTag


#>>> Select 2

#Select2 <<<
class SkillFilterInputForm(forms.Form):
    '''An input form for the multiple skill filter template '''
    country = CountryField(blank=True, blank_label='Country (Optional)').formfield()
