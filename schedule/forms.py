from django import forms
from django.utils.translation import gettext_lazy as _

from django_select2.forms import (
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)

from schedule.models import Event, Occurrence
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


class SpanForm(forms.ModelForm):
    start = forms.SplitDateTimeField(label=_("start"))
    end = forms.SplitDateTimeField(
        label=_("end"), help_text=_("The end time must be later than start time.")
    )

    def clean(self):
        if "end" in self.cleaned_data and "start" in self.cleaned_data:
            if self.cleaned_data["end"] <= self.cleaned_data["start"]:
                raise forms.ValidationError(
                    _("The end time must be later than start time.")
                )
        return self.cleaned_data


class EventForm(SpanForm):
#    companybranch = forms.ModelChoiceField(queryset=None, required=False)

#    prj_co_qs = ProjectPersonalDetails.objects.filter(talent=request.user).values_list(companybranch__id, flat=True).distinct()
#    company_qs = Branch.objects.filter(prj_co_qs__in=pk)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
#        self.fields['companybranch'].queryset = company_qs


    end_recurring_period = forms.DateTimeField(
        label=_("End recurring period"),
        help_text=_("This date is ignored for one time only events."),
        required=False,
    )

    class Meta:
        model = Event
        exclude = ("creator", "created_on", "calendar")
        widgets={
            'project_data': ProjectSelect2Widget(),
            'companybranch': FullCompanyBranchSelect2Widget(),
            'task': ProjectPersonalTaskSelect2Widget(),
            'start': DateInput(),
            'end': DateInput(),
            'skills': SkillModelSelect2MultipleWidget(),
            'end_recurring_period': DateInput(),
        }
        help_texts = {
            'project_data': 'Search by project name, company name or branch, region or city',
            'companybranch': 'Search by company name, branch, region or city',
            'tasks': 'Search by task, company name or client name',
        }

class OccurrenceForm(SpanForm):
    class Meta:
        model = Occurrence
        exclude = ("original_start", "original_end", "event", "cancelled")
        widgets={
            'project_data': ProjectSelect2Widget(),
            'companybranch': FullCompanyBranchSelect2Widget(),
            'task': ProjectPersonalTaskSelect2Widget(),
            'start': DateInput(),
            'end': DateInput(),
            'skills': SkillModelSelect2MultipleWidget(),
            'end_recurring_period': DateInput(),
        }
        help_texts = {
            'project_data': 'Search by project name, company name or branch, region or city',
            'companybranch': 'Search by company name, branch, region or city',
            'tasks': 'Search by task, company name or client name',
        }

class EventAdminForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = Event
        widgets = {"color_event": ColorInput}
