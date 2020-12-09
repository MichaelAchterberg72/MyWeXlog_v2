from django import forms
from django.contrib.auth.models import User
from users.models import CustomUser
from django.utils.encoding import force_text
from django.db.models import Q
from django.forms import ModelChoiceField
from django.utils import timezone

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


from django_select2.forms import (
    ModelSelect2TagWidget, ModelSelect2Widget, ModelSelect2MultipleWidget,
    Select2Widget, Select2MultipleWidget, HeavySelect2MultipleWidget
)

from .models import (
    Topic, Result, CourseType, Course, Lecturer, ClassMates, WorkClient, WorkExperience, WorkColleague, Superior, WorkCollaborator, Designation, Achievements, LicenseCertification
    )

from enterprises.models import Enterprise, Branch, Industry
from project.models import ProjectData
from db_flatten.models import SkillTag
from users.models import CustomUser
from locations.models import Region


class EmailFormModal(forms.Form):
    recipient = forms.EmailField(label='To', max_length=40)
    sender = forms.EmailField(label='From', max_length=40)
    subject = forms.CharField(label='Subject', max_length=120)
    message = forms.CharField(label='Message', widget=forms.Textarea, max_length=300)

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
        'name__icontains', 'pk__startswith', 'company__ename__icontains', 'region__region__icontains', 'city__city__icontains',
    ]


class ProjectSelect2Widget(ProjectSearchFieldMixin, ModelSelect2Widget):
    model = ProjectData

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


class LicenseCertificationForm(forms.ModelForm):
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
            'issue_date': 'The date the license / certification / membership was first held.',
            'expiry_date': 'The date the license / certification / membership expires (Leave Blank if never expires).',
            'current': 'Is the license / certification / membership currently valid?',
            'region': 'Not all certifications are region specific, in which case, this field can be blank, however some are, in which case this field must be populated.',
        }

class PreLoggedExperienceForm(forms.ModelForm):
    '''Form to capture experience earned and captured on previously approved timesheets'''
    class Meta:
        model = WorkExperience
        fields = ('date_from', 'date_to', 'company', 'companybranch', 'project', 'industry', 'hours_worked', 'comment', 'designation', 'upload', 'skills',)
        widgets={
            'company': CompanySelect2Widget(),
            'companybranch': BranchSelect2Widget(),
            'designation': DesignationSelect2Widget(),
            'project': ProjectSelect2Widget(),
            'date_from': DateInput(),
            'date_to': DateInput(),
            'skills': SkillModelSelect2MultipleWidget(),
            }
        lables = {
            'companybranch': 'Branch',
        }
        help_texts = {
            'company': 'Please complete the Company field before the Branch Field',
            'companybranch': 'This field is dependant on the Company Field - fill Company Field first',
        }

    def clean_date_to(self):
        '''Ensures the end date is after the begin date and before current date'''
        date_to = self.cleaned_data.get("date_to")
        date_from = self.cleaned_data.get("date_from")
        today = timezone.now().date()

        if date_to < date_from:
            raise forms.ValidationError("You can't finish a period before it starts!, please ensure End date is after Start date.")
        elif date_to > today:
            raise forms.ValidationError("You can't claim experience in the future! End date must be  equal to, or less than today")

        return date_to

    def clean_hours_worked(self):
        '''Ensures excessive hours per day are not claimed'''
        date_to = self.cleaned_data.get("date_to")
        date_from = self.cleaned_data.get("date_from")
        hours_worked = self.cleaned_data.get("hours_worked")
        duration = date_to - date_from
        max = duration.days * 12

        if hours_worked > max:
            raise forms.ValidationError("You can't claim more than 12 hours per day!")

        return hours_worked

class WorkClientResponseForm(forms.ModelForm):
    class Meta:
        model = WorkClient
        fields = ('response', )


class WorkClientConfirmForm(forms.ModelForm):
    class Meta:
        model = WorkClient
        fields = ('confirm', 'comments', )

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise forms.ValidationError("Please Confirm or Reject this claim")
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
            raise forms.ValidationError("This person is already in your confirmation list! Please Choose another person.")
        return client_passed


class WorkCollaboratorResponseForm(forms.ModelForm):
    class Meta:
        model = WorkCollaborator
        fields = ('response', )


class WorkCollaboratorConfirmForm(forms.ModelForm):
    class Meta:
        model = WorkCollaborator
        fields = ('confirm', 'comments', )

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise forms.ValidationError("Please Confirm or Reject this claim")
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
            raise forms.ValidationError("This person is already in your confirmation list! Please Choose another person.")
        return collaborator_passed

class SuperiorResponseForm(forms.ModelForm):
    class Meta:
        model = Superior
        fields = ('response', )


class SuperiorConfirmForm(forms.ModelForm):
    class Meta:
        model = Superior
        fields = ('confirm', 'comments', )

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise forms.ValidationError("Please Confirm or Reject this claim")
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
            raise forms.ValidationError("This person is already in your confirmation list! Please Choose another person.")
        return superior_passed


class WorkColleagueResponseForm(forms.ModelForm):
    class Meta:
        model = WorkColleague
        fields = ('response', )


class WorkColleagueConfirmForm(forms.ModelForm):
    class Meta:
        model = WorkColleague
        fields = ('confirm', 'comments')

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise forms.ValidationError("Please Confirm or Reject this claim")
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
            raise forms.ValidationError("This person is already in your confirmation list! Please Choose another person.")
        else:
            return colleague_passed

class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = (
            'date_from', 'date_to', 'company', 'companybranch', 'estimated', 'project', 'industry', 'hours_worked', 'comment', 'designation', 'upload', 'skills'
            )
        widgets={
            'company': CompanySelect2Widget(),
            'designation': DesignationSelect2Widget(),
            'project': ProjectSelect2Widget(),
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
        }
        help_texts = {
            'company': 'Please complete the Company field before the Branch Field',
            'companybranch': 'This field is dependant on the Company Field - fill Company Field first',
        }

    def clean_date_to(self):
        '''Ensures the end date is after the begin date and before current date'''
        date_to = self.cleaned_data.get("date_to")
        date_from = self.cleaned_data.get("date_from")
        today = timezone.now().date()

        if date_to < date_from:
            raise forms.ValidationError("You can't finish a period before it starts!, please ensure End date is after Start date.")
        if date_to > today:
            raise forms.ValidationError("You can't claim experience in the future! End date must be equal to, or less than today")

        return date_to

    def clean_hours_worked(self):
        '''Ensures excessive hours per day are not claimed'''
        date_to = self.cleaned_data.get("date_to")
        date_from = self.cleaned_data.get("date_from")
        hours_worked = self.cleaned_data.get("hours_worked")
        duration = date_to - date_from
        max = duration.days * 12

        if hours_worked > max:
            raise forms.ValidationError("You can't claim more than 12 hours per day!")

        return hours_worked


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
            raise forms.ValidationError("An entry with this designation type has already been captured! Please enter another designation.")
        return designation_passed


class ClassMatesCommentForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('comments', 'confirm',)

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise forms.ValidationError("Please Confirm or Reject this claim")
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
            raise forms.ValidationError("This person is already in your confirmation list! Please Choose another person.")
        return colleague_passed


class ClassMatesConfirmForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('confirm', 'comments')

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise forms.ValidationError("Please Confirm or Reject this claim")
        return confirm_entry


class LecturerCommentForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('comments', 'confirm',)

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise forms.ValidationError("Please Confirm or Reject this claim")
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
            raise forms.ValidationError("This person is already in your confirmation list! Please Choose another person.")
        return lecturer_passed


class LecturerConfirmForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('confirm', 'comments')

    def clean_confirm(self):
        confirm_entry = self.cleaned_data.get("confirm")

        if confirm_entry == 'S':
            raise forms.ValidationError("Please Confirm or Reject this claim")
        return confirm_entry

class LecturerRespondForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('response',)


#Combined into WorkExperience table (20191210)
class EducationForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ('course', 'date_from', 'date_to', 'topic', 'upload', 'comment',)
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
            raise forms.ValidationError("You can't finish a period before it starts!, please ensure End date is after Start date.")
        elif date_to > today:
            raise forms.ValidationError("You can't claim experience in the future! End date must be  equal to, or less than today")

        return date_to


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('name', 'company', 'course_type', 'website', 'certification')
        widgets={
            'company': CompanySelect2Widget(),
            'course_type': CourseTypeSelect2Widget(),
        }


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
