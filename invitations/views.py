from django.shortcuts import render, redirect, reverse
from django.utils.http import is_safe_url
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

#html to pdf
from django.utils import timezone
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from Profile.models import (
        Profile, BriefCareerHistory, OnlineRegistrations, IdentificationDetail, PassportDetail, LanguageTrack, Email, PhysicalAddress, PostalAddress, PhoneNumber
)
from marketplace.models import (
        TalentRequired, BidShortList, BidInterviewList, WorkBid, TalentAvailabillity, WorkIssuedTo, VacancyRate, TalentRate
)
from talenttrack.models import (
        Achievements, LicenseCertification, Lecturer, ClassMates, WorkExperience, WorkColleague, Superior, WorkClient, WorkCollaborator
)
from booklist.models import ReadBy
from .models import Invitation

#email
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags


#pinax_referrals
from pinax.notifications.models import send, send_now
from pinax.referrals.models import Referral
from django.contrib.contenttypes.models import ContentType

from .forms import InvitationForm, InvitationLiteForm

@login_required()
#in the app, add information relating to the job
def InvitationView(request):
    invitee = request.user
    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        form = InvitationForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.invited_by = request.user
            if 'confirm' in request.COOKIES:
                rel = request.COOKIES['confirm']
                new.relationship = rel
            new.save()
            cd = form.cleaned_data

            temp = Referral.objects.get(user=request.user)

            name = cd['name']
            print(name)
            surname = cd['surname']
            worked_for = cd['worked_for']
            print(name, surname, worked_for)

            subject = f"Invitation to WeXlog"
            context = {'form': form,  'temp': temp }
            html_message = render_to_string('invitations/invitation.html', context)
            plain_message = strip_tags(html_message)

            invitee = cd['email']
            send_mail(subject, html_message, 'admin@wexlog.io', [invitee,])
            template = 'invitations/invitation.html'
            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Talent:Home')
            #response =  HttpResponseRedirect(next_url)
            response = render(request, template, context)
            response.delete_cookie("confirm")
            return response

    else:
        form = InvitationForm()
        template = 'invitations/invite_form.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
def FlatInviteview(request):
    invitee = request.user
    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        form = InvitationLiteForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.invited_by = request.user
            new.relationship = 'AF'
            new.save()

            cd = form.cleaned_data
            referral_code = Referral.objects.get(user=request.user)

            name = cd['name']
            surname = cd['surname']

            subject = f"{invitee.first_name} {invitee.last_name} invites you to WeXlog"
            context = {'form': form,  'referral_code': referral_code }
            html_message = render_to_string('invitations/flat_invitation.html', context)
            plain_message = strip_tags(html_message)

            invitee = cd['email']
            send_mail(subject, html_message, 'no-reply@wexlog.io', [invitee,])
            template = 'invitations/flat_invitation.html'
            #return redirect(reverse('Profile:ProfileHome'))
            return render(request, template, context)

    else:
        form = InvitationLiteForm()
        template = 'invitations/invite_lite_form.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
def profile_2_pdf(request):
    tlt = request.user
    tdy = timezone.now()
    pfl = Profile.objects.get(talent=tlt)
    bch = BriefCareerHistory.objects.filter(talent=tlt).order_by('-date_from')
    osr = OnlineRegistrations.objects.filter(talent=tlt)
    idt = IdentificationDetail.objects.filter(talent=tlt)
    psp = PassportDetail.objects.filter(talent=tlt)
    lng = LanguageTrack.objects.filter(talent=tlt)
    eml = Email.objects.filter(talent=tlt)
    pad = PhysicalAddress.objects.filter(talent=tlt)
    pst = PostalAddress.objects.filter(talent=tlt)
    pnr = PhoneNumber.objects.filter(talent=tlt)
    bks = ReadBy.objects.filter(talent=tlt)
    ite = Invitation.objects.filter(invited_by=tlt)
    vac = TalentRequired.objects.filter(requested_by=tlt)
    bsl = BidShortList.objects.filter(talent=tlt)
    bil = BidInterviewList.objects.filter(talent=tlt)
    wkb = WorkBid.objects.filter(talent=tlt)
    tla = TalentAvailabillity.objects.filter(talent=tlt)
    wit = WorkIssuedTo.objects.filter(talent=tlt)
    vyr = VacancyRate.objects.filter(talent=tlt)
    tlr = TalentRate.objects.filter(talent=tlt)
    ach = Achievements.objects.filter(talent=tlt)
    lcn = LicenseCertification.objects.filter(talent=tlt)

    lco = Lecturer.objects.filter(education__talent=tlt)
    cmo = ClassMates.objects.filter(education__talent=tlt)
    wke = WorkExperience.objects.filter(talent=tlt).order_by("-date_from")

    wco = WorkColleague.objects.filter(experience__talent=tlt)
    wso = Superior.objects.filter(experience__talent=tlt)
    wco = WorkClient.objects.filter(experience__talent=tlt)
    wlo = WorkCollaborator.objects.filter(experience__talent=tlt)

    lct = Lecturer.objects.filter(lecturer=tlt)
    cmt = ClassMates.objects.filter(colleague=tlt)
    wct = WorkColleague.objects.filter(colleague_name=tlt)
    wst = Superior.objects.filter(superior_name=tlt)
    wct = WorkClient.objects.filter(client_name=tlt)
    wlt = WorkCollaborator.objects.filter(collaborator_name=tlt)

    response = HttpResponse(content_type="application/pdf")
    content = "inline; filename=MyWeXlogProfile.pdf"

    template = 'invitations/prrofile_2_pdf.html'
    context = {
            'pfl': pfl, 'tdy': tdy, 'bch': bch, 'osr': osr, 'psp': psp, 'lng': lng, 'eml': eml,'pad': pad, 'pst': pst, 'pnr': pnr, 'bks': bks, 'ite': ite, 'vac': vac, 'bsl': bsl, 'bil': bil, 'wkb': wkb, 'tla': tla, 'wit': wit, 'vyr': vyr, 'tlr': tlr, 'ach': ach, 'lcn': lcn, 'lco': lco, 'cmo': cmo, 'wke': wke, 'wco': wco, 'wlo': wlo, 'lct': lct, 'cmt': cmt, 'wct': wct, 'wst': wst, 'wct': wct, 'wlt': wlt,
            }
    download = request.GET.get("download")
    if download:
        content2 = "attachment; filename=MyWeXlogProfile.pdf"
        response['Content-Disposition'] = content2
    response['Content-Disposition'] = content
    html = render_to_string(template, context)
    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config)
    return response
