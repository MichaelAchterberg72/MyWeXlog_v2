from __future__ import absolute_import, unicode_literals
#from .celery import app
from celery import Celery
from celery.task import Task
from celery.schedules import crontab
from tasks.celery import app as celery_app

from django.conf import settings
from django.utils import timezone

from celery.task.schedules import crontab
from celery.task import periodic_task

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.template.loader import get_template
from django.db.models import Count, Sum, F, Q

import sendgrid
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Subject, To, ReplyTo, SendAt, Content, From, CustomArg, Header)

import datetime
from datetime import timedelta

from WeXlog.app_config import (
    skill_pass_score,
)

from payments.tasks import FreeMonthExpiredTask

from users.models import CustomUser, CustomUserSettings, ExpandedView

from talenttrack.models import (
        WorkExperience, Lecturer, ClassMates, WorkColleague, Superior, WorkClient,  WorkCollaborator, LicenseCertification
)
from marketplace.models import (
        TalentRequired, WorkBid, TalentAvailabillity, SkillRequired, SkillLevel, WorkBid,  BidShortList, VacancyViewed
)

from db_flatten.models import SkillTag

from Profile.models import PhysicalAddress, LanguageTrack, WillingToRelocate

from invitations.models import Invitation


@celery_app.task(name="UpdateSubscriptionPaidDate")
@periodic_task(run_every=(crontab(hour=0, minute=0)), name="UpdateSubscriptionPaidDate", ignore_result=True)
def UpdateSubscriptionPaidDate():

    monthly = datetime.timedelta(days=31, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0)
    six_monthly = datetime.timedelta(days=183, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0)
    twelve_monthly = datetime.timedelta(days=366, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0)

    users = CustomUser.objects.all()

    for u in users:
        username = CustomUser.objects.get(pk=u.id)
        instance2 = ExpandedView.objects.get(talent=u.id)
        if username.paid == True:
            if username.paid_type == 1:
                if username.paid_date <= timezone.now() - monthly:
                    username.paid = False
                    username.subscription = 0
                    if username.free_month == True:
                        FreeMonthExpiredTask.delay(username)
                        username.free_month = False
                        instance2.trial_expired = False
                    username.save()
                    instance2.save()
                    # send user an email to let them know the subscription has expired
    #                SubscriptionExpiredTask.delay(username)

            elif username.paid_type == 2:
                if username.paid_date <= datetime.now() - six_monthly:
                    username.paid = False
                    username.subscription = 0
                    if username.free_month == True:
                        username.free_month = False
                        instance2.trial_expired = False
                    username.save()
                    instance2.save()
                    # send user an email to let them know the subscription has expired
    #                SubscriptionExpiredTask.delay(username)

            elif username.paid_type == 3:
                if username.paid_date <= datetime.now() - twelve_monthly:
                    username.paid = False
                    username.subscription = 0
                    if username.free_month == True:
                        username.free_month = False
                        instance2.trial_expired = False
                    username.save()
                    instance2.save()
                    # send user an email to let them know the subscription has expired
    #                SubscriptionExpiredTask.delay(username)
        username.save()
        instance2.save()


def UpgradeRefunds():
    from paypal.standard.ipn.models import PayPalIPN

    monthly = datetime.timedelta(days=31)
    mda = datetime.today() - monthly  #.strftime('%d/%m/%Y')

    qs = PayPalIPN.objects.filter(Q(txn_type='subscr_signup') & Q(item_name__icontains='Upgrade'))
    item = qs.filter(subscr_date__gte=mda).values_list('payer_id', flat=True)

#    for r in item:
#        username = CustomUser.objects.get(pk=r.custom)
#        useremail = username.email
#        tlt = username.pk

#        p = PayPalIPN.objects.filter(custom=r.custom)
#        q = p.filter(flag = True).order_by(-payment_date)
#        subscriber = q[1]

#        npd = subscriber.next_payment_date
#        npdd = npd.strftime('%d/%m/%Y')
#        cd = date.today().strftime('%d/%m/%Y')
#        nsd = cd - npd
#        daysdelta = nsd.days

#        opd = subscriber.payment_date
#        opdd = opd.strftime('%d/%m/%Y')
#        sd = npdd - opdd
#        subscriptiondaysdelta = sd.days

#        amp = subscriber.amount1
#        subscriptionperday = amp / subscriptiondaysdelta
#        refundamount = subscriptionperday * daysdelta

#        payment_txn_id = subscriber.txn_id

#        if refundamount > 0.48:
#            SubscriptionRefundTask.delay(username, useremail, refundamount, payment_txn_id)
#            RemindDeleteOldSubscription.delay(useremail, payment_txn_id)


    subject = f"Refunds for MyWeXlog Upgrades"
    context = {'item': item }
    html_message = render_to_string('payments/email_subscription_subscription_refund.html', context).strip()
    plain_message = strip_tags(html_message)

    message = Mail(
        from_email = settings.SENDGRID_FROM_EMAIL,
        to_emails = settings.ACCOUNTS_EMAIL,
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


@celery_app.task(name="WeeklyUpdateEmail")
@periodic_task(run_every=(crontab(day_of_week=1, hour=0, minute=0)), name="WeeklyUpdateEmail", ignore_result=True)
def weekly_email():
    user_settings = CustomUserSettings.objects.filter(Q(unsubscribe=False) & Q(receive_newsletter=True)).values_list('Talent__id')
    users = CustomUser.objects.filter(id__icontains=user_settings)

    for talent in users:
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
        invitation_sent_count = invitation_sent.count()

        # sened email if has info relevant to member
        email_score = rem_vac + sum_req + invitation_sent_count

        if email_score > 0:

            subject = f"MyWeXlog Weekly Update"
            context = {
                'rem_vac': rem_vac,
                'dsd': dsd,
                'tr_count': tr_count,
                'edu_req_lect': edu_req_lect,
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
            html_message = render_to_string('email/weekly/weekly_email_update.html', context)
            plain_message = strip_tags(html_message)

            message = Mail(
                from_email = settings.SENDGRID_FROM_EMAIL,
                to_emails = username.email,
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
