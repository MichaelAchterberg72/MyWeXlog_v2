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
    Topic, Result, CourseType, Course, Education, Lecturer, ClassMates, WorkClient, WorkExperience, WorkColleague, Superior, WorkCollaborator, PreLoggedExperience, PreColleague
    )

from enterprises.models import Enterprise


from .forms import (
        TopicForm, ResultForm, ResultTypeForm, CourseForm
)


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
#Select2<<<


class ClassMatesSelectForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('colleague',)


class ClassMatesConfirmForm(forms.ModelForm):
    class Meta:
        model = ClassMates
        fields = ('confirm', 'comments')


class LecturerSelectForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('lecturer',)


class LecturerConfirmForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ('confirm', 'comments')


class Education(forms.ModelForm):
    class Meta:
        model = Education
        fields = ('course', 'date_from', 'date_to', 'subject', 'certification', 'file')
        widgets={
            'course': CompanySelect2Widget(),
            'subject': CourseTypeSelect2Widget(),
            #'skills': SkillsXXXWidget(),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('name', 'institution', 'course_type', 'website', 'skills')
        widgets={
            'institution': CompanySelect2Widget(),
            'course_type': CourseTypeSelect2Widget(),
            #'skills': SkillsXXXWidget(),
        }

class ResultTypeForm(forms.ModelForm):
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
        fields = ('topic',)
