from django import forms
from django.utils.translation import gettext_lazy as _

from django_select2.forms import (
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)

from django.contrib.contenttypes import fields
from .MinimalSplitDateTimeMultiWidget import MinimalSplitDateTimeMultiWidget

from schedule.models import Event, Occurrence, Rule
from schedule.widgets import ColorInput
from project.models import ProjectPersonalDetails, ProjectPersonalDetailsTask
from enterprises.models import Branch

from talenttrack.forms import ProjectSelect2Widget, SkillModelSelect2MultipleWidget
from enterprises.forms import FullCompanyBranchSelect2Widget


class DateInput(forms.DateInput):
    input_type = 'date'


class ProjectPersonalTaskSearchFieldMixin:
    search_fields = [
        'task__icontains', 'pk__startswith', 'ppd__project__company__ename__icontains', 'company__company__ename__icontains', 'client__name__icontains',
    ]

    dependent_fields = {'ppd': 'ppd'}

class ProjectPersonalTaskSelect2Widget(ProjectPersonalTaskSearchFieldMixin, ModelSelect2Widget):
    model = ProjectPersonalDetailsTask

    def create_value(self, value):
        self.get_queryset().create(name=value)


class RuleSearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith',
    ]

class RuleSelect2Widget(RuleSearchFieldMixin, ModelSelect2Widget):
    model = Rule

    def create_value(self, value):
        self.get_queryset().create(name=value)


class SpanForm(forms.ModelForm):
    start = forms.DateTimeField(widget=MinimalSplitDateTimeMultiWidget(), label=_("start"))
    end = forms.DateTimeField(
            widget=MinimalSplitDateTimeMultiWidget(),
            required=False,
            label=_("end"),
            help_text=_("The end time must be later than start time.")
    )
    end_recurring_period = forms.DateTimeField(widget=MinimalSplitDateTimeMultiWidget(), required=False)

    def clean(self):
        if "end" in self.cleaned_data and "start" in self.cleaned_data:
            if self.cleaned_data["end"] <= self.cleaned_data["start"]:
                raise forms.ValidationError(
                    _("The end time must be later than start time.")
                )
        return self.cleaned_data


class EventForm(SpanForm):

    class Meta:
        model = Event
        exclude = ("creator", "created_on", "calendar")
        widgets={
            'project_data': ProjectSelect2Widget(data_view='project_data_json'),
            'companybranch': FullCompanyBranchSelect2Widget(),
            'task': ProjectPersonalTaskSelect2Widget(data_view='project_task_data_json'),
            'skills': SkillModelSelect2MultipleWidget(),
            'rule': RuleSelect2Widget(data_view='rule_data_json'),
        }
        help_texts = {
            'project_data': 'Search by project name, company name or branch, region or city',
            'companybranch': 'Search by company name, branch, region or city',
            'tasks': 'Search by task, company name or client name',
            'skills': '<button class="btn badge btn-outline-primary float-right" id="clear-skills" type="button" name="button">Clear Skills</button>'
        }

class OccurrenceForm(SpanForm):
    class Meta:
        model = Occurrence
        exclude = ("original_start", "original_end", "event", "cancelled")
        widgets={
            'project_data': ProjectSelect2Widget(data_view='project_data_json'),
            'companybranch': FullCompanyBranchSelect2Widget(),
            'task': ProjectPersonalTaskSelect2Widget(data_view='project_task_data_json'),
            'skills': SkillModelSelect2MultipleWidget(),
            'rule': RuleSelect2Widget(data_view='rule_data_json'),
        }
        help_texts = {
            'project_data': 'Search by project name, company name or branch, region or city',
            'companybranch': 'Search by company name, branch, region or city',
            'tasks': 'Search by task, company name or client name',
            'skills': '<button class="btn badge btn-outline-primary float-right" id="clear-skills" type="button" name="button">Clear Skills</button>'
        }

class EventAdminForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = Event
        widgets = {"color_event": ColorInput}


class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        exclude = ('talent',)
        help_texts = {
                'name': 'Enter a recognisable name for the rule',
                'params': 'Enter your tailor made parameters for the rule',
        }
