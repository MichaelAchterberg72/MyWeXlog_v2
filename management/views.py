from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


from csp.decorators import csp_exempt

from django.contrib.auth import get_user_model
User = get_user_model()

import datetime as dt
from datetime import datetime, timedelta
from django.utils import timezone, dateformat
import pytz


from core.decorators import subscription



from db_flatten.models import SkillTag
from enterprises.models import Enterprise
from marketplace.models import (
    TalentRequired, BidShortList, BidInterviewList, WorkBid, WorkIssuedTo
    )
from paypal.standard.ipn.models import PayPalIPN

from django.urls import reverse


@login_required()
@subscription(3)
def ManagementDashboardView(request):

    mcount = User.objects.all().count()
    macount = User.objects.filter(subscription='2').count()
    mpcount = User.objects.filter(subscription='1').count()
    mfcount = User.objects.filter(subscription='0').count()
    pmcount = macount + mpcount
    scount = SkillTag.objects.all().count()
    ecount= Enterprise.objects.all().count()
    vcount = TalentRequired.objects.all().count()

    free_members = User.objects.filter(subscription='0')
    paid_members = PayPalIPN.objects.filter(txn_type="subscr_signup").values_list('custom', flat=True).distinct()
    passive_members = paid_members.filter(item_name__icontains='Passive Subscription')
    active_members = paid_members.filter(item_name__icontains='Active Subscription')

    date = timezone.now()
    d1 = date - timedelta(days=7)
    d2 = d1 - timedelta(days=7)
    d3 = d2 - timedelta(days=7)
    d4 = d3 - timedelta(days=7)
    d5 = d4 - timedelta(days=7)
    d6 = d5 - timedelta(days=7)
    d7 = d6 - timedelta(days=7)
    d8 = d7 - timedelta(days=7)
    d9 = d8 - timedelta(days=7)
    d10 = d9 - timedelta(days=7)
    d11 = d10 - timedelta(days=7)
    d12 = d11 - timedelta(days=7)
    d13 = d12 - timedelta(days=7)
    d14 = d13 - timedelta(days=7)
    d15 = d14 - timedelta(days=7)
    d16 = d15 - timedelta(days=7)
    d17 = d16 - timedelta(days=7)
    d18 = d17 - timedelta(days=7)
    d19 = d18 - timedelta(days=7)
    d20 = d19 - timedelta(days=7)
    d21 = d20 - timedelta(days=7)
    d22 = d21 - timedelta(days=7)
    d23 = d22 - timedelta(days=7)
    d24 = d23 - timedelta(days=7)

    monday1 = (d1 - timedelta(days=d1.weekday()))
    monday2 = (d2 - timedelta(days=d2.weekday()))
    monday3 = (d3 - timedelta(days=d3.weekday()))
    monday4 = (d4 - timedelta(days=d4.weekday()))
    monday5 = (d5 - timedelta(days=d5.weekday()))
    monday6 = (d6 - timedelta(days=d6.weekday()))
    monday7 = (d7 - timedelta(days=d7.weekday()))
    monday8 = (d8 - timedelta(days=d8.weekday()))
    monday9 = (d9 - timedelta(days=d9.weekday()))
    monday10 = (d10 - timedelta(days=d10.weekday()))
    monday11 = (d11 - timedelta(days=d11.weekday()))
    monday12 = (d12 - timedelta(days=d12.weekday()))
    monday13 = (d13 - timedelta(days=d13.weekday()))
    monday14 = (d14 - timedelta(days=d14.weekday()))
    monday15 = (d15 - timedelta(days=d15.weekday()))
    monday16 = (d16 - timedelta(days=d16.weekday()))
    monday17 = (d17 - timedelta(days=d17.weekday()))
    monday18 = (d18 - timedelta(days=d18.weekday()))
    monday19 = (d19 - timedelta(days=d19.weekday()))
    monday20 = (d20 - timedelta(days=d20.weekday()))
    monday21 = (d21 - timedelta(days=d21.weekday()))
    monday22 = (d22 - timedelta(days=d22.weekday()))
    monday23 = (d23 - timedelta(days=d23.weekday()))
    monday24 = (d24 - timedelta(days=d24.weekday()))

    week3_date = dateformat.format(monday2, "d-M")
    week4_date = dateformat.format(monday3, "d-M")
    week5_date = dateformat.format(monday4, "d-M")
    week6_date = dateformat.format(monday5, "d-M")
    week7_date = dateformat.format(monday6, "d-M")
    week8_date = dateformat.format(monday7, "d-M")
    week9_date = dateformat.format(monday8, "d-M")
    week10_date = dateformat.format(monday9, "d-M")
    week11_date = dateformat.format(monday10, "d-M")
    week12_date = dateformat.format(monday11, "d-M")
    week13_date = dateformat.format(monday12, "d-M")
    week14_date = dateformat.format(monday13, "d-M")
    week15_date = dateformat.format(monday14, "d-M")
    week16_date = dateformat.format(monday15, "d-M")
    week17_date = dateformat.format(monday16, "d-M")
    week18_date = dateformat.format(monday17, "d-M")
    week19_date = dateformat.format(monday18, "d-M")
    week20_date = dateformat.format(monday19, "d-M")
    week21_date = dateformat.format(monday20, "d-M")
    week22_date = dateformat.format(monday21, "d-M")
    week23_date = dateformat.format(monday22, "d-M")
    week24_date = dateformat.format(monday23, "d-M")

    fm_week1 = free_members.filter(registered_date__range=(monday1, date)).count()
    fm_week2 = free_members.filter(registered_date__range=(monday2, monday1)).count()
    fm_week3 = free_members.filter(registered_date__range=(monday3, monday2)).count()
    fm_week4 = free_members.filter(registered_date__range=(monday4, monday3)).count()
    fm_week5 = free_members.filter(registered_date__range=(monday5, monday4)).count()
    fm_week6 = free_members.filter(registered_date__range=(monday6, monday5)).count()
    fm_week7 = free_members.filter(registered_date__range=(monday7, monday6)).count()
    fm_week8 = free_members.filter(registered_date__range=(monday8, monday7)).count()
    fm_week9 = free_members.filter(registered_date__range=(monday9, monday8)).count()
    fm_week10 = free_members.filter(registered_date__range=(monday10, monday9)).count()
    fm_week11 = free_members.filter(registered_date__range=(monday11, monday10)).count()
    fm_week12 = free_members.filter(registered_date__range=(monday12, monday11)).count()
    fm_week13 = free_members.filter(registered_date__range=(monday13, monday12)).count()
    fm_week14 = free_members.filter(registered_date__range=(monday14, monday13)).count()
    fm_week15 = free_members.filter(registered_date__range=(monday15, monday14)).count()
    fm_week16 = free_members.filter(registered_date__range=(monday16, monday14)).count()
    fm_week17 = free_members.filter(registered_date__range=(monday17, monday16)).count()
    fm_week18 = free_members.filter(registered_date__range=(monday18, monday17)).count()
    fm_week19 = free_members.filter(registered_date__range=(monday19, monday18)).count()
    fm_week20 = free_members.filter(registered_date__range=(monday20, monday19)).count()
    fm_week21 = free_members.filter(registered_date__range=(monday21, monday20)).count()
    fm_week22 = free_members.filter(registered_date__range=(monday22, monday21)).count()
    fm_week23 = free_members.filter(registered_date__range=(monday23, monday22)).count()
    fm_week24 = free_members.filter(registered_date__range=(monday24, monday23)).count()

    pm_week1 = passive_members.filter(subscr_date__range=(monday1, date)).count()
    pm_week2 = passive_members.filter(subscr_date__range=(monday2, monday1)).count()
    pm_week3 = passive_members.filter(subscr_date__range=(monday3, monday2)).count()
    pm_week4 = passive_members.filter(subscr_date__range=(monday4, monday3)).count()
    pm_week5 = passive_members.filter(subscr_date__range=(monday5, monday4)).count()
    pm_week6 = passive_members.filter(subscr_date__range=(monday6, monday5)).count()
    pm_week7 = passive_members.filter(subscr_date__range=(monday7, monday6)).count()
    pm_week8 = passive_members.filter(subscr_date__range=(monday8, monday7)).count()
    pm_week9 = passive_members.filter(subscr_date__range=(monday9, monday8)).count()
    pm_week10 = passive_members.filter(subscr_date__range=(monday10, monday9)).count()
    pm_week11 = passive_members.filter(subscr_date__range=(monday11, monday10)).count()
    pm_week12 = passive_members.filter(subscr_date__range=(monday12, monday11)).count()
    pm_week13 = passive_members.filter(subscr_date__range=(monday13, monday12)).count()
    pm_week14 = passive_members.filter(subscr_date__range=(monday14, monday13)).count()
    pm_week15 = passive_members.filter(subscr_date__range=(monday15, monday14)).count()
    pm_week16 = passive_members.filter(subscr_date__range=(monday16, monday14)).count()
    pm_week17 = passive_members.filter(subscr_date__range=(monday17, monday16)).count()
    pm_week18 = passive_members.filter(subscr_date__range=(monday18, monday17)).count()
    pm_week19 = passive_members.filter(subscr_date__range=(monday19, monday18)).count()
    pm_week20 = passive_members.filter(subscr_date__range=(monday20, monday19)).count()
    pm_week21 = passive_members.filter(subscr_date__range=(monday21, monday20)).count()
    pm_week22 = passive_members.filter(subscr_date__range=(monday22, monday21)).count()
    pm_week23 = passive_members.filter(subscr_date__range=(monday23, monday22)).count()
    pm_week24 = passive_members.filter(subscr_date__range=(monday24, monday23)).count()

    am_week1 = active_members.filter(subscr_date__range=(monday1, date)).count()
    am_week2 = active_members.filter(subscr_date__range=(monday2, monday1)).count()
    am_week3 = active_members.filter(subscr_date__range=(monday3, monday2)).count()
    am_week4 = active_members.filter(subscr_date__range=(monday4, monday3)).count()
    am_week5 = active_members.filter(subscr_date__range=(monday5, monday4)).count()
    am_week6 = active_members.filter(subscr_date__range=(monday6, monday5)).count()
    am_week7 = active_members.filter(subscr_date__range=(monday7, monday6)).count()
    am_week8 = active_members.filter(subscr_date__range=(monday8, monday7)).count()
    am_week9 = active_members.filter(subscr_date__range=(monday9, monday8)).count()
    am_week10 = active_members.filter(subscr_date__range=(monday10, monday9)).count()
    am_week11 = active_members.filter(subscr_date__range=(monday11, monday10)).count()
    am_week12 = active_members.filter(subscr_date__range=(monday12, monday11)).count()
    am_week13 = active_members.filter(subscr_date__range=(monday13, monday12)).count()
    am_week14 = active_members.filter(subscr_date__range=(monday14, monday13)).count()
    am_week15 = active_members.filter(subscr_date__range=(monday15, monday14)).count()
    am_week16 = active_members.filter(subscr_date__range=(monday16, monday14)).count()
    am_week17 = active_members.filter(subscr_date__range=(monday17, monday16)).count()
    am_week18 = active_members.filter(subscr_date__range=(monday18, monday17)).count()
    am_week19 = active_members.filter(subscr_date__range=(monday19, monday18)).count()
    am_week20 = active_members.filter(subscr_date__range=(monday20, monday19)).count()
    am_week21 = active_members.filter(subscr_date__range=(monday21, monday20)).count()
    am_week22 = active_members.filter(subscr_date__range=(monday22, monday21)).count()
    am_week23 = active_members.filter(subscr_date__range=(monday23, monday22)).count()
    am_week24 = active_members.filter(subscr_date__range=(monday24, monday23)).count()

    report_members_labels = [week24_date, week23_date, week22_date, week21_date, week20_date, week19_date, week18_date, week17_date, week16_date, week15_date, week14_date, week13_date, week12_date, week11_date, week10_date, week9_date, week8_date, week7_date, week6_date, week5_date, week4_date, week3_date, 'Last Week', 'This Week']

    free_members_weekly_data = [fm_week24, fm_week23, fm_week22, fm_week21, fm_week20, fm_week19, fm_week18, fm_week17, fm_week16, fm_week15, fm_week14, fm_week13, fm_week12, fm_week11, fm_week10, fm_week9, fm_week8, fm_week7, fm_week6, fm_week5, fm_week4, fm_week3, fm_week2, fm_week1]

    passive_members_weekly_data = [pm_week24, pm_week23, pm_week22, pm_week21, pm_week20, pm_week19, pm_week18, pm_week17, pm_week16, pm_week15, pm_week14, pm_week13, pm_week12, pm_week11, pm_week10, pm_week9, pm_week8, pm_week7, pm_week6, pm_week5, pm_week4, pm_week3, pm_week2, pm_week1]

    active_members_weekly_data = [am_week24, am_week23, am_week22, am_week21, am_week20, am_week19, am_week18, am_week17, am_week16, am_week15, am_week14, am_week13, am_week12, am_week11, am_week10, am_week9, am_week8, am_week7, am_week6, am_week5, am_week4, am_week3, am_week2, am_week1]

    template_name = 'management/dashboard.html'
    context = {
        'mcount': mcount,
        'macount': macount,
        'mpcount': mpcount,
        'mfcount': mfcount,
        'pmcount': pmcount,
        'scount': scount,
        'ecount': ecount,
        'vcount': vcount,
        'report_members_labels': report_members_labels,
        'free_members_weekly_data': free_members_weekly_data,
        'passive_members_weekly_data': passive_members_weekly_data,
        'active_members_weekly_data': active_members_weekly_data,
    }
    return render(request, template_name, context)


@login_required()
@subscription(3)
def ManagementActiveMembersView(request):

    mcount = User.objects.all().count()
    macount = User.objects.filter(subscription='2').count()
    mpcount = User.objects.filter(subscription='1').count()
    mfcount = User.objects.filter(subscription='0').count()
    pmcount = macount + mpcount
    scount = SkillTag.objects.all().count()
    ecount= Enterprise.objects.all().count()
    vcount = TalentRequired.objects.all().count()

    paid_members = PayPalIPN.objects.filter(txn_type="subscr_signup").values_list('payer_email', flat=True)
    active_members = paid_members.filter(item_name__icontains='Active Subscription')

    date = timezone.now()
    d1 = date - timedelta(days=30)
    month1 = (d1 - timedelta(days=d1.monthly()))
    am_month1 = active_members.filter(payment_date__range=(month1, date)).count()

    template_name = 'management/active_members.html'
    context = {
        'mcount': mcount,
        'macount': macount,
        'am_month1': am_month1,
        'mpcount': mpcount,
        'mfcount': mfcount,
        'pmcount': pmcount,
        'scount': scount,
        'ecount': ecount,
        'vcount': vcount
    }
    return render(request, template_name, context)


@login_required()
@subscription(3)
def all_open_vacancies(request):
    '''Management view to see all vacancies'''
    qs = TalentRequired.objects.all()

    qs_o = qs.filter(offer_status='O').order_by('-bid_open')
    qs_oc = qs_o.count()

    qs_c = qs.filter(offer_status='C').order_by('-bid_open')
    qs_cc = qs_c.count()

    template = 'management/vacancies_status.html'
    context = {
        'qs_o': qs_o,
        'qs_oc': qs_oc,
        'qs_c': qs_c,
        'qs_cc': qs_cc,
    }
    return render(request, template, context)

@login_required()
@subscription(3)
def all_bids(request):
    '''Management view to see all bids'''
    qs = WorkBid.objects.all()

    qs_o = qs.filter(work__offer_status='O').order_by('-date_applied')
    qs_oc = qs_o.count()

    qs_c = qs.filter(work__offer_status='C').order_by('-date_applied')
    qs_cc = qs_c.count()

    template = 'management/vacancies_bids.html'
    context = {
        'qs_o': qs_o,
        'qs_oc': qs_oc,
        'qs_c': qs_c,
        'qs_cc': qs_cc,
    }
    return render(request, template, context)


@login_required()
@subscription(3)
def work_issued(request):
    '''Management view to see all vacancy placements'''
    qs = WorkIssuedTo.objects.all().order_by('-date_complete')
    qs_c = qs.count()

    template = 'management/vacancies_issued.html'
    context = {
        'qs': qs,
        'qs_c': qs_c,
    }
    return render(request, template, context)
