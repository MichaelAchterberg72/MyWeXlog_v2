from django import forms
from django.contrib.auth.models import User


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


from django_select2.forms import (
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)


from .models import BookList, Author, ReadBy, Format, Publisher
from db_flatten.models import SkillTag
from .widgets import XDSoftDateTimePickerInput, BootstrapDateTimePickerInput, FengyuanChenDatePickerInput


#class AddressForm(forms.Form):
#    email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))
#    password = forms.CharField(widget=forms.PasswordInput())
#    address_1 = forms.CharField(
#        label='Address',
#        widget=forms.TextInput(attrs={'placeholder': '1234 Main St'})
#    )
#    address_2 = forms.CharField(
#        widget=forms.TextInput(attrs={'placeholder': 'Apartment, studio, or floor'})
#    )
#    city = forms.CharField()
#    state = forms.ChoiceField(choices=STATES)
#    zip_code = forms.CharField(label='Zip')
#    check_me_out = forms.BooleanField(required=False)
#
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.helper = FormHelper()
#        self.helper.layout = Layout(
#            Row(
#                Column('email', css_class='form-group col-md-6 mb-0'),
#                Column('password', css_class='form-group col-md-6 mb-0'),
#                css_class='form-row'
#            ),
#            'address_1',
#            'address_2',
#            Row(
#                Column('city', css_class='form-group col-md-6 mb-0'),
#                Column('state', css_class='form-group col-md-4 mb-0'),
#                Column('zip_code', css_class='form-group col-md-2 mb-0'),
#                css_class='form-row'
#            ),
#            'check_me_out',
#            Submit('submit', 'Sign in')
#        )
class PublisherSearchFieldMixin:
    search_fields = [
        'publisher__icontains', 'pk__startswith'
    ]
class PublisherSelect2Widget(PublisherSearchFieldMixin, ModelSelect2Widget):
    model = Publisher

    def create_value(self, value):
        self.get_queryset().create(publisher=value)

class BookAddForm(forms.ModelForm):
    class Meta:
        model = BookList
        fields = ('title','publisher','author','tag','link')
        widgets = {
            'publisher': PublisherSelect2Widget(),
        }

class AuthorAddForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ["name",]


class PublisherAddForm(forms.ModelForm):
    class Meta:
        model=Publisher
        fields=("publisher",)


class FormatAddForm(forms.ModelForm):
    class Meta:
        model=Format
        fields=('format',)


class TagAddForm(forms.ModelForm):
    class Meta:
        model = SkillTag
        fields = ["skill",]

class BookSearchFieldMixin:
    search_fields = [
        'title__icontains', 'pk__startswith'
    ]
class BookSelect2Widget(BookSearchFieldMixin, ModelSelect2Widget):
    model = BookList

    def create_value(self, value):
        self.get_queryset().create(title=value)

class TypeSearchFieldMixin:
    search_fields = [
        'format__icontains', 'pk__startswith'
    ]
class TypeSelect2Widget(TypeSearchFieldMixin, ModelSelect2Widget):
    model = Format

    def create_value(self, value):
        self.get_queryset().create(format=value)

class DateInput(forms.DateInput):
    input_type = 'date'

class AddBookReadForm(forms.ModelForm):

    class Meta:
        model = ReadBy
        fields = ('book','type','date',)
        widgets = {
            'date': DateInput(),
            'book': BookSelect2Widget(),
            'type': TypeSelect2Widget(),
        }


class DateForm(forms.Form):
    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )


class BookSearchForm(forms.Form):
    query = forms.CharField()
