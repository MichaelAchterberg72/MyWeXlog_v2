from django.shortcuts import render, get_object_or_404, redirect
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import PermissionDenied
import json
from django.db.models import Count, Sum, F, Q
from django.utils import timezone
from decimal import Decimal

from csp.decorators import csp_exempt
from core.decorators import subscription
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


#email
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags


from .forms import (
        TalentAvailabillityForm, SkillRequiredForm, SkillLevelForm, DeliverablesForm, TalentRequiredForm, WorkLocationForm, WorkBidForm, TalentRequiredEditForm, TalentInterViewComments, EmployerInterViewComments, AssignWorkForm,
)

from .models import(
    TalentRequired, SkillRequired, Deliverables, TalentAvailabillity, WorkBid, SkillLevel, BidShortList, WorkIssuedTo, BidInterviewList,
)

from talenttrack.models import WorkExperience
from db_flatten.models import SkillTag
from users.models import CustomUser
from Profile.models import Profile
from booklist.models import ReadBy

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required()
@subscription(1)
def InterviewDeclineView(request, int_id):
    instance = BidInterviewList.objects.get(pk=int_id)
    form = TalentInterViewComments(request.POST, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return redirect(reverse('Profile:ProfileHome'))
    else:
        template = 'marketplace/interview_comment_tlt.html'
        context={'form': form, 'instance': instance,}
        return render(request, template, context)


@login_required()
@subscription(2)
def TalentRFIView(request, slug):
    instance = WorkIssuedTo.objects.get(slug=slug)

    template = 'marketplace/rfi_view.html'
    context = {'instance': instance,}
    return render(request, template, context)


@login_required()
@subscription(2)
def InterviewSuitable(request, vac_id, tlt_id):
    BidInterviewList.objects.filter(Q(scope = vac_id) & Q(talent = tlt_id)).update(outcome='S', emp_intcomplete=True)

    BidShortList.objects.filter(Q(scope = vac_id) & Q(talent = tlt_id)).update(status='P')

    bid_qs = WorkBid.objects.filter(Q(work = vac_id) & Q(talent = tlt_id))

    if bid_qs:
        bid_qs.update(bidreview = 'P')
    else:
        pass

    return redirect(reverse('MarketPlace:InterviewList', kwargs={ 'vac_id': vac_id}))


@login_required()
@subscription(2)
def InterviewNotSuitable(request, vac_id, tlt_id):
    bidinterviewlist_qs = BidInterviewList.objects.filter(Q(scope = vac_id) & Q(talent = tlt_id))
    bidinterviewlist_qs.update(outcome='N', emp_intcomplete=True)

    bidshortlist_qs = BidShortList.objects.filter(Q(scope = vac_id) & Q(talent = tlt_id))

    bidshortlist_qs.update(status='R')
    bid_qs = WorkBid.objects.filter(Q(work = vac_id) & Q(talent = tlt_id))

    if bid_qs:
        bid_qs.update(bidreview = 'R')
    else:
        pass

    return redirect(reverse('MarketPlace:InterviewList', kwargs={ 'vac_id': vac_id}))

@login_required()
@subscription(2)
def InterviewListView(request, vac_id):
    scope = TalentRequired.objects.get(pk=vac_id)
    intv_qs = BidInterviewList.objects.filter(scope=vac_id)
    intv_pending = intv_qs.filter(outcome = 'P')
    intv_suitable = intv_qs.filter(outcome = 'S')
    intv_notsuitable = intv_qs.filter(outcome = 'N')
    intv_declined = intv_qs.filter(tlt_response = 'D')
    vacancy_declined = WorkIssuedTo.objects.filter(work=vac_id, tlt_response='D' )

    we = WorkExperience.objects.filter(talent__subscription__gte=1)
    applicants = WorkBid.objects.filter(work=vac_id)
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

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')

        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        interview_s[app]={'we':awetv, 'te':atetv,'s_no':askill_count, 'rb':rb, 'ro':rate}

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

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        interview_p[app]={'we':awetv, 'te':atetv,'s_no':askill_count, 'rb':rb, 'ro':rate}

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
        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        interview_n[app]={'we':awetv, 'te':atetv,'s_no':askill_count, 'rb':rb, 'ro':rate}

    template = 'marketplace/interview_list.html'
    context = {'interview_p': interview_p, 'interview_n': interview_n, 'interview_s': interview_s, 'scope': scope, 'intv_declined': intv_declined, 'vacancy_declined': vacancy_declined,}
    return render(request, template, context)


@login_required()
@subscription(2)
def WorkBidView(request, pk):
    detail = TalentRequired.objects.get(pk=pk)

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


@login_required()
@subscription(2)
def VacancyDetailView(request, pk):
    vacancy = TalentRequired.objects.filter(pk=pk)
    skills = SkillRequired.objects.filter(scope=pk)
    deliver = Deliverables.objects.filter(scope=pk)

    template = 'marketplace/vacancy_detail.html'
    context = {'vacancy': vacancy, 'skills': skills, 'deliver': deliver}
    return render(request, template, context)


@login_required()
@subscription(1)
def VacancyDetailView_Profile(request, pk):
    vacancy = TalentRequired.objects.filter(pk=pk)
    skills = SkillRequired.objects.filter(scope=pk)
    deliver = Deliverables.objects.filter(scope=pk)

    template = 'marketplace/vacancy_detail_profile.html'
    context = {'vacancy': vacancy, 'skills': skills, 'deliver': deliver}
    return render(request, template, context)


@login_required()
@subscription(2)
def AllPostedVacanciesView(request):
    #>>>Queryset caching
    tr = TalentRequired.objects.filter(requested_by=request.user)
    #Queryset caching<<<
    ipost = tr.order_by('-bid_open')

    template = 'marketplace/vacancy_posts_all.html'
    context ={
        'ipost': ipost,
        }
    return render(request, template, context)


@login_required()
def MarketHome(request):
    #>>>Queryset caching
    talent=request.user
    pfl = Profile.objects.filter(talent=talent)
    tr = TalentRequired.objects.all()
    trt = tr.filter(requested_by=talent)
    wb = WorkBid.objects.filter(work__requested_by=talent, work__offer_status__iexact='O')
    ta = TalentAvailabillity.objects.filter(talent=talent)
    we = WorkExperience.objects.filter(talent=talent).prefetch_related('topic')
    sr = SkillRequired.objects.filter(scope__offer_status__exact='O')
    sl = SkillLevel.objects.all()
    #Queryset caching<<<

    ipost = trt.filter(offer_status__iexact='O').order_by('-bid_open')[:5]
    ipost_closed = trt.filter(offer_status__iexact='C').order_by('-bid_open')[:5]
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

    req_experience = tr.filter(Q(experience_level__level=tlt_lvl) & Q(offer_status__iexact='O')).values_list('id',flat=True)

    match = []

    for key in req_experience:
        skill_required = sr.filter(scope=key).values_list('skills', flat=True).distinct()

        for sk in skill_required:
            match.append(sk)


    ds = sr.none()
    matchd = set(match) #remove duplicates

    for item in matchd:
        display = sr.filter(
                Q(skills__in=match)
                & Q(scope__bid_closes__gte=timezone.now()) & Q(scope__experience_level__level=tlt_lvl)
                )

        ds = ds | display

    dsd=ds.distinct('scope__title')

    already_applied = wb.values_list('work__id', flat=True).distinct()
    #Experience Level check & list skills required in vacancies<<<

    template = 'marketplace/vacancy_home.html'
    context ={
        'capacity': capacity, 'ipost': ipost, 'ipost_bid_flat': ipost_bid_flat, 'dsd': dsd, 'already_applied': already_applied, 'ipost_closed': ipost_closed}
    return render(request, template, context)


@login_required()
def VacanciesListView(request):
    #>>>Queryset caching
    talent=request.user
    pfl = Profile.objects.filter(talent=talent)
    tr = TalentRequired.objects.all()
    wb = WorkBid.objects.filter(work__requested_by=talent, work__offer_status__iexact='O')

    we = WorkExperience.objects.filter(talent=talent).prefetch_related('topic')
    sr = SkillRequired.objects.filter(scope__offer_status__exact='O')
    sl = SkillLevel.objects.all()

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

    req_experience = tr.filter(Q(experience_level__level=tlt_lvl) & Q(offer_status__iexact='O')).values_list('id',flat=True)

    match = []

    for key in req_experience:
        skill_required = sr.filter(scope=key).values_list('skills', flat=True).distinct()

        for sk in skill_required:
            match.append(sk)


    ds = sr.none()
    matchd = set(match) #remove duplicates

    for item in matchd:
        display = sr.filter(
                Q(skills__in=match)
                & Q(scope__bid_closes__gte=timezone.now()) & Q(scope__experience_level__level=tlt_lvl)
                )

        ds = ds | display

    dsd=ds.distinct('scope__title')

    already_applied = wb.values_list('work__id', flat=True).distinct()
    #Experience Level check & list skills required in vacancies<<<

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
        'pageitems': pageitems, 'already_applied': already_applied, 'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(2)
def ApplicationHistoryView(request):
    talent = request.user
    role = WorkBid.objects.filter(talent=talent).order_by('-date_applied')
    applied = role.filter(bidreview__exact='P')
    rejected = role.filter(bidreview__exact='R')
    accepted = role.filter(bidreview__exact='A')
    s_list = BidShortList.objects.filter(Q(talent=talent) & ~Q(status='A')).order_by('-date_listed')
    p_rejected = s_list.filter(status='R')
    p_accepted = s_list.filter(status='A')

    template = 'marketplace/vacancy_application_history.html'
    context ={
        'applied': applied, 'accepted': accepted, 'rejected': rejected, 'p_rejected': p_rejected, 'p_accepted': p_accepted, 's_list': s_list}
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
def VacancyPostView(request, pk):
    #>>>Queryset Cache
    instance = get_object_or_404(TalentRequired, pk=pk)
    skille = SkillRequired.objects.filter(scope=pk)
    delivere = Deliverables.objects.filter(scope=pk)
    applicants = WorkBid.objects.filter(work=pk)
    we = WorkExperience.objects.filter(talent__subscription__gte=1)
    s_list = BidShortList.objects.filter(scope=pk)
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

        slist = talent_skill + talent_skillt
        skillset = set(slist)
        skill_count = len(skillset)

        suitable[item]={'we':wetv, 'te':tetv,'s_no':skill_count, 'rb':rb, 'ro':rate}

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

    template = 'marketplace/vacancy_post_view.html'
    context = {'instance': instance, 'skille': skille, 'delivere': delivere, 'applicants': applicants, 'suitable': suitable, 'applied': applied, 's_list': s_list}
    return render(request, template, context)


@csp_exempt
@login_required()
def VacancySkillsAddView(request, pk):
    instance = get_object_or_404(TalentRequired, pk=pk)
    skill_list = SkillRequired.objects.filter(scope=pk)
    form = SkillRequiredForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.scope = instance
            new.save()
            if 'another' in request.POST:
                return redirect(reverse('MarketPlace:Skills', kwargs={'pk': pk}))
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
def VacancySkillsAdd2View(request, pk):
    instance = get_object_or_404(TalentRequired, pk=pk)
    skill_list = SkillRequired.objects.filter(scope=pk)
    form = SkillRequiredForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.scope = instance
            new.save()
            return redirect(reverse('MarketPlace:VacancyPost', kwargs={'pk': pk})+'#skills')
        else:
            template = 'marketplace/vacancy_skills2.html'
            context = {'form': form, 'instance': instance, 'skill_list': skill_list}
            return render(request, template, context)
    else:
        template = 'marketplace/vacancy_skills2.html'
        context = {'form': form, 'instance': instance, 'skill_list': skill_list}
        return render(request, template, context)


@login_required()
def SkillDeleteView(request, pk):
    if request.method == 'POST':
        skilld = SkillRequired.objects.get(pk=pk)
        skilld.delete()
        return redirect(reverse('MarketPlace:VacancyPost', kwargs={'pk':skilld.scope.id})+'#skills')


@login_required()
@subscription(2)
def AddToShortListView(request, s_list, tlt):
    job = get_object_or_404(TalentRequired, pk=s_list)
    talent = get_object_or_404(CustomUser, pk=tlt)
    if request.method == 'POST':
        b = BidShortList.objects.create(talent=talent, scope=job)

        if 'active' in request.POST:
            upd = WorkBid.objects.get(Q(talent=talent) & Q(work=job))
            upd.bidreview = 'S'
            upd.save()

        return redirect(reverse('MarketPlace:VacancyPost', kwargs={'pk':s_list})+'#suited')


@login_required()
@subscription(2)
def AddToInterviewListView(request, vac, tlt):
    job = get_object_or_404(TalentRequired, pk=vac)
    talent = get_object_or_404(CustomUser, pk=tlt)
    if request.method == 'POST':
        BidInterviewList.objects.create(talent=talent, scope=job)

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

        return redirect(reverse('MarketPlace:ShortListView', kwargs={'slv':vac}))


@login_required()
@subscription(2)
def TalentAssign(request, tlt, vac):
    job = get_object_or_404(TalentRequired, pk=vac)
    talent = get_object_or_404(CustomUser, pk=tlt)
    bids = WorkBid.objects.filter(work=vac)
    s_list = BidShortList.objects.filter(scope=vac)

    form = AssignWorkForm(request.POST or None)
    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = talent
            new.work = job
            new.save()

            s_list.filter(talent=talent).update(status='A')

            subs = list(Profile.objects.filter(talent=talent).values_list('talent__subscription', flat=True))
            subsi = subs[0]

            if subsi == 2:
                s = bids.get(talent=talent)
                s.bidreview ='A'
                s.save()

            #>>>email
            subject = f"WeXlog - Job assigned: {job.title} ({job.ref_no})"

            context = {'job': job, 'talent': talent}

            html_message = render_to_string('marketplace/email_vacancy_assign.html', context)
            plain_message = strip_tags(html_message)

            send_to = job.requested_by.email
            send_mail(subject, html_message, 'no-reply@wexlog.io', [send_to,])
            #template = 'marketplace/email_vacancy_assign.html'
            #return render(request, template, context)
            #<<<email

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('MarketPlace:Entrance')
            else:
                return HttpResponseRedirect(next_url)
        else:
            template = 'marketplace/vacancy_assign.html'
            context = {'form': form,}
            return render(request, template, context)
    else:
        template = 'marketplace/vacancy_assign.html'
        context = {'form': form,}
        return render(request, template, context)

@login_required()
@subscription(2)
def TalentDecline(request, tlt, vac):
    job = get_object_or_404(TalentRequired, pk=vac)
    talent = get_object_or_404(CustomUser, pk=tlt)
    bids = WorkBid.objects.filter(work=vac)
    s_list = BidShortList.objects.filter(scope=vac)

    if request.method == 'POST':
        WorkIssuedTo.objects.create(talent=talent, work=job)
        s_list.filter(talent=talent).update(status='A')

        #sets all status fields to "rejected"
        subs = list(Profile.objects.filter(talent=talent).values_list('talent__subscription', flat=True))
        subsi = subs[0]

        if subsi == 2:
            s = bids.get(talent=talent)
            s.bidreview ='R'
            s.save()

            bids.filter(~Q(bidreview='A')).update(bidreview='R')
            s_list.filter(status='S').update(status='R')

        else:
            bids.update(bidreview='R')
            s_list.filter(status='S').update(status='R')

    return redirect(reverse('MarketPlace:ShortListView',kwargs={'slv':'vac'}))


@login_required()
@subscription(2)
def ShortListView(request, slv):
    vacancy = get_object_or_404(TalentRequired, pk=slv)
    s_list = BidShortList.objects.filter(scope=slv)
    we = WorkExperience.objects.filter(talent__subscription__gte=1)
    applicants = WorkBid.objects.filter(work=slv)
    book = ReadBy.objects.all()

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

        applied = applicants.filter(talent=app)

        if applied:
            rate = applied.values_list('rate_bid', 'currency__currency_abv', 'rate_unit', 'motivation','talent__alias')
        else:
            rate = Profile.objects.filter(talent=app).values_list('std_rate', 'currency__currency_abv', 'rate_unit', 'motivation', 'alias')

        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        short[app]={'we':awetv, 'te':atetv,'s_no':askill_count, 'rb':rb, 'ro':rate}

    template = 'marketplace/shortlist_view.html'
    context = {'s_list': s_list, 'short': short, 'vacancy': vacancy}
    return render(request, template, context)


@login_required()
def DeliverablesEditView(request, pk):
    instance = get_object_or_404(Deliverables, pk=pk)
    form = DeliverablesForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return redirect(reverse('MarketPlace:VacancyPost', kwargs={'pk': instance.scope.id})+'#deliverables')
    else:
        template = 'marketplace/vacancy_deliverables_edit.html'
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


@login_required()
def DeliverablesAdd2View(request, pk):
    instance = get_object_or_404(TalentRequired, pk=pk)
    form = DeliverablesForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.scope = instance
            new.save()
            return redirect(reverse('MarketPlace:VacancyPost', kwargs={'pk': pk})+'#deliverables')
    else:
        template = 'marketplace/vacancy_deliverables_edit.html'
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


@login_required()
def DeliverableDeleteView(request, pk):
    if request.method == 'POST':
        deld = Deliverables.objects.get(pk=pk)
        deld.delete()
    return redirect(reverse('MarketPlace:VacancyPost', kwargs={'pk':deld.scope.id})+'#deliverables')


@login_required()
def DeliverablesAddView(request, pk):
    instance = get_object_or_404(TalentRequired, pk=pk)
    deliverable = Deliverables.objects.filter(scope=pk)
    form = DeliverablesForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.scope = instance
            new.save()
            if 'another' in request.POST:
                return redirect(reverse('MarketPlace:Deliverables', kwargs={'pk': pk}))
            elif 'done' in request.POST:
                return redirect(reverse('MarketPlace:Skills', kwargs={'pk': pk}))
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
            return redirect(reverse('MarketPlace:Deliverables', kwargs={'pk':new.id}))
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
def VacancyEditView(request, pk):
    instance=get_object_or_404(TalentRequired, pk=pk)

    if request.method == 'POST':
        form = TalentRequiredEditForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
            return redirect(reverse('MarketPlace:VacancyPost', kwargs={'pk':pk}))
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
