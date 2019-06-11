from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
import json

from .models import Profile, PhysicalAddress, Email


from .forms import (
    ProfileForm, EmailForm
)


class ProfileHome(TemplateView):
    template_name = 'Profile/profile_home.html'


@login_required()
def ProfileView(request, profile_id):
    detail = Profile.objects.get(talent=profile_id)
    if detail.talent == request.user:
        info = Profile.objects.filter(talent=profile_id)
        email=Email.objects.filter(talent=profile_id)

        template='Profile/profile_view.html'
        context= {'info':info, 'email':email}
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


#>>>Company Popup
@login_required()
def CompanyAddPopup(request):
    form = EnterpriseAddForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_company");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template = 'testapp/artist_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_company_id(request):
    if request.is_ajax():
        company = request.Get['company']
        company_id = Enterprise.objects.get(name = enterprise).id
        data = {'company_id':company_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Company Popup


@login_required()
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
