from django import forms
from django.utils.translation import gettext_lazy as _

from schedule.models import Event, Occurrence
from schedule.widgets import ColorInput
from project.models import ProjectPersonalDetails
from enterprises.models import Branch

from talenttrack.forms import ProjectSelect2Widget


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
#            'start': DateInput(),
#            'end': DateInput(),
#            'skills': SkillModelSelect2MultipleWidget(),
        }


class OccurrenceForm(SpanForm):
    class Meta:
        model = Occurrence
        exclude = ("original_start", "original_end", "event", "cancelled")
        widgets={
            'project_data': ProjectSelect2Widget(),
#            'start': DateInput(),
#            'end': DateInput(),
#            'skills': SkillModelSelect2MultipleWidget(),
        }


class EventAdminForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = Event
        widgets = {"color_event": ColorInput}
