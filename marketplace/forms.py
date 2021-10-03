from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.encoding import force_text
from django_select2.forms import (ModelSelect2MultipleWidget,
                                  ModelSelect2TagWidget, ModelSelect2Widget,
                                  Select2MultipleWidget, Select2Widget)

from db_flatten.models import LanguageList, SkillTag
from enterprises.models import Branch
from locations.models import City, Currency
from talenttrack.forms import DesignationSelect2Widget
from talenttrack.models import Result

from .models import (BidInterviewList, Deliverables, SkillLevel, SkillRequired,
                     TalentAvailabillity, TalentRate, TalentRequired,
                     VacancyRate, WorkBid, WorkIssuedTo, WorkLocation)


#>>> Select 2
class BranchSearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith', 'company__ename__icontains', 'city__city__icontains', 'region__region__icontains',
    ]

class BranchSelect2Widget(BranchSearchFieldMixin, ModelSelect2Widget):
    model = Branch

    def create_value(self, value):
        self.get_queryset().create(name=value)


class LanguageSearchFieldMixin:
    search_fields = [
        'language__icontains', 'pk__startswith'
    ]

class LanguageWidget(LanguageSearchFieldMixin, ModelSelect2MultipleWidget):
    model = LanguageList

    def create_value(self, value):
        self.get_queryset().create(language=value)


class VacancySkillSearchFieldMixin:
    search_fields = [
        'skill__icontains', 'pk__startswith'
    ]

class VacancySkillSelect2Widget(VacancySkillSearchFieldMixin, ModelSelect2Widget):
    model = SkillTag

    def create_value(self, value):
        self.get_queryset().create(skill=value)

class CurrencySearchFieldMixin:
    search_fields = [
        'currency_name__icontains', 'pk__startswith', 'currency_abv__icontains',
    ]

class CurrencySelect2Widget(CurrencySearchFieldMixin, ModelSelect2Widget):
    model = Currency

    def create_value(self, value):
        self.get_queryset().create(currency=value)

class CitySearchFieldMixin:
    search_fields = [
        'city__icontains', 'pk__startswith', 'region__region__icontains',
    ]

class CitySelect2Widget(CitySearchFieldMixin, ModelSelect2Widget):
    model = City

    def create_value(self, value):
        self.get_queryset().create(city=value)


class CertSearchFieldMixin:
    search_fields = [
        'type__icontains', 'pk__startswith',
    ]

class CertModelSelect2MultipleWidget(CertSearchFieldMixin, ModelSelect2MultipleWidget):
    model = Result

    def create_value(self, value):
        self.get_queryset().create(type=value)


class SkillSearchFieldMixin:
    search_fields = [
        'skill__icontains', 'pk__startswith'
    ]

class SkillModelSelect2MultipleWidget(SkillSearchFieldMixin, ModelSelect2MultipleWidget):
    model = SkillTag

    def create_value(self, value):
        self.get_queryset().create(skill=value)
#Select2<<<


class DateInput(forms.DateInput):
    input_type = 'date'


#Employer rating the talent
class VacancyRateForm(forms.ModelForm):
    class Meta:
        model = VacancyRate
        fields = ('rate_1', 'rate_2', 'rate_3', 'comment', 'personal_comment', 'suggestions',)
        labels = {
            'comment': 'Talent Public Commendation ',
            'personal_comment': 'Personal Comments',
        }

#Talent rating the employer
class TalentRateForm(forms.ModelForm):
    class Meta:
        model = TalentRate
        fields = ('rate_1', 'rate_2', 'rate_3', 'comment', 'payment_time', 'suggestions',)
        labels = {
            'comment': 'My Comments',
        }

class VacancySearchForm(forms.Form):
    query = forms.CharField()
    class Meta:
        labels = {
            'query': 'Reference Number',
        }


#This form used to make comments on a completed interview
class TltIntCommentForm(forms.ModelForm):
    class Meta:
        model = BidInterviewList
        fields = ('comments_tlt',)
        labels = {'comments_tlt': 'My Comment'}


#This form used when declining an interview
class TalentInterViewComments(forms.ModelForm):
    class Meta:
        model = BidInterviewList
        fields = ('comments_tlt', 'tlt_decline_reason',)
        labels = {'comments_tlt': 'Reason for Declining Interview'}


class AssignWorkForm(forms.ModelForm):
    class Meta:
        model = WorkIssuedTo
        fields = ('rate_offered', 'date_begin', 'date_deliverable')
        labels = {
            'date_begin': 'Work Start Date',
            'date_deliverable': 'Work Completion Date',
        }
        widgets = {
            'date_deliverable': DateInput(),
            'date_begin': DateInput(),
        }


class AssignmentClarifyForm(forms.ModelForm):
    class Meta:
        model = WorkIssuedTo
        fields = ('clarification_required', )
        labels = {
            'clarification_required': 'Information Required',
            }


class AssignmentDeclineReasonsForm(forms.ModelForm):
    class Meta:
        model=WorkIssuedTo
        fields = ('comments', 'tlt_decline_reason',)
        labels = {
            'comments': 'Details',
            'tlt_decline_reason': 'Reason',
            }


#Why is this not being picked up
class EmployerInterViewComments(forms.ModelForm):
    class Meta:
        model=BidInterviewList
        fields = ('comments_emp',)
        labels = {'comments_emp': 'Comments',}


class WorkBidForm(forms.ModelForm):
    class Meta:
        model = WorkBid
        fields = ('rate_bid', 'motivation',)
        labels = {
            'rate_bid': 'My Required Rate'
        }


#class TalentAvailabillityForm(forms.ModelForm):
#    class Meta:
#        model = TalentAvailabillity
#        fields = ('date_from', 'date_to', 'hours_available', 'unit')
#        widgets = {
#            "date_from": DateInput(),
#            "date_to": DateInput(),
#        }

class TalentAvailabillityForm(forms.ModelForm):
    class Meta:
        model = TalentAvailabillity
        fields = ('freelance', 'remote_freelance', 'contract', 'part_time', 'permanent')


class SkillRequiredForm(forms.ModelForm):
    dup = None
    def __init__(self, *args, **kwargs):
        global dup
        dup = kwargs.pop('dup')
        super().__init__(*args, **kwargs)

    class Meta:
        model = SkillRequired
        fields = ('skills', )
        widgets = {
            'skills': VacancySkillSelect2Widget(),
        }

        labels = {
            'skills':'Add Skill',
        }

    def clean_skills(self):
        skill_passed = self.cleaned_data.get("skills")
        als = skill_passed.id

        if als in dup:
            raise ValidationError("The above skill has already been added! Please choose another skill.")
        return skill_passed


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

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        scope = cleaned_data.get("scope")
        deliverable = cleaned_data.get("deliverable")

        if Deliverables.objects.filter(scope = scope, deliverable = deliverable).count() > 0:
            del cleaned_data["scope"]
            del cleaned_data["deliverable"]

            raise ValidationError("This combination of Deliverable and Scope already exists! Please enter another combination.")

        return cleaned_data


class TalentRequiredForm(forms.ModelForm):

    companybranch = forms.ModelChoiceField(queryset=None)
    def __init__(self, *args, **kwargs):
        self.company_qs = kwargs.pop('company_qs', None)

        super().__init__(*args, **kwargs)
        self.fields['companybranch'].queryset = Branch.objects.filter(id__in=self.company_qs)

        self.helper = FormHelper(self)
        self.helper.form_show_errors = False


    class Meta:
        model = TalentRequired
        fields = ('title', 'companybranch', 'designation', 'date_deadline', 'permpos', 'hours_required', 'unit', 'worklocation', 'rate_offered', 'rate_unit', 'currency', 'rate_unit', 'certification', 'scope', 'expectations', 'terms', 'city', 'experience_level', 'bid_closes', 'own_ref_no', 'language',)
        widgets={
            'city': CitySelect2Widget(),
            'currency': CurrencySelect2Widget(),
            'designation': DesignationSelect2Widget(),
            'language': LanguageWidget(),
            'date_deadline': DateInput(),
            'bid_closes': DateInput(),
            'certification': CertModelSelect2MultipleWidget(),
        }
        labels = {
            'companybranch': 'Company',
            'title': 'Vacancy Title',
            'bid_closes': 'Applications Close',
            'offer_status': 'Vacancy Status',
            'worklocation': 'Configuration',
            'language': 'Language Required',
            'date_deadline': 'Work Completed By',
            'hours_required': 'Hours',
            'own_ref_no': 'Own Internal Vacancy Reference Number',
        }

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        companybranch = cleaned_data.get("companybranch")
        title = cleaned_data.get("title")
        requested_by = cleaned_data.get("requested_by")
        own_ref_no = cleaned_data.get("own_ref_no")

        if TalentRequired.objects.filter(companybranch = companybranch, title = title, requested_by = requested_by).count() > 0:
            del cleaned_data["companybranch"]
            del cleaned_data["title"]
            del cleaned_data["requested_by"]
            raise ValidationError("This combination of Title, Company and Branch already exists! Please enter another combination.")

        elif ProjectData.objects.filter(companybranch = companybranch, own_ref_no = own_ref_no).count() > 0:
            del cleaned_data["companybranch"]
            del cleaned_data["own_ref_no"]

            raise ValidationError("This combination of Reference Number and Branch already exists! Please enter another combination.")

        return cleaned_data


class TalentRequiredEditForm(forms.ModelForm):
    class Meta:
        model = TalentRequired
        fields = ('title', 'designation', 'companybranch', 'date_deadline', 'hours_required', 'unit', 'worklocation', 'rate_offered', 'rate_unit', 'currency', 'rate_unit', 'offer_status', 'certification', 'scope', 'expectations', 'terms', 'city', 'experience_level', 'bid_closes', 'own_ref_no', 'language')
        widgets={
            'city': CitySelect2Widget(),
            'designation': DesignationSelect2Widget(),
            'currency': CurrencySelect2Widget(),
            'companybranch': BranchSelect2Widget(),
            'language': LanguageWidget(),
            'date_deadline': DateInput(),
            'bid_closes': DateInput(),
            'certification': CertModelSelect2MultipleWidget(),
        }
        labels = {
            'title': 'Vacancy Title',
            'bid_closes': 'Vacancy Closes',
            'offer_status': 'Vacancy Status',
            'language': 'Language Required',
            'worklocation': 'Work Configuration',
            'date_deadline': 'Completion Date',
            'hours_required': 'Hours',
            'own_ref_no': 'Own Internal Vacancy Reference Number',
        }

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        companybranch = cleaned_data.get("companybranch")
        title = cleaned_data.get("title")
        requested_by = cleaned_data.get("requested_by")
        own_ref_no = cleaned_data.get("own_ref_no")

        if TalentRequired.objects.filter(companybranch = companybranch, title = title, requested_by = requested_by).count() > 0:
            del cleaned_data["companybranch"]
            del cleaned_data["title"]
            del cleaned_data["requested_by"]
            raise ValidationError("This combination of Title, Company and Branch already exists! Please enter another combination.")

        elif ProjectData.objects.filter(companybranch = companybranch, own_ref_no = own_ref_no).count() > 0:
            del cleaned_data["companybranch"]
            del cleaned_data["own_ref_no"]

            raise ValidationError("This combination of Reference Number and Branch already exists! Please enter another combination.")

        return cleaned_data


class WorkLocationForm(forms.ModelForm):
    class Meta:
        model = WorkLocation
        fields = ('type', 'description')
