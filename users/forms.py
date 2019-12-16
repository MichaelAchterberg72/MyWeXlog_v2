from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, CustomUserSettings

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class CustomUserSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUserSettings
        fields = ('right_to_say_no',
                    'unsubscribe',
                    'receive_newsletter',
                    'validation_requests',
                    'subscription_notifications',
                    'payment_notifications',
                    'takeout',
                    'dnt',
                    'right_to_be_forgotten')


class RightToSayNoForm(forms.ModelForm):
    class Meta:
        model = CustomUserSettings
        fields = ('right_to_say_no',)
