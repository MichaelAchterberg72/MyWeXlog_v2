from django import forms
from django.contrib.auth.models import User
from django.utils.encoding import force_text

from django.contrib.admin.widgets import FilteredSelectMultiple
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.utils import timezone

from django_select2.forms import (
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)


from .models import (
            Profile, Email, PhysicalAddress, PostalAddress, PhoneNumber, OnlineRegistrations, SiteName, FileUpload, IdentificationDetail, IdType, PassportDetail, LanguageTrack, BriefCareerHistory, WillingToRelocate
          )
from enterprises.models import Enterprise, Branch
from locations.models import Region, City, Suburb
from talenttrack.models import Designation
from users.models import CustomUser
from db_flatten.models import LanguageList
from users.models import CustomUser, ExpandedView


class WillingToRelocateForm(forms.ModelForm):
    class Meta:
        model = WillingToRelocate
        fields = ('country', 'documents')
        labels = {
            'documents': '',
        }


class ExpandedIntroWalkthroughForm(forms.ModelForm):
    class Meta:
        model = ExpandedView
        fields = ('intro_walkthrough',)

#>>> Select 2
class LanguageSearchFieldMixin:
    search_fields = [
        'language__icontains', 'pk__startswith'
    ]

class LanguageWidget(LanguageSearchFieldMixin, ModelSelect2Widget):
    model = LanguageList

    def create_value(self, value):
        self.get_queryset().create(language=value)


class DesignationSearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
    ]

class DesignationSelect2Widget(DesignationSearchFieldMixin, ModelSelect2Widget):
    model = Designation

    def create_value(self, value):
        self.get_queryset().create(name=value)


class BranchSearchFieldMixin:
    search_fields = [
        'pk__startswith', 'company__ename__icontains', 'type__type__icontains', 'city__city__icontains', 'region__region__icontains'
    ]

class BranchWidget(BranchSearchFieldMixin, ModelSelect2Widget):
    model = Branch

    def create_value(self, value):
        self.get_queryset().create(name=value)

#Select 2 <<<


class DateInput(forms.DateInput):
    input_type = 'date'


class BriefCareerHistoryForm(forms.ModelForm):
    class Meta:
        model = BriefCareerHistory
        fields = ('work_configeration', 'companybranch', 'date_from', 'date_to', 'designation',)
        widgets = {
            'companybranch': BranchWidget(),
            'date_from': DateInput(),
            'date_to': DateInput(),
            'designation': DesignationSelect2Widget(),
        }
        labels = {
            'work_configeration': 'Work Configuration',
            'companybranch': 'Home Base',
        }


class ResignedForm(forms.ModelForm):
    class Meta:
        model = BriefCareerHistory
        fields = ('date_to',)
        widgets = {
        'date_to': DateInput(),
            }


class LanguageTrackForm(forms.ModelForm):
    class Meta:
        model = LanguageTrack
        fields = ('language', 'level')
        widgets= {
            'language': LanguageWidget(),
            }


class LanguageListForm(forms.ModelForm):
    class Meta:
        model = LanguageList
        fields = ('language',)


class PassportDetailForm(forms.ModelForm):
    class Meta:
        model = PassportDetail
        fields = ('passport_number', 'expiry_date', 'issue')
        widgets = {
            'expiry_date': DateInput(),
        }
        labels = {
            'issue':'Country of issue',
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
        fields = ('birth_date', 'mentor', 'std_rate', 'currency', 'alias', 'f_name', 'l_name')
        widgets = {
            'birth_date': DateInput(),
            }
        labels = {
            'f_name': 'First Name',
            'l_name': 'Last Name / Surname',
            'std_rate':'Standard Rate (per Hour)',
        }
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get("birth_date")
        age = int((timezone.now().date() - birth_date).days/365.25)
        if age < 18:
            raise forms.ValidationError("You need to be older than 18 to use MyWeXlog")
        else:
            return birth_date


class ProfileBackgroundForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('background',)


class ProfileMotivationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('motivation',)


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('alias', )


#>>> Select2 Company Field in email
class CompanySearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
    ]

class CitySearchFieldMixin:
    search_fields = [
        'city__icontains', 'pk__startswith', 'region__region__icontains',
    ]
    dependent_fields={'region': 'region'}

class SuburbSearchFieldMixin:
    search_fields = [
        'suburb__icontains', 'pk__startswith', 'city__city__icontains',
    ]
    dependent_fields={'city': 'city'}

class RegionSearchFieldMixin:
    search_fields = [
        'region__icontains', 'pk__startswith'
    ]
    dependent_fields={'country': 'country'}

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
        exclude = ['talent', 'line3', 'suburb']
        widgets={
            'region': RegionSelect2Widget(),
            'city': CitySelect2Widget(),
            #'suburb': SuburbSelect2Widget(),
        }
        labels = {
            'city': 'City / Town / Village',
        }


class PostalAddressForm(forms.ModelForm):
    class Meta:
        model = PostalAddress
        exclude = ['talent', 'line3', 'suburb']
        widgets={
            'region': RegionSelect2Widget(),
            'city': CitySelect2Widget(),
            #'suburb': SuburbSelect2Widget(),
        }

        labels = {
            'city': 'City / Town / Village',
        }

class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        fields = ('number', 'type', 'current')
        widgets = {
            'current': forms.CheckboxInput(attrs={'style':'width:30px;height:30px;'})
            }
        labels = {
            'current': '__Yes',
        }


class OnlineProfileForm(forms.ModelForm):
    class Meta:
        model = OnlineRegistrations
        fields = ('profileurl', 'sitename', )

        labels = {
            'profileurl':'Site address (url)',

        }


class ProfileTypeForm(forms.ModelForm):
    class Meta:
        model = SiteName
        fields = ('site', )
