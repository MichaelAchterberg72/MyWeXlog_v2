from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
import json


from csp.decorators import csp_exempt


from .models import Profile, Email, PhysicalAddress


from .forms import (
    ProfileForm, EmailForm, EmailStatusForm, PhysicalAddressForm
)


class ProfileHome(TemplateView):
    template_name = 'Profile/profile_home.html'


@login_required()
def ProfileView(request, profile_id):
    detail = Profile.objects.get(talent=profile_id)
    if detail.talent == request.user:
        info = Profile.objects.filter(talent=profile_id)
        email = Email.objects.filter(talent=profile_id)
        physical = PhysicalAddress.objects.get(talent=profile_id)

        template='Profile/profile_view.html'
        context= {'info':info, 'email':email, 'physical':physical}
        return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def ProfileEditView(request, profile_id):
    detail = get_object_or_404(Profile, pk=profile_id)
    if detail.talent == request.user:
        form = ProfileForm(request.POST or None, instance=detail)
        if request.method =='POST':
            next_url=request.POST.get('next','/')

            if form.is_valid():
                new=form.save(commit=False)
                new.talent = request.user
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Profile:ProfileHome')
                return HttpResponseRedirect(next_url)
        else:
            template = 'Profile/profile_edit.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def EmailEditView(request, profile_id):
    detail = get_object_or_404(Profile, pk=profile_id)
    if detail.talent == request.user:
        form = EmailForm(request.POST or None)
        if request.method =='POST':
            next_url=request.POST.get('next','/')
            if form.is_valid():
                new=form.save(commit=False)
                new.talent = request.user
                new.save()
                if 'Done' in request.POST:
                    if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                        next_url = reverse('Profile:ProfileHome')
                    return HttpResponseRedirect(next_url)
                elif 'Another' in request.POST:
                    form=EmailForm()
        else:
            form=EmailForm()
        template = 'Profile/email_edit.html'
        context = {'form': form}
        return render(request, template, context)
    else:
        raise PermissionDenied

@login_required()
@csp_exempt
def EmailStatusView(request, profile_id, email_id):
    detail = Profile.objects.get(talent=profile_id)
    detail2 = get_object_or_404(Email, pk=email_id)
    if detail.talent == request.user:
        form = EmailStatusForm(request.POST or None, instance=detail2)
        if request.method =='POST':
            next_url=request.POST.get('next','/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':profile_id}))

        else:

            template = 'Profile/email_status.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def PhysicalAddressView(request, profile_id):
    detail = get_object_or_404(Profile, pk=profile_id)
    if detail.talent == request.user:
        form = PhysicalAddressForm(request.POST or None)
        if request.method =='POST':
            next_url=request.POST.get('next','/')
            if form.is_valid():
                new=form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':profile_id}))
        else:
            template = 'Profile/physical_address_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied
