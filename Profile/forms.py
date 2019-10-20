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
            Profile, Email, PhysicalAddress, PostalAddress, PhoneNumber, OnlineRegistrations, SiteName, FileUpload, IdentificationDetail, IdType, PassportDetail, LanguageList, LanguageTrack
          )
from enterprises.models import Enterprise
from locations.models import Region, City, Suburb


class LanguageTrackForm(forms.ModelForm):
    class Meta:
        model = LanguageTrack
        fields = ('language', 'level')


class LanguageListForm(forms.ModelForm):
    class Meta:
        model = LanguageList
        fields = ('language',)


class DateInput(forms.DateInput):
    input_type = 'date'


class PassportDetailForm(forms.ModelForm):
    class Meta:
        model = PassportDetail
        fields = ('passport_number', 'expiry_date', 'issue')
        widgets = {
            'expiry_date': DateInput(),
        }


class IdentificationDetailForm(forms.ModelForm):
    class Meta:
        model = IdentificationDetail
        fields = ('identification', 'id_type')


class IdTypeForm(forms.ModelForm):
    class Meta:
        model = IdType
        fields = ('type',)


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ('title', 'file')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('birth_date', 'background', 'mentor',)
        widgets = {
            'birth_date': DateInput(),
            }

#>>> Select2 Company Field in email
class CompanySearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
    ]

class CitySearchFieldMixin:
    search_fields = [
        'city__icontains', 'pk__startswith'
    ]

class SuburbSearchFieldMixin:
    search_fields = [
        'suburb__icontains', 'pk__startswith'
    ]

class RegionSearchFieldMixin:
    search_fields = [
        'region__icontains', 'pk__startswith'
    ]

class CompanySelect2Widget(CompanySearchFieldMixin, ModelSelect2Widget):
    model = Enterprise

    def create_value(self, value):
        self.get_queryset().create(name=value)

class CitySelect2Widget(CitySearchFieldMixin, ModelSelect2Widget):
    model = City

    def create_value(self, value):
        self.get_queryset().create(city=value)

class SuburbSelect2Widget(SuburbSearchFieldMixin, ModelSelect2Widget):
    model = Suburb

    def create_value(self, value):
        self.get_queryset().create(suburb=value)

class RegionSelect2Widget(RegionSearchFieldMixin, ModelSelect2Widget):
    model = Region

    def create_value(self, value):
        self.get_queryset().create(region=value)
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
        widgets={
            'region': RegionSelect2Widget(),
            'city': CitySelect2Widget(),
            'suburb': SuburbSelect2Widget(),
        }
'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['region'].queryset = Region.objects.none()

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['region'].queryset = Region.objects.filter(country=country_id)
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Region queryset
        elif self.instance.pk:
            pass
'''


class PostalAddressForm(forms.ModelForm):
    class Meta:
        model = PostalAddress
        exclude = ['talent']
        widgets={
            'region': RegionSelect2Widget(),
            'city': CitySelect2Widget(),
            'suburb': SuburbSelect2Widget(),
        }


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        fields = ('number', 'type', 'current')


class OnlineProfileForm(forms.ModelForm):
    class Meta:
        model = OnlineRegistrations
        fields = ('profileurl', 'sitename', )


class ProfileTypeForm(forms.ModelForm):
    class Meta:
        model = SiteName
        fields = ('site', )
