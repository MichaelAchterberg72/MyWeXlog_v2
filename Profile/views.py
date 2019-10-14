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


from .models import (
        Profile, Email, PhysicalAddress, PostalAddress, PhoneNumber, SiteName, OnlineRegistrations, FileUpload, IdentificationDetail, IdType, PassportDetail, LanguageList, LanguageTrack
        )

from talenttrack.models import (
        Lecturer, ClassMates, WorkColleague, Superior, WorkCollaborator,  WorkClient, PreColleague, Education
)

from talenttrack.forms import (
        LecturerCommentForm, ClassMatesCommentForm
)
from locations.models import Region


from .forms import (
    ProfileForm, EmailForm, EmailStatusForm, PhysicalAddressForm, PostalAddressForm, PhoneNumberForm, OnlineProfileForm, ProfileTypeForm, FileUploadForm, IdTypeForm, LanguageTrackForm, LanguageListForm, PassportDetailForm, IdentificationDetailForm
)


def ProfileHome(request):
    #WorkFlow Card
    wf1 = Lecturer.objects.filter(confirm__exact='S').count()
    cm1 = ClassMates.objects.filter(confirm__exact='S').count()
    wk1 = WorkColleague.objects.filter(confirm__exact='S').count()
    spr1 = Superior.objects.filter(confirm__exact='S').count()
    wclr1 = WorkCollaborator.objects.filter(confirm__exact='S').count()
    wc1 = WorkClient.objects.filter(confirm__exact='S').count()
    pc1 = PreColleague.objects.filter(confirm__exact='S').count()

    total = wf1 + cm1 + wk1 + spr1 + wclr1 + wc1 + pc1

    template = 'Profile/profile_home.html'
    context = {
        'wf1': wf1, 'total': total
    }
    return render(request, template, context)

@login_required()
def ConfirmView(request):
    wf1 = Lecturer.objects.filter(confirm__exact='S')
    cm1 = ClassMates.objects.filter(confirm__exact='S')
    wk1 = WorkColleague.objects.filter(confirm__exact='S')
    spr1 = Superior.objects.filter(confirm__exact='S')
    wclr1 = WorkCollaborator.objects.filter(confirm__exact='S')
    wc1 = WorkClient.objects.filter(confirm__exact='S')
    pc1 = PreColleague.objects.filter(confirm__exact='S')

    template = 'Profile/experience_confirm.html'
    context = {
            'wf1': wf1, 'cm1': cm1, 'wk1': wk1, 'spr1': spr1, 'wclr1': wclr1, 'wc1': wc1, 'pc1': pc1
    }
    return render(request, template, context)


@login_required()
def LecturerConfirmView(request, pk):
    if request.method == 'POST':
        info = Lecturer.objects.get(pk=pk)
        info.confirm = 'C'
        info.save()
        edu = Education.objects.get(pk=info.education.id)
        edu.score += 2
        edu.save()
    return redirect(reverse('Profile:Confirm')+'#Lecturer')


@login_required()
def LecturerRejectView(request, pk):
    if request.method == 'POST':
        info = Lecturer.objects.get(pk=pk)
        info.confirm = 'R'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#Lecturer')


@login_required()
def LecturerWrongPersonView(request, pk):
    if request.method == 'POST':
        info = Lecturer.objects.get(pk=pk)
        info.confirm = 'Y'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#Lecturer')


@login_required()
def LecturerCommentView(request, pk):
    info = get_object_or_404(Lecturer, pk=pk)
    form = LecturerCommentForm(request.POST or None, instance=info)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            if new.confirm == 'C':
                edu = Education.objects.get(pk=info.education.id)
                edu.score += 2
                edu.save()
            else:
                pass

            return redirect(reverse('Profile:Confirm')+'#Lecturer')

    else:
        template ='talenttrack/confirm_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)



@login_required()
def ClassMatesConfirmView(request, pk):
    if request.method == 'POST':
        info = ClassMates.objects.get(pk=pk)
        info.confirm = 'C'
        info.save()
        edu = Education.objects.get(pk=info.education.id)
        edu.score += 1
        edu.save()
    return redirect(reverse('Profile:Confirm')+'#ClassMates')


@login_required()
def ClassMatesRejectView(request, pk):
    if request.method == 'POST':
        info = ClassMates.objects.get(pk=pk)
        info.confirm = 'R'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#ClassMates')


@login_required()
def ClassMatesCommentView(request, pk):
    info = get_object_or_404(ClassMates, pk=pk)
    form = ClassMatesCommentForm(request.POST or None, instance=info)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            if new.confirm == 'C':
                edu = Education.objects.get(pk=info.education.id)
                edu.score += 1
                edu.save()
            else:
                pass

            return redirect(reverse('Profile:Confirm')+'#ClassMates')

    else:
        template ='talenttrack/confirm_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)


@login_required()
def ClassMatesWrongPersonView(request, pk):
    if request.method == 'POST':
        info = ClassMates.objects.get(pk=pk)
        info.confirm = 'Y'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#ClassMates')


@login_required()
def OnlineDelete(request, pk):
    if request.method == 'POST':
        site = OnlineRegistrations.objects.get(pk=pk)
        site.delete()
    return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':site.talent.id})+'#online')


@login_required()
def PassportAddView(request, profile_id):
    detail = Profile.objects.get(talent=profile_id)
    if detail.talent == request.user:
        form = PassportDetailForm(request.POST or None)
        if request.method =='POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':profile_id})+'#passport')
        else:
            template = 'Profile/passport_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def PassportDeleteView(request, pk):
    info = PassportDetail.objects.get(pk=pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':info.talent.id})+'#passport')
    else:
        raise PermissionDenied


@login_required()
def PassportEditView(request, p_id, profile_id):
    #detail = Profile.objects.get(talent=profile_id)
    info = PassportDetail.objects.get(pk=p_id)
    if info.talent == request.user:
        form = PassportDetailForm(request.POST or None, instance=info)
        if request.method =='POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':profile_id})+'#passport')
        else:
            template = 'Profile/passport_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


#>>>Language Views
@csp_exempt
@login_required()
def LanguageAddView(request, profile_id):
    detail = Profile.objects.get(talent=profile_id)
    if detail.talent == request.user:
        form = LanguageTrackForm(request.POST or None)
        if request.method =='POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':profile_id}))
        else:
            template = 'Profile/language_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def LanguageEditView(request, profile_id, lang_id):
    detail = Profile.objects.get(talent=profile_id)
    info = LanguageTrack.objects.get(pk=lang_id)
    if detail.talent == request.user:
        form = LanguageTrackForm(request.POST or None, instance=info)
        if request.method =='POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':profile_id}))
        else:
            template = 'Profile/language_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied

@login_required()
@csp_exempt
def LanguagePopup(request):
    form = LanguageListForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_language");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template = 'Profile/language_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_language_id(request):
    if request.is_ajax():
        language = request.Get['language']
        language_id = SiteName.objects.get(language = language).id
        data = {'language_id':language_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Language Views

@csp_exempt
@login_required()
def IdentificationView(request, profile_id):
    detail = Profile.objects.get(talent=profile_id)
    info = IdentificationDetail.objects.get(talent=profile_id)
    if detail.talent == request.user:
        form = IdentificationDetailForm(request.POST or None, instance=info)
        if request.method =='POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':profile_id}))
        else:
            template = 'Profile/id_edit.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


#>>>Id Popup
@login_required()
@csp_exempt
def IdTypePopup(request):
    form = IdTypeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_id_type");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template = 'Profile/id_type_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_IdType_id(request):
    if request.is_ajax():
        type = request.Get['type']
        type_id = SiteName.objects.get(type = type).id
        data = {'type_id':type_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Id Popup


@login_required()
def FileUploadView(request, profile_id):
    detail = Profile.objects.get(talent=profile_id)
    if detail.talent == request.user:
        form = FileUploadForm(request.POST, request.FILES)
        if request.method =='POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':profile_id}))
        else:
            template = 'Profile/file_upload.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


login_required()
def FileDelete(request, pk):
    detail = FileUpload.objects.get(pk=pk)
    if detail.talent == request.user:
        if request.method =='POST':
            detail.delete()
            return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':detail.talent.id})+'#online')
    else:
        raise PermissionDenied

login_required()
def EmailDelete(request, pk):
    detail = Email.objects.get(pk=pk)
    if detail.talent == request.user:
        if request.method =='POST':
            detail.delete()
            return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':detail.talent.id})+'#email')
    else:
        raise PermissionDenied



@login_required()
def ProfileView(request, profile_id):
    detail = Profile.objects.get(talent=profile_id)
    if detail.talent == request.user:
        info = Profile.objects.filter(talent=profile_id)
        email = Email.objects.filter(talent=profile_id)
        physical = PhysicalAddress.objects.get(talent=profile_id)
        postal = PostalAddress.objects.get(talent=profile_id)
        pnumbers = PhoneNumber.objects.filter(talent=profile_id)
        online = OnlineRegistrations.objects.filter(talent=profile_id)
        upload = FileUpload.objects.filter(talent=profile_id)
        id = IdentificationDetail.objects.filter(talent=profile_id)
        passport = PassportDetail.objects.filter(talent=profile_id)
        speak = LanguageTrack.objects.filter(talent=profile_id)

        template='Profile/profile_view.html'
        context= {'info':info, 'email':email, 'physical':physical, 'postal': postal, 'pnumbers': pnumbers, 'online': online, 'upload': upload, 'id': id, 'passport': passport, 'speak': speak}
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
    detail = Profile.objects.get(talent=profile_id)
    if detail.talent == request.user:
        info = get_object_or_404(PhysicalAddress, pk=profile_id)
        form = PhysicalAddressForm(request.POST or None, instance=info)
        if request.method =='POST':
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


@login_required()
@csp_exempt
def PostalAddressView(request, profile_id):
    detail = Profile.objects.get(talent=profile_id)
    if detail.talent == request.user:
        info = get_object_or_404(PostalAddress, pk=profile_id)
        form = PostalAddressForm(request.POST or None, instance=info)
        if request.method =='POST':
            if form.is_valid():
                new=form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':profile_id}))
        else:
            template = 'Profile/postal_address_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def PhoneNumberAdd(request, profile_id):
    detail = Profile.objects.get(talent=profile_id)
    if detail.talent == request.user:
        form =PhoneNumberForm(request.POST or None)
        if request.method =='POST':
            if form.is_valid():
                new=form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':profile_id})+'#phone')
        else:
            template = 'Profile/phone_number_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def PhoneNumberDelete(request, pk):
    detail = PhoneNumber.objects.get(pk=pk)
    if detail.talent == request.user:
        if request.method =='POST':
            detail.delete()
            return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':detail.talent.id})+'#phone')
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def OnlineProfileAdd(request, profile_id):
    detail = Profile.objects.get(talent=profile_id)
    if detail.talent == request.user:
        form =OnlineProfileForm(request.POST or None)
        if request.method =='POST':
            if form.is_valid():
                new=form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':profile_id})+'#online')
        else:
            template = 'Profile/online_profile_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


#>>>Site Type Popup
@login_required()
@csp_exempt
def ProfileTypePopup(request):
    form = ProfileTypeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_sitename");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template = 'Profile/site_type_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_SiteType_id(request):
    if request.is_ajax():
        type = request.Get['site']
        site_id = SiteName.objects.get(site = site).id
        data = {'site_id':site_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< SiteType Popup
