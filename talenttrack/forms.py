from datetime import timedelta

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import ModelChoiceField
from django.utils import timezone
from django.utils.encoding import force_text
from django_countries.fields import CountryField
from django_select2.forms import (HeavySelect2MultipleWidget,
                                  ModelSelect2MultipleWidget,
                                  ModelSelect2TagWidget, ModelSelect2Widget,
                                  Select2MultipleWidget, Select2Widget)

from booklist.forms import (AuthorModelSelect2MultipleWidget, GenreWidget,
                            PublisherSelect2Widget,
                            TagModelSelect2MultipleWidget)
from db_flatten.models import SkillTag
from enterprises.models import Branch, Enterprise, Industry
from locations.models import Region
from marketplace.models import TalentRequired
from project.models import ProjectData, ProjectPersonalDetails
from users.models import CustomUser

from .models import (Achievements, Awards, ClassMates, Course, CourseType,
                     Designation, EmailRemindValidate, Lecturer,
                     LicenseCertification, Publications, Result, Superior,
                     Topic, WorkClient, WorkCollaborator, WorkColleague,
                     WorkExperience)
from .widgets import ListTextWidget


class EmailFormModal(forms.ModelForm):

    class Meta:
        model = EmailRemindValidate
        fields = ('subject', 'message')

#>>> Select 2
class UserSearchFieldMixin:
    search_fields = [
        'last_name__icontains', 'pk__startswith', 'first_name__icontains',
    ]
class UserSelect2Widget(UserSearchFieldMixin, ModelSelect2Widget):
    model = CustomUser

    def create_value(self, value):
        self.get_queryset().exclude(id__in=pwd).create(Q(last_name=value) | Q(first_name=value))


class CompanySearchFieldMixin:
    search_fields = [
        'ename__icontains', 'pk__startswith'
        ]

class CompanySelect2Widget(CompanySearchFieldMixin, ModelSelect2Widget):
    model = Enterprise

    def create_value(self, value):
        self.get_queryset().create(ename=value)


class ResultSearchFieldMixin:
    search_fields = [
        'type__icontains', 'pk__startswith'
        ]

class ResultWidget(ResultSearchFieldMixin, ModelSelect2Widget):
    model = Result

    def create_value(self, value):
        self.get_queryset().create(type=value)


class BranchSearchFieldMixin:
    dependent_fields = {'company': 'company'}
    search_fields = [
        'name__icontains', 'pk__startswith', 'company__ename__icontains', 'city__city__icontains', 'region__region__icontains',
        ]


class BranchSelect2Widget(BranchSearchFieldMixin, ModelSelect2Widget):
    model = Branch

    def create_value(self, value):
        self.get_queryset().create(name=value)


class CourseTypeSearchFieldMixin:
    search_fields = [
        'type__icontains', 'pk__startswith'
    ]

class CourseTypeSelect2Widget(CourseTypeSearchFieldMixin, ModelSelect2Widget):
    model = CourseType

    def create_value(self, value):
        self.get_queryset().create(type=value)

class TopicSearchFieldMixin:
    search_fields = [
        'topic__icontains', 'pk__startswith'
        ]
    dependent_fields = {'name': 'name'}

class TopicSelect2Widget(TopicSearchFieldMixin, ModelSelect2Widget):
    model = Topic

    def create_value(self, value):
        self.get_queryset().create(topic=value)

class CourseSearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
    ]

class CourseSelect2Widget(CourseSearchFieldMixin, ModelSelect2Widget):
    model = Course

    def create_value(self, value):
        self.get_queryset().create(name=value)

class DesignationSearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
    ]

class DesignationSelect2Widget(DesignationSearchFieldMixin, ModelSelect2Widget):
    model = Designation

    def create_value(self, value):
        self.get_queryset().create(name=value)


class ProjectSearchFieldMixin:
    search_fields = [
        'project__name__icontains', 'project__company__ename__icontains', 'companybranch__name__icontains', 'pk__startswith', 'company__ename__icontains', 'companybranch__region__region__icontains', 'companybranch__city__city__icontains',
    ]

    dependent_fields = {'companybranch': 'companybranch'}

class ProjectSelect2Widget(ProjectSearchFieldMixin, ModelSelect2Widget):
    model = ProjectPersonalDetails
    #TODO this has to filter the queryset by request.user
    def create_value(self, value):
        self.get_queryset().create(name=value)


class SkillSearchFieldMixin:
    search_fields = [
        'skill__icontains', 'pk__startswith'
    ]

class SkillModelSelect2MultipleWidget(SkillSearchFieldMixin, ModelSelect2MultipleWidget):
    model = SkillTag

    def create_value(self, value):
        self.get_queryset().create(skill=value)


class IndSearchFieldMixin:
    search_fields = [
        'industry__icontains', 'pk__startswith'
    ]

class IndSelect2Widget(IndSearchFieldMixin, ModelSelect2Widget):
    model = Industry

    def create_value(self, value):
        self.get_queryset().create(industry=value)


class RegionSearchFieldMixin:
    search_fields = [
        'region__icontains', 'pk__startswith'
    ]
    dependent_fields = {'country': 'country'}


class RegionWidget(RegionSearchFieldMixin, ModelSelect2Widget):
    model = Region

    def create_value(self, value):
        self.get_queryset().create(region=value)
#Select2<<<


class DateInput(forms.DateInput):
    input_type = 'date'


class ProfileSearchForm(forms.Form):
    query = forms.CharField()
    class Meta:
        labels = {
            'query': 'Search by Alias or Name',
        }


class AchievementsForm(forms.ModelForm):
    class Meta:
        model = Achievements
        fields = ('achievement', 'date_achieved', 'description', 'upload',)
        widgets = {
            'date_achieved': DateInput(),
            'achievement': forms.TextInput(),
        }
        labels = {
            'description': 'Achievement Description',
        }
        help_texts = {
            'achievement': 'Brief description or name of the achievement',
            'description': 'Background of what the achiement is, and what led to you receiving it.',
        }

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        talent = cleaned_data.get("talent")
        achievement = cleaned_data.get("achievement")
        date_achieved = cleaned_data.get("date_achieved")

        if Achievements.objects.filter(talent = talent, achievement = achievement, date_achieved = date_achieved).count() > 0:
            del cleaned_data["talent"]
            del cleaned_data["achievement"]
            del cleaned_data["date_achieved"]
            raise ValidationError("This achievement already exists in your profile! Please enter another.")

        return cleaned_data


class AwardsForm(forms.ModelForm):
    class Meta:
        model = Awards
        fields = ('award', 'date_achieved', 'description', 'tag', 'upload',)
        widgets = {
            'date_achieved': DateInput(),
            'award': forms.TextInput(),
            'tag': TagModelSelect2MultipleWidget(),
        }
        labels = {
            'description': 'Award Description',
        }
        help_texts = {
            'award': 'Brief description or name of the award',
            'description': 'Background of what the award is, and what led to you receiving it.',
        }

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        talent = cleaned_data.get("talent")
        award = cleaned_data.get("award")
        date_achieved = cleaned_data.get("date_achieved")

        if Awards.objects.filter(talent = talent, award = award, date_achieved = date_achieved).count() > 0:
            del cleaned_data["talent"]
            del cleaned_data["award"]
            del cleaned_data["date_achieved"]
            raise ValidationError("This award already exists in your profile! Please enter another.")

        return cleaned_data


class PublicationsForm(forms.ModelForm):
    class Meta:
        model = Publications
        fields = ('title', 'publisher', 'date_published', 'author', 'tag', 'link', 'type', 'genre', 'description', 'upload')
        widgets = {
            'publisher': PublisherSelect2Widget(),
            'tag': TagModelSelect2MultipleWidget(),
            'author': AuthorModelSelect2MultipleWidget(),
            'genre': GenreWidget(),
            'date_published': DateInput(),
        }
        help_texts = {
            'title': 'Brief description or name of the publication',
            'description': 'Background of what the publication is, and what led to you creating it.',
        }

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        talent = cleaned_data.get("talent")
        title = cleaned_data.get("title")
        date_published = cleaned_data.get("date_published")

        if Publications.objects.filter(talent = talent, title = title, date_published = date_published).count() > 0:
            del cleaned_data["talent"]
            del cleaned_data["title"]
            del cleaned_data["date_published"]
            raise ValidationError("This publication already exists in your profile! Please enter another.")

        return cleaned_data


class LicenseCertificationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_show_errors = False

    class Meta:
        model = LicenseCertification
        fields = ('certification', 'cm_no', 'companybranch', 'issue_date', 'expiry_date', 'current', 'country', 'region', 'upload', 'cert_name')
        widgets = {
            'issue_date': DateInput(),
            'expiry_date': DateInput(),
            'companybranch': CompanySelect2Widget(),
            'certification': ResultWidget(),
            'region': RegionWidget(),
        }
        labels = {
            'certification': 'License / Certification / Membership Type',
            'cm_no': 'Licence / Certification / Membership Number',
            'companybranch': 'Managing Organisation',
            'cert_name': 'Name',
        }
        help_texts = {
            'region': 'Not all certifications are region specific, in which case, this field can be blank, however some are, in which case this field must be populated.',
        }

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        talent = cleaned_data.get("talent")
        cm_no = cleaned_data.get("cm_no")

        if LicenseCertification.objects.filter(talent = talent, cm_no = cm_no).count() > 0:
            del cleaned_data["talent"]
            del cleaned_data["cm_no"]
            raise ValidationError("This license/certification already exists in your profile! Please enter another.")

        return cleaned_data


class PreLoggedExperienceForm(forms.ModelForm):
    '''Form to capture experience earned and captured on previously approved timesheets'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_show_errors = True

    class Meta:
        model = WorkExperience
        fields = ('date_from', 'date_to', 'company', 'companybranch', 'employment_type', 'project_data', 'industry', 'hours_worked', 'title', 'comment', 'designation', 'upload', 'skills',)
        widgets={
            'company': CompanySelect2Widget(),
            'companybranch': BranchSelect2Widget(),
            'designation': DesignationSelect2Widget(),
            'project_data': ProjectSelect2Widget(data_view='Project:project_data_json'),
            'date_from': DateInput(),
            'date_to': DateInput(),
            'skills': SkillModelSelect2MultipleWidget(),
            }
        lables = {
            'companybranch': 'Branch',
            'project_data': 'On Project'
        }
        help_texts = {
            'project_data': 'Search by project name, company name or branch, region or city',
        }

    def clean_date_to(self):
        '''Ensures the end date is after the begin date and before current date'''
        date_to = self.cleaned_data.get("date_to")
        date_from = self.cleaned_data.get("date_from")
        today = timezone.now().date()

        if date_to < date_from:
            raise ValidationError("You can't finish a period before it starts!, please ensure End date is after Start date.")
        elif date_to > today:
            raise ValidationError("You can't claim experience in the future! End date must be  equal to, or less than today")

        return date_to

    def clean_hours_worked(self):
        '''Ensures excessive hours per day are not claimed'''
        date_to = self.cleaned_data.get("date_to")
        date_from = self.cleaned_data.get("date_from")
        hours_worked = self.cleaned_data.get("hours_worked")
        duration = (date_to - date_from)+timedelta(days=1)
        max = duration.days * 12

        if hours_worked > max:
            raise ValidationError("You can't claim more than 12 hours per day!")

        return hours_worked

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        talent = cleaned_data.get("talent")
        hours_worked = cleaned_data.get("hours_worked")
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        course = cleaned_data.get("course")
        topic = cleaned_data.get("topic")
        company = cleaned_data.get("company")

        if WorkExperience.objects.filter(talent = talent, hours_worked = hours_worked, date_from = date_from, date_to = date_to, course = course, topic = topic, company = company).count() > 0:
            del cleaned_data["talent"]
            del cleaned_data["hours_worked"]
            del cleaned_data["date_from"]
            del cleaned_data["date_to"]
            del cleaned_data["course"]
            del cleaned_data["topic"]
            del cleaned_data["company"]
            raise ValidationError("This experience already exists in your profile! Please enter another combination.")

        return cleaned_data


class WorkClientResponseForm(forms.ModelForm):
    class Meta:
        model = WorkClient
        fields = ('response', )


class WorkClientConfirmForm(forms.ModelForm):
    class Meta:
        model = WorkClient
        fields = ('confirm', 'comments', 'quality', 'time_taken', 'complexity')

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise ValidationError("Please Confirm or Reject this claim")
        return confirm_entry


class WorkClientSelectForm(forms.ModelForm):
    class Meta:
        model = WorkClient
        fields = ('client_name', 'designation', 'company', 'companybranch', )
        widgets={
            'company': CompanySelect2Widget(),
            'designation': DesignationSelect2Widget(),
            'companybranch': BranchSelect2Widget(),
            }

        labels = {
            'companybranch': 'Branch'
        }

    pwd = None
    def __init__(self, *args, **kwargs):
        global pwd
        pwd = kwargs.pop('pwd')
        super().__init__(*args, **kwargs)
        self.fields['client_name'].queryset = CustomUser.objects.none()

        if 'client_name' in self.data:
            self.fields['client_name'].queryset = CustomUser.objects.all()

        '''
        #if the form needs to be edited, use this to pupolate the field.
        elif self.instance:
            self.fields['client_name'].queryset = CustomUser.objects.filter(pk=self.instance.[field].id)
        '''

    def clean_client_name(self):
        client_passed = self.cleaned_data.get("client_name")
        als = client_passed.id

        if als in pwd:
            raise ValidationError("This person is already in your confirmation list! Please Choose another person.")
        return client_passed


class WorkCollaboratorResponseForm(forms.ModelForm):
    class Meta:
        model = WorkCollaborator
        fields = ('response', )


class WorkCollaboratorConfirmForm(forms.ModelForm):
    class Meta:
        model = WorkCollaborator
        fields = ('confirm', 'comments', 'quality', 'time_taken', 'complexity')

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise ValidationError("Please Confirm or Reject this claim")
        return confirm_entry

class WorkCollaboratorSelectForm(forms.ModelForm):
    class Meta:
        model = WorkCollaborator
        fields = ('collaborator_name', 'designation', 'company', 'companybranch', )
        widgets={
            'company': CompanySelect2Widget(),
            'designation': DesignationSelect2Widget(),
            'companybranch': BranchSelect2Widget(),
            }

        labels = {
            'companybranch': 'Branch'
        }

    pwd = None
    def __init__(self, *args, **kwargs):
        global pwd
        pwd = kwargs.pop('pwd')
        super().__init__(*args, **kwargs)
        self.fields['collaborator_name'].queryset = CustomUser.objects.none()

        if 'collaborator_name' in self.data:
            self.fields['collaborator_name'].queryset = CustomUser.objects.all()

        '''
        #if the form needs to be edited, use this to pupolate the field.
        elif self.instance:
            self.fields['collaborator_name'].queryset = CustomUser.objects.filter(pk=self.instance.[field].id)
        '''

    def clean_collaborator_name(self):
        collaborator_passed = self.cleaned_data.get("collaborator_name")
        als = collaborator_passed.id

        if als in pwd:
            raise ValidationError("This person is already in your confirmation list! Please Choose another person.")
        return collaborator_passed

class SuperiorResponseForm(forms.ModelForm):
    class Meta:
        model = Superior
        fields = ('response', )


class SuperiorConfirmForm(forms.ModelForm):
    class Meta:
        model = Superior
        fields = ('confirm', 'comments', 'quality', 'time_taken', 'complexity')

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise ValidationError("Please Confirm or Reject this claim")
        return confirm_entry

class SuperiorSelectForm(forms.ModelForm):
    class Meta:
        model = Superior
        fields = ('superior_name', 'designation', )
        widgets={
            'designation': DesignationSelect2Widget(),
            }

    pwd = None
    def __init__(self, *args, **kwargs):
        global pwd
        pwd = kwargs.pop('pwd')
        super().__init__(*args, **kwargs)
        self.fields['superior_name'].queryset = CustomUser.objects.none()

        if 'superior_name' in self.data:
            self.fields['superior_name'].queryset = CustomUser.objects.all()

        '''
        #if the form needs to be edited, use this to pupolate the field.
        elif self.instance:
            self.fields['superior_name'].queryset = CustomUser.objects.filter(pk=self.instance.[field].id)
        '''

    def clean_superior_name(self):
        superior_passed = self.cleaned_data.get("superior_name")
        als = superior_passed.id

        if als in pwd:
            raise ValidationError("This person is already in your confirmation list! Please Choose another person.")
        return superior_passed


class WorkColleagueResponseForm(forms.ModelForm):
    class Meta:
        model = WorkColleague
        fields = ('response', )


class WorkColleagueConfirmForm(forms.ModelForm):
    class Meta:
        model = WorkColleague
        fields = ('confirm', 'comments', 'quality', 'time_taken', 'complexity')

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise ValidationError("Please Confirm or Reject this claim")
        return confirm_entry


class WorkColleagueSelectForm(forms.ModelForm):
    pwd = None

    class Meta:
        model = WorkColleague
        fields = ('colleague_name', 'designation')
        widgets={
            'designation': DesignationSelect2Widget(),
            }
    def __init__(self, *args, **kwargs):
        global pwd
        pwd = kwargs.pop('pwd')
        super().__init__(*args, **kwargs)
        self.fields['colleague_name'].queryset = CustomUser.objects.none()

        if 'colleague_name' in self.data:
            self.fields['colleague_name'].queryset = CustomUser.objects.all()

        '''
        #if the form needs to be edited, use this to pupolate the field.
        elif self.instance:
            self.fields['colleague_name'].queryset = CustomUser.objects.filter(pk=self.instance.[field].id)
        '''

    def clean_colleague_name(self):
        colleague_passed = self.cleaned_data.get("colleague_name")
        als = colleague_passed.id
        if als in pwd:
            raise ValidationError("This person is already in your confirmation list! Please Choose another person.")
        else:
            return colleague_passed

class WorkExperienceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_show_errors = True

    class Meta:
        model = WorkExperience
        fields = (
            'date_from', 'date_to', 'company', 'companybranch', 'employment_type', 'estimated', 'project_data', 'industry', 'hours_worked', 'title', 'comment', 'designation', 'upload', 'skills'
            )
        widgets={
            'company': CompanySelect2Widget(),
            'designation': DesignationSelect2Widget(),
            'project_data': ProjectSelect2Widget(data_view='Project:project_data_json'),
            'date_from': DateInput(),
            'date_to': DateInput(),
            'skills': SkillModelSelect2MultipleWidget(),
            'industry': IndSelect2Widget(),
            'companybranch': BranchSelect2Widget(),
            }
        labels = {
            'hours_worked': 'Hours',
            'companybranch': 'Branch',
            'upload': 'Upload File (Optional)',
            'comment': 'Comment (Optional)',
            'project_data': 'On Project'
        }
        help_texts = {
            'project_data': 'Search by project name, company name or branch, region or city',
        }

    def clean_date_to(self):
        '''Ensures the end date is after the begin date and before current date'''
        date_to = self.cleaned_data.get("date_to")
        date_from = self.cleaned_data.get("date_from")
        today = timezone.now().date()

        if date_to < date_from:
            raise ValidationError("You can't finish a period before it starts!, please ensure End date is after Start date.")
        if date_to > today:
            raise ValidationError("You can't claim experience in the future! End date must be equal to, or less than today")

        return date_to

    def clean_hours_worked(self):
        '''Ensures excessive hours per day are not claimed'''
        date_to = self.cleaned_data.get("date_to")
        date_from = self.cleaned_data.get("date_from")
        hours_worked = self.cleaned_data.get("hours_worked")
        duration = (date_to - date_from)+timedelta(days=1)
        max = duration.days * 12

        if hours_worked > max:
            raise ValidationError("You can't claim more than 12 hours per day!")

        return hours_worked

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        talent = cleaned_data.get("talent")
        hours_worked = cleaned_data.get("hours_worked")
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        course = cleaned_data.get("course")
        topic = cleaned_data.get("topic")
        company = cleaned_data.get("company")

        if WorkExperience.objects.filter(talent = talent, hours_worked = hours_worked, date_from = date_from, date_to = date_to, course = course, topic = topic, company = company).count() > 0:
            del cleaned_data["talent"]
            del cleaned_data["hours_worked"]
            del cleaned_data["date_from"]
            del cleaned_data["date_to"]
            del cleaned_data["course"]
            del cleaned_data["topic"]
            del cleaned_data["company"]
            raise ValidationError("This experience already exists in your profile! Please enter another combination.")

        return cleaned_data


class DesignationForm(forms.ModelForm):
    pwd = None
    def __init__(self, *args, **kwargs):
        global pwd
        pwd = kwargs.pop('pwd')
        super().__init__(*args, **kwargs)

    class Meta:
        model = Designation
        fields = ('name', )

    def clean_designation(self):
        designation_passed = self.cleaned_data.get("name")
        als = designation_passed

        if als in pwd:
            raise ValidationError("An entry with this designation type has already been captured! Please enter another designation.")
        return designation_passed


class ClassMatesCommentForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('comments', 'confirm',)

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise ValidationError("Please Confirm or Reject this claim")
        return confirm_entry

class ClassMatesResponseForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('response', )


class ClassMatesSelectForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('colleague',)
        labels = {
            'colleague': 'Classmate',
            }

    pwd = None
    def __init__(self, *args, **kwargs):
        global pwd
        pwd = kwargs.pop('pwd')
        super().__init__(*args, **kwargs)
        self.fields['colleague'].queryset = CustomUser.objects.none()

        if 'colleague' in self.data:
            self.fields['colleague'].queryset = CustomUser.objects.all()

        '''
        #if the form needs to be edited, use this to pupolate the field.
        elif self.instance:
            self.fields['colleague'].queryset = CustomUser.objects.filter(pk=self.instance.[field].id)
        '''

    def clean_colleague(self):
        colleague_passed = self.cleaned_data.get("colleague")
        als = colleague_passed.id

        if als in pwd:
            raise ValidationError("This person is already in your confirmation list! Please Choose another person.")
        return colleague_passed


class ClassMatesConfirmForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('confirm', 'comments')

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise ValidationError("Please Confirm or Reject this claim")
        return confirm_entry


class LecturerCommentForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('comments', 'confirm',)

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise ValidationError("Please Confirm or Reject this claim")
        return confirm_entry


class LecturerResponseForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('response',)


class ClassMatesRespondForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('response',)


class LecturerSelectForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('lecturer',)

    pwd = None
    def __init__(self, *args, **kwargs):
        global pwd
        pwd = kwargs.pop('pwd')
        super().__init__(*args, **kwargs)

        self.fields['lecturer'].queryset = CustomUser.objects.none()

        if 'lecturer' in self.data:
            self.fields['lecturer'].queryset = CustomUser.objects.all()

        '''
        #if the form needs to be edited, use this to pupolate the field.
        elif self.instance:
            self.fields['lecturer'].queryset = CustomUser.objects.filter(pk=self.instance.[field].id)
        '''

    def clean_lecturer(self):
        lecturer_passed = self.cleaned_data.get("lecturer")
        als = lecturer_passed.id
        if als in pwd:
            raise ValidationError("This person is already in your confirmation list! Please Choose another person.")
        return lecturer_passed


class LecturerConfirmForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('confirm', 'comments')

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise ValidationError("Please Confirm or Reject this claim")
        return confirm_entry

class LecturerRespondForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('response',)


#Combined into WorkExperience table (20191210)
class EducationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EducationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_show_errors = False

    class Meta:
        model = WorkExperience
        fields = ('course', 'date_from', 'date_to', 'topic', 'employment_type', 'upload', 'comment',)
        widgets={
            'course': CourseSelect2Widget(),
            'topic': TopicSelect2Widget(),
            'date_from': DateInput(),
            'date_to': DateInput(),
        }
        labels = {
            'course': 'Course Name',
            'topic' : 'Course Subject',
            'comment': 'Comment (Optional)',
            'upload': 'File Upload (Optional)',
        }

    def clean_date_to(self):
        '''Ensures the end date is after the begin date and before current date'''
        date_to = self.cleaned_data.get("date_to")
        date_from = self.cleaned_data.get("date_from")
        today = timezone.now().date()

        if date_to < date_from:
            raise ValidationError("You can't finish a period before it starts!, please ensure End date is after Start date.")
        elif date_to > today:
            raise ValidationError("You can't claim experience in the future! End date must be  equal to, or less than today")

        return date_to

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        talent = cleaned_data.get("talent")
        hours_worked = cleaned_data.get("hours_worked")
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        course = cleaned_data.get("course")
        topic = cleaned_data.get("topic")
        company = cleaned_data.get("company")

        if WorkExperience.objects.filter(talent = talent, hours_worked = hours_worked, date_from = date_from, date_to = date_to, course = course, topic = topic, company = company).count() > 0:
            del cleaned_data["talent"]
            del cleaned_data["hours_worked"]
            del cleaned_data["date_from"]
            del cleaned_data["date_to"]
            del cleaned_data["course"]
            del cleaned_data["topic"]
            del cleaned_data["company"]
            raise ValidationError("This experience already exists in your profile! Please enter another combination.")

        return cleaned_data


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('name', 'company', 'course_type', 'website', 'certification')
        widgets={
            'company': CompanySelect2Widget(),
            'course_type': CourseTypeSelect2Widget(),
        }

    def clean_unique(self):
        '''Error message for unique_together condition in this model'''
        cleaned_data = self.cleaned_data

        name = cleaned_data.get("name")
        company = cleaned_data.get("company")

        if Course.objects.filter(name = name, company = company).count() > 0:
            del cleaned_data["name"]
            del cleaned_data["company"]
            raise ValidationError("This course already exists for the company! Please enter another combination or select the existing combination.")

        return cleaned_data


class CourseTypeForm(forms.ModelForm):
    class Meta:
        model = CourseType
        fields = ('type',)


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ('type',)


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('topic', 'hours', 'skills')
        widgets={
            'skills': SkillModelSelect2MultipleWidget(),
            }


class TopicPopForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('topic', 'hours', 'skills')
        widgets={
            'skills': SkillModelSelect2MultipleWidget(),
            }


class SiteSkillStatsFilter(forms.Form):
    country = CountryField(blank=True).formfield()
    region = forms.CharField(max_length=30, required=False)
    designation = forms.CharField(max_length=30, required=False)
    industry = forms.CharField(max_length=30, required=False)
    date_from = forms.DateField(required=False, widget=DateInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    date_to = forms.DateField(required=False, widget=DateInput(attrs={'placeholder': 'YYYY-MM-DD'}))

    def __init__(self, *args, **kwargs):
        _country_list = kwargs.pop('data_list', None)
        super(SiteSkillStatsFilter, self).__init__(*args, **kwargs)

#        self.fields['designation'].widget = ListTextWidget(data_list=Designation.objects.all().only('name'), name='designation-list')
#        self.fields['industry'].widget = ListTextWidget(data_list=Industry.objects.all().only('industry'), name='industry-list')

    class Meta():
        fields = ('country', 'region', 'designation', 'industry', 'date_from', 'date_to')


class SiteDemandSkillStatsFilter(forms.Form):
    WTPE = (
        ('',''),
        ('Remote freelance','Remote freelance'),
        ('Freelance','Freelance'),
        ('Consultant','Consultant'),
        ('Contractor','Contractor'),
        ('Employee','Employee'),
        ('FiFo','FiFo'),
    )

    LEVEL = (
        ('',''),
        (0,'Student'),
        (1,'Beginner'),
        (2,'Junior'),
        (3,'Intermediate'),
        (4,'Senior'),
        (5,'Lead'),
    )

    country = CountryField(blank=True).formfield()
    worklocation = forms.ChoiceField(required=False, choices=WTPE)
    designation = forms.CharField(max_length=30, required=False)
    experience_level = forms.ChoiceField(required=False, choices=LEVEL)
    title = forms.CharField(max_length=30, required=False)
    date_entered = forms.DateField(required=False, widget=DateInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    date_to = forms.DateField(required=False, widget=DateInput(attrs={'placeholder': 'YYYY-MM-DD'}))

# the "name" parameter will allow you to use the same widget more than once in the same
# form, not setting this parameter differently will cuse all inputs display the same list.

    def __init__(self, *args, **kwargs):
        _country_list = kwargs.pop('data_list', None)
        super(SiteDemandSkillStatsFilter, self).__init__(*args, **kwargs)

        #moved to vies.py to incorporate query
#        self.fields['designation'].widget = ListTextWidget(data_list=Designation.objects.all().only('name'), name='designation-list')
#        self.fields['title'].widget = ListTextWidget(data_list=TalentRequired.objects.filter(pk=vac_list_qs_id).values_list('title', flat=True).distinct(), name='title-list')

    class Meta():
        fields = ('country', 'worklocation', 'designation', 'title', 'experience_level', 'date_entered', 'date_to')
