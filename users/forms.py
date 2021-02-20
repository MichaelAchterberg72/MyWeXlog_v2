from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, CustomUserSettings
from allauth.account.forms import SignupForm


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name', widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    terms = forms.BooleanField(required=True, label='Accept <a type="button" data-toggle="modal" data-target="#exampleModalCenter"><span class="link">Terms and Conditions</span></a>')
    age_accept = forms.BooleanField(required=True, label="Confirm you are 18 Years or Older")

    class Meta:
        model = CustomUser

    def save(self, request):
        CustomUser = super(CustomSignupForm, self).save(request)
        terms = self.cleaned_data.get('terms')
        age = self.cleaned_data.get('age_accept')
        CustomUser.first_name=self.cleaned_data['first_name']
        CustomUser.last_name=self.cleaned_data['last_name']

        return CustomUser


class CustomUserSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUserSettings
        fields = (  'theme',
                    'right_to_say_no',
                    'unsubscribe',
                    'receive_newsletter',
                    'validation_requests',
                    'subscription_notifications',
                    'payment_notifications',
                    'dnt')


class RightToSayNoForm(forms.ModelForm):
    class Meta:
        model = CustomUserSettings
        fields = ('right_to_say_no',)


class PrivacyPolicyForm(forms.ModelForm):
    class Meta:
        model = CustomUserSettings
        fields = ('privacy',)


class UserAgreementForm(forms.ModelForm):
    class Meta:
        model = CustomUserSettings
        fields = ('useragree',)
