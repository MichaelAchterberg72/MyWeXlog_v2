from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from allauth.account.forms import SignupForm

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'synonym')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    middle_name = forms.CharField(max_length=30, label='Middle Name (Optional)', required=False)
    last_name = forms.CharField(max_length=30, label='Last Name')
    synonym = forms.CharField(max_length=30, label='Alias')

    def save(self, request):
        CustomUser = super(CustomSignupForm,self).save(request)
        CustomUser.first_name=self.cleaned_data['first_name']
        CustomUser.middle_name=self.cleaned_data['middle_name']
        CustomUser.last_name=self.cleaned_data['last_name']
        CustomUser.synonym=self.cleaned_data['synonym']

        return CustomUser
