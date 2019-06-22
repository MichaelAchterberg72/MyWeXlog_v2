from django import forms
from django.contrib.auth.models import User


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


from .models import BookList, Author, ReadBy, Format, Publisher
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


class BookAddForm(forms.ModelForm):
    class Meta:
        model = BookList
        fields = ('title','publisher','author','tag','link')


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


class AddBookReadForm(forms.ModelForm):
    date = forms.DateField(input_formats=['%d/%m/%Y'], widget=FengyuanChenDatePickerInput())

    class Meta:
        model = ReadBy
        fields = ('book','type','date',)
        widgets = {
            'date': FengyuanChenDatePickerInput(),
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
