from django import forms
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django.db.models import Q

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


from django_select2.forms import (
    ModelSelect2TagWidget, ModelSelect2Widget, ModelSelect2MultipleWidget,
    Select2Widget, Select2MultipleWidget
)

from .models import (
    Topic, Result, CourseType, Course, Lecturer, ClassMates, WorkClient, WorkExperience, WorkColleague, Superior, WorkCollaborator, Designation
    )

from enterprises.models import Enterprise, Branch
from project.models import ProjectData
from db_flatten.models import SkillTag
from enterprises.models import Industry
from users.models import CustomUser

#>>> Select 2
class UserSearchFieldMixin:
    search_fields = [
        'last_name__icontains', 'pk__startswith', 'first_name__icontains',
    ]
class UserSelect2Widget(UserSearchFieldMixin, ModelSelect2Widget):
    model = CustomUser

    def create_value(self, value):
        self.get_queryset().create(Q(last_name=value) | Q(first_name=value))


class CompanySearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
        ]

class CompanySelect2Widget(CompanySearchFieldMixin, ModelSelect2Widget):
    model = Enterprise

    def create_value(self, value):
        self.get_queryset().create(name=value)


class BranchSearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
        ]
    dependent_fields = {'company': 'company'}

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
        'name__icontains', 'pk__startswith'
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
#Select2<<<


class DateInput(forms.DateInput):
    input_type = 'date'


class PreLoggedExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ('date_from', 'date_to', 'company', 'project', 'industry', 'hours_worked', 'comment', 'designation', 'upload', 'skills',)
        widgets={
            'company': CompanySelect2Widget(),
            'designation': DesignationSelect2Widget(),
            'project': ProjectSelect2Widget(),
            'date_from': DateInput(),
            'date_to': DateInput(),
            'skills': SkillModelSelect2MultipleWidget(),
            }


class WorkClientResponseForm(forms.ModelForm):
    class Meta:
        model = WorkClient
        fields = ('response', )


class WorkClientConfirmForm(forms.ModelForm):
    class Meta:
        model = WorkClient
        fields = ('confirm', 'comments', )


class WorkClientSelectForm(forms.ModelForm):
    class Meta:
        model = WorkClient
        fields = ('client_name', 'designation', 'company', 'branch', )
        widgets={
            'enterprise': CompanySelect2Widget(),
            'client_name': UserSelect2Widget(),
            'designation': DesignationSelect2Widget(),
            'branch': BranchSelect2Widget(),
            }


class WorkCollaboratorResponseForm(forms.ModelForm):
    class Meta:
        model = WorkCollaborator
        fields = ('response', )


class WorkCollaboratorConfirmForm(forms.ModelForm):
    class Meta:
        model = WorkCollaborator
        fields = ('confirm', 'comments', )


class WorkCollaboratorSelectForm(forms.ModelForm):
    class Meta:
        model = WorkCollaborator
        fields = ('collaborator_name', 'designation', 'company', 'branch', )
        widgets={
            'enterprise': CompanySelect2Widget(),
            'superior_name': UserSelect2Widget(),
            'designation': DesignationSelect2Widget(),
            'branch': BranchSelect2Widget(),
            }


class SuperiorResponseForm(forms.ModelForm):
    class Meta:
        model = Superior
        fields = ('response', )


class SuperiorConfirmForm(forms.ModelForm):
    class Meta:
        model = Superior
        fields = ('confirm', 'comments', )


class SuperiorSelectForm(forms.ModelForm):
    class Meta:
        model = Superior
        fields = ('superior_name', 'designation', )
        widgets={
            'superior_name': UserSelect2Widget(),
            'designation': DesignationSelect2Widget(),
            }

class WorkColleagueResponseForm(forms.ModelForm):
    class Meta:
        model = WorkColleague
        fields = ('response', )


class WorkColleagueConfirmForm(forms.ModelForm):
    class Meta:
        model = WorkColleague
        fields = ('confirm', 'comments')


class WorkColleagueSelectForm(forms.ModelForm):
    class Meta:
        model = WorkColleague
        fields = ('colleague_name', 'designation')
        widgets={
            'colleague_name': UserSelect2Widget(),
            'designation': DesignationSelect2Widget(),
            }

class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = (
            'date_from', 'date_to', 'company', 'estimated', 'project', 'industry', 'hours_worked', 'comment', 'designation', 'upload', 'skills'
            )
        widgets={
            'company': CompanySelect2Widget(),
            'designation': DesignationSelect2Widget(),
            'project': ProjectSelect2Widget(),
            'date_from': DateInput(),
            'date_to': DateInput(),
            'skills': SkillModelSelect2MultipleWidget(),
            'industry': IndSelect2Widget(),
}


class DesignationForm(forms.ModelForm):
    class Meta:
        model = Designation
        fields = ('name', )


class ClassMatesCommentForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('comments', 'confirm',)


class ClassMatesResponseForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('response', )


class ClassMatesSelectForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('colleague', 'topic',)
        widgets={
            'topic': TopicSelect2Widget(),
            'colleague': UserSelect2Widget(),
            }

class ClassMatesConfirmForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('confirm', 'comments')


class LecturerCommentForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('comments', 'confirm',)


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
        fields = ('lecturer', 'topic',)
        widgets={
            'topic': TopicSelect2Widget(),
            'lecturer': UserSelect2Widget(),
            }

class LecturerConfirmForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('confirm', 'comments')


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
        }


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
