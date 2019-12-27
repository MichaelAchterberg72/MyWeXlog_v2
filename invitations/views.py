from django.shortcuts import render, redirect, reverse
from django.utils.http import is_safe_url

#email
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags


#pinax_referrals
from pinax.notifications.models import send, send_now
from pinax.referrals.models import Referral
from django.contrib.contenttypes.models import ContentType

from .forms import InvitationForm

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
            surname = cd['surname']
            worked_for = cd['worked_for']

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
#frust
    else:
        form = InvitationForm()

    template = 'invitations/invite_form.html'
    context = {'form': form}
    return render(request, template, context)
