from django.shortcuts import render, redirect, reverse
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
        form = InvitationForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.invited_by = request.user

            new.save()
            cd = form.cleaned_data
            """
            referral = Referral.create(
                user=request.user,
                redirect_to=reverse('Sel2:Home'),
                label = 'referral',
            )
            """
            #ste = Referral.objects.get(user=request.user, label__iexact='Referral_Invitation')'ste': ste,

            temp = request.user

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
            return render(request, template, context)
#frust
    else:
        form = InvitationForm()

    template = 'invitations/invite_form.html'
    context = {'form': form}
    return render(request, template, context)
