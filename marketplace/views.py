from django.shortcuts import render, get_object_or_404, redirect
from django.utils.http import is_safe_url
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import PermissionDenied
import json
from django.db.models import Count, Sum, Max, Min, F, Q
from django.db.models.functions import Greatest
from django.utils import timezone
import datetime
from datetime import timedelta
from decimal import getcontext, Decimal
import itertools

from csp.decorators import csp_exempt
from core.decorators import subscription
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.postgres.search import SearchVector, TrigramSimilarity

from xml.etree.ElementTree import Element, SubElement, tostring
from django.utils.html import strip_tags

#email
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags


from .forms import (
        TalentAvailabillityForm, SkillRequiredForm, SkillLevelForm, DeliverablesForm, TalentRequiredForm, WorkLocationForm, WorkBidForm, TalentRequiredEditForm, TalentInterViewComments, EmployerInterViewComments, AssignWorkForm, VacancySearchForm, TltIntCommentForm
)

from .models import(
    TalentRequired, SkillRequired, Deliverables, TalentAvailabillity, WorkBid, SkillLevel, BidShortList, WorkIssuedTo, BidInterviewList, WorkLocation, VacancyViewed, VacancyViewed
)

from WeXlog.app_config import (
    skill_pass_score,
)
from talenttrack.models import WorkExperience, LicenseCertification, Result
from locations.models import Region
from db_flatten.models import SkillTag
from users.models import CustomUser, ExpandedView
from Profile.models import (
    Profile, LanguageTrack, PhysicalAddress, BriefCareerHistory, WillingToRelocate
    )
from booklist.models import ReadBy
from enterprises.models import Branch

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from analytics.signals import object_viewed_signal

import sendgrid
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Subject, To, ReplyTo, SendAt, Content, From, CustomArg, Header)

from .models import UNIT, RATE_UNIT

def jooble_feed(request):
    """<link> - the full URL of a job, where Jooble will forward users to. The link must lead to a page with a complete job description.
    <name> - job title.
    <region> - list of regions/cities. Regions can be listed in a text format and separated by any punctuation marks.
    <description> - a complete job description. Please note that we are able to index an XML feed that contains complete jobs descriptions. If there are additional fields such as “job description”, “candidates’ requirements”, “responsibilities”, “working conditions” on a job page, they must be included to the <description> tag.
    <pubdate> - original publication date of a job. Please specify the date in the DD.MM.YYYY format.
    <updated> * - last modification date of a job. By this, we mean the last time when the original publication date of a job was updated, or when a job description was edited by an employer. Please specify the date in the DD.MM.YYYY format.
    <salary> ** - salary + currency. For example, "300$", "1500€" or "167£".
    <company> ** - a company name, name of employer.
    <expire> ** - date when a job gets expired. Please specify the date in the DD.MM.YYYY format.
    <jobtype> ** - type of a job. For example, full-time, part-time, contract, internship, temporary."""

    now = timezone.now()
    monthly = datetime.timedelta(days=45)

    indexable_date = now - monthly

    current_vacancies = TalentRequired.objects.filter(Q(bid_open__gte=indexable_date) & Q(offer_status='O'))

    vacancies = current_vacancies.values_list('ref_no', flat=True).distinct()

    jobs = []
    jobs = Element('jobs')
    for vac in vacancies:
        job = SubElement(jobs, 'job')
        link = SubElement(job, 'link')
        name = SubElement(job, 'name')
        region = SubElement(job, 'region')
        salary = SubElement(job, 'salary')
        description = SubElement(job, 'description')
        company = SubElement(job, 'company')
        pubdate = SubElement(job, 'pubdate')
        updated = SubElement(job, 'updated')
        expire = SubElement(job, 'expire')
        jobtype = SubElement(job, 'jobtype')

        job_id = current_vacancies.get(ref_no=vac).id
        job.set("id", f'{job_id}')

        ref = current_vacancies.get(ref_no=vac).ref_no
        link.text = f'<![CDATA[https://app.mywexlog.com/marketplace/public/vacancy/{ref}/]]>'
        name.text = f'<![CDATA[{current_vacancies.get(ref_no=vac).title}]]>'
        region_qs = current_vacancies.get(ref_no=vac).city.region.region
        city_qs = current_vacancies.get(ref_no=vac).city.city
        region.text = f'<![CDATA[{city_qs}, {region_qs}]]>'
        description_scope_qs = strip_tags(current_vacancies.get(ref_no=vac).scope)
        description_expectations_qs = strip_tags(current_vacancies.get(ref_no=vac).expectations)

        description_skills = SkillRequired.objects.filter(scope__ref_no=vac).values_list('skills__skill')
        skills_string_list = [", ".join(s) for s in description_skills]
        skills_string = ", ".join(skills_string_list)

        description.text = f'<![CDATA[Scope: {description_scope_qs}\n Expectations: {description_expectations_qs}\n Skills: {skills_string}]]>'
        pubdate.text = f'{current_vacancies.get(ref_no=vac).bid_open.strftime("%d.%m.%Y")}'
        updated.text = f'{current_vacancies.get(ref_no=vac).date_modified.strftime("%d.%m.%Y")}'
        salary_rate = current_vacancies.get(ref_no=vac).rate_offered
        salary_curency = current_vacancies.get(ref_no=vac).currency.currency_abv

        rate_unit = []
        for p in current_vacancies.get(ref_no=vac).rate_unit:
            ru_choice = {k: v for k, v in RATE_UNIT}[p[-1]]
#            rate_unit.append(list(p[:-1]) + [ru_choice])

        salary.text = f'<![CDATA[{salary_rate}{salary_curency}/{ru_choice}]]>'
        company.text = f'<![CDATA[{current_vacancies.get(ref_no=vac).companybranch.company.ename}]]>'
        expire.text = f'{current_vacancies.get(ref_no=vac).bid_closes.strftime("%d.%m.%Y")}'
        result = []
        for p in current_vacancies.get(ref_no=vac).unit:
            choice = {k: v for k, v in UNIT}[p[-1]]
        jobtype.text = f'{choice}'
#            result.append(list(p[:-1]) + [choice])

    xml = tostring(jobs, encoding='utf8').decode('utf8')

    return HttpResponse(xml, content_type="text/xml")


@login_required()
@subscription(2)
def VacancySearch(request):
    form = VacancySearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = VacancySearchForm(request.GET)
        if form.is_valid():
            query=form.cleaned_data['query']
            results = TalentRequired.objects.annotate(similarity=Greatest(
                                          TrigramSimilarity('ref_no', query),
                                          TrigramSimilarity('own_ref_no', query)
                                          )).filter(similarity__gt=0.3).order_by('-similarity')

    template = 'marketplace/vacancy_search.html'
    context = {'form': form, 'query': query, 'results': results,}
    return render(request, template, context)


@login_required()
@subscription(1)
def TalentInterviewHistoryView(request, tlt):
    interviews = BidInterviewList.objects.filter(talent__alias=tlt).order_by('-date_listed')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(interviews, 20)

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

    template = 'marketplace/talent_interview_history.html'
    context = {'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


@login_required()
def TltInterviewClose(request, bil, tlt):
    bil_qs = BidInterviewList.objects.filter(slug=bil)

    bil_qs.update(tlt_intcomplete=True)

    return redirect(reverse('MarketPlace:TalentInterviewHistory', kwargs={'tlt': tlt}))


@login_required()
@subscription(1)
def TltIntFullDetail(request, bil, tlt):
    bil_qs = BidInterviewList.objects.filter(slug=bil)
    user = request.user

    template = 'marketplace/talent_interview_detail.html'
    context = {'bil_qs': bil_qs, 'user': user}
    return render(request, template, context)


@login_required()
@subscription(2)
def EmployerInterviewHistoryView(request, tlt):
    interviews = BidInterviewList.objects.filter(scope__requested_by__alias=tlt).order_by('-date_listed')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(interviews, 20)

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

    template = 'marketplace/interview_history_employer.html'
    context = {'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(2)
def EmpInterviewClose(request, bil, tlt):
    bil_qs = BidInterviewList.objects.filter(slug=bil)

    bil_qs.update(emp_intcomplete=True)

    return redirect(reverse('MarketPlace:EmployerInterviewHistory', kwargs={'tlt': tlt}))


@login_required()
@subscription(2)
def emp_dashint_close(request, bil, tlt):
    '''Closes an interview and return to the Vacancy Dashboard'''
    bil_qs = BidInterviewList.objects.filter(slug=bil)
    vac = bil_qs[0].scope.ref_no

    bil_qs.update(emp_intcomplete=True)

    return redirect(reverse('MarketPlace:InterviewList', kwargs={'vac': vac}))


@login_required()
@subscription(2)
def EmpIntFullDetail(request, bil, tlt):
    bil_qs = BidInterviewList.objects.filter(slug=bil)

    template = 'marketplace/interview_detail_employer.html'
    context = {'bil_qs': bil_qs}
    return render(request, template, context)


@login_required()
def TltIntCommentView(request, bil, tlt):
    instance = BidInterviewList.objects.get(slug=bil)

    form = TltIntCommentForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.tlt_reponded = timezone.now()
            new.save()

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('MarketPlace:Entrance')
            return HttpResponseRedirect(next_url)
    else:
        template = 'marketplace/talent_interview_comment.html'
        context={'form': form, 'instance': instance,}
        return render(request, template, context)


#View all interviews grouped per vacancy
@login_required()
@subscription(2)
def EmpIntDetailVacancy(request, vac):
    bil_qs = BidInterviewList.objects.filter(scope__ref_no=vac)
    info = TalentRequired.objects.get(ref_no=vac)

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(bil_qs, 20)

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


    template = 'marketplace/interview_history_vacancy.html'
    context = {'bil_qs': bil_qs, 'info': info, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


@login_required()
def EmpIntCommentView(request, bil, tlt):
    instance = BidInterviewList.objects.get(slug=bil)
    form = EmployerInterViewComments(request.POST or None, instance=instance)

    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.save()

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('MarketPlace:Entrance')
            return HttpResponseRedirect(next_url)

    else:
        template = 'marketplace/interview_comment_employer.html'
        context={'form': form, 'instance': instance,}
        return render(request, template, context)


#comments when lablelling talent as unsuitable in the short list
@login_required()
def EmpSlDeclineComment(request, bil, tlt):
    instance = BidInterviewList.objects.get(slug=bil)
    vac = instance.scope.ref_no
    form = EmployerInterViewComments(request.POST or None, instance=instance)

    BidShortList.objects.filter(Q(scope__ref_no = vac) & Q(talent__alias = tlt)).update(status='R')#1

    bid_qs = WorkBid.objects.filter(Q(work__ref_no = vac) & Q(talent__alias = tlt))

    if bid_qs:
        bid_qs.update(bidreview = 'R')#2

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.outcome = 'N'#3
            new.tlt_response = 'N'#3
            new.emp_intcomplete = True#3
            new.tlt_intcomplete = True#3
            new.save()

            return redirect(reverse('MarketPlace:ShortListView', kwargs={'vac': vac,}))

    else:
        template = 'marketplace/interview_comment_employer.html'
        context={'form': form, 'instance': instance,}
        return render(request, template, context)


@login_required()
@subscription(1)
def InterviewDeclineView(request, int_id):
    instance = BidInterviewList.objects.get(pk=int_id)
    form = TalentInterViewComments(request.POST, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.tlt_reponded = timezone.now()
            new.save()
            return redirect(reverse('Profile:ProfileHome'))
    else:
        template = 'marketplace/interview_comment_tlt.html'
        context={'form': form, 'instance': instance,}
        return render(request, template, context)


@login_required()
@subscription(2)
def TalentRFIView(request, wit):
    instance = WorkIssuedTo.objects.get(slug=wit)
    instance.tlt_reponded = timezone.now()
    instance.save()

    template = 'marketplace/rfi_view.html'
    context = {'instance': instance,}
    return render(request, template, context)


@login_required()
@subscription(2)
def InterviewSuitable(request, vac, tlt):
    instance = BidInterviewList.objects.get(Q(talent__alias=tlt) & Q(scope__ref_no=vac))

    if request.method == 'POST':
        form = EmployerInterViewComments(request.POST, instance=instance)
        if form.is_valid():
            new = form.save(commit=False)
            new.outcome = 'S'#3
            new.emp_intcomplete=True#3
            new.save()

            BidShortList.objects.filter(Q(scope__ref_no = vac) & Q(talent__alias = tlt)).update(status='P')#1

            bid_qs = WorkBid.objects.filter(Q(work__ref_no = vac) & Q(talent__alias = tlt))

            if bid_qs:
                bid_qs.update(bidreview = 'P')#2

            return redirect(reverse('MarketPlace:InterviewList', kwargs={'vac': vac,}))

    form = EmployerInterViewComments(instance=instance)
    template = 'marketplace/interview_comment_employer.html'
    context = {'form': form, 'instance': instance,}
    return render(request, template, context)

@login_required()
@subscription(2)
def dash_int_suitable(request, vac, tlt):
    '''The button on the Interview detail view from the dashboard to comment page'''
    instance = BidInterviewList.objects.get(Q(talent__alias=tlt) & Q(scope__ref_no=vac))

    if request.method == 'POST':
        form = EmployerInterViewComments(request.POST, instance=instance)
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.outcome = 'S'#3
            new.emp_intcomplete=True#3
            BidShortList.objects.filter(Q(scope__ref_no = vac) & Q(talent__alias = tlt)).update(status='P')#1

            bid_qs = WorkBid.objects.filter(Q(work__ref_no = vac) & Q(talent__alias = tlt))

            if bid_qs:
                bid_qs.update(bidreview = 'P')#2
            new.save()

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('MarketPlace:Home')
            return HttpResponseRedirect(next_url)

            #return redirect(reverse('MarketPlace:EmployerIntDetail', kwargs={'bil': instance.slug, 'tlt': tlt,}))

    form = EmployerInterViewComments(instance=instance)
    template = 'marketplace/interview_comment_employer.html'
    context = {'form': form, 'instance': instance,}
    return render(request, template, context)

@login_required()
@subscription(2)
def PendingInterviewSuitable(request, vac, tlt):
    instance = BidInterviewList.objects.get(Q(talent__alias=tlt) & Q(scope__ref_no=vac))

    form = EmployerInterViewComments(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()

        instance.outcome = 'S'#3
        instance.emp_intcomplete=True#3
        instance.save()

        BidShortList.objects.filter(Q(scope__ref_no = vac) & Q(talent__alias = tlt)).update(status='P')#1

        bid_qs = WorkBid.objects.filter(Q(work__ref_no = vac) & Q(talent__alias = tlt))

        if bid_qs:
            bid_qs.update(bidreview = 'P')#2

    return redirect(reverse('MarketPlace:PendingInterviewList', kwargs={'vac': vac,}))


@login_required()
@subscription(2)
def UnsuitableInterviewSuitable(request, vac, tlt):
    instance = BidInterviewList.objects.get(Q(talent__alias=tlt) & Q(scope__ref_no=vac))

    form = EmployerInterViewComments(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()

        instance.outcome = 'S'#3
        instance.emp_intcomplete=True#3
        instance.save()

        BidShortList.objects.filter(Q(scope__ref_no = vac) & Q(talent__alias = tlt)).update(status='P')#1

        bid_qs = WorkBid.objects.filter(Q(work__ref_no = vac) & Q(talent__alias = tlt))

        if bid_qs:
            bid_qs.update(bidreview = 'P')#2

    return redirect(reverse('MarketPlace:UnsuitableInterviewList', kwargs={'vac': vac,}))

#Switch in InterviewList view to mark talent as not-suitable
@login_required()
@subscription(2)
def InterviewNotSuitable(request, vac, tlt):
    instance = BidInterviewList.objects.get(Q(talent__alias=tlt) & Q(scope__ref_no=vac))

    form = EmployerInterViewComments(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.outcome = 'N'#3
            new.emp_intcomplete = True#3
            new.save()

            BidShortList.objects.filter(Q(scope__ref_no = vac) & Q(talent__alias = tlt)).update(status='R')#1

            bid_qs = WorkBid.objects.filter(Q(work__ref_no = vac) & Q(talent__alias = tlt))

            if bid_qs:
                bid_qs.update(bidreview = 'R')#2

        return redirect(reverse('MarketPlace:InterviewList', kwargs={'vac': vac,}))

    template = 'marketplace/interview_comment_employer.html'
    context = {'form': form, 'instance': instance,}
    return render(request, template, context)


@login_required()
@subscription(2)
def dash_notsuitable(request, vac, tlt):
    '''The button on the Interview detail view from the dashboard'''
    instance = BidInterviewList.objects.get(Q(talent__alias=tlt) & Q(scope__ref_no=vac))

    form = EmployerInterViewComments(request.POST or None, instance=instance)
    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.outcome = 'N'#3
            new.emp_intcomplete = True#3
            BidShortList.objects.filter(Q(scope__ref_no = vac) & Q(talent__alias = tlt)).update(status='R')#1

            bid_qs = WorkBid.objects.filter(Q(work__ref_no = vac) & Q(talent__alias = tlt))

            if bid_qs:
                bid_qs.update(bidreview = 'R')#2

            new.save()

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('MarketPlace:Home')
            return HttpResponseRedirect(next_url)

    template = 'marketplace/interview_comment_employer.html'
    context = {'form': form, 'instance': instance,}
    return render(request, template, context)


@login_required()
@subscription(2)
def PendingInterviewNotSuitable(request, vac, tlt):
    instance = BidInterviewList.objects.get(Q(talent__alias=tlt) & Q(scope__ref_no=vac))

    form = EmployerInterViewComments(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.outcome = 'N'#3
            new.emp_intcomplete = True#3
            new.save()

            BidShortList.objects.filter(Q(scope__ref_no = vac) & Q(talent__alias = tlt)).update(status='R')#1

            bid_qs = WorkBid.objects.filter(Q(work__ref_no = vac) & Q(talent__alias = tlt))

            if bid_qs:
                bid_qs.update(bidreview = 'R')#2

        return redirect(reverse('MarketPlace:PendingInterviewList', kwargs={'vac': vac,}))

    template = 'marketplace/interview_comment_employer.html'
    context = {'form': form, 'instance': instance,}
    return render(request, template, context)


@login_required()
@subscription(2)
def SuitableInterviewNotSuitable(request, vac, tlt):
    instance = BidInterviewList.objects.get(Q(talent__alias=tlt) & Q(scope__ref_no=vac))

    form = EmployerInterViewComments(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.outcome = 'N'#3
            new.emp_intcomplete = True#3
            new.save()

            BidShortList.objects.filter(Q(scope__ref_no = vac) & Q(talent__alias = tlt)).update(status='R')#1

            bid_qs = WorkBid.objects.filter(Q(work__ref_no = vac) & Q(talent__alias = tlt))

            if bid_qs:
                bid_qs.update(bidreview = 'R')#2

        return redirect(reverse('MarketPlace:SuitableInterviewList', kwargs={'vac': vac,}))

    template = 'marketplace/interview_comment_employer.html'
    context = {'form': form, 'instance': instance,}
    return render(request, template, context)

#This has been re-purposed for a vacancy dashboard
@login_required()
@subscription(2)
def InterviewListView(request, vac):
    scope = TalentRequired.objects.get(ref_no=vac)
    intv_qs = BidInterviewList.objects.filter(scope__ref_no=vac)
    bid_qs = BidShortList.objects.filter(scope__ref_no=vac)

    intv_pending = intv_qs.filter(Q(outcome='I')).filter(Q(tlt_response='A') | Q(tlt_response='P'))

    intv_suitable = intv_qs.filter(Q(outcome = 'S') & ~Q(tlt_response='D'))
    intv_notsuitable = intv_qs.filter(Q(outcome = 'N') & ~Q(tlt_response='D'))
    bid_rejected = bid_qs.filter(status = 'Z')
    intv_declined = intv_qs.filter(tlt_response = 'D')[:5]
    intv_accepted = intv_qs.filter(tlt_response = 'A')[:5]
    vacancy_declined = WorkIssuedTo.objects.filter(work__ref_no=vac, tlt_response='D')[:5]

    intv_accepted_count = intv_accepted.count()
    intv_declined_count = intv_declined.count()
    vacancy_declined_count = vacancy_declined.count()

    wit_qs = WorkIssuedTo.objects.filter(Q(work__ref_no=vac)).filter(Q(tlt_response='A'))
    wit_qs_p = WorkIssuedTo.objects.filter(Q(work__ref_no=vac)).filter(Q(tlt_response='P') | Q(tlt_response='C'))

    if wit_qs is None:
        active ='True'
    else:
        active = 'False'

    we = WorkExperience.objects.filter(Q(talent__subscription__gte=0) & Q(score__gte=skill_pass_score))
    skille = SkillRequired.objects.filter(scope__ref_no=vac)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    book = ReadBy.objects.all()
    vac_exp = ExpandedView.objects.get(talent=request.user)
    pending_interviews_list_view = vac_exp.pending_interviews_list
    suitable_applicants_list_view = vac_exp.suitable_applicants_list
    unsuitable_applicants_list_view = vac_exp.unsuitable_applicants_list
    rejected_applicants_list_view = vac_exp.rejected_applicants_list
    sk_st = SkillLevel.objects.get(level=0).min_hours
    sk_bg = SkillLevel.objects.get(level=1).min_hours
    sk_jn = SkillLevel.objects.get(level=2).min_hours
    sk_in = SkillLevel.objects.get(level=3).min_hours
    sk_sn = SkillLevel.objects.get(level=4).min_hours
    sk_ld = SkillLevel.objects.get(level=5).min_hours

    #Information for all suitable applicants
    suitable_list = list(intv_suitable.values_list('talent', flat=True))

    skill_rs = skille.values_list('skills__skill', flat=True).distinct()
    skill_rc = skill_rs.count()

    interview_s ={}
    for app in suitable_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        talent_skill_l = we.filter(talent=app, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=app, edt=True).values_list('topic__skills__skill', flat=True)
        atalent_skill = list(talent_skill_l)
        rb = book.filter(talent=app).count()
        atalent_skillt = list(talent_skillt_l)
        des = list(BriefCareerHistory.objects.filter(talent=app, current=True).values_list('designation__name', flat=True))
        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count
        bg = pfl.background

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')

        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        slist_l = talent_skill_l.union(talent_skillt_l)
        skill_intersection = skill_rs.intersection(slist_l)
        skill_int_count = skill_intersection.count()
        skill_match = skill_int_count / skill_rc * 100

        interview_s[app]={
            'we':awetv, 'te':atetv, 's_no': askill_count, 'skill_rc': skill_rc, 'skill_int_count': skill_int_count, 'skill_match': skill_match, 'skillset': askillset, 'rb':rb, 'ro':rate, 'score':avg, 'count': cnt, 'background': bg, 'des': des,
            }

    interview_s_slice = dict(itertools.islice(interview_s.items(), 5))
    interview_s_count = len(interview_s)

    #Information for all pending applicants
    pending_list = list(intv_pending.values_list('talent', flat=True))

    interview_p ={}
    for app in pending_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        talent_skill_l = we.filter(talent=app, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=app, edt=True).values_list('topic__skills__skill', flat=True)
        atalent_skill = list(talent_skill_l)
        rb = book.filter(talent=app).count()
        atalent_skillt = list(talent_skillt_l)
        applied = applicants.filter(talent=app)
        des = list(BriefCareerHistory.objects.filter(talent=app, current=True).values_list('designation__name', flat=True))
        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count
        bg = pfl.background

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        slist_l = talent_skill_l.union(talent_skillt_l)
        skill_intersection = skill_rs.intersection(slist_l)
        skill_int_count = skill_intersection.count()
        skill_match = skill_int_count / skill_rc * 100


        interview_p[app]={'we':awetv, 'te':atetv, 's_no': askill_count, 'skill_rc': skill_rc, 'skill_int_count': skill_int_count, 'skill_match': skill_match, 'skillset': askillset, 'rb':rb, 'ro':rate, 'score':avg, 'count':cnt, 'background': bg, 'des': des,}

    interview_p_slice = dict(itertools.islice(interview_p.items(), 5))
    interview_p_count = len(interview_p)

    #Information for all not suitable applicants
    nots_list = list(intv_notsuitable.values_list('talent', flat=True))

    interview_n ={}
    for app in nots_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        talent_skill_l = we.filter(talent=app, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=app, edt=True).values_list('topic__skills__skill', flat=True)
        atalent_skill = list(talent_skill_l)
        rb = book.filter(talent=app).count()
        atalent_skillt = list(talent_skillt_l)
        des = list(BriefCareerHistory.objects.filter(talent=app, current=True).values_list('designation__name', flat=True))
        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count
        bg = pfl.background

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        slist_l = talent_skill_l.union(talent_skillt_l)
        skill_intersection = skill_rs.intersection(slist_l)
        skill_int_count = skill_intersection.count()
        skill_match = skill_int_count / skill_rc * 100


        interview_n[app]={'we':awetv, 'te':atetv, 's_no': askill_count, 'skill_rc': skill_rc, 'skill_int_count': skill_int_count, 'skill_match': skill_match, 'skillset': askillset, 'rb':rb, 'ro':rate, 'score':avg, 'count': cnt, 'background': bg, 'des': des,}

    interview_n_slice = dict(itertools.islice(interview_n.items(), 5))
    interview_n_count = len(interview_n)

    #Information for all not rejected applicants
    rej_list = list(bid_rejected.values_list('talent', flat=True))

    rej_bid_n ={}
    for app in rej_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        talent_skill_l = we.filter(talent=app, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=app, edt=True).values_list('topic__skills__skill', flat=True)
        atalent_skill = list(talent_skill_l)
        rb = book.filter(talent=app).count()
        atalent_skillt = list(talent_skillt_l)
        des = list(BriefCareerHistory.objects.filter(talent=app, current=True).values_list('designation__name', flat=True))
        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count
        bg = pfl.background

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        slist_l = talent_skill_l.union(talent_skillt_l)
        skill_intersection = skill_rs.intersection(slist_l)
        skill_int_count = skill_intersection.count()
        skill_match = skill_int_count / skill_rc * 100


        rej_bid_n[app]={'we':awetv, 'te':atetv, 's_no': askill_count, 'skill_rc': skill_rc, 'skill_int_count': skill_int_count, 'skill_match': skill_match, 'skillset': askillset, 'rb':rb, 'ro':rate, 'score':avg, 'count': cnt, 'background': bg, 'des': des,}

    rej_bid_n_slice = dict(itertools.islice(rej_bid_n.items(), 5))
    rej_bid_n_count = len(rej_bid_n)

    template = 'marketplace/interview_list.html'
    context = {
        'vac': vac,
        'sk_st': sk_st,
        'sk_bg': sk_bg,
        'sk_jn': sk_jn,
        'sk_in': sk_in,
        'sk_sn': sk_sn,
        'sk_ld': sk_ld,
        'interview_p': interview_p,
        'interview_p_slice': interview_p_slice,
        'interview_p_count': interview_p_count,
        'interview_n': interview_n,
        'interview_n_slice': interview_n_slice,
        'interview_n_count': interview_n_count,
        'rej_bid_n': rej_bid_n,
        'rej_bid_n_slice': rej_bid_n_slice,
        'rej_bid_n_count': rej_bid_n_count,
        'interview_s': interview_s,
        'interview_s_slice': interview_s_slice,
        'interview_s_count': interview_s_count,
        'scope': scope,
        'intv_accepted': intv_accepted,
        'intv_accepted_count': intv_accepted_count,
        'intv_declined': intv_declined,
        'intv_declined_count': intv_declined_count,
        'vacancy_declined': vacancy_declined,
        'vacancy_declined_count': vacancy_declined_count,
        'pending_interviews_list_view': pending_interviews_list_view,
        'suitable_applicants_list_view': suitable_applicants_list_view,
        'unsuitable_applicants_list_view': unsuitable_applicants_list_view,
        'rejected_applicants_list_view': rejected_applicants_list_view,
        'wit_qs': wit_qs,
        'wit_qs_p': wit_qs_p,
        'active': active,
        'vac': vac,
        }
    return render(request, template, context)


@login_required()
@subscription(2)
def PendingInterviewListView(request, vac):
    scope = TalentRequired.objects.get(ref_no=vac)
    intv_qs = BidInterviewList.objects.filter(scope__ref_no=vac)

    intv_pending = intv_qs.filter(Q(outcome='I')).filter(Q(tlt_response='A') | Q(tlt_response='P'))

    we = WorkExperience.objects.filter(Q(talent__subscription__gte=0) & Q(score__gte=skill_pass_score))
    skille = SkillRequired.objects.filter(scope__ref_no=vac)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    book = ReadBy.objects.all()
    vac_exp = ExpandedView.objects.get(talent=request.user)
    pending_interviews_list_view = vac_exp.pending_interviews_list
    sk_st = SkillLevel.objects.get(level=0).min_hours
    sk_bg = SkillLevel.objects.get(level=1).min_hours
    sk_jn = SkillLevel.objects.get(level=2).min_hours
    sk_in = SkillLevel.objects.get(level=3).min_hours
    sk_sn = SkillLevel.objects.get(level=4).min_hours
    sk_ld = SkillLevel.objects.get(level=5).min_hours
    vac = vac

    skill_rs = skille.values_list('skills__skill', flat=True).distinct()
    skill_rc = skill_rs.count()

    #Information for all pending applicants
    pending_list = list(intv_pending.values_list('talent', flat=True))

    interview_p ={}
    for app in pending_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        talent_skill_l = we.filter(talent=app, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=app, edt=True).values_list('topic__skills__skill', flat=True)
        atalent_skill = list(talent_skill_l)
        rb = book.filter(talent=app).count()
        atalent_skillt = list(talent_skillt_l)
        applied = applicants.filter(talent=app)
        des = list(BriefCareerHistory.objects.filter(talent=app, current=True).values_list('designation__name', flat=True))
        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count
        bg = pfl.background

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        slist_l = talent_skill_l.union(talent_skillt_l)
        skill_intersection = skill_rs.intersection(slist_l)
        skill_int_count = skill_intersection.count()
        skill_match = skill_int_count / skill_rc * 100


        interview_p[app]={'we':awetv, 'te':atetv, 's_no': askill_count, 'skill_rc': skill_rc, 'skill_int_count': skill_int_count, 'skill_match': skill_match, 'skillset': askillset, 'rb':rb, 'ro':rate, 'score': avg, 'count': cnt, 'background': bg, 'des': des,}

    interview_p_count = len(interview_p)

    t = tuple(interview_p.items())

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(t, 20)

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


    template = 'marketplace/pending_interview_list.html'
    context = {
        'sk_st': sk_st,
        'sk_bg': sk_bg,
        'sk_jn': sk_jn,
        'sk_in': sk_in,
        'sk_sn': sk_sn,
        'sk_ld': sk_ld,
        'interview_p': interview_p,
        'interview_p_count': interview_p_count,
        'scope': scope,
        'vac': vac,
        'pending_interviews_list_view': pending_interviews_list_view,
        'pageitems': pageitems,
        'page_range': page_range
        }
    return render(request, template, context)


@login_required()
@subscription(2)
def SuitableInterviewListView(request, vac):
    scope = TalentRequired.objects.get(ref_no=vac)
    intv_qs = BidInterviewList.objects.filter(scope__ref_no=vac)

    intv_pending = intv_qs.filter(Q(outcome='I')).filter(Q(tlt_response='A') | Q(tlt_response='P'))

    intv_suitable = intv_qs.filter(Q(outcome = 'S') & ~Q(tlt_response='D'))

    wit_qs = WorkIssuedTo.objects.filter(Q(work__ref_no=vac)).filter(Q(tlt_response='A') | Q(tlt_response='P') | Q(tlt_response='C'))

    vac = vac

    if wit_qs is None:
        active ='True'
    else:
        active = 'False'

    we = WorkExperience.objects.filter(Q(talent__subscription__gte=0) & Q(score__gte=skill_pass_score))
    skille = SkillRequired.objects.filter(scope__ref_no=vac)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    book = ReadBy.objects.all()
    vac_exp = ExpandedView.objects.get(talent=request.user)
    suitable_applicants_list_view = vac_exp.suitable_applicants_list
    sk_st = SkillLevel.objects.get(level=0).min_hours
    sk_bg = SkillLevel.objects.get(level=1).min_hours
    sk_jn = SkillLevel.objects.get(level=2).min_hours
    sk_in = SkillLevel.objects.get(level=3).min_hours
    sk_sn = SkillLevel.objects.get(level=4).min_hours
    sk_ld = SkillLevel.objects.get(level=5).min_hours

    skill_rs = skille.values_list('skills__skill', flat=True).distinct()
    skill_rc = skill_rs.count()

    #Information for all suitable applicants
    suitable_list = list(intv_suitable.values_list('talent', flat=True))

    interview_s ={}
    for app in suitable_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        talent_skill_l = we.filter(talent=app, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=app, edt=True).values_list('topic__skills__skill', flat=True)
        atalent_skill = list(talent_skill_l)
        rb = book.filter(talent=app).count()
        atalent_skillt = list(talent_skillt_l)
        des = list(BriefCareerHistory.objects.filter(talent=app, current=True).values_list('designation__name', flat=True))
        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count
        bg = pfl.background

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')

        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        slist_l = talent_skill_l.union(talent_skillt_l)
        skill_intersection = skill_rs.intersection(slist_l)
        skill_int_count = skill_intersection.count()
        skill_match = skill_int_count / skill_rc * 100

        interview_s[app]={
            'we':awetv, 'te':atetv, 's_no': askill_count, 'skill_rc': skill_rc, 'skill_int_count': skill_int_count, 'skill_match': skill_match, 'skillset': askillset, 'rb':rb, 'ro':rate, 'score': avg, 'count': cnt, 'background': bg, 'des': des,
            }

    interview_s_count = len(interview_s)

    t = tuple(interview_s.items())

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(t, 20)

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


    template = 'marketplace/suitable_interview_list.html'
    context = {
        'vac': vac,
        'sk_st': sk_st,
        'sk_bg': sk_bg,
        'sk_jn': sk_jn,
        'sk_in': sk_in,
        'sk_sn': sk_sn,
        'sk_ld': sk_ld,
        'interview_s': interview_s,
        'interview_s_count': interview_s_count,
        'scope': scope,
        'wit_qs': wit_qs,
        'active': active,
        'suitable_applicants_list_view': suitable_applicants_list_view,
        'pageitems': pageitems,
        'page_range': page_range
        }
    return render(request, template, context)


@login_required()
@subscription(2)
def UnsuitableInterviewListView(request, vac):
    scope = TalentRequired.objects.get(ref_no=vac)
    intv_qs = BidInterviewList.objects.filter(scope__ref_no=vac)

    intv_notsuitable = intv_qs.filter(Q(outcome = 'N') & ~Q(tlt_response='D'))

    vacancy_declined = WorkIssuedTo.objects.filter(work__ref_no=vac, tlt_response='D')

    we = WorkExperience.objects.filter(Q(talent__subscription__gte=0) & Q(score__gte=skill_pass_score))
    skille = SkillRequired.objects.filter(scope__ref_no=vac)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    book = ReadBy.objects.all()
    vac_exp = ExpandedView.objects.get(talent=request.user)
    unsuitable_applicants_list_view = vac_exp.unsuitable_applicants_list
    sk_st = SkillLevel.objects.get(level=0).min_hours
    sk_bg = SkillLevel.objects.get(level=1).min_hours
    sk_jn = SkillLevel.objects.get(level=2).min_hours
    sk_in = SkillLevel.objects.get(level=3).min_hours
    sk_sn = SkillLevel.objects.get(level=4).min_hours
    sk_ld = SkillLevel.objects.get(level=5).min_hours

    skill_rs = skille.values_list('skills__skill', flat=True).distinct()
    skill_rc = skill_rs.count()

    #Information for all not suitable applicants
    nots_list = list(intv_notsuitable.values_list('talent', flat=True))

    interview_n ={}
    for app in nots_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        talent_skill_l = we.filter(talent=app, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=app, edt=True).values_list('topic__skills__skill', flat=True)
        atalent_skill = list(talent_skill_l)
        rb = book.filter(talent=app).count()
        atalent_skillt = list(talent_skillt_l)
        des = list(BriefCareerHistory.objects.filter(talent=app, current=True).values_list('designation__name', flat=True))
        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count
        bg = pfl.background

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        slist_l = talent_skill_l.union(talent_skillt_l)
        skill_intersection = skill_rs.intersection(slist_l)
        skill_int_count = skill_intersection.count()
        skill_match = skill_int_count / skill_rc * 100

        interview_n[app]={
            'we':awetv, 'te':atetv, 's_no': askill_count, 'skill_rc': skill_rc, 'skill_int_count': skill_int_count, 'skill_match': skill_match, 'skillset': askillset, 'rb':rb, 'ro':rate, 'score': avg, 'count': cnt, 'background': bg, 'des': des,
            }

    interview_n_count = len(interview_n)

    t = tuple(interview_n.items())

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(t, 20)

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


    template = 'marketplace/unsuitable_interview_list.html'
    context = {
        'vac': vac,
        'sk_st': sk_st,
        'sk_bg': sk_bg,
        'sk_jn': sk_jn,
        'sk_in': sk_in,
        'sk_sn': sk_sn,
        'sk_ld': sk_ld,
        'interview_n': interview_n,
        'interview_n_count': interview_n_count,
        'unsuitable_applicants_list_view': unsuitable_applicants_list_view,
        'scope': scope,
        'pageitems': pageitems,
        'page_range': page_range
        }
    return render(request, template, context)


@login_required()
@subscription(2)
def BidRejectedListView(request, vac):
    scope = TalentRequired.objects.get(ref_no=vac)
    bid_qs = BidShortList.objects.filter(scope__ref_no=vac)

    bid_rejected = bid_qs.filter(status = 'Z')

    vacancy_declined = WorkIssuedTo.objects.filter(work__ref_no=vac, tlt_response='D')

    we = WorkExperience.objects.filter(Q(talent__subscription__gte=0) & Q(score__gte=skill_pass_score))
    skille = SkillRequired.objects.filter(scope__ref_no=vac)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    book = ReadBy.objects.all()
    vac_exp = ExpandedView.objects.get(talent=request.user)
    rejected_applicants_list_view = vac_exp.rejected_applicants_list
    sk_st = SkillLevel.objects.get(level=0).min_hours
    sk_bg = SkillLevel.objects.get(level=1).min_hours
    sk_jn = SkillLevel.objects.get(level=2).min_hours
    sk_in = SkillLevel.objects.get(level=3).min_hours
    sk_sn = SkillLevel.objects.get(level=4).min_hours
    sk_ld = SkillLevel.objects.get(level=5).min_hours

    skill_rs = skille.values_list('skills__skill', flat=True).distinct()
    skill_rc = skill_rs.count()

    #Information for all not suitable applicants
    rej_list = list(bid_rejected.values_list('talent', flat=True))

    rej_bid_n ={}
    for app in rej_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        talent_skill_l = we.filter(talent=app, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=app, edt=True).values_list('topic__skills__skill', flat=True)
        atalent_skill = list(talent_skill_l)
        rb = book.filter(talent=app).count()
        atalent_skillt = list(talent_skillt_l)
        des = list(BriefCareerHistory.objects.filter(talent=app, current=True).values_list('designation__name', flat=True))
        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count
        bg = pfl.background

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        slist_l = talent_skill_l.union(talent_skillt_l)
        skill_intersection = skill_rs.intersection(slist_l)
        skill_int_count = skill_intersection.count()
        skill_match = skill_int_count / skill_rc * 100

        rej_bid_n[app]={
            'we':awetv, 'te':atetv, 's_no': askill_count, 'skill_rc': skill_rc, 'skill_int_count': skill_int_count, 'skill_match': skill_match, 'skillset': askillset, 'rb':rb, 'ro':rate, 'score': avg, 'count': cnt, 'background': bg, 'des': des,
            }

    rej_bid_n_count = len(rej_bid_n)

    t = tuple(rej_bid_n.items())

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(t, 20)

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


    template = 'marketplace/bids_rejected_list.html'
    context = {
        'vac': vac,
        'sk_st': sk_st,
        'sk_bg': sk_bg,
        'sk_jn': sk_jn,
        'sk_in': sk_in,
        'sk_sn': sk_sn,
        'sk_ld': sk_ld,
        'rej_bid_n': rej_bid_n,
        'rej_bid_n_count': rej_bid_n_count,
        'rejected_applicants_list_view': rejected_applicants_list_view,
        'scope': scope,
        'pageitems': pageitems,
        'page_range': page_range
        }
    return render(request, template, context)


@login_required()
@subscription(2)
def DeclinedInvInterviewListView(request, vac):
    scope = TalentRequired.objects.get(ref_no=vac)
    intv_qs = BidInterviewList.objects.filter(scope__ref_no=vac)

    intv_declined = intv_qs.filter(tlt_response = 'D')
    intv_declined_count = intv_declined.count()

    vac = vac

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(intv_declined, 20)

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


    template = 'marketplace/decline_inv_interview_list.html'
    context = {
        'intv_declined': intv_declined,
        'intv_declined_count': intv_declined_count,
        'scope': scope,
        'vac': vac,
        'pageitems': pageitems,
        'page_range': page_range
        }
    return render(request, template, context)


@login_required()
@subscription(2)
def DeclinedAssignmentInterviewListView(request, vac):
    scope = TalentRequired.objects.get(ref_no=vac)
    vacancy_declined = WorkIssuedTo.objects.filter(work__ref_no=vac, tlt_response='D')
    vacancy_declined_count = vacancy_declined.count()

    vac = vac

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(vacancy_declined, 20)

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


    template = 'marketplace/declined_assignments_interview_list.html'
    context = {
        'vacancy_declined': vacancy_declined,
        'vacancy_declined_count': vacancy_declined_count,
        'vac': vac,
        'scope': scope,
        'pageitems': pageitems,
        'page_range': page_range
        }
    return render(request, template, context)


@login_required()
@subscription(2)
def WorkBidView(request, vac):
    detail = TalentRequired.objects.get(ref_no=vac)
    bid_qs = WorkBid.objects.filter(Q(work__ref_no=vac) & Q(talent=request.user))

    form = WorkBidForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.work = detail
            new.currency = detail.currency
            new.rate_unit = detail.rate_unit
            new.save()
            if 'profile' in request.POST:
                return redirect(reverse('Profile:ProfileView'))
            elif 'another' in request.POST:
                return redirect(reverse('MarketPlace:Entrance'))
    else:

        template = 'marketplace/vacancy_apply.html'
        context={'form': form, 'detail': detail, 'bid_qs': bid_qs,}
        return render(request, template, context)

#This is the detail view for talent and where active users can apply for the role
@login_required()
@subscription(2)
def VacancyDetailView(request, vac):
    tlt = request.user.id
    vacancy = TalentRequired.objects.filter(ref_no=vac)
    vac_id = vacancy[0]
    skills = SkillRequired.objects.filter(scope__ref_no=vac)
    deliver = Deliverables.objects.filter(scope__ref_no=vac)
    bch = vacancy[0].companybranch.slug
    rate_b = Branch.objects.get(slug=bch)
    int = BidInterviewList.objects.filter(Q(scope__ref_no=vac)).count()
    bid_qs = WorkBid.objects.filter(work__ref_no=vac).order_by('rate_bid')
    bid = bid_qs.count()
    slist = BidShortList.objects.filter(scope__ref_no=vac).count()
    wit = WorkIssuedTo.objects.filter(Q(tlt_response='A') & Q(work__ref_no=vac))
    applied = bid_qs.filter(talent=request.user)

    date1 = vacancy[0].bid_closes
    date2 = timezone.now()
    date3 = date1 - date2
    date4 = abs(date3.days)

    if date1 < date2:
        vacancy.update(offer_status = 'C')

    cu = CustomUser.objects.get(id=tlt)
    VacancyViewed.objects.create(talent=cu, vacancy=vac_id, read=True,  date_read=timezone.now()).save()

    template = 'marketplace/vacancy_detail.html'
    context = {
        'vacancy': vacancy,
        'skills': skills,
        'deliver': deliver,
        'rate_b': rate_b,
        'int': int,
        'bid': bid,
        'slist': slist,
        'wit': wit,
        'bid_qs': bid_qs,
        'date2': date2,
        'date4': date4,
        'applied': applied,
        }
    return render(request, template, context)


def VacancyDetailPublicView(request, vac):
    vacancy = TalentRequired.objects.filter(ref_no=vac)
    vac_id = vacancy[0]
    skills = SkillRequired.objects.filter(scope__ref_no=vac)
    deliver = Deliverables.objects.filter(scope__ref_no=vac)
    bch = vacancy[0].companybranch.slug
    rate_b = Branch.objects.get(slug=bch)
    int = BidInterviewList.objects.filter(Q(scope__ref_no=vac)).count()
    bid_qs = WorkBid.objects.filter(work__ref_no=vac).order_by('rate_bid')
    bid = bid_qs.count()
    slist = BidShortList.objects.filter(scope__ref_no=vac).count()
    wit = WorkIssuedTo.objects.filter(Q(tlt_response='A') & Q(work__ref_no=vac))
    try:
        applied = bid_qs.filter(talent=request.user)
    except:
        applied = False

    date1 = vacancy[0].bid_closes
    date2 = timezone.now()
    date3 = date1 - date2
    date4 = abs(date3.days)

    if date1 < date2:
        vacancy.update(offer_status = 'C')


    template = 'marketplace/vacancy_detail_public.html'
    context = {
        'vacancy': vacancy,
        'skills': skills,
        'deliver': deliver,
        'rate_b': rate_b,
        'int': int,
        'bid': bid,
        'slist': slist,
        'wit': wit,
        'bid_qs': bid_qs,
        'date2': date2,
        'date4': date4,
        'applied': applied,
        }
    return render(request, template, context)


@login_required()
@subscription(1)
def VacancyDetailView_Profile(request, vac):
    vacancy = TalentRequired.objects.filter(ref_no=vac)
    skills = SkillRequired.objects.filter(scope__ref_no=vac)
    deliver = Deliverables.objects.filter(scope__ref_no=vac)
    bch = vacancy[0].companybranch.slug
    bch_r = Branch.objects.get(slug=bch)

    template = 'marketplace/vacancy_detail_profile.html'
    context = {'vacancy': vacancy, 'skills': skills, 'deliver': deliver, 'bch_r': bch_r}
    return render(request, template, context)


@login_required()
@subscription(2)
def AllPostedVacanciesView(request):
    #>>>Queryset caching
    talent=request.user
    tr = TalentRequired.objects.filter(requested_by=request.user)
    wb = WorkBid.objects.filter(work__requested_by=talent)
    #Queryset caching<<<
    ipost = tr.order_by('-bid_open')
    ipost_bid = wb.filter(Q(bidreview__exact='R') | Q(bidreview__exact='P') | Q(bidreview__exact='A'))
    ipost_bid_flat = ipost_bid.values_list('work', flat=True).distinct()

    ipost_count = tr.order_by('-bid_open').count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(ipost, 20)

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

    template = 'marketplace/vacancy_posts_all.html'
    context ={
        'ipost_count': ipost_count,
        'ipost_bid_flat': ipost_bid_flat,
        'pageitems': pageitems,
        'page_range': page_range
    }
    return render(request, template, context)


@login_required()
@subscription(2)
def AllPostedVacanciesOpenView(request):
    #>>>Queryset caching
    talent=request.user
    tr = TalentRequired.objects.filter(requested_by=request.user)
    wb = WorkBid.objects.filter(work__requested_by=talent, work__offer_status__iexact='O')
    #Queryset caching<<<
    ipost = tr.filter(offer_status='O').order_by('-bid_open')
    ipost_bid = wb.filter(Q(bidreview__exact='R') | Q(bidreview__exact='P') | Q(bidreview__exact='A'))
    ipost_bid_flat = ipost_bid.values_list('work', flat=True).distinct()

    ipost_count = tr.filter(offer_status='O').order_by('-bid_open').count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(ipost, 20)

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

    template = 'marketplace/vacancy_posts_open.html'
    context ={
        'ipost_count': ipost_count,
        'ipost_bid_flat': ipost_bid_flat,
        'pageitems': pageitems,
        'page_range': page_range
    }
    return render(request, template, context)


@login_required()
@subscription(2)
def AllPostedVacanciesClosedView(request):
    #>>>Queryset caching
    talent=request.user
    tr = TalentRequired.objects.filter(requested_by=request.user)
    wb = WorkBid.objects.filter(work__requested_by=talent, work__offer_status__iexact='C')
    #Queryset caching<<<
    ipost = tr.filter(offer_status='C').order_by('-bid_open')
    ipost_bid = wb.filter(Q(bidreview__exact='R') | Q(bidreview__exact='P') | Q(bidreview__exact='A'))
    ipost_bid_flat = ipost_bid.values_list('work', flat=True).distinct()

    ipost_count = tr.filter(offer_status='C').order_by('-bid_open').count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(ipost, 20)

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

    template = 'marketplace/vacancy_posts_closed.html'
    context ={
        'ipost_count': ipost_count,
        'ipost_bid_flat': ipost_bid_flat,
        'pageitems': pageitems,
        'page_range': page_range
    }
    return render(request, template, context)


@login_required()
def MarketHome(request):
    #>>>Queryset caching
    talent=request.user
    tlt = talent.id
    pfl = Profile.objects.filter(talent=talent)
    #TalentRequired.objects.filter()
    tr = TalentRequired.objects.filter(offer_status='O')
    tr_emp = TalentRequired.objects.filter(requested_by=talent)
    wb = WorkBid.objects.filter(work__requested_by=talent)
    ta = TalentAvailabillity.objects.filter(talent=talent).last()
    we = WorkExperience.objects.filter(Q(talent=talent) & Q(score__gte=skill_pass_score)).prefetch_related('topic')
    bch = BriefCareerHistory.objects.filter(talent=talent)
    sr = SkillRequired.objects.filter(scope__offer_status='O')
    sl = SkillLevel.objects.all()
    wbt = WorkBid.objects.filter(Q(talent=talent) & Q(work__offer_status='O'))
    bsl = BidShortList.objects.filter(Q(talent=talent) & Q(scope__offer_status='O'))
    vv = set(VacancyViewed.objects.filter(Q(talent=talent) & Q(closed=True)).values_list('vacancy__id', flat=True))
    vvv = VacancyViewed.objects.filter(Q(talent=request.user) & Q(viewed=True)).values_list('vacancy__id', flat=True).distinct()
    vac_exp = ExpandedView.objects.get(talent=request.user)
    vacancies_suited_list_view = vac_exp.vacancies_suited_list
    #  vo = VacancyViewed.objects.filter(closed=False)

    #Queryset caching<<<

    tr_emp_count = tr_emp.count()
    ipost = tr_emp.filter(offer_status='O').order_by('-bid_open')
    ipost_list = ipost[:5]
    ipost_count = ipost.count()
    ipost_closed = tr_emp.filter(offer_status='C').order_by('-bid_open')
    ipost_closed_list = ipost_closed[:5]
    ipost_closed_count = ipost_closed.count()
    ipost_bid = wb.filter(~Q(bidreview='D'))
    ipost_bid_flat = ipost_bid.values_list('work', flat=True).distinct()
#    capacity = ta.filter(date_to__gte=timezone.now()).order_by('-date_to')[:5]

    #Code for stacked lookup for talent's skills

    #>>>Create a set of all skills
    e_skill = we.filter(edt=True, score__gte=skill_pass_score).only('pk').values_list('pk', flat=True)
    l_skill = we.filter(edt=False, score__gte= skill_pass_score).only('pk').values_list('pk', flat=True)
    bch_skill = bch.filter(talent=talent).only('pk').values_list('pk', flat=True)

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

    for bs in bch_skill:
        e = bch.get(pk=bs)
        f = e.skills.all().values_list('skill', flat=True)

        skill_set = skill_set | f

    skill_set = skill_set.distinct().order_by('skill')#all skills the talent has
    skill_setv = skill_set.values_list('id', flat=True)#gets the id's of all the skills
    #Create a set of all skills<<<

    #>>>Experience Level check & list skills required in vacancies
    tlt_lev = pfl.values_list('exp_lvl__level', flat=True)
    tlt_lvl = tlt_lev[0]

    try:
        pre_bch_df = bch.aggregate(df_min=Min('date_from'))
        pre_bch_dt = bch.aggregate(dt_max=Max('date_to'))

        p_bch_df = pre_bch_df.get('df_min')
        p_bch_dt = pre_bch_dt.get('dt_max')

        p_delta = p_bch_dt - p_bch_df
        exp_lvls = [Decimal(p_delta.days / 7 * 5 * 8)]
    except:
        exp_lvls = [Decimal(0)]

    std = list(sl.filter(level__exact=0).values_list('min_hours', flat=True))
    grd = list(sl.filter(level__exact=1).values_list('min_hours', flat=True))
    jnr = list(sl.filter(level__exact=2).values_list('min_hours', flat=True))
    int = list(sl.filter(level__exact=3).values_list('min_hours', flat=True))
    snr = list(sl.filter(level__exact=4).values_list('min_hours', flat=True))
    lead = list(sl.filter(level__exact=5).values_list('min_hours', flat=True))

    if exp_lvls < std:
        iama = 0
    elif exp_lvls >= std and exp_lvls < grd:
        iama = 1
    elif exp_lvls >= grd and exp_lvls < jnr:
        iama = 2
    elif exp_lvls >= jnr and exp_lvls < int:
        iama = 3
    elif exp_lvls >= int and exp_lvls < snr:
        iama = 4
    elif exp_lvls >= snr:
        iama = 5

    if iama > tlt_lvl:
        tlt_lvl = iama
    else:
        tlt_lvl = tlt_lvl

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
    matchd = set(skl_lst) #remove duplicates; these are the required skills

    matchd = matchd.intersection(set(skill_setv))

    for item in matchd:
        display = set(sr.filter(
                Q(skills__in=skl_lst)
                & Q(scope__bid_closes__gte=timezone.now())).values_list('scope__id', flat=True))
        ds = ds | display #set of all open vacancies

    dsi = ds.intersection(req_experience) #open vacancies which the talent qualifies for (certification, location)

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



    template = 'marketplace/vacancy_home.html'
    context ={
        'vvv': vvv,
        'vacancies_suited_list_view': vacancies_suited_list_view,
        'tlt': tlt,
        'tlent': talent,
        'ta': ta,
        'tr_emp_count': tr_emp_count,
        'ipost': ipost,
        'ipost_list': ipost_list,
        'ipost_count': ipost_count,
        'ipost_closed_list': ipost_closed_list,
        'ipost_bid_flat': ipost_bid_flat,
        'ipost_closed_count': ipost_closed_count,
        'dsd': dsd,
        'ipost_closed': ipost_closed,
        'rem_vac': rem_vac,
        'bsl_c': bsl_c,
        'wbt_c': wbt_c,
        'tot_vac': tot_vac,
    }
    return render(request, template, context)


def CloseVacancyAvailableCard(request, tlt, vac):
    cu = CustomUser.objects.get(id=tlt)
    tr = TalentRequired.objects.get(id=vac)
    if request.method == 'POST':
        VacancyViewed.objects.create(talent=cu, vacancy=tr, closed=True,  date_closed=timezone.now()).save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def MinimiseVacancyAvailableCard(request, tlt, vac):

    cu = CustomUser.objects.get(id=tlt)
    tr = TalentRequired.objects.get(id=vac)

    VacancyViewed.objects.create(talent=cu, vacancy=tr, viewed=False,  date_viewed=timezone.now()).save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER')+f'#{ vac }')


def MaximiseVacancyAvailableCard(request, tlt, vac):

    cu = CustomUser.objects.get(id=tlt)
    tr = TalentRequired.objects.get(id=vac)

    VacancyViewed.objects.create(talent=cu, vacancy=tr, viewed=True,  date_viewed=timezone.now()).save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER')+f'#{ vac }')


def VacancyViewedJsonView(request):
    data = json.loads(request.body)
    vac = data['vac']
    # tlt = data['tlt']
    tlt = data['tlt']

    cu = CustomUser.objects.get(id=tlt)
    tr = TalentRequired.objects.get(ref_no=vac)

    VacancyViewed.objects.create(talent=cu, vacancy=tr, viewed=True,  date_viewed=timezone.now()).save()

    return JsonResponse('vacancy viewed', safe=False)


@login_required()
def VacanciesListView(request):
    #>>>Queryset caching
    talent=request.user
    tlt = talent.id
    pfl = Profile.objects.filter(talent=talent)
    #TalentRequired.objects.filter()
    tr = TalentRequired.objects.filter(offer_status='O')
    tr_emp = TalentRequired.objects.filter(requested_by=talent)
    wb = WorkBid.objects.filter(work__requested_by=talent)
    ta = TalentAvailabillity.objects.filter(talent=talent).last()
    we = WorkExperience.objects.filter(Q(talent=talent) & Q(score__gte=skill_pass_score)).prefetch_related('topic')
    bch = BriefCareerHistory.objects.filter(talent=talent)
    sr = SkillRequired.objects.filter(scope__offer_status='O')
    sl = SkillLevel.objects.all()
    wbt = WorkBid.objects.filter(Q(talent=talent) & Q(work__offer_status='O'))
    bsl = BidShortList.objects.filter(Q(talent=talent) & Q(scope__offer_status='O'))
    vv = set(VacancyViewed.objects.filter(Q(talent=talent) & Q(closed=True)).values_list('vacancy__id', flat=True))
    vvv = VacancyViewed.objects.filter(Q(talent=request.user) & Q(viewed=True)).values_list('vacancy__id', flat=True).distinct()
    vac_exp = ExpandedView.objects.get(talent=request.user)
    vacancies_suited_list_view = vac_exp.vacancies_suited_list
    #  vo = VacancyViewed.objects.filter(closed=False)

    #Queryset caching<<<

    tr_emp_count = tr_emp.count()
    ipost = tr_emp.filter(offer_status='O').order_by('-bid_open')
    ipost_list = ipost[:5]
    ipost_count = ipost.count()
    ipost_closed = tr_emp.filter(offer_status='C').order_by('-bid_open')
    ipost_closed_list = ipost_closed[:5]
    ipost_closed_count = ipost_closed.count()
    ipost_bid = wb.filter(~Q(bidreview='D'))
    ipost_bid_flat = ipost_bid.values_list('work', flat=True).distinct()
#    capacity = ta.filter(date_to__gte=timezone.now()).order_by('-date_to')[:5]

    #Code for stacked lookup for talent's skills

    #>>>Create a set of all skills
    e_skill = we.filter(edt=True, score__gte=skill_pass_score).only('pk').values_list('pk', flat=True)
    l_skill = we.filter(edt=False, score__gte= skill_pass_score).only('pk').values_list('pk', flat=True)
    bch_skill = bch.filter(talent=talent).only('pk').values_list('pk', flat=True)

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

    for bs in bch_skill:
        e = bch.get(pk=bs)
        f = e.skills.all().values_list('skill', flat=True)

        skill_set = skill_set | f

    skill_set = skill_set.distinct().order_by('skill')#all skills the talent has
    skill_setv = skill_set.values_list('id', flat=True)#gets the id's of all the skills
    #Create a set of all skills<<<

    #>>>Experience Level check & list skills required in vacancies
    tlt_lev = pfl.values_list('exp_lvl__level', flat=True)
    tlt_lvl = tlt_lev[0]

    try:
        pre_bch_df = bch.aggregate(df_min=Min('date_from'))
        pre_bch_dt = bch.aggregate(dt_max=Max('date_to'))

        p_bch_df = pre_bch_df.get('df_min')
        p_bch_dt = pre_bch_dt.get('dt_max')

        p_delta = p_bch_dt - p_bch_df
        exp_lvls = [Decimal(p_delta.days / 7 * 5 * 8)]
    except:
        exp_lvls = [Decimal(0)]

    std = list(sl.filter(level__exact=0).values_list('min_hours', flat=True))
    grd = list(sl.filter(level__exact=1).values_list('min_hours', flat=True))
    jnr = list(sl.filter(level__exact=2).values_list('min_hours', flat=True))
    int = list(sl.filter(level__exact=3).values_list('min_hours', flat=True))
    snr = list(sl.filter(level__exact=4).values_list('min_hours', flat=True))
    lead = list(sl.filter(level__exact=5).values_list('min_hours', flat=True))

    if exp_lvls < std:
        iama = 0
    elif exp_lvls >= std and exp_lvls < grd:
        iama = 1
    elif exp_lvls >= grd and exp_lvls < jnr:
        iama = 2
    elif exp_lvls >= jnr and exp_lvls < int:
        iama = 3
    elif exp_lvls >= int and exp_lvls < snr:
        iama = 4
    elif exp_lvls >= snr:
        iama = 5

    if iama > tlt_lvl:
        tlt_lvl = iama
    else:
        tlt_lvl = tlt_lvl

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
    matchd = set(skl_lst) #remove duplicates; these are the required skills

    matchd = matchd.intersection(set(skill_setv))

    for item in matchd:
        display = set(sr.filter(
                Q(skills__in=skl_lst)
                & Q(scope__bid_closes__gte=timezone.now())).values_list('scope__id', flat=True))
        ds = ds | display #set of all open vacancies

    dsi = ds.intersection(req_experience) #open vacancies which the talent qualifies for (certification, location)

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

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(dsd, 20)

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

    template = 'marketplace/vacancy_list.html'
    context ={
        'vvv': vvv,
        'vacancies_suited_list_view': vacancies_suited_list_view,
        'tlt': tlt,
#        'capacity': capacity,
        'tr_emp_count': tr_emp_count,
        'ipost': ipost,
        'ipost_list': ipost_list,
        'ipost_count': ipost_count,
        'ipost_closed_list': ipost_closed_list,
        'ipost_bid_flat': ipost_bid_flat,
        'ipost_closed_count': ipost_closed_count,
        'dsd': dsd,
        'ipost_closed': ipost_closed,
        'rem_vac': rem_vac,
        'bsl_c': bsl_c,
        'wbt_c': wbt_c,
        'tot_vac': tot_vac,
        'pageitems': pageitems,
        'page_range': page_range,
    }
    return render(request, template, context)


@login_required()
@subscription(1)
def ApplicationHistoryView(request):
    talent = request.user
    role = WorkBid.objects.filter(talent=talent).order_by('-date_applied')
    role_c = role.count()

    applied_c = role.filter(Q(bidreview='P') | Q(bidreview='I')).count()
    applied = role.filter(Q(bidreview='P') | Q(bidreview='I'))[:5]

    rejected_c = role.filter(bidreview='R').count()
    rejected = role.filter(bidreview='R')[:5]

    accepted_c = role.filter(bidreview='A').count()
    accepted = role.filter(bidreview='A')[:5]

    applied_sl_c = role.filter(bidreview='S').count()
    applied_sl = role.filter(bidreview='S')[:5]

    int_qs = role.filter(bidreview='I')
    int_qs_c = int_qs.count()
    int_qs_s = int_qs[:5]

    sl_qs = BidShortList.objects.filter(talent=talent).order_by('-date_listed')
    sl_qs_c = sl_qs.count()

    sl_pending = sl_qs.filter(status='S')
    sl_pending_c = sl_pending.count()
    sl_pending_s = sl_pending[:5]

    sl_interview = sl_qs.filter(status='I')
    sl_interview_c = sl_interview.count()
    sl_interview_s = sl_interview[:5]

    sl_accepted = sl_qs.filter(status='A')
    sl_accepted_c = sl_accepted.count()
    sl_accepted_s = sl_accepted[:5]

    sl_rejected = sl_qs.filter(status='R')
    sl_rejected_c = sl_rejected.count()
    sl_rejected_s = sl_rejected[:5]

    template = 'marketplace/vacancy_application_history.html'
    context ={
        'role_c': role_c,
        'applied_c': applied_c,
        'rejected_c': rejected_c,
        'accepted_c': accepted_c,
        'applied_sl_c': applied_sl_c,
        'applied_sl': applied_sl,
        'applied': applied,
        'accepted': accepted,
        'rejected': rejected,
        'int_qs_c': int_qs_c,
        'int_qs_s': int_qs_s,
        'sl_qs_c': sl_qs_c,
        'sl_interview_c': sl_interview_c,
        'sl_interview_s': sl_interview_s,
        'sl_pending_c': sl_pending_c,
        'sl_pending_s': sl_pending_s,
        'sl_accepted_c': sl_accepted_c,
        'sl_accepted_s': sl_accepted_s,
        'sl_rejected_c': sl_rejected_c,
        'sl_rejected_s': sl_rejected_s,
        }
    return render(request, template, context)


@login_required()
@subscription(2)
def RolesAppliedForApplicationHistoryView(request):
    talent = request.user
    role = WorkBid.objects.filter(talent=talent).order_by('-date_applied')
    role_c = role.count()

    applied_c = role.filter(Q(bidreview='P') | Q(bidreview='I')).count()
    applied = role.filter(Q(bidreview='P') | Q(bidreview='I'))

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(applied, 20)

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


    template = 'marketplace/roles_applied_for_application_history_full_list.html'
    context ={
        'role_c': role_c,
        'applied_c': applied_c,
        'pageitems': pageitems,
        'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(2)
def RolesShortlistedForApplicationHistoryView(request):
    talent = request.user
    role = WorkBid.objects.filter(talent=talent).order_by('-date_applied')
    role_c = role.count()

    applied_sl_c = role.filter(bidreview='S').count()
    applied_sl = role.filter(bidreview='S')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(applied_sl, 20)

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


    template = 'marketplace/roles_shortlisted_for_application_history_full_list.html'
    context ={
        'role_c': role_c,
        'applied_sl_c': applied_sl_c,
        'pageitems': pageitems,
        'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(2)
def RolesOpenInterviewsApplicationHistoryView(request):
    talent = request.user
    role = WorkBid.objects.filter(talent=talent).order_by('-date_applied')
    role_c = role.count()

    int_qs = role.filter(bidreview='I')
    int_qs_c = int_qs.count()
    int_qs_s = int_qs

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(int_qs_s, 20)

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


    template = 'marketplace/roles_open_interviews_application_history_full_list.html'
    context ={
        'role_c': role_c,
        'int_qs_c': int_qs_c,
        'pageitems': pageitems,
        'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(2)
def UnsuccessfulApplicationHistoryView(request):
    talent = request.user
    role = WorkBid.objects.filter(talent=talent).order_by('-date_applied')
    role_c = role.count()

    rejected_c = role.filter(bidreview='R').count()
    rejected = role.filter(bidreview='R')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(rejected, 20)

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


    template = 'marketplace/unsuccessful_applications_history_full_list.html'
    context ={
        'role_c': role_c,
        'rejected_c': rejected_c,
        'pageitems': pageitems,
        'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(2)
def SuccessfulApplicationHistoryView(request):
    talent = request.user
    role = WorkBid.objects.filter(talent=talent).order_by('-date_applied')
    role_c = role.count()

    accepted_c = role.filter(bidreview='A').count()
    accepted = role.filter(bidreview='A')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(accepted, 20)

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


    template = 'marketplace/successful_applications_history_full_list.html'
    context ={
        'role_c': role_c,
        'accepted_c': accepted_c,
        'pageitems': pageitems,
        'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(1)
def RolesAppliedForShortlistedApplicationHistoryView(request):
    talent = request.user
    sl_qs = BidShortList.objects.filter(talent=talent).order_by('-date_listed')
    sl_qs_c = sl_qs.count()

    sl_pending = sl_qs.filter(status='S')
    sl_pending_c = sl_pending.count()
    sl_pending_s = sl_pending

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(sl_pending_s, 20)

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


    template = 'marketplace/roles_applied_for_shortlisted_application_history_full_list.html'
    context ={
        'sl_qs_c': sl_qs_c,
        'sl_pending_c': sl_pending_c,
        'pageitems': pageitems,
        'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(1)
def RolesAppliedForInterviewsApplicationHistoryView(request):
    talent = request.user
    sl_qs = BidShortList.objects.filter(talent=talent).order_by('-date_listed')
    sl_qs_c = sl_qs.count()

    sl_interview = sl_qs.filter(status='I')
    sl_interview_c = sl_interview.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(sl_interview, 20)

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


    template = 'marketplace/roles_applied_for_interviews_application_history_full_list.html'
    context ={
        'sl_qs_c': sl_qs_c,
        'sl_interview_c': sl_interview_c,
        'pageitems': pageitems,
        'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(1)
def RolesAppliedForSuccessfulApplicationHistoryView(request):
    talent = request.user
    sl_qs = BidShortList.objects.filter(talent=talent).order_by('-date_listed')
    sl_qs_c = sl_qs.count()

    sl_accepted = sl_qs.filter(status='A')
    sl_accepted_c = sl_accepted.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(sl_accepted, 20)

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


    template = 'marketplace/roles_applied_for_successful_application_history_full_list.html'
    context ={
        'sl_qs_c': sl_qs_c,
        'sl_accepted_c': sl_accepted_c,
        'pageitems': pageitems,
        'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(1)
def RolesAppliedForUnsuccessfulApplicationHistoryView(request):
    talent = request.user
    sl_qs = BidShortList.objects.filter(talent=talent).order_by('-date_listed')
    sl_qs_c = sl_qs.count()

    sl_rejected = sl_qs.filter(status='R')
    sl_rejected_c = sl_rejected.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(sl_rejected, 20)

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


    template = 'marketplace/roles_applied_for_unsuccessful_application_history_full_list.html'
    context ={
        'sl_qs_c': sl_qs_c,
        'sl_rejected_c': sl_rejected_c,
        'pageitems': pageitems,
        'page_range': page_range}
    return render(request, template, context)


@login_required()
def TalentAvailabillityView(request):
    instance = TalentAvailabillity.objects.filter(talent=request.user).last()
    form = TalentAvailabillityForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.save()
            return redirect(reverse('MarketPlace:Entrance')+'#Availabillity')
    else:
        template = 'marketplace/talent_availabillity.html'
        context = {'form':form}
        return render(request, template, context)


@login_required()
def AvailabillityRemoveView(request, avl_id):
    if request.method == 'POST':
        item = TalentAvailabillity.objects.get(pk=avl_id)
        item.delete()
    return redirect(reverse('MarketPlace:Entrance')+'#Availabillity')


@login_required()
@subscription(2)
def VacancyPostView(request, vac):
    #>>>Queryset Cache
    instance = get_object_or_404(TalentRequired, ref_no=vac)
    skille = SkillRequired.objects.filter(scope__ref_no=vac)
    delivere = Deliverables.objects.filter(scope__ref_no=vac)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    we = WorkExperience.objects.filter(Q(talent__subscription__gte=0) & Q(score__gte=skill_pass_score))
    s_list = BidShortList.objects.filter(scope__ref_no=vac)
    book = ReadBy.objects.all()
    vac_exp = ExpandedView.objects.get(talent=request.user)
    applicants_list_view = vac_exp.applicants_list
    suited_list_view = vac_exp.talent_suited_list
    sk_st = SkillLevel.objects.get(level=0).min_hours
    sk_bg = SkillLevel.objects.get(level=1).min_hours
    sk_jn = SkillLevel.objects.get(level=2).min_hours
    sk_in = SkillLevel.objects.get(level=3).min_hours
    sk_sn = SkillLevel.objects.get(level=4).min_hours
    sk_ld = SkillLevel.objects.get(level=5).min_hours
    tr_qs = TalentRequired.objects.filter(ref_no=vac)
    tlt = Profile.objects.filter(talent__subscription__gte=0)
    #Queryset Cache<<<

    #>>> List all skills required
    skill_r = skille.values_list('skills', flat=True).distinct()
    skill_rl = list(skill_r)
    skill_rs = skille.values_list('skills__skill', flat=True).distinct()
    skill_rc = skill_rs.count()

    #List all skills required<<<

    #>>> Find all talent with required skill
    wes = set(we.filter(Q(skills__in=skill_r) | Q(topic__skills__in=skill_r)).values_list('talent', flat=True))
    #Find all talent with required skill<<<

    #>>> Find all talent that have the required Experience
    wex = set(tlt.filter(exp_lvl__gte=instance.experience_level).values_list('talent', flat=True))

    wee = wex.intersection(wes)

    #Find all talent that have the required Experience<<<

    #>>> Find all talent that are in the correct geographic location
    vac_type = instance.worklocation.type

    if vac_type == 'Remote freelance' or vac_type == 'Consultant':
        wel_i=wee
    else:
        cty = Region.objects.get(city__city=instance.city).country

        wel = set(PhysicalAddress.objects.filter(country=cty).values_list('talent', flat=True))
        #Willing to Relocate


        wtr = set(WillingToRelocate.objects.filter(country=cty).values_list('talent', flat=True))
        wel = wel|wtr

        wel_i = wel.intersection(wee)
    #Find all talent that are in the correct geographic location<<<

    #>>> Find all talent that have the required certifications
    certnull = tr_qs.filter(certification__isnull=False).exists()

    if certnull is False:
        wec = wel_i
    else:
        cert_req = tr_qs.values_list('certification')
        tlt_cert = set(LicenseCertification.objects.filter(certification__in=cert_req).values_list('talent', flat=True))
        wec = wel_i.intersection(tlt_cert)
    #Find all talent that have the required certifications<<<

    #ensure apllicants don't appear in the suitable skills window
    app_list = set(applicants.values_list('talent', flat=True))
    suit_list = wec
    short_list = set(s_list.values_list('talent', flat=True))
    short_list_a = set(s_list.filter(talent__subscription__gte=2).values_list('talent', flat=True))

    diff_list0 = suit_list.difference(app_list)#removes talent that has applied
    diff_list = diff_list0.difference(short_list)#removes shortlists talent
    app_list = app_list.difference(short_list_a)

    we_list = list(diff_list)

    suitable={}
    for item in we_list:
        w_exp = we.filter(talent=item, edt=False).aggregate(wet=Sum('hours_worked'))
        wetv = w_exp.get('wet')
        t_exp = we.filter(talent=item, edt=True).aggregate(tet=Sum('topic__hours'))
        tetv = t_exp.get('tet')
        talent_skill_l = we.filter(talent=item, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=item, edt=True).values_list('topic__skills__skill', flat=True)
        talent_skill = list(talent_skill_l)
        rb = book.filter(talent=item).count()
        talent_skillt = list(talent_skillt_l)
        rate = Profile.objects.filter(talent=item).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias',)
        des = list(BriefCareerHistory.objects.filter(talent=item, current=True).values_list('designation__name', flat=True))
        pfl = Profile.objects.get(talent=item)
        avg = pfl.avg_rate
        cnt = pfl.rate_count
        bg = pfl.background

        slist = talent_skill + talent_skillt
        skillset = set(slist)
        skill_count = len(skillset)

        slist_l = talent_skill_l.union(talent_skillt_l)
        skill_intersection = skill_rs.intersection(slist_l)
        skill_int_count = skill_intersection.count()
        skill_match = skill_int_count / skill_rc * 100

        suitable[item]={
            'we':wetv, 'te':tetv,'s_no':skill_count, 'skill_rc': skill_rc, 'skill_int_count': skill_int_count, 'skill_match': skill_match, 'skillset': skillset, 'rb':rb, 'ro':rate, 'score': avg, 'count': cnt, 'background': bg, 'des': des,
            }

        #Extracting information for the applicants
    applied ={}
    for app in app_list:
            aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
            awetv = aw_exp.get('awet')
            at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
            atetv = at_exp.get('tet')
            talent_skill_l = we.filter(talent=app, edt=False).values_list('skills__skill', flat=True)
            talent_skillt_l = we.filter(talent=app, edt=True).values_list('topic__skills__skill', flat=True)
            atalent_skill = list(talent_skill_l)
            atalent_skillt = list(talent_skillt_l)
            rb = book.filter(talent=app).count()
            rate = applicants.filter(talent=app).values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation', 'talent__alias')
            des = list(BriefCareerHistory.objects.filter(talent=app, current=True).values_list('designation__name', flat=True))
            pfl = Profile.objects.get(talent=app)
            avg = pfl.avg_rate
            cnt = pfl.rate_count
            bg = pfl.background

            aslist = atalent_skill + atalent_skillt
            askillset = set(aslist)
            askill_count = len(askillset)

            slist_l = talent_skill_l.union(talent_skillt_l)
            skill_intersection = skill_rs.intersection(slist_l)
            skill_int_count = skill_intersection.count()
            skill_match = skill_int_count / skill_rc * 100

            applied[app]={
                'we':awetv, 'te':atetv, 's_no': askill_count, 'skill_rc': skill_rc, 'skill_int_count': skill_int_count, 'skill_match': skill_match, 'skillset': askillset, 'rb':rb, 'ro':rate, 'score': avg, 'count': cnt, 'background': bg, 'des': des,
                }

    suitable_slice = dict(itertools.islice(suitable.items(), 5))
    applied_slice = dict(itertools.islice(applied.items(), 5))

    suitable_count = len(suitable)
    applied_count = len(applied)

    template = 'marketplace/vacancy_post_view.html'
    context = {
            'vac': vac,
            'sk_st': sk_st,
            'sk_bg': sk_bg,
            'sk_jn': sk_jn,
            'sk_in': sk_in,
            'sk_sn': sk_sn,
            'sk_ld': sk_ld,
            'instance': instance,
            'skille': skille,
            'delivere': delivere,
            'applicants': applicants,
            'suitable': suitable,
            'suitable_slice': suitable_slice,
            'suitable_count': suitable_count,
            'applied': applied,
            'applied_slice': applied_slice,
            'applied_count': applied_count,
            'applicants_list_view': applicants_list_view,
            'suited_list_view': suited_list_view,
            's_list': s_list
    }

    return render(request, template, context)


@login_required
def CertificateDeleteView(request, vac, cert):
    if request.method == 'POST':
        vacancy = TalentRequired.objects.get(ref_no=vac)
        cert_instance = Result.objects.get(type=cert)
        vacancy.certification.remove(cert_instance)
    return redirect(reverse('MarketPlace:VacancyPost', kwargs={'vac':vac})+'#certifications')


@login_required()
@subscription(2)
def VacancyCloseSwitch(request, vac):
    interview = TalentRequired.objects.filter(ref_no=vac).update(offer_status='C')

    return redirect(reverse('MarketPlace:VacancyPost', kwargs={'vac': vac,}))


@login_required()
@subscription(2)
def TalentSuitedVacancyListView(request, vac):
    #>>>Queryset Cache
    instance = get_object_or_404(TalentRequired, ref_no=vac)
    skille = SkillRequired.objects.filter(scope__ref_no=vac)
    delivere = Deliverables.objects.filter(scope__ref_no=vac)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    we = WorkExperience.objects.filter(Q(talent__subscription__gte=0) & Q(score__gte=skill_pass_score))
    s_list = BidShortList.objects.filter(scope__ref_no=vac)
    skill_rs = skille.values_list('skills__skill', flat=True).distinct()
    skill_rc = skill_rs.count()
    book = ReadBy.objects.all()
    tr_qs = TalentRequired.objects.filter(ref_no=vac)
    tlt = Profile.objects.filter(talent__subscription__gte=0)
    vac_exp = ExpandedView.objects.get(talent=request.user)
    list_view = vac_exp.talent_suited_list
    sk_st = SkillLevel.objects.get(level=0).min_hours
    sk_bg = SkillLevel.objects.get(level=1).min_hours
    sk_jn = SkillLevel.objects.get(level=2).min_hours
    sk_in = SkillLevel.objects.get(level=3).min_hours
    sk_sn = SkillLevel.objects.get(level=4).min_hours
    sk_ld = SkillLevel.objects.get(level=5).min_hours
    #Queryset Cache<<<

    #>>> List all skills required
    skill_r = skille.values_list('skills', flat=True).distinct()
    skill_rl = list(skill_r)
    skill_rs = skille.values_list('skills__skill', flat=True).distinct()
    skill_rc = len(skill_rl)

    #List all skills required<<<

    #>>> Find all talent with required skill
    wes = set(we.filter(Q(skills__in=skill_r) | Q(topic__skills__in=skill_r)).values_list('talent', flat=True))
    #Find all talent with required skill<<<

    #>>> Find all talent that have the required Experience
    wee = set(tlt.filter(exp_lvl__lte=instance.experience_level).values_list('talent', flat=True))

    wee = wee.intersection(wes)

    #Find all talent that have the required Experience<<<

    #>>> Find all talent that are in the correct geographic location
    vac_type = instance.worklocation.id

    if vac_type == 0:
        wel_i=wee
    else:
        wel = set(PhysicalAddress.objects.filter(region=instance.city.region).values_list('talent', flat=True))
        wel_i = wel.intersection(wee)
    #Find all talent that are in the correct geographic location<<<

    #>>> Find all talent that have the required certifications
    certnull = tr_qs.filter(certification__isnull=False).exists()

    if certnull is False:
        wec = wel_i
    else:
        cert_req = tr_qs.values_list('certification')
        tlt_cert = set(LicenseCertification.objects.filter(certification__in=cert_req).values_list('talent', flat=True))
        wec = wel_i.intersection(tlt_cert)
    #Find all talent that have the required certifications<<<

    #ensure apllicants don't appear in the suitable skills window
    app_list = set(applicants.values_list('talent', flat=True))
    suit_list = wec
    short_list = set(s_list.values_list('talent', flat=True))
    short_list_a = set(s_list.filter(talent__subscription__gte=2).values_list('talent', flat=True))

    diff_list0 = suit_list.difference(app_list)#removes talent that has applied
    diff_list = diff_list0.difference(short_list)#removes shortlists talent
    app_list = app_list.difference(short_list_a)

    we_list = list(diff_list)

    suitable={}
    for item in we_list:
        w_exp = we.filter(talent=item, edt=False).aggregate(wet=Sum('hours_worked'))
        wetv = w_exp.get('wet')
        t_exp = we.filter(talent=item, edt=True).aggregate(tet=Sum('topic__hours'))
        tetv = t_exp.get('tet')
        talent_skill_l = we.filter(talent=item, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=item, edt=True).values_list('topic__skills__skill', flat=True)
        talent_skill = list(talent_skill_l)
        rb = book.filter(talent=item).count()
        talent_skillt = list(talent_skillt_l)
        rb = book.filter(talent=item).count()
        rate = Profile.objects.filter(talent=item).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias',)
        des = list(BriefCareerHistory.objects.filter(talent=item, current=True).values_list('designation__name', flat=True))
        pfl = Profile.objects.get(talent=item)
        avg = pfl.avg_rate
        cnt = pfl.rate_count
        bg = pfl.background

        slist = talent_skill + talent_skillt
        skillset = set(slist)
        skill_count = len(skillset)

        slist_l = talent_skill_l.union(talent_skillt_l)
        skill_intersection = skill_rs.intersection(slist_l)
        skill_int_count = skill_intersection.count()
        skill_match = skill_int_count / skill_rc * 100


        suitable[item]={
            'we':wetv, 'te':tetv,'s_no':skill_count, 'skill_rc': skill_rc, 'skill_int_count': skill_int_count, 'skill_match': skill_match, 'skillset': skillset, 'rb':rb, 'ro':rate, 'score':avg, 'count':cnt, 'background': bg, 'des': des,
            }


    suitable_slice = dict(itertools.islice(suitable.items(), 5))

    suitable_count = len(suitable)

    t = tuple(suitable.items())

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(t, 20)

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


    template = 'marketplace/talent_suited_vacancy_list_view.html'
    context = {
            'vac': vac,
            'sk_st': sk_st,
            'sk_bg': sk_bg,
            'sk_jn': sk_jn,
            'sk_in': sk_in,
            'sk_sn': sk_sn,
            'sk_ld': sk_ld,
            'instance': instance,
            'skille': skille,
            'delivere': delivere,
            'suitable': suitable,
            'suitable_count': suitable_count,
            'list_view': list_view,
            's_list': s_list,
            'pageitems': pageitems,
            'page_range': page_range
    }

    return render(request, template, context)


@login_required()
@subscription(2)
def ApplicantsForVacancyListView(request, vac):
    #>>>Queryset Cache
    instance = get_object_or_404(TalentRequired, ref_no=vac)
    skille = SkillRequired.objects.filter(scope__ref_no=vac)
    delivere = Deliverables.objects.filter(scope__ref_no=vac)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    we = WorkExperience.objects.filter(Q(talent__subscription__gte=0) & Q(score__gte=skill_pass_score))
    s_list = BidShortList.objects.filter(scope__ref_no=vac)
    book = ReadBy.objects.all()
    vac_exp = ExpandedView.objects.get(talent=request.user)
    list_view = vac_exp.applicants_list
    sk_st = SkillLevel.objects.get(level=0).min_hours
    sk_bg = SkillLevel.objects.get(level=1).min_hours
    sk_jn = SkillLevel.objects.get(level=2).min_hours
    sk_in = SkillLevel.objects.get(level=3).min_hours
    sk_sn = SkillLevel.objects.get(level=4).min_hours
    sk_ld = SkillLevel.objects.get(level=5).min_hours
    #Queryset Cache<<<

    #>>> List all skills required
    skill_r = skille.values_list('skills', flat=True).distinct()
    skill_rl = list(skill_r)
    skill_rs = skille.values_list('skills__skill', flat=True).distinct()
    skill_rc = skill_rs.count()

    #List all skills required<<<

    #>>> Find all talent with required skill

    wes = we.filter(Q(skills__in=skill_r) | Q(topic__skills__in=skill_r)).distinct('talent')

    #ensure apllicats don't appear in the suitable skills window
    app_list = applicants.values_list('talent')
    suit_list = wes.values_list('talent')
    short_list = s_list.values_list('talent')
    short_list_a = s_list.filter(talent__subscription__gte=2).values_list('talent')

    diff_list0 = suit_list.difference(app_list)#removes talent that has applied
    #removes shortlists talent
    diff_list = diff_list0.difference(short_list)
    app_list = app_list.difference(short_list_a)

    we_list = list(diff_list.values_list('talent', flat=True))

    #Extracting information for the applicants
    applied ={}
    app_list = list(app_list.values_list('talent', flat=True))
    for app in app_list:
            aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
            awetv = aw_exp.get('awet')
            at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
            atetv = at_exp.get('tet')
            talent_skill_l = we.filter(talent=app, edt=False).values_list('skills__skill', flat=True)
            talent_skillt_l = we.filter(talent=app, edt=True).values_list('topic__skills__skill', flat=True)
            atalent_skill = list(talent_skill_l)
            atalent_skillt = list(talent_skillt_l)
            rb = book.filter(talent=app).count()
            rate = applicants.filter(talent=app).values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation', 'talent__alias')
            des = list(BriefCareerHistory.objects.filter(talent=app, current=True).values_list('designation__name', flat=True))
            pfl = Profile.objects.get(talent=app)
            avg = pfl.avg_rate
            cnt = pfl.rate_count
            bg = pfl.background

            aslist = atalent_skill + atalent_skillt
            askillset = set(aslist)
            askill_count = len(askillset)

            slist_l = talent_skill_l.union(talent_skillt_l)
            skill_intersection = skill_rs.intersection(slist_l)
            skill_int_count = skill_intersection.count()
            skill_match = skill_int_count / skill_rc * 100

            applied[app]={'we':awetv, 'te':atetv, 's_no': askill_count, 'skill_rc': skill_rc, 'skill_int_count': skill_int_count, 'skill_match': skill_match, 'skillset': askillset, 'rb':rb, 'ro':rate, 'score': avg, 'count': cnt, 'background': bg, 'des': des,}

    applied_count = len(applied)

    t = tuple(applied.items())

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(t, 20)

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


    template = 'marketplace/applicants_applied_vacancy_list_view.html'
    context = {
            'vac': vac,
            'sk_st': sk_st,
            'sk_bg': sk_bg,
            'sk_jn': sk_jn,
            'sk_in': sk_in,
            'sk_sn': sk_sn,
            'sk_ld': sk_ld,
            'instance': instance,
            'skille': skille,
            'delivere': delivere,
            'applicants': applicants,
            'applied': applied,
            'applied_count': applied_count,
            'list_view': list_view,
            's_list': s_list,
            'pageitems': pageitems,
            'page_range': page_range
    }

    return render(request, template, context)


@login_required()
@subscription(2)
def AppliedListRejectedView(request, vac, tlt):

    job = get_object_or_404(TalentRequired, ref_no=vac)
    talent = get_object_or_404(CustomUser, alias=tlt)

    if request.method == 'POST':
        BidShortList.objects.create(talent=talent, scope=job, status = 'Z')#1

        bid_qs = WorkBid.objects.filter(Q(work__ref_no = vac) & Q(talent__alias = tlt))

        if bid_qs:
            bid_qs.update(bidreview = 'R')#2

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def ExpandVacanciesSuitedView(request):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.vacancies_suited_list
    if list_view == True:
        instance.vacancies_suited_list = False
    elif list_view == False:
        instance.vacancies_suited_list = True
    instance.save()

    return redirect(reverse('MarketPlace:Entrance'))


def ExpandVacanciesSuitedFLView(request):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.vacancies_fl_suited_list
    if list_view == True:
        instance.vacancies_fl_suited_list = False
    elif list_view == False:
        instance.vacancies_fl_suited_list = True
    instance.save()

    return redirect(reverse('MarketPlace:VacanciesList'))


def ExpandApplicantsView(request, vac):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.applicants_list
    if list_view == True:
        instance.applicants_list = False
    elif list_view == False:
        instance.applicants_list = True
    instance.save()

    return redirect(reverse('MarketPlace:VacancyPost', kwargs={'vac':vac})+'#applicants')


def ExpandApplicantsFLView(request, vac):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.applicants_fl_list
    if list_view == True:
        instance.applicants_fl_list = False
    elif list_view == False:
        instance.applicants_fl_list = True
    instance.save()

    return redirect(reverse('MarketPlace:ApplicantsForVacancy', kwargs={'vac':vac})+'#applicants')


def ExpandTalentSuitedView(request, vac):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.talent_suited_list
    if list_view == True:
        instance.talent_suited_list = False
    elif list_view == False:
        instance.talent_suited_list = True
    instance.save()

    return redirect(reverse('MarketPlace:VacancyPost', kwargs={'vac':vac})+'#suited')


def ExpandTalentSuitedFLView(request, vac):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.talent_fl_suited_list
    if list_view == True:
        instance.talent_fl_suited_list = False
    elif list_view == False:
        instance.talent_fl_suited_list = True
    instance.save()

    return redirect(reverse('MarketPlace:TalentSuitedToVacancy', kwargs={'vac':vac})+'#suited')


def ExpandShortListView(request):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.shortlist_list
    if list_view == True:
        instance.shortlist_list = False
    elif list_view == False:
        instance.shortlist_list = True
    instance.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def ExpandPendingInterviewsView(request, vac):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.pending_interviews_list
    if list_view == True:
        instance.pending_interviews_list = False
    elif list_view == False:
        instance.pending_interviews_list = True
    instance.save()

    return redirect(reverse('MarketPlace:InterviewList', kwargs={'vac':vac})+'#pending')


def ExpandPendingInterviewsFLView(request, vac):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.pending_fl_interviews_list
    if list_view == True:
        instance.pending_fl_interviews_list = False
    elif list_view == False:
        instance.pending_fl_interviews_list = True
    instance.save()

    return redirect(reverse('MarketPlace:PendingInterviewList', kwargs={'vac':vac})+'#pending')


def ExpandSuitableApplicantsView(request, vac):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.suitable_applicants_list
    if list_view == True:
        instance.suitable_applicants_list = False
    elif list_view == False:
        instance.suitable_applicants_list = True
    instance.save()

    return redirect(reverse('MarketPlace:InterviewList', kwargs={'vac':vac})+'#suitable')


def ExpandSuitableApplicantsFLView(request, vac):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.suitable_fl_applicants_list
    if list_view == True:
        instance.suitable_fl_applicants_list = False
    elif list_view == False:
        instance.suitable_fl_applicants_list = True
    instance.save()

    return redirect(reverse('MarketPlace:SuitableInterviewList', kwargs={'vac':vac})+'#suitable')


def ExpandUnSuitableApplicantsView(request, vac):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.unsuitable_applicants_list
    if list_view == True:
        instance.unsuitable_applicants_list = False
    elif list_view == False:
        instance.unsuitable_applicants_list = True
    instance.save()

    return redirect(reverse('MarketPlace:InterviewList', kwargs={'vac':vac})+'#unsuitable')


def ExpandUnSuitableApplicantsFLView(request, vac):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.unsuitable_fl_applicants_list
    if list_view == True:
        instance.unsuitable_fl_applicants_list = False
    elif list_view == False:
        instance.unsuitable_fl_applicants_list = True
    instance.save()

    return redirect(reverse('MarketPlace:UnsuitableInterviewList', kwargs={'vac':vac})+'#unsuitable')


def ExpandRejectedApplicantsView(request, vac):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.rejected_applicants_list
    if list_view == True:
        instance.rejected_applicants_list = False
    elif list_view == False:
        instance.rejected_applicants_list = True
    instance.save()

    return redirect(reverse('MarketPlace:InterviewList', kwargs={'vac':vac})+'#rejected')


def ExpandRejectedApplicantsFLView(request, vac):
    instance = ExpandedView.objects.get(talent=request.user)
    list_view = instance.rejected_fl_applicants_list
    if list_view == True:
        instance.rejected_fl_applicants_list = False
    elif list_view == False:
        instance.rejected_fl_applicants_list = True
    instance.save()

    return redirect(reverse('MarketPlace:BidRejectedList', kwargs={'vac':vac})+'#rejected')


@csp_exempt
@login_required()
def VacancySkillsAddView(request, vac):
    instance = get_object_or_404(TalentRequired, ref_no=vac)
    skill_list = SkillRequired.objects.filter(scope__ref_no=vac).order_by('skills')
    skill_kwa = skill_list.values_list('skills', flat=True)

    form = SkillRequiredForm(request.POST or None, dup = skill_kwa)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.scope = instance
            new.save()
            if 'another' in request.POST:
                return redirect(reverse('MarketPlace:Skills', kwargs={'vac': vac}))
            elif 'done' in request.POST:
                return redirect(reverse('MarketPlace:Entrance'))
        else:
            template = 'marketplace/vacancy_skills.html'
            context = {'form': form, 'instance': instance, 'skill_list': skill_list}
            return render(request, template, context)
    else:
        template = 'marketplace/vacancy_skills.html'
        context = {'form': form, 'instance': instance, 'skill_list': skill_list}
        return render(request, template, context)


@login_required()
@csp_exempt
def VacancySkillsAdd2View(request, vac):
    instance = get_object_or_404(TalentRequired, ref_no=vac)
    skill_list = SkillRequired.objects.filter(scope__ref_no=vac)
    skill_kwa = skill_list.values_list('skills', flat=True)

    form = SkillRequiredForm(request.POST or None, dup = skill_kwa)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.scope = instance
            new.save()
            return redirect(reverse('MarketPlace:VacancyPost', kwargs={'vac': vac})+'#skills')
        else:
            template = 'marketplace/vacancy_skills2.html'
            context = {'form': form, 'instance': instance, 'skill_list': skill_list}
            return render(request, template, context)
    else:
        template = 'marketplace/vacancy_skills2.html'
        context = {'form': form, 'instance': instance, 'skill_list': skill_list}
        return render(request, template, context)


@login_required()
def SkillDeleteView(request, id):
    if request.method == 'POST':
        skilld = SkillRequired.objects.get(pk=id)
        skilld.delete()
        return redirect(reverse('MarketPlace:VacancyPost', kwargs={'vac':skilld.scope.ref_no})+'#skills')


@login_required()
@subscription(2)
def AddToShortListView(request, vac, tlt):
    job = get_object_or_404(TalentRequired, ref_no=vac)
    talent = get_object_or_404(CustomUser, alias=tlt)
    if request.method == 'POST':
        b = BidShortList.objects.create(talent=talent, scope=job, status = 'S')#1

        WorkBid.objects.filter(Q(talent=talent) & Q(work=job)).update(bidreview="S")#2

        return redirect(reverse('MarketPlace:VacancyPost', kwargs={'vac':vac})+'#suited')


@login_required()
@subscription(2)
def AddToShortListFullListView(request, vac, tlt):
    job = get_object_or_404(TalentRequired, ref_no=vac)
    talent = get_object_or_404(CustomUser, alias=tlt)
    if request.method == 'POST':
        b = BidShortList.objects.create(talent=talent, scope=job, status = 'S')#1

        if 'active' in request.POST:
            upd = WorkBid.objects.get(Q(talent=talent) & Q(work=job))
            upd.bidreview = 'S'#2
            upd.save()

        return redirect(reverse('MarketPlace:TalentSuitedToVacancy', kwargs={'vac':vac})+'#suited')


@login_required()
@subscription(2)
def AddToShortListApplicantsView(request, vac, tlt):
    job = get_object_or_404(TalentRequired, ref_no=vac)
    talent = get_object_or_404(CustomUser, alias=tlt)
    if request.method == 'POST':
        b = BidShortList.objects.create(talent=talent, scope=job, status = 'S')#1

        if 'active' in request.POST:
            upd = WorkBid.objects.get(Q(talent=talent) & Q(work=job))
            upd.bidreview = 'S'#2
            upd.save()

        return redirect(reverse('MarketPlace:ApplicantsForVacancy', kwargs={'vac':vac})+'#suited')


@login_required()
@subscription(2)
def AddShortListApplicantsView(request, vac, tlt):
    job = get_object_or_404(TalentRequired, ref_no=vac)
    talent = get_object_or_404(CustomUser, alias=tlt)
    if request.method == 'POST':
        bid_qs = BidShortList.objects.filter(Q(talent=talent) & Q(scope=job))#1

        if bid_qs:
            bid_qs.update(status = 'S')#2

        if 'active' in request.POST:
            upd = WorkBid.objects.get(Q(talent=talent) & Q(work=job))
            upd.bidreview = 'S'#2
            upd.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
@subscription(2)
def AddToInterviewListView(request, vac, tlt):
    job = get_object_or_404(TalentRequired, ref_no=vac)
    talent = get_object_or_404(CustomUser, alias=tlt)
    if request.method == 'POST':
        BidInterviewList.objects.create(talent=talent, scope=job, outcome='I', tlt_response='P')#1
        BidShortList.objects.filter(Q(talent=talent) & Q(scope=job)).update(status='I')#4

        WorkBid.objects.filter(Q(talent=talent) & Q(work=job)).update(bidreview='I')#2

        job.vac_wkfl == 'I'
        job.save()#3

        #>>>email
        subject = f"MyWeXlog - {job.title} ({job.ref_no}): Interview request"

        context = {'job': job, 'talent': talent, 'user': talent}

        html_message = render_to_string('marketplace/email_interview_request.html', context).strip()
        plain_message = strip_tags(html_message)

        send_to = talent.email

        message = Mail(
            from_email = (settings.SENDGRID_FROM_EMAIL, 'MyWeXlog Interview Request'),
            to_emails = send_to,
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

#        send_mail(subject, html_message, 'no-reply@mywexlog.com', [send_to,])
        #template = 'marketplace/email_interview_request.html'
        #return render(request, template, context)
        #<<<email

        return redirect(reverse('MarketPlace:ShortListView', kwargs={'vac':vac}))


@login_required()
@subscription(2)
def TalentAssign(request, tlt, vac):
    #instance = WorkIssuedTo.objects.get(Q(talent__alias=tlt) & Q(work__ref_no=vac))
    job = get_object_or_404(TalentRequired, ref_no=vac)
    talent = get_object_or_404(CustomUser, alias=tlt)
    pfl_qs = Profile.objects.get(alias=tlt)
    bids = WorkBid.objects.filter(Q(work__ref_no=vac) & Q(talent__alias=tlt))
    s_list = BidShortList.objects.filter(scope__ref_no=vac)
    iview_list = BidInterviewList.objects.filter(talent=talent, scope=job)

    form = AssignWorkForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = talent
            new.work = job
            new.currency = job.currency
            new.rate_unit = job.rate_unit
            new.tlt_response = 'P'#4
            new.save()

            #clearing interview table
            if iview_list:
                iview_list.update(outcome='P')
                if iview_list[0].tlt_response == 'P':
                    iview_list.update(tlt_response = 'Z', tlt_intcomplete=True, emp_intcomplete=True)

            s_list.filter(talent=talent).update(status='P')#2

            job.vac_wkfl = 'S'
            job.save()#3

            BidInterviewList.objects.filter(Q(talent=talent) & Q(scope=job)).update(outcome='P')#5

            if bids:
                bids.update(bidreview='P')#1

            #>>>email
            subject = f"MyWeXlog - Job assigned: {job.title} ({job.ref_no})"

            context = {'job': job, 'talent': talent, 'user': talent}

            html_message = render_to_string('marketplace/email_vacancy_assign.html', context).strip()
            plain_message = strip_tags(html_message)

            send_to = talent.email

            message = Mail(
                from_email = (settings.SENDGRID_FROM_EMAIL, 'MyWeXlog Vacancy Assigned'),
                to_emails = send_to,
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

            #send_mail(subject, html_message, 'no-reply@mywexlog.com', [send_to,])
            #template = 'marketplace/email_vacancy_assign.html'
            #return render(request, template, context)
            #<<<email

            return redirect(reverse('MarketPlace:InterviewList', kwargs={'vac': vac,}))
        else:
            template = 'marketplace/vacancy_assign.html'
            context = {'form': form, 'job': job, 'talent': talent, 'bids': bids, 'pfl_qs': pfl_qs,}
            return render(request, template, context)

    else:
        template = 'marketplace/vacancy_assign.html'
        context = {'form': form, 'job': job, 'talent': talent, 'bids': bids,}
        return render(request, template, context)


@login_required()
@subscription(2)
def talent_assign_edit(request, wit):
    instance = get_object_or_404(WorkIssuedTo, slug=wit)
    vac=instance.work.ref_no
    tlt=instance.talent.alias

    job = get_object_or_404(TalentRequired, ref_no=vac)
    talent = get_object_or_404(CustomUser, alias=tlt)
    pfl_qs = Profile.objects.get(alias=tlt)
    bids = WorkBid.objects.filter(Q(work__ref_no=vac) & Q(talent__alias=tlt))
    s_list = BidShortList.objects.filter(scope__ref_no=vac)

    form = AssignWorkForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()

            return redirect(reverse('MarketPlace:InterviewList', kwargs={'vac': vac,}))
        else:
            template = 'marketplace/vacancy_assign.html'
            context = {'form': form, 'job': job, 'talent': talent, 'bids': bids, 'pfl_qs': pfl_qs,}
            return render(request, template, context)

    else:
        template = 'marketplace/vacancy_assign.html'
        context = context = {'form': form, 'job': job, 'talent': talent, 'bids': bids, 'pfl_qs': pfl_qs,}
        return render(request, template, context)


@login_required()
@subscription(2)
def SuitableTalentAssign(request, tlt, vac):
    #instance = WorkIssuedTo.objects.get(Q(talent__alias=tlt) & Q(work__ref_no=vac))
    job = get_object_or_404(TalentRequired, ref_no=vac)
    talent = get_object_or_404(CustomUser, alias=tlt)
    bids = WorkBid.objects.filter(Q(work__ref_no=vac) & Q(talent__alias=tlt))
    s_list = BidShortList.objects.filter(scope__ref_no=vac)

    form = AssignWorkForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = talent
            new.work = job
            new.tlt_response = 'P'#4
            new.save()

            s_list.filter(talent=talent).update(status='P')#2

            job.vac_wkfl = 'S'
            job.save()#3

            BidInterviewList.objects.filter(Q(talent=talent) & Q(scope=job)).update(outcome='P')#5

            if bids:
                bids.update(bidreview='P')#1

            #>>>email
            subject = f"MyWeXlog - Job assigned: {job.title} ({job.ref_no})"

            context = {'job': job, 'talent': talent, 'user': talent}

            html_message = render_to_string('marketplace/email_vacancy_assign.html', context).strip()

            send_to = job.requested_by.email
            #send_mail(subject, html_message, 'no-reply@wexlog.io', [send_to,])
            message = Mail(
                from_email = (settings.SENDGRID_FROM_EMAIL, 'MyWeXlog Vacancy Assigned'),
                to_emails = send_to,
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
            #<<<email

            return redirect(reverse('MarketPlace:SuitableInterviewList', kwargs={'vac': vac,}))
        else:
            template = 'marketplace/vacancy_assign.html'
            context = {'form': form, 'job': job, 'talent': talent, 'bids': bids,}
            return render(request, template, context)

    else:
        template = 'marketplace/vacancy_assign.html'
        context = {'form': form, 'job': job, 'talent': talent, 'bids': bids,}
        return render(request, template, context)

#used in the Shortlistview to decline a person
@login_required()
@subscription(2)
def TalentDecline(request, tlt, vac):
    job = get_object_or_404(TalentRequired, ref_no=vac)
    talent = get_object_or_404(CustomUser, alias=tlt)
    bids = WorkBid.objects.filter(Q(talent__alias=tlt) & Q(work__ref_no=vac))
    s_list = BidShortList.objects.filter(scope__ref_no=vac)

    if request.method == 'POST':
        BidInterviewList.objects.create(talent=talent, scope=job, outcome='N', tlt_response='N', tlt_intcomplete = True, emp_intcomplete = True, comments_tlt='No Interview - Marked as not suitable without an interview by employer')
        job.save()

    s_list.filter(talent__alias=tlt).update(status='R')

    if bids is not None:
        bids.update(bidreview='R')

    bil_qs = BidInterviewList.objects.get(talent=talent, scope=job)
    bil = bil_qs.slug

    return redirect(reverse('MarketPlace:SlNotSuitable', kwargs={'bil': bil,'tlt': tlt,}))


@login_required()
@subscription(2)
def ShortListView(request, vac):
    vacancy = get_object_or_404(TalentRequired, ref_no=vac)
    s_list = BidShortList.objects.filter(Q(scope__ref_no=vac) & Q(status='S'))
    we = WorkExperience.objects.filter(Q(talent__subscription__gte=0) & Q(score__gte=skill_pass_score))
    skille = SkillRequired.objects.filter(scope__ref_no=vac)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    book = ReadBy.objects.all()
    vac_exp = ExpandedView.objects.get(talent=request.user)
    list_view = vac_exp.shortlist_list
    sk_st = SkillLevel.objects.get(level=0).min_hours
    sk_bg = SkillLevel.objects.get(level=1).min_hours
    sk_jn = SkillLevel.objects.get(level=2).min_hours
    sk_in = SkillLevel.objects.get(level=3).min_hours
    sk_sn = SkillLevel.objects.get(level=4).min_hours
    sk_ld = SkillLevel.objects.get(level=5).min_hours
    closed = WorkIssuedTo.objects.filter(Q(work__ref_no=vac) & Q(tlt_response='A')).exists()
    active = WorkIssuedTo.objects.filter(Q(work__ref_no=vac)).filter(Q(tlt_response='P')| Q(tlt_response='C')).exists()
    declined = list(WorkIssuedTo.objects.filter(Q(work__ref_no=vac) &Q(tlt_response='D')).values_list('talent', flat=True))
    app_list = list(s_list.values_list('talent', flat=True))

    skill_rs = skille.values_list('skills__skill', flat=True).distinct()
    skill_rc = skill_rs.count()

    short ={}
    for app in app_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        talent_skill_l = we.filter(talent=app, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=app, edt=True).values_list('topic__skills__skill', flat=True)
        atalent_skill = list(talent_skill_l)
        rb = book.filter(talent=app).count()
        atalent_skillt = list(talent_skillt_l)
        des = list(BriefCareerHistory.objects.filter(talent=app, current=True).values_list('designation__name', flat=True))
        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count
        bg = pfl.background

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        slist_l = talent_skill_l.union(talent_skillt_l)
        skill_intersection = skill_rs.intersection(slist_l)
        skill_int_count = skill_intersection.count()
        skill_match = skill_int_count / skill_rc * 100

        short[app]={
            'we':awetv, 'te':atetv, 's_no': askill_count, 'skill_rc': skill_rc, 'skill_int_count': skill_int_count, 'skill_match': skill_match, 'skillset': askillset, 'rb':rb, 'ro':rate, 'score':avg, 'count': cnt, 'background': bg, 'des': des,
            }

    t = tuple(short.items())

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(t, 20)

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


    template = 'marketplace/shortlist_view.html'
    context = {
        'vac': vac,
        'sk_st': sk_st,
        'sk_bg': sk_bg,
        'sk_jn': sk_jn,
        'sk_in': sk_in,
        'sk_sn': sk_sn,
        'sk_ld': sk_ld,
        's_list': s_list,
        'list_view': list_view,
        'short': short,
        'vacancy': vacancy,
        'active': active,
        'declined': declined,
        'closed': closed,
        'pageitems': pageitems,
        'page_range': page_range
        }
    return render(request, template, context)


@login_required()
def DeliverablesEditView(request, vac):
    instance = get_object_or_404(Deliverables, scope__ref_no=vac)
    form = DeliverablesForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return redirect(reverse('MarketPlace:VacancyPost', kwargs={'vac': instance.scope.ref_no})+'#deliverables')
    else:
        template = 'marketplace/vacancy_deliverables_edit_2.html'
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


@login_required()
def DeliverablesAdd2View(request, vac):
    instance = get_object_or_404(TalentRequired, ref_no=vac)
    form = DeliverablesForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.scope = instance
            new.save()
            return redirect(reverse('MarketPlace:VacancyPost', kwargs={'vac': vac})+'#deliverables')
    else:
        template = 'marketplace/vacancy_deliverables_edit.html'
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


@login_required()
def DeliverableDeleteView(request, pk):
    if request.method == 'POST':
        deld = Deliverables.objects.get(pk=pk)
        deld.delete()
    return redirect(reverse('MarketPlace:VacancyPost', kwargs={'vac':deld.scope.ref_no})+'#deliverables')


@login_required()
def DeliverablesAddView(request, vac):
    instance = get_object_or_404(TalentRequired, ref_no=vac)
    deliverable = Deliverables.objects.filter(scope__ref_no=vac)
    form = DeliverablesForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.scope = instance
            new.save()
            if 'another' in request.POST:
                return redirect(reverse('MarketPlace:Deliverables', kwargs={'vac': vac}))
            elif 'done' in request.POST:
                return redirect(reverse('MarketPlace:Skills', kwargs={'vac': instance.ref_no}))
        else:
            template = 'marketplace/vacancy_deliverables.html'
            context = {'form': form, 'instance': instance, 'deliverable': deliverable}
            return render(request, template, context)

    else:
        template = 'marketplace/vacancy_deliverables.html'
        context = {'form': form, 'instance': instance, 'deliverable': deliverable}
        return render(request, template, context)


@login_required()
@csp_exempt
@subscription(2)
def VacancyView(request):
    '''The view used to capture vacancies #capture #vacancies'''
    #query to limit only companies to which user is currently working
    company_qs = BriefCareerHistory.objects.filter(Q(current=True) & Q(talent=request.user)).values_list('companybranch__id', flat=True)
    p_cap_qs = Branch.objects.filter(company__filter_class='S').values_list('id', flat=True)

    qs = company_qs.union(p_cap_qs)

    form = TalentRequiredForm(request.POST or None, request.FILES, company_qs=qs)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.requested_by = request.user
            new.save()
            form.save_m2m()
            return redirect(reverse('MarketPlace:Deliverables', kwargs={'vac':new.ref_no}))
        else:
            template = 'marketplace/vacancy.html'
            context = {'form': form}
            return render(request, template, context)

    else:
        template = 'marketplace/vacancy.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
@csp_exempt
@subscription(2)
def VacancyEditView(request, vac):
    instance=get_object_or_404(TalentRequired, ref_no=vac)

    if request.method == 'POST':
        form = TalentRequiredEditForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
            return redirect(reverse('MarketPlace:VacancyPost', kwargs={'vac':vac}))
        else:
            form = TalentRequiredEditForm(instance=instance)

            template = 'marketplace/vacancy_edit.html'
            context = {'form': form, 'instance': instance}
            return render(request, template, context)
    else:
        form = TalentRequiredEditForm(instance=instance)

        template = 'marketplace/vacancy_edit.html'
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


#>>> WorkLocation Popup
@login_required()
@csp_exempt
def WorkLocationAddPopup(request):
    form = WorkLocationForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_worklocation");</script>' % (instance.pk, instance))

    else:
        context = {'form': form}
        template = 'marketplace/worklocation_popup.html'
        return render(request, template, context)

@csrf_exempt
def get_worklocation_id(request):
    if request.is_ajax():
        new_worklocation = request.Get['worklocation']
        worklocation_id = WorkLocation.objects.get(worklocation = new_worklocation).id
        data = {'worklocation_id':worklocation_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#WorkLocation Popup <<<


#>>>SkillLevel Popup
@login_required()
@csp_exempt
def SkillLevelAddPopup(request):
    form = SkillLevelForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_experience_level");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template = 'marketplace/skilllevel_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_skilllevel_id(request):
    if request.is_ajax():
        skilllevel = request.Get['skilllevel']
        skilllevel_id = SkillLevel.objects.get(name = skilllevel).id
        data = {'skilllevel_id':skilllevel_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< SkillLevel Popup

#>>> Help views
@login_required()
def ExperienceLevelHelpView(request):
    lvl = SkillLevel.objects.all()

    context = {'lvl': lvl}
    template = 'marketplace/help_skill_level.html'
    return render(request, template, context)


@login_required()
def WorkConfigerationHelpView(request):
    wch = WorkLocation.objects.all()

    context = {'wch': wch}
    template = 'marketplace/help_work_configeration.html'
    return render(request, template, context)


@login_required()
def HelpPostVacancyView(request):

    context = {}
    template = 'marketplace/help_post_vacancy.html'
    return render(request, template, context)


@login_required()
def HelpVacancySuitedSummaryView(request):

    context = {}
    template = 'marketplace/help_vacancies_suited_for_me_summary.html'
    return render(request, template, context)


@login_required()
def HelpVacancySuitedFullView(request):

    context = {}
    template = 'marketplace/help_vacancies_suited_for_me_full.html'
    return render(request, template, context)


@login_required()
def HelpVacancyAdvertisedOpenSummaryView(request):

    context = {}
    template = 'marketplace/help_vacancies_advertised_open_summary.html'
    return render(request, template, context)


@login_required()
def HelpVacancyAdvertisedOpenAllView(request):

    context = {}
    template = 'marketplace/help_vacancies_advertised_open_all.html'
    return render(request, template, context)


@login_required()
def HelpVacancyAdvertisedClosedSummaryView(request):

    context = {}
    template = 'marketplace/help_vacancies_advertised_closed_summary.html'
    return render(request, template, context)


@login_required()
def HelpVacancyAdvertisedClosedAllView(request):

    context = {}
    template = 'marketplace/help_vacancies_advertised_closed_all.html'
    return render(request, template, context)


@login_required()
def HelpVacancyAdvertisedFullView(request):

    context = {}
    template = 'marketplace/help_vacancies_advertised_full.html'
    return render(request, template, context)


@login_required()
def HelpAvailabilityView(request):

    context = {}
    template = 'marketplace/help_availability.html'
    return render(request, template, context)


@login_required()
def HelpApplicationHistoryRolesAppliedForSummaryView(request):

    context = {}
    template = 'marketplace/help_application_history_roles_applied_for_summary.html'
    return render(request, template, context)


@login_required()
def HelpApplicationHistoryRolesAppliedForFullView(request):

    context = {}
    template = 'marketplace/help_application_history_roles_applied_for_full.html'
    return render(request, template, context)


@login_required()
def HelpApplicationHistoryRolesShortlistedForSummaryView(request):

    context = {}
    template = 'marketplace/help_application_history_roles_shortlisted_for_summary.html'
    return render(request, template, context)


@login_required()
def HelpApplicationHistoryRolesShortlistedForFullView(request):

    context = {}
    template = 'marketplace/help_application_history_roles_shortlisted_for_full.html'
    return render(request, template, context)


@login_required()
def HelpApplicationHistoryUnsuccessfulApplicationsSummaryView(request):

    context = {}
    template = 'marketplace/help_application_history_unsuccessful_summary.html'
    return render(request, template, context)


@login_required()
def HelpApplicationHistoryUnsuccessfulApplicationsFullView(request):

    context = {}
    template = 'marketplace/help_application_history_unsuccessful_full.html'
    return render(request, template, context)


@login_required()
def HelpApplicationHistorySuccessfulApplicationsSummaryView(request):

    context = {}
    template = 'marketplace/help_application_history_successful_summary.html'
    return render(request, template, context)


@login_required()
def HelpApplicationHistorySuccessfulApplicationsFullView(request):

    context = {}
    template = 'marketplace/help_application_history_successful_full.html'
    return render(request, template, context)


@login_required()
def HelpVacancyPostView(request):

    context = {}
    template = 'marketplace/help_vacancy_post.html'
    return render(request, template, context)


@login_required()
def HelpTalentSuitedToVacancyView(request):

    context = {}
    template = 'marketplace/help_talent_suited_to_vacancy.html'
    return render(request, template, context)


@login_required()
def HelpTalentSuitedToVacancyFullView(request):

    context = {}
    template = 'marketplace/help_talent_suited_to_vacancy_full.html'
    return render(request, template, context)


@login_required()
def HelpApplicantsView(request):

    context = {}
    template = 'marketplace/help_vacancy_applicants.html'
    return render(request, template, context)


@login_required()
def HelpApplicantsFullView(request):

    context = {}
    template = 'marketplace/help_vacancy_applicants_full.html'
    return render(request, template, context)


@login_required()
def HelpInterviewHistoryAllView(request):

    context = {}
    template = 'marketplace/help_interview_history_all.html'
    return render(request, template, context)


@login_required()
def HelpEmployerInterviewHistoryAllView(request):

    context = {}
    template = 'marketplace/help_employer_interview_history_all.html'
    return render(request, template, context)


@login_required()
def HelpInterviewDetailView(request):

    context = {}
    template = 'marketplace/help_interview_detail.html'
    return render(request, template, context)


@login_required()
def HelpDeliverable2View(request):

    context = {}
    template = 'marketplace/help_deliverable2.html'
    return render(request, template, context)


@login_required()
def HelpDeliverablesView(request):

    context = {}
    template = 'marketplace/help_deliverables.html'
    return render(request, template, context)
#Help Views <<<
