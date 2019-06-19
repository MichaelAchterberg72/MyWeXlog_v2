from django import forms
from django.contrib.auth.models import User
from django.utils.encoding import force_text

from . models import PhoneNumberType, SkillTag

class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumberType
        fields = ('type',)

class SkillForm(forms.ModelForm):
    class Meta:
        model = SkillTag
        fields = ('skill',)
