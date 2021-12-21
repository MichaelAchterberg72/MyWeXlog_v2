import os

import sendgrid
from csp.decorators import csp_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
#email
from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import get_template, render_to_string
#html to pdf
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.http import is_safe_url
#pinax_referrals
from pinax.notifications.models import send, send_now
from pinax.referrals.models import Referral
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Content, CustomArg, From, Header, Mail,
                                   ReplyTo, SendAt, Subject, To)
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from booklist.models import ReadBy
from locations.models import Region
from marketplace.models import (BidInterviewList, BidShortList,
                                TalentAvailabillity, TalentRate,
                                TalentRequired, VacancyRate, WorkBid,
                                WorkIssuedTo)
from Profile.models import (BriefCareerHistory, Email, IdentificationDetail,
                            LanguageTrack, OnlineRegistrations, PassportDetail,
                            PhoneNumber, PhysicalAddress, PostalAddress,
                            Profile)
from talenttrack.models import (Achievements, ClassMates, Lecturer,
                                LicenseCertification, Superior, WorkClient,
                                WorkCollaborator, WorkColleague,
                                WorkExperience)
from users.models import CustomUser

from .forms import InvitationForm, InvitationLiteForm
from .models import Invitation
from Profile.utils import create_code9


def ConfigureWorkerInvite():
    invites = Invitation.objects.all()
    for i in invites:
        if i.slug is None or i.slug == "":
            i.slug = create_code9(i)
            i.save()


@login_required
def invite_detail_view(request, invs):
    invite_detail = Invitation.objects.get(Q(invited_by=request.user) & Q(slug=invs) & Q(accpeted=False))

    template = 'invitations/invite_detail.html'
    context = {'invite_detail': invite_detail}
    return render(request, template, context)


@login_required()
def InvitationsSentView(request):

    tlt = request.user
    invitation_sent = Invitation.objects.filter(Q(invited_by=tlt) & Q(accpeted=False)).order_by('-date_invited')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(invitation_sent, 20)

    try:
        pageitems = paginator.page(page)
    except PageNotAnInteger:
        pageitems = paginator.page(1)
    except EmptyPage:
        pageitems = paginator.page(paginator.num_pages)

    index = pageitems.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 3 if index >= 3 else 0
    end_index = index + 3 if index <= max_index - 3 else max_index
    page_range = list(paginator.page_range)[start_index:end_index]

    template = 'invitations/invitations_sent.html'
    context = {'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


@login_required()
@csp_exempt
#in the app, add information relating to the job
def InvitationView(request, tex):
    qset = get_object_or_404(WorkExperience, slug=tex)
    invitor = request.user
    mem_excl = set(CustomUser.objects.all().values_list('email', flat=True))
    invite_excl = set(Invitation.objects.filter().values_list('email', flat=True))

    filt = mem_excl | invite_excl

    form = InvitationForm(request.POST, pwd=filt)

    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.invited_by = request.user
            new.experience = qset
            if 'confirm' in request.COOKIES:
                rel = request.COOKIES['confirm']
                new.relationship = rel
            new.save()
            cd = form.cleaned_data

            temp = Referral.objects.get(user=request.user)

            name = cd['name']
            surname = cd['surname']
            companybranch = cd['companybranch']
            invitee = cd['email']
            message = cd['message']

            subject = f"Invitation to MyWeXlog"
            context = {'form': form,  'temp': temp, 'user_email': invitee }
            html_message = render_to_string('invitations/invitation.html', context)
            plain_message = strip_tags(html_message)

            message = Mail(
                from_email = (settings.SENDGRID_FROM_EMAIL, f"{invitor.first_name} {invitor.last_name}"),
                to_emails = invitee,
                subject = subject,
                plain_text_content = strip_tags(html_message),
                html_content = html_message)

            try:
                sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)

            except Exception as e:
                print(e)

            template = 'invitations/invitation.html'
            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Talent:Home')
            response = HttpResponseRedirect(next_url)
            response.delete_cookie("confirm")
            return response
        else:
            template = 'invitations/invite_form.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        template = 'invitations/invite_form.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
def FlatInviteview(request):

    invitor = request.user
    mem_excl = set(CustomUser.objects.all().values_list('email', flat=True))
    invite_excl = set(Invitation.objects.filter().values_list('email', flat=True))

    filt = mem_excl | invite_excl

    form = InvitationLiteForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        next_url=request.POST.get('next', '/')

        if form.is_valid():
            new = form.save(commit=False)
            new.invited_by = request.user
            new.relationship = 'AF'
            new.save()

            cd = form.cleaned_data
            referral_code = Referral.objects.get(user=request.user)

            name = cd['name']
            surname = cd['surname']
            message = cd['message']
            invitee = cd['email']

            subject = f"{invitor.first_name} {invitor.last_name} invites you to MyWeXlog"
            context = {'form': form,  'referral_code': referral_code, 'user': invitee}
            html_message = render_to_string('invitations/flat_invitation.html', context)
            plain_message = strip_tags(html_message)

            message = Mail(
                from_email = (settings.SENDGRID_FROM_EMAIL, f"{invitor.first_name} {invitor.last_name}"),
                to_emails = invitee,
                subject = subject,
                plain_text_content = strip_tags(html_message),
                html_content = html_message)

            try:
                sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)

            except Exception as e:
                print(e)

            template = 'invitations/invited.html'
            return render(request, template, context)

        else:
            template = 'invitations/invite_lite_form.html'
            context = {'form': form}
            return render(request, template, context)
#            template = 'invitations/already_invited.html'
#            context = {}
#            return render(request, template, context)

    else:
        template = 'invitations/invite_lite_form.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
def InviteGoogleContactsView(gd_client):

    invitor = request.user
    feed = gd_client.GetContacts()
    for i, entry in enumerate(feed.entry):
        g_full_name = entry.name.full_name.text
        g_name = entry.name.first_name.text
        g_surname = entry.name.last_name.text
        # Display the primary email address for the contact.
        for email in entry.email:
            if email.primary and email.primary == 'true':
                g_email = email.address
        try:
            data = {
                'invited_by': request.user,
                'relationship': 'AF',
                'name': g_name,
                'surname': g_surname,
                'email': g_email,
                }

            Invitation.objects.append(data)

            subject = f"{invitor.first_name} {invitor.last_name} invites you to join MyWeXlog"
            context = {'referral_code': referral_code, 'user_email': g_email}
            html_message = render_to_string('invitations/flat_invitation.html', context).strip()
            plain_message = strip_tags(html_message)

            message = Mail(
                from_email = settings.SENDGRID_FROM_EMAIL,
                to_emails = g_email,
                subject = subject,
                plain_text_content = strip_tags(html_message),
                html_content = html_message)

            try:
                sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)

            except Exception as e:
                print(e)

        except:
            print("This person has already been invited")


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
        content = "inline; attachment; filename=MyWeXlogProfile.pdf"
    response['Content-Disposition'] = content
    html = render_to_string(template, context)
    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config)
    return response






from django.db.models import Count, F, Q, Sum

from db_flatten.models import SkillTag
from invitations.models import Invitation
from marketplace.models import (BidShortList, SkillLevel, SkillRequired,
                                TalentAvailabillity, TalentRequired,
                                VacancyViewed, WorkBid)
from Profile.models import LanguageTrack, PhysicalAddress, WillingToRelocate
from talenttrack.models import (ClassMates, Lecturer, LicenseCertification,
                                Superior, WorkClient, WorkCollaborator,
                                WorkColleague, WorkExperience)
from users.models import CustomUser, ExpandedView
from WeXlog.app_config import skill_pass_score


def email_test_view(request):
    users = CustomUser.objects.all()
    talent = request.user
#    for talent in users:
    username = CustomUser.objects.get(pk=talent.id)

    #Vacancies suited
    tlt = talent.id
    pfl = Profile.objects.filter(talent=talent)
    TalentRequired.objects.filter()
    # tr = TalentRequired.objects.filter(offer_status='O')
    tr = TalentRequired.objects.filter(offer_status='O')
    tr_count = tr.count()
    tr_emp = TalentRequired.objects.filter(requested_by=talent)
    wb = WorkBid.objects.filter(work__requested_by=talent)
    ta = TalentAvailabillity.objects.filter(talent=talent)
    we = WorkExperience.objects.filter(Q(talent=talent) & Q(score__gte=skill_pass_score)).prefetch_related('topic')
    sr = SkillRequired.objects.filter(scope__offer_status='O')
    sl = SkillLevel.objects.all()
    wbt = WorkBid.objects.filter(Q(talent=talent) & Q(work__offer_status='O'))
    bsl = BidShortList.objects.filter(Q(talent=talent) & Q(scope__offer_status='O'))
    vv = set(VacancyViewed.objects.filter(Q(talent=talent) & Q(closed=True)).values_list('vacancy__id', flat=True))
    vvv = VacancyViewed.objects.filter(Q(talent=request.user) & Q(viewed=True)).values_list('vacancy__id', flat=True).distinct()
    vac_exp = ExpandedView.objects.get(talent=request.user)
    vacancies_suited_list_view = vac_exp.vacancies_suited_list
    #  vo = VacancyViewed.objects.filter(closed=False)


    #>>>Create a set of all skills
    e_skill = we.filter(edt=True, score__gte=skill_pass_score).only('pk').values_list('pk', flat=True)
    l_skill = we.filter(edt=False, score__gte= skill_pass_score).only('pk').values_list('pk', flat=True)

    e_len = e_skill.count()
    l_len = l_skill.count()
    tot_len = e_len+l_len

    skill_set = SkillTag.objects.none()

    for ls in l_skill:
        a = we.get(pk=ls)
        b = a.skills.all().values_list('skill', flat=True)

        skill_set = skill_set | b

    for es in e_skill:
        c = we.get(pk=es)
        d = c.topic.skills.all().values_list('skill', flat=True)

        skill_set = skill_set | d

    skill_set = skill_set.distinct().order_by('skill')
    #Create a set of all skills<<<

    #>>>Experience Level check & list skills required in vacancies
    tlt_lvl = pfl.values_list('exp_lvl__level', flat=True)
    tlt_lvl = tlt_lvl[0]

    #finds all vacancies that require talent's experience level and below
    vac_exp = tr.filter(experience_level__level__lte=tlt_lvl)

    #>>> Check for language
    lang_req = tr.values_list('language')

    if lang_req is not None:
        tlt_lang = set(LanguageTrack.objects.filter(talent=talent).values_list('language', flat=True))
        vac_lang=set(vac_exp.filter(language__in=tlt_lang).values_list('id', flat=True))
    else:
        pass

    #Certifications Matching
    #identifies the vacancies that do not required certification
    cert_null_s = set(vac_exp.filter(certification__isnull=True).values_list('id', flat=True))
    vac_cert_s = set(vac_exp.filter(certification__isnull=False).values_list('certification', flat=True))

    if vac_cert_s is None: #if no certifications required, pass
        if vac_lang is None:
            req_experience = set(vac_exp.values_list('id',flat=True))
        else:
            req_experience = set(vac_exp.values_list('id',flat=True)).intersection(vac_lang)
    else:
        tlt_cert = set(LicenseCertification.objects.filter(talent=talent).values_list('certification', flat=True))
        vac_cert = set(vac_exp.filter(certification__in=tlt_cert).values_list('id',flat=True))
        if vac_lang is not None:
            req_experience = vac_cert.intersection(vac_lang)
        else:
            req_experience = vac_cert

    req_experience = req_experience | cert_null_s

    #Checking for locations
    #Remote Freelance, Consultants open to all talent, other vacanciesTypes only for region (to be updated to distances in later revisions) this will require gEOdJANGO
    #gathering all countries where willing to work
    wtr_qs = WillingToRelocate.objects.filter(talent=talent).values_list('country', flat=True)

    reg_set = set()
    for item in wtr_qs:
        reg = set(Region.objects.filter(country=item).values_list('id', flat=True))

        reg_set = reg_set|reg

    tlt_loc = set(PhysicalAddress.objects.filter(talent=talent).values_list('region', flat=True))

    tlt_loc=tlt_loc|reg_set

    vac_loc_rm = set(tr.filter(Q(worklocation__id=1) | Q(worklocation__id=4)).values_list('id', flat=True))

    vac_loc_reg = set(tr.filter(~Q(worklocation__id=1) | ~Q(worklocation__id=4)).filter(city__region__in=tlt_loc).values_list('id', flat=True))

    vac_loc = vac_loc_rm | vac_loc_reg

    req_experience = req_experience.intersection(vac_loc)

    #>>>Skill Matching
    skl_lst = []
    #listing the skills the vacancies already found contain.
    for key in req_experience:
        skill_required = sr.filter(scope=key).values_list('skills', flat=True).distinct()
        #combining the skills from various vacancies into one list
        for sk in skill_required:
            skl_lst.append(sk)

    ds = set()
    matchd = set(skl_lst) #remove duplicates

    for item in matchd:
        display = set(sr.filter(
                Q(skills__in=skl_lst)
                & Q(scope__bid_closes__gte=timezone.now())).values_list('scope__id', flat=True))

        ds = ds | display

    dsi = ds.intersection(req_experience)

    tot_vac = len(dsi)
    #remove the vacancies that have already been applied for
    wbt_s = set(wbt.values_list('work__id', flat=True))
    wbt_c = len(wbt_s)

    #remove the vacancies to which talent has been shortlisted
    bsl_s = set(bsl.values_list('scope__id', flat=True))
    bsl_c = len(bsl_s)

    #finding the difference (suitable vacancies minus x)

    dsi = dsi - wbt_s

    dsi = dsi - bsl_s

    #Removing vacancies that have been rejected by the user
    dsi = dsi - vv

    #Recreating the QuerySet
    suitable = tr.filter(id__in=dsi)

    rem_vac = suitable.count()
    dsd = suitable[:5]

    #Experience Level check & list skills required in vacancies<<<
    if tot_len > 0:
        dsd = dsd
    else:
        dsd = set()
    # end vacancies suited




    #Confirmations required
    edu_req_lect = Lecturer.objects.filter(Q(confirm='S') & Q(lecturer=talent)).order_by('-date_captured')
    edu_req_cm = ClassMates.objects.filter(Q(confirm='S') & Q(colleague=talent)).order_by('-date_captured')
    exp_req_clg = WorkColleague.objects.filter(Q(confirm='S') & Q(colleague_name=talent)).order_by('-date_captured')
    exp_req_sup = Superior.objects.filter(Q(confirm='S') & Q(superior_name=talent)).order_by('-date_captured')
    exp_req_clt = WorkClient.objects.filter(Q(confirm='S') & Q(client_name=talent)).order_by('-date_captured')
    exp_req_clb = WorkCollaborator.objects.filter(Q(confirm='S') & Q(collaborator_name=talent)).order_by('-date_captured')

    edu_req_lect_count = edu_req_lect.count()
    edu_req_cm_count = edu_req_cm.count()
    exp_req_clg_count = exp_req_clg.count()
    exp_req_sup_count = exp_req_sup.count()
    exp_req_clt_count = exp_req_clt.count()
    exp_req_clb_count = exp_req_clb.count()

    sum_req = edu_req_lect_count + edu_req_cm_count + exp_req_clg_count + exp_req_sup_count + exp_req_clt_count + exp_req_clb_count
    #end confimations required


    #Invitations sent not registered
    invitation_sent_qs = Invitation.objects.filter(Q(invited_by=tlt) & Q(accpeted=False)).order_by('-date_invited')
    invitation_sent = invitation_sent_qs[:5]
    invitation_sent_count = invitation_sent_qs.count()

#    template = 'invitations/invitation_email.html'
    template = 'email/weekly/weekly_email_update.html'
    context = {
        'rem_vac': rem_vac,
        'dsd': dsd,
        'tr_count': tr_count,
        'edu_req_lect': edu_req_lect,
        'sum_req': sum_req,
        'edu_req_cm': edu_req_cm,
        'exp_req_clg': exp_req_clg,
        'exp_req_sup': exp_req_sup,
        'exp_req_clt': exp_req_clt,
        'exp_req_clb': exp_req_clb,
        'edu_req_lect_count': edu_req_lect_count,
        'edu_req_cm_count': edu_req_cm_count,
        'exp_req_clg_count': exp_req_clg_count,
        'exp_req_sup_count': exp_req_sup_count,
        'exp_req_clt_count': exp_req_clt_count,
        'exp_req_clb_count': exp_req_clb_count,
        'invitation_sent': invitation_sent,
        'invitation_sent_count': invitation_sent_count,
        'user': username.email,
        'user_email': username.email,
        }
    return render(request, template, context)
