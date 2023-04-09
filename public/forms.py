from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.contrib.auth.models import User

from .models import ContactUs, DataProtection, Suggestions


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ('name','email','comments')


class SuggestionsForm(forms.ModelForm):
    class Meta:
        model = Suggestions
        fields = ('name','email','comments')


class DataProtectionForm(forms.ModelForm):
    class Meta:
        model = DataProtection
        fields = ('name','email','comments')


class DataPrivacyForm(forms.ModelForm):
    class Meta:
        model = Suggestions
        fields = ('name','email','comments')
