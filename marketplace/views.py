from django.shortcuts import render, get_object_or_404, redirect
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import PermissionDenied
import json
from django.db.models import Count, Sum, F, Q
from django.utils import timezone
from decimal import getcontext, Decimal
import itertools

from csp.decorators import csp_exempt
from core.decorators import subscription
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.postgres.search import SearchVector, TrigramSimilarity


#email
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags


from .forms import (
        TalentAvailabillityForm, SkillRequiredForm, SkillLevelForm, DeliverablesForm, TalentRequiredForm, WorkLocationForm, WorkBidForm, TalentRequiredEditForm, TalentInterViewComments, EmployerInterViewComments, AssignWorkForm, VacancySearchForm, TltIntCommentForm
)

from .models import(
    TalentRequired, SkillRequired, Deliverables, TalentAvailabillity, WorkBid, SkillLevel, BidShortList, WorkIssuedTo, BidInterviewList, WorkLocation
)

from talenttrack.models import WorkExperience, LicenseCertification
from db_flatten.models import SkillTag
from users.models import CustomUser
from Profile.models import Profile, LanguageTrack, PhysicalAddress
from booklist.models import ReadBy
from marketplace.models import Branch

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
            results = TalentRequired.objects.annotate(similarity=TrigramSimilarity('ref_no', query),).filter(similarity__gt=0.3).order_by('-similarity')

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

    template = 'marketplace/talent_interview_detail.html'
    context = {'bil_qs': bil_qs}
    return render(request, template, context)


@login_required()
@subscription(2)
def EmployerInterviewHistoryView(request, tlt):
    interviews = BidInterviewList.objects.filter(scope__requested_by__alias=tlt).order_by('-scope__ref_no')

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
def EmpInterviewClose(request, bil, tlt):
    bil_qs = BidInterviewList.objects.filter(slug=bil)

    bil_qs.update(emp_intcomplete=True)

    return redirect(reverse('MarketPlace:EmployerInterviewHistory', kwargs={'tlt': tlt}))


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

    return redirect(reverse('MarketPlace:InterviewList', kwargs={'vac': vac,}))


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

    intv_pending = intv_qs.filter(Q(outcome='I')).filter(Q(tlt_response='A') | Q(tlt_response='P'))

    intv_suitable = intv_qs.filter(Q(outcome = 'S') & ~Q(tlt_response='D'))
    intv_notsuitable = intv_qs.filter(Q(outcome = 'N') & ~Q(tlt_response='D'))
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

    we = WorkExperience.objects.filter(talent__subscription__gte=1)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    book = ReadBy.objects.all()

    #Information for all suitable applicants
    suitable_list = list(intv_suitable.values_list('talent', flat=True))

    interview_s ={}
    for app in suitable_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        atalent_skill = list(we.filter(talent=app, edt=False).values_list('skills', flat=True))
        rb = book.filter(talent=app).count()
        atalent_skillt = list(we.filter(talent=app, edt=True).values_list('topic__skills', flat=True))

        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')

        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        interview_s[app]={
            'we':awetv, 'te':atetv,'s_no':askill_count, 'rb':rb, 'ro':rate, 'score':avg, 'count': cnt
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
        atalent_skill = list(we.filter(talent=app, edt=False).values_list('skills', flat=True))
        rb = book.filter(talent=app).count()
        atalent_skillt = list(we.filter(talent=app, edt=True).values_list('topic__skills', flat=True))
        applied = applicants.filter(talent=app)

        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        interview_p[app]={'we':awetv, 'te':atetv,'s_no':askill_count, 'rb':rb, 'ro':rate, 'score':avg, 'count':cnt}

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
        atalent_skill = list(we.filter(talent=app, edt=False).values_list('skills', flat=True))
        rb = book.filter(talent=app).count()
        atalent_skillt = list(we.filter(talent=app, edt=True).values_list('topic__skills', flat=True))

        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        interview_n[app]={'we':awetv, 'te':atetv,'s_no':askill_count, 'rb':rb, 'ro':rate, 'score':avg, 'count': cnt}

    interview_n_slice = dict(itertools.islice(interview_n.items(), 5))
    interview_n_count = len(interview_n)

    template = 'marketplace/interview_list.html'
    context = {
        'interview_p': interview_p,
        'interview_p_slice': interview_p_slice,
        'interview_p_count': interview_p_count,
        'interview_n': interview_n,
        'interview_n_slice': interview_n_slice,
        'interview_n_count': interview_n_count,
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

    we = WorkExperience.objects.filter(talent__subscription__gte=1)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    book = ReadBy.objects.all()
    vac = vac

    #Information for all pending applicants
    pending_list = list(intv_pending.values_list('talent', flat=True))

    interview_p ={}
    for app in pending_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        atalent_skill = list(we.filter(talent=app, edt=False).values_list('skills', flat=True))
        rb = book.filter(talent=app).count()
        atalent_skillt = list(we.filter(talent=app, edt=True).values_list('topic__skills', flat=True))
        applied = applicants.filter(talent=app)

        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        interview_p[app]={'we':awetv, 'te':atetv,'s_no':askill_count, 'rb':rb, 'ro':rate, 'score':avg, 'count':cnt}

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
        'interview_p': interview_p,
        'interview_p_count': interview_p_count,
        'scope': scope,
        'vac': vac,
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

    we = WorkExperience.objects.filter(talent__subscription__gte=1)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    book = ReadBy.objects.all()

    #Information for all suitable applicants
    suitable_list = list(intv_suitable.values_list('talent', flat=True))

    interview_s ={}
    for app in suitable_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        atalent_skill = list(we.filter(talent=app, edt=False).values_list('skills', flat=True))
        rb = book.filter(talent=app).count()
        atalent_skillt = list(we.filter(talent=app, edt=True).values_list('topic__skills', flat=True))

        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')

        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        interview_s[app]={
            'we':awetv, 'te':atetv,'s_no':askill_count, 'rb':rb, 'ro':rate, 'score':avg, 'count': cnt
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
        'interview_s': interview_s,
        'interview_s_count': interview_s_count,
        'scope': scope,
        'wit_qs': wit_qs,
        'active': active,
        'vac': vac,
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

    we = WorkExperience.objects.filter(talent__subscription__gte=1)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    book = ReadBy.objects.all()

    #Information for all not suitable applicants
    nots_list = list(intv_notsuitable.values_list('talent', flat=True))

    interview_n ={}
    for app in nots_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        atalent_skill = list(we.filter(talent=app, edt=False).values_list('skills', flat=True))
        rb = book.filter(talent=app).count()
        atalent_skillt = list(we.filter(talent=app, edt=True).values_list('topic__skills', flat=True))

        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        interview_n[app]={'we':awetv, 'te':atetv,'s_no':askill_count, 'rb':rb, 'ro':rate, 'score':avg, 'count': cnt}

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
        'interview_n': interview_n,
        'interview_n_count': interview_n_count,
        'scope': scope,
        'vac': vac,
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

    form = WorkBidForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.work = detail
            new.save()
            return redirect(reverse('MarketPlace:Entrance'))
    else:

        template = 'marketplace/vacancy_apply.html'
        context={'form': form, 'detail': detail}
        return render(request, template, context)

#This is the detail view for talent and where active users can apply for the role
@login_required()
@subscription(2)
def VacancyDetailView(request, vac):
    vacancy = TalentRequired.objects.filter(ref_no=vac)
    skills = SkillRequired.objects.filter(scope__ref_no=vac)
    deliver = Deliverables.objects.filter(scope__ref_no=vac)
    bch = vacancy[0].enterprise.slug
    rate_b = Branch.objects.get(slug=bch)
    int = BidInterviewList.objects.filter(Q(scope__ref_no=vac)).count()
    bid_qs = WorkBid.objects.filter(work__ref_no=vac).order_by('rate_bid')
    bid = bid_qs.count()
    slist = BidShortList.objects.filter(scope__ref_no=vac).count()
    wit = WorkIssuedTo.objects.filter(Q(tlt_response='A') & Q(work__ref_no=vac))

    date1 = vacancy[0].bid_closes
    date2 = timezone.now()
    date3 = date1 - date2
    date4 = abs(date3.days)

    if date1 < date2:
        vacancy.update(offer_status = 'C')

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
        }
    return render(request, template, context)


@login_required()
@subscription(1)
def VacancyDetailView_Profile(request, vac):
    vacancy = TalentRequired.objects.filter(ref_no=vac)
    skills = SkillRequired.objects.filter(scope__ref_no=vac)
    deliver = Deliverables.objects.filter(scope__ref_no=vac)
    bch = vacancy[0].enterprise.slug
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
    pfl = Profile.objects.filter(talent=talent)
    tr = TalentRequired.objects.filter(offer_status='O')
    tr_emp = TalentRequired.objects.filter(requested_by=talent)
    wb = WorkBid.objects.filter(work__requested_by=talent, work__offer_status='O')
    ta = TalentAvailabillity.objects.filter(talent=talent)
    we = WorkExperience.objects.filter(talent=talent).prefetch_related('topic')
    sr = SkillRequired.objects.filter(scope__offer_status='O')
    sl = SkillLevel.objects.all()
    wbt = WorkBid.objects.filter(Q(talent=talent) & Q(work__offer_status='O'))
    bsl = BidShortList.objects.filter(Q(talent=talent) & Q(scope__offer_status='O'))
    #Queryset caching<<<

    ipost = tr_emp.filter(offer_status='O').order_by('-bid_open')[:5]
    ipost_count = ipost.count()
    ipost_closed = tr_emp.filter(offer_status='C').order_by('-bid_open')[:5]
    ipost_closed_count = ipost_closed.count()
    ipost_bid = wb.filter(Q(bidreview__exact='R') | Q(bidreview__exact='P') | Q(bidreview__exact='A'))
    ipost_bid_flat = ipost_bid.values_list('work', flat=True).distinct()
    capacity = ta.filter(date_to__gte=timezone.now()).order_by('-date_to')[:5]

    #Code for stacked lookup for talent's skills

    #>>>Create a set of all skills
    e_skill = we.filter(edt=True).only('pk').values_list('pk', flat=True)
    l_skill = we.filter(edt=False).only('pk').values_list('pk', flat=True)

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

    if vac_cert_s is None: #if not certifications required, pass
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
    #Remote Freelance open to all talent, other vacanciesTypes only for region (to be updated to distances in later revisions) this will require gEOdJANGO
    tlt_loc = PhysicalAddress.objects.filter(talent=talent).values_list('region', flat=True)
    tlt_loc=tlt_loc[0]

    vac_loc_rm = set(tr.filter(worklocation__type__icontains='Remote freelance').values_list('id', flat=True))

    vac_loc_reg = set(tr.filter(~Q(worklocation__type__icontains='Remote Freelance')& Q(city__region=tlt_loc)).values_list('id', flat=True))

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

    #Recreating the QuerySet
    suitable = tr.filter(id__in=dsi)

    rem_vac = suitable.count()
    dsd = suitable[:5]

    #Experience Level check & list skills required in vacancies<<<

    template = 'marketplace/vacancy_home.html'
    context ={
        'capacity': capacity,
        'ipost': ipost,
        'ipost_count': ipost_count,
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


@login_required()
def VacanciesListView(request):
    #>>>Queryset caching
    talent=request.user
    pfl = Profile.objects.filter(talent=talent)
    tr = TalentRequired.objects.filter(offer_status='O')
    tr_emp = TalentRequired.objects.filter(requested_by=talent)
    wb = WorkBid.objects.filter(work__requested_by=talent, work__offer_status='O')
    ta = TalentAvailabillity.objects.filter(talent=talent)
    we = WorkExperience.objects.filter(talent=talent).prefetch_related('topic')
    sr = SkillRequired.objects.filter(scope__offer_status='O')
    sl = SkillLevel.objects.all()
    wbt = WorkBid.objects.filter(Q(talent=talent) & Q(work__offer_status='O'))
    bsl = BidShortList.objects.filter(Q(talent=talent) & Q(scope__offer_status='O'))
    #Queryset caching<<<

    ipost = tr_emp.filter(offer_status='O').order_by('-bid_open')[:5]
    ipost_count = ipost.count()
    ipost_closed = tr_emp.filter(offer_status='C').order_by('-bid_open')[:5]
    ipost_closed_count = ipost_closed.count()
    ipost_bid = wb.filter(Q(bidreview__exact='R') | Q(bidreview__exact='P') | Q(bidreview__exact='A'))
    ipost_bid_flat = ipost_bid.values_list('work', flat=True).distinct()
    capacity = ta.filter(date_to__gte=timezone.now()).order_by('-date_to')[:5]

    #Code for stacked lookup for talent's skills

    #>>>Create a set of all skills
    e_skill = we.filter(edt=True).only('pk').values_list('pk', flat=True)
    l_skill = we.filter(edt=False).only('pk').values_list('pk', flat=True)

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
    cert_required = vac_exp.values_list('certification').exists()

    if cert_required is not None:#if not certifications required, pass
        tlt_cert = set(LicenseCertification.objects.filter(talent=talent).values_list('certification', flat=True))
        vac_cert = set(vac_exp.filter(certification__in=tlt_cert).values_list('id',flat=True))
        if vac_lang is not None:
            req_experience = vac_cert.intersection(vac_lang)
        else:
            req_experience = vac_cert
    else:
        if vac_lang is not None:
            req_experience = set(vac_exp.values_list('id',flat=True)).intersection(vac_lang)
        else:
            req_experience = set(vac_exp.values_list('id',flat=True))

    #Checking for locations
    #Remote Freelance open to all talent, other vacanciesTypes only for region (to be updated to distances in later revisions)
    tlt_loc = PhysicalAddress.objects.filter(talent=talent).values_list('region', flat=True)
    tlt_loc=tlt_loc[0]

    vac_loc_rm = set(tr.filter(worklocation__type__icontains='Remote freelance').values_list('id', flat=True))

    vac_loc_reg = set(tr.filter(~Q(worklocation__type__icontains='Remote freelance')& Q(city__region=tlt_loc)).values_list('id', flat=True))

    vac_loc = vac_loc_rm | vac_loc_reg

    req_experience = req_experience.symmetric_difference(vac_loc)

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

    #Recreating the QuerySet
    suitable = tr.filter(id__in=dsi)

    rem_vac = suitable.count()
    dsd = suitable

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
        'dsd': dsd,
        'pageitems': pageitems,
        'ipost_bid_flat': ipost_bid_flat,
        'page_range': page_range,
        'rem_vac': rem_vac,
    }
    return render(request, template, context)


@login_required()
@subscription(2)
def ApplicationHistoryView(request):
    talent = request.user
    role = WorkBid.objects.filter(talent=talent).order_by('-date_applied')
    applied = role.filter(bidreview__exact='P')[:10]
    rejected = role.filter(bidreview__exact='R')[:10]
    accepted = role.filter(bidreview__exact='A')[:10]
    s_list = BidShortList.objects.filter(Q(talent=talent) & ~Q(status='A')).order_by('-date_listed')[:10]
    q_list = BidShortList.objects.filter(Q(talent=talent) & ~Q(status='A')).order_by('-date_listed')
    p_rejected = q_list.filter(status='R')[:10]
    p_accepted = q_list.filter(status='A')[:10]

    unsuccessful = rejected.union(p_rejected)

    s_list_count = s_list.count()
    applied_count = applied.count()
    rejected_count = rejected.count()
    accepted_count = accepted.count()

    template = 'marketplace/vacancy_application_history.html'
    context ={
        'applied': applied,
        'applied_count': applied_count,
        'accepted': accepted,
        'accepted_count': accepted_count,
        'rejected': rejected,
        'rejected_count': rejected_count,
        'p_rejected': p_rejected,
        'p_accepted': p_accepted,
        's_list': s_list,
        's_list_count': s_list_count,
        }
    return render(request, template, context)


@login_required()
@subscription(2)
def RolesAppliedForApplicationHistoryView(request):
    talent = request.user
    role = WorkBid.objects.filter(talent=talent).order_by('-date_applied')
    applied = role.filter(bidreview__exact='P')

    applied_count = applied.count()

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
        'applied_count': applied_count,
        'pageitems': pageitems,
        'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(2)
def RolesShortlistedForApplicationHistoryView(request):
    talent = request.user
    s_list = BidShortList.objects.filter(Q(talent=talent) & ~Q(status='A')).order_by('-date_listed')

    s_list_count = s_list.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(s_list, 20)

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
        's_list_count': s_list_count,
        'pageitems': pageitems,
        'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(2)
def UnsuccessfulApplicationHistoryView(request):
    talent = request.user
    role = WorkBid.objects.filter(talent=talent).order_by('-date_applied')
    rejected = role.filter(bidreview__exact='R')
    s_list = BidShortList.objects.filter(Q(talent=talent) & ~Q(status='A')).order_by('-date_listed')
    p_rejected = s_list.filter(status='R')

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
        'rejected': rejected,
        'p_rejected': p_rejected,
        's_list': s_list,
        'pageitems': pageitems,
        'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(2)
def SuccessfulApplicationHistoryView(request):
    talent = request.user
    role = WorkBid.objects.filter(talent=talent).order_by('-date_applied')
    accepted = role.filter(bidreview__exact='A')
    s_list = BidShortList.objects.filter(Q(talent=talent) & ~Q(status='A')).order_by('-date_listed')
    p_accepted = s_list.filter(status='A')

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
        'accepted': accepted,
        'p_accepted': p_accepted,
        's_list': s_list,
        'pageitems': pageitems,
        'page_range': page_range}
    return render(request, template, context)


@login_required()
def TalentAvailabillityView(request):
    form = TalentAvailabillityForm(request.POST or None)
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
    we = WorkExperience.objects.filter(talent__subscription__gte=1)
    s_list = BidShortList.objects.filter(scope__ref_no=vac)
    book = ReadBy.objects.all()
    #Queryset Cache<<<

    #>>> List all skills required
    skill_r = skille.values_list('skills', flat=True).distinct()
    skill_rl = list(skill_r)
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

    suitable={}
    for item in we_list:
        w_exp = we.filter(talent=item, edt=False).aggregate(wet=Sum('hours_worked'))
        wetv = w_exp.get('wet')
        t_exp = we.filter(talent=item, edt=True).aggregate(tet=Sum('topic__hours'))
        tetv = t_exp.get('tet')
        talent_skill = list(we.filter(talent=item, edt=False).values_list('skills', flat=True))
        rb = book.filter(talent=item).count()
        talent_skillt = list(we.filter(talent=item, edt=True).values_list('topic__skills', flat=True))
        rate = Profile.objects.filter(talent=item).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias',)

        pfl = Profile.objects.get(talent=item)
        avg = pfl.avg_rate
        cnt = pfl.rate_count

        slist = talent_skill + talent_skillt
        skillset = set(slist)
        skill_count = len(skillset)

        suitable[item]={
            'we':wetv, 'te':tetv,'s_no':skill_count, 'rb':rb, 'ro':rate, 'score':avg, 'count':cnt
            }

        #Extracting information for the applicants
    applied ={}
    app_list = list(app_list.values_list('talent', flat=True))
    for app in app_list:
            aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
            awetv = aw_exp.get('awet')
            at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
            atetv = at_exp.get('tet')
            atalent_skill = list(we.filter(talent=app, edt=False).values_list('skills', flat=True))
            atalent_skillt = list(we.filter(talent=app, edt=True).values_list('topic__skills', flat=True))
            rb = book.filter(talent=app).count()
            rate = applicants.filter(talent=app).values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation', 'talent__alias')
            pfl = Profile.objects.get(talent=app)
            avg = pfl.avg_rate
            cnt = pfl.rate_count

            aslist = atalent_skill + atalent_skillt
            askillset = set(aslist)
            askill_count = len(askillset)

            applied[app]={
                'we':awetv, 'te':atetv,'s_no':askill_count, 'rb':rb, 'ro':rate, 'score': avg, 'count': cnt
                }

    suitable_slice = dict(itertools.islice(suitable.items(), 5))
    applied_slice = dict(itertools.islice(applied.items(), 5))

    suitable_count = len(suitable)
    applied_count = len(applied)

    template = 'marketplace/vacancy_post_view.html'
    context = {
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
            's_list': s_list
    }

    return render(request, template, context)


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
    we = WorkExperience.objects.filter(talent__subscription__gte=1)
    s_list = BidShortList.objects.filter(scope__ref_no=vac)
    book = ReadBy.objects.all()
    #Queryset Cache<<<

    #>>> List all skills required
    skill_r = skille.values_list('skills', flat=True).distinct()
    skill_rl = list(skill_r)
    #List all skills required<<<

    #>>> Find all talent with required skill

    wes = we.filter(Q(skills__in=skill_r) | Q(topic__skills__in=skill_r)).distinct('talent')

    #ensure applicants don't appear in the suitable skills window
    app_list = applicants.values_list('talent')
    suit_list = wes.values_list('talent')
    short_list = s_list.values_list('talent')
    short_list_a = s_list.filter(talent__subscription__gte=2).values_list('talent')

    diff_list0 = suit_list.difference(app_list)#removes talent that has applied
    #removes shortlists talent
    diff_list = diff_list0.difference(short_list)
    app_list = app_list.difference(short_list_a)

    we_list = list(diff_list.values_list('talent', flat=True))

    suitable={}
    for item in we_list:
        w_exp = we.filter(talent=item, edt=False).aggregate(wet=Sum('hours_worked'))
        wetv = w_exp.get('wet')
        t_exp = we.filter(talent=item, edt=True).aggregate(tet=Sum('topic__hours'))
        tetv = t_exp.get('tet')
        talent_skill = list(we.filter(talent=item, edt=False).values_list('skills', flat=True))
        rb = book.filter(talent=item).count()
        talent_skillt = list(we.filter(talent=item, edt=True).values_list('topic__skills', flat=True))
        rate = Profile.objects.filter(talent=item).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias',)

        slist = talent_skill + talent_skillt
        skillset = set(slist)
        skill_count = len(skillset)

        suitable[item]={'we':wetv, 'te':tetv,'s_no':skill_count, 'rb':rb, 'ro':rate}

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
            'instance': instance,
            'skille': skille,
            'delivere': delivere,
            'suitable': suitable,
            'suitable_count': suitable_count,
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
    we = WorkExperience.objects.filter(talent__subscription__gte=1)
    s_list = BidShortList.objects.filter(scope__ref_no=vac)
    book = ReadBy.objects.all()
    #Queryset Cache<<<

    #>>> List all skills required
    skill_r = skille.values_list('skills', flat=True).distinct()
    skill_rl = list(skill_r)
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
            atalent_skill = list(we.filter(talent=app, edt=False).values_list('skills', flat=True))
            atalent_skillt = list(we.filter(talent=app, edt=True).values_list('topic__skills', flat=True))
            rb = book.filter(talent=app).count()
            rate = applicants.filter(talent=app).values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation', 'talent__alias')

            aslist = atalent_skill + atalent_skillt
            askillset = set(aslist)
            askill_count = len(askillset)

            applied[app]={'we':awetv, 'te':atetv,'s_no':askill_count, 'rb':rb, 'ro':rate}

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
            'instance': instance,
            'skille': skille,
            'delivere': delivere,
            'applicants': applicants,
            'applied': applied,
            'applied_count': applied_count,
            's_list': s_list,
            'pageitems': pageitems,
            'page_range': page_range
    }

    return render(request, template, context)


@csp_exempt
@login_required()
def VacancySkillsAddView(request, vac):
    instance = get_object_or_404(TalentRequired, ref_no=vac)
    skill_list = SkillRequired.objects.filter(scope__ref_no=vac)
    form = SkillRequiredForm(request.POST or None)
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
    form = SkillRequiredForm(request.POST or None)
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

        if 'active' in request.POST:
            upd = WorkBid.objects.get(Q(talent=talent) & Q(work=job))
            upd.bidreview = 'S'#2
            upd.save()

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
def AddToInterviewListView(request, vac, tlt):
    job = get_object_or_404(TalentRequired, ref_no=vac)
    talent = get_object_or_404(CustomUser, alias=tlt)
    if request.method == 'POST':
        BidInterviewList.objects.create(talent=talent, scope=job, outcome='I', tlt_response='P')#1
        BidShortList.objects.filter(Q(talent=talent) & Q(scope=job)).update(status='I')#4

        wb_qs = WorkBid.objects.filter(Q(talent=talent) & Q(work=job))
        if wb_qs:
            wb_qs.update(bidreview='I')#2

        job.vac_wkfl == 'I'
        job.save()#3

        #>>>email
        subject = f"WeXlog - {job.title} ({job.ref_no}): Interview request"

        context = {'job': job, 'talent': talent}

        html_message = render_to_string('marketplace/email_interview_request.html', context)
        plain_message = strip_tags(html_message)

        send_to = job.requested_by.email
        send_mail(subject, html_message, 'no-reply@wexlog.io', [send_to,])
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

            if bids is not None:
                bids.update(bidreview='P')#1

            #>>>email
            subject = f"WeXlog - Job assigned: {job.title} ({job.ref_no})"

            context = {'job': job, 'talent': talent, }

            html_message = render_to_string('marketplace/email_vacancy_assign.html', context)
            plain_message = strip_tags(html_message)

            send_to = job.requested_by.email
            send_mail(subject, html_message, 'no-reply@mywexlog.com', [send_to,])
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

            if bids is not None:
                bids.update(bidreview='P')#1

            #>>>email
            subject = f"WeXlog - Job assigned: {job.title} ({job.ref_no})"

            context = {'job': job, 'talent': talent, }

            html_message = render_to_string('marketplace/email_vacancy_assign.html', context)
            plain_message = strip_tags(html_message)

            send_to = job.requested_by.email
            send_mail(subject, html_message, 'no-reply@wexlog.io', [send_to,])
            #template = 'marketplace/email_vacancy_assign.html'
            #return render(request, template, context)
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
    we = WorkExperience.objects.filter(talent__subscription__gte=1)
    applicants = WorkBid.objects.filter(work__ref_no=vac)
    book = ReadBy.objects.all()
    closed = WorkIssuedTo.objects.filter(Q(work__ref_no=vac) & Q(tlt_response='A')).exists()
    active = WorkIssuedTo.objects.filter(Q(work__ref_no=vac)).filter(Q(tlt_response='P')| Q(tlt_response='C')).exists()
    declined = list(WorkIssuedTo.objects.filter(Q(work__ref_no=vac) &Q(tlt_response='D')).values_list('talent', flat=True))
    app_list = list(s_list.values_list('talent', flat=True))

    short ={}
    for app in app_list:

        aw_exp = we.filter(talent=app, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        at_exp = we.filter(talent=app, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        atalent_skill = list(we.filter(talent=app, edt=False).values_list('skills', flat=True))
        rb = book.filter(talent=app).count()
        atalent_skillt = list(we.filter(talent=app, edt=True).values_list('topic__skills', flat=True))

        pfl = Profile.objects.get(talent=app)
        avg = pfl.avg_rate
        cnt = pfl.rate_count

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        short[app]={
            'we':awetv, 'te':atetv,'s_no':askill_count, 'rb':rb, 'ro':rate, 'score':avg, 'count': cnt
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
        's_list': s_list,
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
        template = 'marketplace/vacancy_deliverables_edit.html'
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
    form = TalentRequiredForm(request.POST or None, request.FILES)
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
