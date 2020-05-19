from django.shortcuts import render, redirect, reverse
from django.utils.http import is_safe_url
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

#html to pdf
from django.utils import timezone
from invitations.utils import render_to_pdf
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from Profile.models import Profile

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

            subject = f"Invitation to MyWeXlog"
            context = {'form': form,  'temp': temp }
            html_message = render_to_string('invitations/invitation.html', context)
            plain_message = strip_tags(html_message)

            invitee = cd['email']
            send_mail(subject, html_message, 'admin@mywexlog.com', [invitee,])
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

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "inline; filename=MyWeXlogProfile.pdf"
    template = 'invitations/prrofile_2_pdf.html'
    context = {
            'pfl': pfl, 'tdy': tdy,
            }
    html = render_to_string(template, context)
    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config)

    return response
