from django import forms
from django.contrib.auth.models import User


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


from .models import (
            Profile, Email
            )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('synonym', 'birth_date', 'background', 'mentor',)


class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ('email', 'active', 'company',)
