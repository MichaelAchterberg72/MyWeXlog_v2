from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse


from .models import CustomUserSettings, CustomUser
from Profile.models import Profile


from .forms import CustomUserSettingsForm, RightToSayNoForm, PrivacyPolicyForm, UserAgreementForm


@login_required
def CustomUserSettingsView(request):
    user_id = request.user
    detail = CustomUserSettings.objects.get(talent=user_id)
    u = CustomUser.objects.get(id=user_id.id)
    if detail.talent == user_id:
        form = CustomUserSettingsForm(request.POST or None, instance=detail)
        if request.method == 'POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.save()
                if new.right_to_be_forgotten == True:
                    u.delete()
                    messages.success(request, "Your account has been deleted")

                return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':user_id.id})+'#online')
        else:
            context = {'form': form}
            template = 'users/custom_user_settings.html'
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required
def RightToSayNoView(request):
    user_id = request.user
    detail = CustomUserSettings.objects.get(talent=user_id)
    if detail.talent == user_id:
        form = RightToSayNoForm(request.POST or None, instance=detail)
        if request.method == 'POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.save()
                return redirect(reverse('Profile:ProfileView', kwargs={'profile_id': user_id.id})+'#online')
        else:
            context = {'form': form}
            template = 'users/right_to_say_no.html'
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def UserAgreementView(request):
    user_id = request.user
    detail = CustomUserSettings.objects.get(talent=user_id)
    u = CustomUser.objects.get(id = user_id.id)
    if detail.talent == user_id:
        form = UserAgreementForm(request.POST or None, instance=detail)
        if request.method == 'POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.save()
                if new.useragree == False:
                    u.delete()
                    messages.success(request, "Your account has been deleted")

                return redirect(reverse('Profile:ProfileHome',))
        else:
            context = {'form': form}
            template = 'users/terms_user_agreement.html'
            return render(request, template, context)

    else:
        raise PermissionDenied


@login_required()
def PrivacyPolicyView(request):
    user_id = request.user
    detail = CustomUserSettings.objects.get(talent=user_id)
    u = CustomUser.objects.get(id = user_id.id)
    if detail.talent == user_id:
        form = PrivacyPolicyForm(request.POST or None, instance=detail)
        if request.method == 'POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.save()
                if new.privacy == False:
                    u.delete()
                    messages.success(request, "Your account has been deleted")

                return redirect(reverse('Profile:ProfileHome'))
        else:
            context = {'form': form}
            template = 'users/terms_privacy_policy.html'
            return render(request, template, context)
    else:
        raise PermissionDenied


def LoginUserAgreementView(request):

    context = {}
    template = 'users/login_user_agreement.html'
    return render(request, template, context)


def LoginPrivacyView(request):

    context = {}
    template = 'users/login_privacy_policy.html'
    return render(request, template, context)


def LoginCookieView(request):

    context = {}
    template = 'users/login_cookie_policy.html'
    return render(request, template, context)
