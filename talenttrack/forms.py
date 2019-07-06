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
    Topic, Result, CourseType, Course, Education, Lecturer, ClassMates, WorkClient, WorkExperience, WorkColleague, Superior, WorkCollaborator, PreLoggedExperience, PreColleague, Designation
    )

from enterprises.models import Enterprise
from project.models import ProjectData


#>>> Select 2
class CompanySearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
    ]
class CompanySelect2Widget(CompanySearchFieldMixin, ModelSelect2Widget):
    model = Enterprise

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
#Select2<<<


class PreColleagueResponseForm(forms.ModelForm):
    class Meta:
        model = PreColleague
        fields = ('response',)


class PreColleagueConfirmForm(forms.ModelForm):
    class Meta:
        model = PreColleague
        fields = ('confirm', 'comments')


class PreColleagueSelectForm(forms.ModelForm):
    class Meta:
        model = PreColleague
        fields = ('colleague_name', 'designation')
        widgets={
        'designation': DesignationSelect2Widget(),
        }

class PreLoggedExperienceForm(forms.ModelForm):
    class Meta:
        model = PreLoggedExperience
        fields = ('date_from', 'date_to', 'enterprise', 'project', 'industry', 'hours_worked', 'comment', 'designation', 'upload', 'skills',)
        widgets={
            'enterprise': CompanySelect2Widget(),
            'designation': DesignationSelect2Widget(),
            'project': ProjectSelect2Widget(),
            #'skills': SkillsXXXWidget(),
            }


class WorkClientResponseForm(forms.ModelForm):
    class Meta:
        form = WorkClient
        fields = ('response', )


class WorkClientConfirmForm(forms.ModelForm):
    class Meta:
        form = WorkClient
        fields = ('confirm', 'comments', )


class WorkClientSelectForm(forms.ModelForm):
    class Meta:
        form = WorkClient
        fields = ('client_name', 'designation', 'company' )
        widgets={
            'enterprise': CompanySelect2Widget(),
            }

class WorkCollaboratorResponseForm(forms.ModelForm):
    class Meta:
        form = WorkCollaborator
        fields = ('response', )


class WorkCollaboratorConfirmForm(forms.ModelForm):
    class Meta:
        form = WorkCollaborator
        fields = ('confirm', 'comments', )


class WorkCollaboratorSelectForm(forms.ModelForm):
    class Meta:
        form = WorkCollaborator
        fields = ('collaborator_name', 'designation', 'company' )
        widgets={
            'enterprise': CompanySelect2Widget(),
            }

class SuperiorResponseForm(forms.ModelForm):
    class Meta:
        form = Superior
        fields = ('response', )


class SuperiorConfirmForm(forms.ModelForm):
    class Meta:
        form = Superior
        fields = ('confirm', 'comments', )


class SuperiorSelectForm(forms.ModelForm):
    class Meta:
        form = Superior
        fields = ('superior_name', 'designation', )


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

}

class DesignationForm(forms.ModelForm):
    class Meta:
        model = Designation
        fields = ('name', )


class ClassMatesResponseForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('response', )


class ClassMatesSelectForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('colleague',)


class ClassMatesConfirmForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('confirm', 'comments')


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


class LecturerConfirmForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('confirm', 'comments')


class LecturerRespondForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('response',)

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ('course', 'date_from', 'date_to', 'topic', 'file', 'hours_worked')
        widgets={
            'course': CourseSelect2Widget(),
            'topic': TopicSelect2Widget(),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('name', 'company', 'course_type', 'website', 'skills', 'certification')
        widgets={
            'company': CompanySelect2Widget(),
            'course_type': CourseTypeSelect2Widget(),
            #'skills': SkillsXXXWidget(),
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
        fields = ('topic', 'course')


class TopicPopForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('topic',)
