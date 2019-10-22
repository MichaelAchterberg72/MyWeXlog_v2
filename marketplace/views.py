from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
import json
from django.db.models import Count, Sum, F, Q
from django.utils import timezone
from decimal import Decimal

from csp.decorators import csp_exempt
from core.decorators import subscription

from .forms import (
        TalentAvailabillityForm, SkillRequiredForm, SkillLevelForm, DeliverablesForm, TalentRequiredForm, WorkLocationForm, WorkBidForm
)

from .models import(
    TalentRequired, SkillRequired, Deliverables, TalentAvailabillity, WorkBid, SkillLevel
)

from talenttrack.models import(
    WorkExperience, PreLoggedExperience, Education
)

from db_flatten.models import(
    SkillTag,
)


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
def MarketHome(request):
    #>>>Queryset caching
    talent=request.user
    tr = TalentRequired.objects.filter(offer_status__iexact='O')
    wb = WorkBid.objects.filter(work__requested_by=talent, work__offer_status__iexact='O')
    ta = TalentAvailabillity.objects.filter(talent=talent)
    we = WorkExperience.objects.all()
    pl = PreLoggedExperience.objects.all()
    me = Education.objects.all()
    sr = SkillRequired.objects.filter(scope__offer_status__exact='O')
    sl = SkillLevel.objects.all()
    #Queryset caching<<<

    ipost = tr.filter(requested_by=talent).order_by('-bid_open')[:5]
    ipost_bid = wb.filter(Q(bidreview__exact='R') | Q(bidreview__exact='P') | Q(bidreview__exact='A'))
    ipost_bid_flat = ipost_bid.values_list('work', flat=True).distinct()
    capacity = ta.filter(date_to__gte=timezone.now()).order_by('-date_to')[:5]

    #Code for stacked lookup for talent's skills

    #>>>summing all hours
    my_logged = we.filter(talent=talent).aggregate(myl=Sum('hours_worked'))
    my_prelogged = pl.filter(talent=talent).aggregate(mypl=Sum('hours_worked'))
    my_training = me.filter(talent=talent).prefetch_related('course')
    training_time = my_training.aggregate(mytr=Sum('topic__hours'))

    myli = my_logged.get('myl')
    mypli = my_prelogged.get('mypl')
    mytri = training_time.get('mytr')

    if myli:
        myli = myli
    else:
        myli = 0

    if mypli:
        mypli = mypli
    else:
        mypli = 0

    if mytri:
        mytri = mytri
    else:
        mytri = 0

    mye = myli+mypli+mytri
    myed = [Decimal(mye)]
    #Summing all hours<<<

    #>>>Create a set of all skills
    l_skill = we.only('pk').values_list('pk', flat=True)
    p_skill = pl.only("pk").values_list('pk', flat=True)

    skill_set = SkillTag.objects.none()

    for ls in l_skill:
        a = we.get(pk=ls)
        b = a.skills.all().values_list('skill', flat=True)

        skill_set = skill_set | b

    for ps in p_skill:
        c = pl.get(pk=ps)
        d = a.skills.all().values_list('skill', flat=True)

        skill_set = skill_set | d

    skill_set = skill_set.distinct().order_by('skill')
    #Create a set of all skills<<<

    #>>>Experience Level check & list skills required in vacancies
    std = list(sl.filter(level__exact=0).values_list('min_hours', flat=True))
    grd = list(sl.filter(level__exact=1).values_list('min_hours', flat=True))
    jnr = list(sl.filter(level__exact=2).values_list('min_hours', flat=True))
    int = list(sl.filter(level__exact=3).values_list('min_hours', flat=True))
    snr = list(sl.filter(level__exact=4).values_list('min_hours', flat=True))
    lead = list(sl.filter(level__exact=5).values_list('min_hours', flat=True))

    if myed <= grd:
        iama = 0
    elif myed >= grd and myed <= jnr:
        iama = 1
    elif myed >= jnr and myed <= int:
        iama = 2
    elif myed >= int and myed <= snr:
        iama = 3
    elif myed >= snr and myed <= lead:
        iama = 4
    elif myed >= lead:
        iama = 5

    req_experience = tr.filter(experience_level__level__exact=iama).values_list('id', flat=True)

    match = []

    for key in req_experience:
        skill_required = sr.filter(scope=key).values_list('skill', flat=True).distinct()

        for sk in skill_required:
            match.append(sk)

    ds = sr.none()
    matchd = set(match) #remove duplicates

    for item in matchd:
        display = sr.filter(
                Q(skill__in=match)
                & Q(scope__bid_closes__gte=timezone.now()
                ))

        ds = ds | display

    dsd=ds.distinct('scope__title')

    already_applied = wb.values_list('work__id', flat=True).distinct()
    #Experience Level check & list skills required in vacancies<<<



    template = 'marketplace/vacancy_home.html'
    context ={
        'capacity': capacity, 'ipost': ipost, 'ipost_bid_flat': ipost_bid_flat, 'dsd': dsd, 'already_applied': already_applied}
    return render(request, template, context)


@login_required()
@subscription(2)
def ApplicationHistoryView(request):
    role = WorkBid.objects.filter(talent=request.user).order_by('-date_applied')
    applied = role.filter(bidreview__exact='P')
    rejected = role.filter(bidreview__exact='R')
    accepted = role.filter(bidreview__exact='A')

    template = 'marketplace/vacancy_application_history.html'
    context ={
        'applied': applied, 'accepted': accepted, 'rejected': rejected}
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
@subscription(2)
def VacancyPostView(request, pk):
    #>>>Queryset Cache
    instance = get_object_or_404(TalentRequired, pk=pk)
    skille = SkillRequired.objects.filter(scope=pk)
    delivere = Deliverables.objects.filter(scope=pk)
    applicants = WorkBid.objects.filter(work=pk)
    we = WorkExperience.objects.filter(talent__subscription__gte=1)
    pl = PreLoggedExperience.objects.filter(talent__subscription__gte=1)
    me = Education.objects.filter(talent__subscription__gte=1)
    #Queryset Cache<<<

    #>>> List all skills required
    skill_r = skille.values_list('skill', flat=True).distinct()
    skill_rl = list(skill_r)
    print('skill_rl',skill_rl)
    #List all skills required<<<

    #>>> Find all talent with required skill
    wes = list(we.filter(skills__in=skill_r).distinct('talent').values_list('talent', flat=True))

    pls = list(pl.filter(skills__in=skill_r).distinct('talent').values_list('talent', flat=True))

    mes = list(me.filter(topic__skills__in=skill_r).distinct('talent').values_list('talent', flat=True))

    skill_a = set(wes+pls+mes)
    talent_qs = we.none()

    for t in skill_a:
        extract = we.filter(id=t)

        talent_qs = talent_qs | extract

    #Find all talent with required skill<<<
    skill_sum = {}
    talent_skill = {}
    for person in skill_a:
        wes = we.filter(talent=person)
        pls = pl.filter(talent=person)
        mes = me.filter(talent=person)
        for skr in skill_rl:
            wess= wes.filter(skills__in=[skr,]).aggregate(s_sk=Sum('hours_worked'))
            plss = pls.filter(skills__in=[skr,]).aggregate(p_sk=Sum('hours_worked'))
            mess = mes.filter(topic__skills__in=[skr,]).aggregate(m_sk=Sum('topic__hours'))

            wesse = wess.get('s_sk')
            plsse = plss.get('p_sk')
            messe = mess.get('m_sk')

            if wesse:
                wesse = wesse
            else:
                wesse=0

            if plsse:
                plsse = plsse
            else:
                plsse = 0

            if messe:
                messe = messe
            else:
                messe = 0

            skt = wesse + plsse + messe

            skill_sum[skr] = [skt]

        talent_skill[person] = [skill_sum]

    print('talent', talent_skill)

    weff = we.none()
    plff = pl.none()
    meff = me.none()
    e_dict = {}
    for person in skill_a:
        nme = we.filter(talent=person).values('talent__first_name')
        wef = we.filter(talent=person).aggregate(s_wef=Sum('hours_worked'))
        plf = pl.filter(talent=person).aggregate(s_plf=Sum('hours_worked'))
        mef = me.filter(talent=person).aggregate(s_mef=Sum('topic__hours'))

        wefg = wef.get('s_wef')
        plfg = plf.get('s_plf')
        mefg = mef.get('s_mef')

        if wefg:
            wefg = wefg
        else:
            wefg=0

        if plfg:
            plfg = plfg
        else:
            plfg = 0
        if mefg:
            mefg = mefg
        else:
            mefg = 0

        skfg = wefg + plfg + mefg
        nmed = nme.distinct('talent')
        e_dict[nmed] = [skfg]

    print(e_dict)



    #weffs = weff.annotate(wsum=Sum('hours_worked'))

    #2. Display result


    template = 'marketplace/vacancy_post_view.html'
    context = {'instance': instance, 'skille': skille, 'delivere': delivere, 'applicants': applicants, 'talent_qs': talent_qs}
    return render(request, template, context)



@login_required()
def VacancySkillsAddView(request, pk):
    instance = get_object_or_404(TalentRequired, pk=pk)
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
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


@login_required()
def VacancySkillsAdd2View(request, pk):
    instance = get_object_or_404(TalentRequired, pk=pk)
    form = SkillRequiredForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.scope = instance
            new.save()
            return redirect(reverse('MarketPlace:VacancyPost', kwargs={'pk': pk})+'#skills')
    else:
        template = 'marketplace/vacancy_skills2.html'
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


@login_required()
def SkillDeleteView(request, pk):
    if request.method == 'POST':
        skilld = SkillRequired.objects.get(pk=pk)
        skilld.delete()
        return redirect(reverse('MarketPlace:VacancyPost', kwargs={'pk':skilld.scope.id})+'#skills')


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
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


@login_required()
@csp_exempt
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


@login_required()
@csp_exempt
@subscription(2)
def VacancyEditView(request, pk):
    instance=get_object_or_404(TalentRequired, pk=pk)

    if request.method == 'POST':
        form = TalentRequiredForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            new = form.save(commit=False)
            new.requested_by=request.user
            new.save()
            form.save_m2m()
            return redirect(reverse('MarketPlace:VacancyPost', kwargs={'pk':pk}))
    else:
        form = TalentRequiredForm(instance=instance)

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
