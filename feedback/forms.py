from django import forms

from .models import FeedBack


class FeedBackForm(forms.ModelForm):
    class Meta:
        model = FeedBack
        fields = ('type', 'details', 'optional_1', 'optional_2',)
