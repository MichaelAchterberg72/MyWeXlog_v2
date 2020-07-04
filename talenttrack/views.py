from django.shortcuts import(
    render, get_object_or_404, redirect, render_to_response
    )
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import PermissionDenied
import json
from django.db.models import Count, Sum, Q, F
from django.db.models.functions import Greatest
from decimal import Decimal
from django.contrib.postgres.search import SearchVector, TrigramSimilarity


from csp.decorators import csp_exempt
from core.decorators import subscription
from WeXlog.app_config import(
        client_score, lecturer_score, classmate_score, colleague_score, pre_colleague_score, collaborator_score, superior_score
        )


from .forms import (
        TopicForm, ResultForm, CourseTypeForm, CourseForm, DesignationForm, ClassMatesSelectForm, ClassMatesConfirmForm, LecturerSelectForm, LecturerConfirmForm, EducationForm, WorkExperienceForm, WorkColleagueSelectForm, WorkColleagueConfirmForm, WorkColleagueResponseForm, ClassMatesResponseForm, LecturerResponseForm, SuperiorSelectForm, WorkCollaboratorResponseForm, WorkCollaboratorConfirmForm, WorkCollaboratorSelectForm, WorkClientResponseForm, WorkClientConfirmForm, WorkClientSelectForm, PreLoggedExperienceForm, TopicPopForm, LecturerRespondForm, ClassMatesRespondForm, AchievementsForm, LicenseCertificationForm, ProfileSearchForm,
)

from .models import (
        Lecturer, Course, ClassMates, WorkExperience, Superior, WorkCollaborator, WorkClient, WorkColleague, Designation, Achievements, LicenseCertification,
)

from db_flatten.models import SkillTag
from marketplace.models import(
    SkillLevel, SkillRequired, WorkBid, BidShortList, TalentRequired, BidInterviewList,
)
from enterprises.models import Branch
from project.models import ProjectData
from Profile.models import (
        BriefCareerHistory, Profile, LanguageTrack, PhysicalAddress
)
from booklist.models import ReadBy
from users.models import CustomUser

from WeXlog.app_config import (
    skill_pass_score, locked_age,
)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from analytics.signals import object_viewed_signal


@login_required()
def ExperienceHome(request):
    '''The view for the main page for Talenttrack app'''
    #>>>Step 1
    basequery = WorkExperience.objects.select_related('topic').filter(talent=request.user)
    skills = SkillTag.objects.all()
    sl = SkillLevel.objects.all()
    we_c = basequery.filter(score__gte=skill_pass_score)
    #<<<Step 1

    talent = request.user
    tlt = talent.alias

    #>>>Step 2
    #unconfirmed
    train_base = basequery.filter(Q(edt=True)).order_by('-date_from')
    train_sum = train_base.aggregate(Edu_sum=Sum('topic__hours'))
    train_count = train_base.count()
    train = train_base[:5]
    #Confirmed
    train_c = train_base.filter(Q(score__gte=skill_pass_score))
    train_sum_c = train_c.aggregate(Edu_sumc=Sum('topic__hours'))
    train_count_c = train_c.count()

    #unconfirmed
    exp_base = basequery.filter(wexp=True).order_by('-date_from')
    exp_sum = exp_base.aggregate(we_sum=Sum('hours_worked'))
    exp_count = exp_base.count()
    experience = exp_base[:5]
    #Confirmed
    exp_c = exp_base.filter(Q(score__gte=skill_pass_score))
    exp_sum_c = exp_c.aggregate(we_sumc=Sum('hours_worked'))
    exp_count_c = exp_c.count()

    #unconfirmed
    pre_base = basequery.filter(prelog=True).order_by('-date_from')
    prelog = pre_base[:5]
    pre_sum = pre_base.aggregate(p_sum=Sum('hours_worked'))
    pre_count = pre_base.count()
    #Confirmed
    pre_c = pre_base.filter(Q(score__gte=skill_pass_score))
    pre_sum_c = pre_c.aggregate(p_sumc=Sum('hours_worked'))
    pre_count_c = pre_c.count()

    #UNCONFIRMED
    t_sum = train_sum.get('Edu_sum')
    e_sum = exp_sum.get('we_sum')
    p_sum= pre_sum.get('p_sum')


    if t_sum:
        t_sum = t_sum
    else:
        t_sum=0

    if e_sum:
        e_sum = e_sum
    else:
        e_sum = 0

    if p_sum:
        p_sum = p_sum
    else:
        p_sum = 0

    tot_sum = t_sum + e_sum + p_sum

    #CONFIRMED
    t_sum_c = train_sum_c.get('Edu_sumc')
    e_sum_c = exp_sum_c.get('we_sumc')
    p_sum_c= pre_sum_c.get('p_sumc')


    if t_sum_c:
        t_sum_c = t_sum_c
    else:
        t_sum_c=0

    if e_sum_c:
        e_sum_c = e_sum_c
    else:
        e_sum_c = 0

    if p_sum_c:
        p_sum_c = p_sum_c
    else:
        p_sum_c = 0

    tot_sum_c = t_sum_c + e_sum_c + p_sum_c
    exp_lvls = [Decimal(e_sum_c + p_sum_c)]

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

    level = sl.get(level=iama)

    Profile.objects.filter(talent=request.user.id).update(exp_lvl=level)

    #<<<Step 2

    #>>>Step 3
    e_skill = basequery.filter(edt=True).values_list('topic__skills', flat=True)
    l_skill = basequery.filter(edt=False).values_list('skills', flat=True)

    e_skill_l = list(e_skill)
    l_skill_l = list(l_skill)

    skill_list = e_skill_l + l_skill_l
    skill_set = set(skill_list)
    skill_count = len(skill_set)


    skill_name = skills.none()

    for ls in skill_set:
        b = skills.filter(pk=ls).values_list('skill', flat=True)

        skill_name = skill_name | b
    #<<< Step 3

    #>>> Summary of confirmation activity
    #>>> As Confirmer
    edu_lect = Lecturer.objects.filter(lecturer=talent)
    edu_lect_r = edu_lect.filter(confirm="R").count()
    edu_lect_c = edu_lect.filter(confirm="C").count()
    edu_lect_s = edu_lect.filter(confirm="S").count()
    edu_lect_y = edu_lect.filter(confirm="Y").count()

    edu_cm = ClassMates.objects.filter(colleague=talent)
    edu_cm_r = edu_cm.filter(confirm="R").count()
    edu_cm_c = edu_cm.filter(confirm="C").count()
    edu_cm_s = edu_cm.filter(confirm="S").count()
    edu_cm_y = edu_cm.filter(confirm="Y").count()

    exp_clg = WorkColleague.objects.filter(colleague_name=talent)
    exp_clg_r = exp_clg.filter(confirm="R").count()
    exp_clg_c = exp_clg.filter(confirm="C").count()
    exp_clg_s = exp_clg.filter(confirm="S").count()
    exp_clg_y = exp_clg.filter(confirm="Y").count()

    exp_sup = Superior.objects.filter(superior_name=talent)
    exp_sup_r = exp_sup.filter(confirm="R").count()
    exp_sup_c = exp_sup.filter(confirm="C").count()
    exp_sup_s = exp_sup.filter(confirm="S").count()
    exp_sup_y = exp_sup.filter(confirm="Y").count()

    exp_clt = WorkClient.objects.filter(client_name=talent)
    exp_clt_r = exp_clt.filter(confirm="R").count()
    exp_clt_c = exp_clt.filter(confirm="C").count()
    exp_clt_s = exp_clt.filter(confirm="S").count()
    exp_clt_y = exp_clt.filter(confirm="Y").count()

    exp_cbr = WorkCollaborator.objects.filter(collaborator_name=talent)
    exp_cbr_r = exp_cbr.filter(confirm="R").count()
    exp_cbr_c = exp_cbr.filter(confirm="C").count()
    exp_cbr_s = exp_cbr.filter(confirm="S").count()
    exp_cbr_y = exp_cbr.filter(confirm="Y").count()
    #As Confirmer<<<

    #>>>As Requestioner
    edu_req_lect = Lecturer.objects.filter(education__talent=talent)
    edu_req_lect_r = edu_req_lect.filter(confirm="R").count()
    edu_req_lect_c = edu_req_lect.filter(confirm="C").count()
    edu_req_lect_s = edu_req_lect.filter(confirm="S").count()
    edu_req_lect_y = edu_req_lect.filter(confirm="Y").count()

    edu_req_cm = ClassMates.objects.filter(education__talent=talent)
    edu_req_cm_r = edu_req_cm.filter(confirm="R").count()
    edu_req_cm_c = edu_req_cm.filter(confirm="C").count()
    edu_req_cm_s = edu_req_cm.filter(confirm="S").count()
    edu_req_cm_y = edu_req_cm.filter(confirm="Y").count()

    exp_req_clg = WorkColleague.objects.filter(experience__talent=talent)
    exp_req_clg_r = exp_req_clg.filter(confirm="R").count()
    exp_req_clg_c = exp_req_clg.filter(confirm="C").count()
    exp_req_clg_s = exp_req_clg.filter(confirm="S").count()
    exp_req_clg_y = exp_req_clg.filter(confirm="Y").count()

    exp_req_sup = Superior.objects.filter(experience__talent=talent)
    exp_req_sup_r = exp_req_sup.filter(confirm="R").count()
    exp_req_sup_c = exp_req_sup.filter(confirm="C").count()
    exp_req_sup_s = exp_req_sup.filter(confirm="S").count()
    exp_req_sup_y = exp_req_sup.filter(confirm="Y").count()

    exp_req_clt = WorkClient.objects.filter(experience__talent=talent)
    exp_req_clt_r = exp_req_clt.filter(confirm="R").count()
    exp_req_clt_c = exp_req_clt.filter(confirm="C").count()
    exp_req_clt_s = exp_req_clt.filter(confirm="S").count()
    exp_req_clt_y = exp_req_clt.filter(confirm="Y").count()

    exp_req_cbr = WorkCollaborator.objects.filter(experience__talent=talent)
    exp_req_cbr_r = exp_req_cbr.filter(confirm="R").count()
    exp_req_cbr_c = exp_req_cbr.filter(confirm="C").count()
    exp_req_cbr_s = exp_req_cbr.filter(confirm="S").count()
    exp_req_cbr_y = exp_req_cbr.filter(confirm="Y").count()
    #As Requestioner<<<
    #Summary of confirmation activity<<<


    template = 'talenttrack/track_home.html'
    context = {
        'tlt': tlt,
        'train': train,
        'train_sum': train_sum,
        'train_sum_c': train_sum_c,
        'train_count_c': train_count_c,
        'train_count': train_count,
        'experience': experience,
        'exp_sum': exp_sum,
        'exp_sum_c': exp_sum_c,
        'exp_count': exp_count,
        'exp_count_c': exp_count_c,
        'prelog': prelog,
        'pre_sum': pre_sum,
        'pre_count': pre_count,
        'pre_sum_c': pre_sum_c,
        'pre_count_c': pre_count_c,
        'tot_sum': tot_sum,
        'tot_sum_c': tot_sum_c,
        'skill_name': skill_name,
        'skill_count': skill_count,
        'level': level,
        'edu_lect': edu_lect, 'edu_lect_r': edu_lect_r, 'edu_lect_c': edu_lect_c, 'edu_lect_s': edu_lect_s, 'edu_lect_y': edu_lect_y,
        'edu_cm': edu_cm, 'edu_cm_r': edu_cm_r, 'edu_cm_c': edu_cm_c, 'edu_cm_s': edu_cm_s, 'edu_cm_y': edu_cm_y,
        'exp_clg': exp_clg, 'exp_clg_c': exp_clg_c, 'exp_clg_r': exp_clg_r, 'exp_clg_s': exp_clg_s, 'exp_clg_y': exp_clg_y,
        'exp_sup': exp_sup, 'exp_sup_c': exp_sup_c, 'exp_sup_r': exp_sup_r, 'exp_sup_s': exp_sup_s, 'exp_sup_y': exp_sup_y,
        'exp_clt': exp_clt, 'exp_clt_c': exp_clt_c, 'exp_clt_r': exp_clt_r, 'exp_clt_s': exp_clt_s, 'exp_clt_y': exp_clt_y,
        'exp_cbr': exp_cbr, 'exp_cbr_c': exp_cbr_c, 'exp_cbr_r': exp_cbr_r, 'exp_cbr_s': exp_cbr_s, 'exp_cbr_y': exp_cbr_y,
        'edu_req_lect': edu_req_lect, 'edu_req_lect_r': edu_req_lect_r, 'edu_req_lect_c': edu_req_lect_c, 'edu_req_lect_s': edu_req_lect_s, 'edu_req_lect_y': edu_req_lect_y,
        'edu_req_cm': edu_req_cm, 'edu_req_cm_r': edu_req_cm_r, 'edu_req_cm_c': edu_req_cm_c, 'edu_req_cm_s': edu_req_cm_s, 'edu_req_cm_y': edu_req_cm_y,
        'exp_req_clg': exp_req_clg, 'exp_req_clg_c': exp_req_clg_c, 'exp_req_clg_r': exp_req_clg_r, 'exp_req_clg_s': exp_req_clg_s, 'exp_req_clg_y': exp_req_clg_y,
        'exp_req_sup': exp_req_sup, 'exp_req_sup_c': exp_req_sup_c, 'exp_req_sup_r': exp_req_sup_r, 'exp_req_sup_s': exp_req_sup_s, 'exp_req_sup_y': exp_req_sup_y,
        'exp_req_clt': exp_req_clt, 'exp_req_clt_c': exp_req_clt_c, 'exp_req_clt_r': exp_req_clt_r, 'exp_req_clt_s': exp_req_clt_s, 'exp_req_clt_y': exp_req_clt_y,
        'exp_req_cbr': exp_req_cbr, 'exp_req_cbr_c': exp_req_cbr_c, 'exp_req_cbr_r': exp_req_cbr_r, 'exp_req_cbr_s': exp_req_cbr_s, 'exp_req_cbr_y': exp_req_cbr_y,
    }
    return render(request, template, context)


@login_required()
@subscription(2)
def profile_search(request):
    form = ProfileSearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = ProfileSearchForm(request.GET)
        if form.is_valid():
            query=form.cleaned_data['query']
            results = Profile.objects.annotate(similarity=Greatest(
                TrigramSimilarity('alias', query),
                TrigramSimilarity('f_name', query),
                TrigramSimilarity('l_name', query),
                )).filter(similarity__gt=0.3).order_by('-similarity')

    template = 'talenttrack/profile_search_results.html'
    context = {'form': form, 'query': query, 'results': results,}
    return render(request, template, context)


@login_required()
def lecturer_conf_summary_list(request):
    '''Confirmations the logged-in user has received'''
    tlt = request.user
    lect_qs = Lecturer.objects.filter(lecturer=tlt)
    lect_qs_unlocked = lect_qs.filter(Q(locked=False) & ~Q(confirm="S"))

    today = timezone.now().date()

    for item in lect_qs_unlocked:
        age = (today - item.date_confirmed).days
        if age > locked_age:
            item.locked = True
            item.save()
        else:
            pass
    lect_qs = Lecturer.objects.filter(lecturer=tlt).order_by('-date_confirmed').order_by('-confirm')

    template = 'talenttrack/confirm_edu_lect_list.html'
    context = {'lect_qs': lect_qs, 'age': locked_age,}
    return render(request, template, context)


@login_required()
def classmate_conf_summary_list(request):
    '''Confirmations the logged-in user has received'''
    tlt = request.user
    cm_qs = ClassMates.objects.filter(colleague=tlt)
    cm_qs_unlocked = cm_qs.filter(Q(locked=False) & ~Q(confirm="S"))

    today = timezone.now().date()

    for item in cm_qs_unlocked:
        age = (today - item.date_confirmed).days
        if age > locked_age:
            item.locked = True
            item.save()
        else:
            pass

    cm_qs = ClassMates.objects.filter(colleague=tlt).order_by('-date_confirmed').order_by('-confirm')

    template = 'talenttrack/confirm_edu_cm_list.html'
    context = {'cm_qs': cm_qs, 'age': locked_age,}
    return render(request, template, context)


@login_required()
def colleague_conf_summary_list(request):
    '''Confirmations the logged-in user has received'''
    tlt = request.user
    clg_c_qs = WorkColleague.objects.filter(colleague_name=tlt)
    clg_c_qs_unlocked = clg_c_qs.filter(Q(locked=False) & ~Q(confirm="S"))

    today = timezone.now().date()

    for item in clg_c_qs_unlocked:
        age = (today - item.date_confirmed).days
        if age > locked_age:
            item.locked = True
            item.save()
        else:
            pass

    clg_c_qs = WorkColleague.objects.filter(colleague_name=tlt).order_by('-date_confirmed').order_by('-confirm')

    template = 'talenttrack/confirm_exp_clg_list.html'
    context = {'clg_c_qs': clg_c_qs, 'age': locked_age,}
    return render(request, template, context)


@login_required()
def superior_conf_summary_list(request):
    '''Confirmations the logged-in user has received'''
    tlt = request.user
    sup_c_qs = Superior.objects.filter(superior_name=tlt)
    sup_c_qs_unlocked = sup_c_qs.filter(Q(locked=False) & ~Q(confirm="S"))

    today = timezone.now().date()

    for item in sup_c_qs_unlocked:
        age = (today - item.date_confirmed).days
        if age > locked_age:
            item.locked = True
            item.save()
        else:
            pass

    sup_c_qs = Superior.objects.filter(superior_name=tlt).order_by('-date_confirmed').order_by('-confirm')

    template = 'talenttrack/confirm_exp_sup_list.html'
    context = {'sup_c_qs': sup_c_qs, 'age': locked_age,}
    return render(request, template, context)


@login_required()
def collaborator_conf_summary_list(request):
    '''Confirmations the logged-in user has received'''
    tlt = request.user
    clb_c_qs = WorkCollaborator.objects.filter(collaborator_name=tlt)
    clb_c_qs_unlocked = clb_c_qs.filter(Q(locked=False) & ~Q(confirm="S"))

    today = timezone.now().date()

    for item in clb_c_qs_unlocked:
        age = (today - item.date_confirmed).days
        if age > locked_age:
            item.locked = True
            item.save()
        else:
            pass

    clb_c_qs = WorkCollaborator.objects.filter(collaborator_name=tlt).order_by('-date_confirmed').order_by('-confirm')

    template = 'talenttrack/confirm_exp_clb_list.html'
    context = {'clb_c_qs': clb_c_qs, 'age': locked_age,}
    return render(request, template, context)


@login_required()
def client_conf_summary_list(request):
    '''Confirmations the logged-in user has received'''
    tlt = request.user
    clt_c_qs = WorkClient.objects.filter(client_name=tlt)
    clt_c_qs_unlocked = clt_c_qs.filter(Q(locked=False) & ~Q(confirm="S"))

    today = timezone.now().date()

    for item in clt_c_qs_unlocked:
        age = (today - item.date_confirmed).days
        if age > locked_age:
            item.locked = True
            item.save()
        else:
            pass

    clt_c_qs = WorkClient.objects.filter(client_name=tlt).order_by('-date_confirmed').order_by('-confirm')

    template = 'talenttrack/confirm_exp_clt_list.html'
    context = {'clt_c_qs': clt_c_qs, 'age': locked_age,}
    return render(request, template, context)


@login_required()
def lect_req_list(request):
    '''Filters for the view where all requests for lecturer are listed'''
    talent = request.user
    edu_req_lect = Lecturer.objects.filter(education__talent=talent).order_by('-date_confirmed').order_by('-confirm')

    template = 'talenttrack/request_lect_list.html'
    context = {'edu_req_lect': edu_req_lect,}
    return render(request, template, context)


@login_required()
def cm_req_list(request):
    '''Filters for the view where all requests for classmate are listed'''
    talent = request.user
    edu_req_cm = ClassMates.objects.filter(education__talent=talent).order_by('-date_confirmed').order_by('-confirm')

    template = 'talenttrack/request_cm_list.html'
    context = {'edu_req_cm': edu_req_cm,}
    return render(request, template, context)


@login_required()
def clg_req_list(request):
    '''Filters for the view where all requests to colleagues are listed'''
    talent = request.user
    exp_req_clg = WorkColleague.objects.filter(experience__talent=talent).order_by('-date_confirmed').order_by('-confirm')

    template = 'talenttrack/request_clg_list.html'
    context = {'exp_req_clg': exp_req_clg,}
    return render(request, template, context)


@login_required()
def sup_req_list(request):
    '''Filters for the view where all requests to superiors are listed'''
    talent = request.user
    exp_req_sup = Superior.objects.filter(experience__talent=talent).order_by('-date_confirmed').order_by('-confirm')

    template = 'talenttrack/request_sup_list.html'
    context = {'exp_req_sup': exp_req_sup,}
    return render(request, template, context)


@login_required()
def clt_req_list(request):
    '''Filters for the view where all requests to clients are listed'''
    talent = request.user
    exp_req_clt = WorkClient.objects.filter(experience__talent=talent).order_by('-date_confirmed').order_by('-confirm')

    template = 'talenttrack/request_clt_list.html'
    context = {'exp_req_clt': exp_req_clt,}
    return render(request, template, context)


@login_required()
def clb_req_list(request):
    '''Filters for the view where all requests to collaborators are listed'''
    talent = request.user
    exp_req_clb = WorkCollaborator.objects.filter(experience__talent=talent).order_by('-date_confirmed').order_by('-confirm')

    template = 'talenttrack/request_clb_list.html'
    context = {'exp_req_clb': exp_req_clb,}
    return render(request, template, context)


@login_required()
def HelpExperienceHomeView(request):
    template_name = 'talenttrack/help_experience_home.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpExperienceEducationView(request):
    template_name = 'talenttrack/help_experience_education.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpExperienceExperienceView(request):
    template_name = 'talenttrack/help_experience_experience.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpExperiencePreExperienceView(request):
    template_name = 'talenttrack/help_experience_pre_experience.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpCaptrueEducationView(request):
    template_name = 'talenttrack/help_capture_education.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpCaptrueExperienceView(request):
    template_name = 'talenttrack/help_capture_experience.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpHowCaptrueSkillsView(request):
    template_name = 'talenttrack/help_how_to_capture_skills.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def TrainingListView(request):
    basequery = WorkExperience.objects.select_related('topic').filter(talent=request.user)

    train = basequery.filter(edt=True).order_by('-date_from')
    train_sum = train.aggregate(Edu_sum=Sum('topic__hours'))
    train_count = train.count()

    t_sum = train_sum.get('Edu_sum')

    if t_sum:
        t_sum = t_sum
    else:
        t_sum=0

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(train, 20)

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

    template = 'talenttrack/training_list.html'
    context = {
        'train_sum': train_sum,
        'train_count': train_count,
        'pageitems': pageitems,
        'page_range': page_range
    }
    return render(request, template, context)


@login_required()
def PreExperienceListView(request):
    basequery = WorkExperience.objects.select_related('topic').filter(talent=request.user)

    prelog = basequery.filter(prelog=True).order_by('-date_from')
    pre_sum = prelog.aggregate(p_sum=Sum('hours_worked'))
    pre_count = prelog.count()

    p_sum= pre_sum.get('p_sum')

    if p_sum:
        p_sum = p_sum
    else:
        p_sum = 0

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(prelog, 20)

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

    template = 'talenttrack/pre_experience_list.html'
    context = {
        'pre_sum': pre_sum,
        'pre_count': pre_count,
        'pageitems': pageitems,
        'page_range': page_range
    }
    return render(request, template, context)


@login_required()
def WorkExperienceListView(request):
    basequery = WorkExperience.objects.select_related('topic').filter(talent=request.user)

    experience = basequery.filter(wexp=True).order_by('-date_from')
    exp_sum = experience.aggregate(we_sum=Sum('hours_worked'))
    exp_count = experience.count()

    e_sum = exp_sum.get('we_sum')

    if e_sum:
        e_sum = e_sum
    else:
        e_sum = 0

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(experience, 20)

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

    template = 'talenttrack/experience_list.html'
    context = {
        'exp_sum': exp_sum,
        'exp_count': exp_count,
        'pageitems': pageitems,
        'page_range': page_range
    }
    return render(request, template, context)


@login_required()
def CaptureAchievementView(request):
    pfl = get_object_or_404(CustomUser, pk=request.user.id)
    form = AchievementsForm(request.POST or None)

    if request.method == 'POST':
        new = form.save(commit=False)
        new.talent = pfl
        new.save()
        return redirect(reverse('Profile:ProfileView', kwargs={'tlt':pfl.alias})+'#achievements')
    else:
        template = 'talenttrack/achievement_capture.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def EditAchievementView(request, ach):
    instance = get_object_or_404(Achievements, slug=ach)

    form = AchievementsForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        new = form.save(commit=False)
        new.save()
        return redirect(reverse('Profile:ProfileView', kwargs={'tlt': instance.talent.alias})+'#achievements')
    else:
        template = 'talenttrack/achievement_capture.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def DeleteAchievementView(request, ach_i, tlt):
    info = Achievements.objects.get(pk=ach_i)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Profile:ProfileView', kwargs={'tlt': tlt})+'#achievements')
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def LicenseCertificationCaptureView(request):
    tlt_i = get_object_or_404(CustomUser, pk=request.user.id)
    form = LicenseCertificationForm(request.POST or None)

    if form.is_valid():
        new = form.save(commit=False)
        new.talent = tlt_i
        new.save()
        return redirect(reverse ('Profile:ProfileView', kwargs={'tlt':tlt_i.alias})+'#memberships')
    else:
        template = 'talenttrack/membership_view.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
@csp_exempt
def LicenseCertificationEditView(request, lcm):
    lcm_i = LicenseCertification.objects.get(slug=lcm)
    form = LicenseCertificationForm(request.POST or None, instance=lcm_i)

    if form.is_valid():
        edit = form.save(commit=False)
        edit.save()
        return redirect(reverse ('Profile:ProfileView', kwargs={'tlt':lcm_i.talent.alias})+'#memberships')
    else:
        template = 'talenttrack/membership_view.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def LicenseCertificationDeleteView(request, pk, tlt):
    lcm = LicenseCertification.objects.get(pk=pk)
    if lcm.talent == request.user:
        if request.method =='POST':
            lcm.delete()
            return redirect(reverse('Profile:ProfileView', kwargs={'tlt':tlt})+'#memberships')
    else:
        raise PermissionDenied


def TltRatingDetailView(request, tlt):
    pfl = Profile.objects.get(alias=tlt)

    r_1 = pfl.rate_1/100
    r_2 = pfl.rate_2/100
    r_3 = pfl.rate_3/100

    template = 'talenttrack/rating_detail_tlt.html'
    context = {'pfl': pfl, 'r_1': r_1, 'r_2': r_2, 'r_3': r_3,}
    return render(request, template, context)


@login_required()
def ActiveProfileView(request, tlt, vac):
    '''View for profile and skills for specified vacancy'''
    #caching
    bch = BriefCareerHistory.objects.filter(talent__alias=tlt).order_by('-date_from')
    pfl = Profile.objects.filter(alias=tlt).first()
    als = get_object_or_404(Profile, alias=tlt)
    padd = PhysicalAddress.objects.only('country', 'region', 'city').get(talent__alias=tlt)
    vacancy = TalentRequired.objects.filter(ref_no=vac)
    skr = SkillRequired.objects.filter(scope__ref_no=vac).values_list('skills', flat=True).distinct('skills')
    skill_qs = SkillTag.objects.all()
    exp = WorkExperience.objects.filter(talent__alias=tlt).select_related('topic', 'course', 'project')
    edtexp = exp.filter(edt=True).order_by('-date_from')
    bkl = ReadBy.objects.filter(talent__alias=tlt).select_related('book', 'type')[:6]
    bkl_count = bkl.count()
    prj_qs = ProjectData.objects.all()
    bid_qs = WorkBid.objects.filter(Q(talent__alias=tlt) & Q(work__ref_no=vac))
    achievement_qs = Achievements.objects.filter(talent__alias=tlt).order_by('-date_achieved')
    language_qs = LanguageTrack.objects.filter(talent__alias=tlt).order_by('-language')
    membership_qs = LicenseCertification.objects.filter(talent__alias=tlt).order_by('-issue_date')
    bslist_qs = BidShortList.objects.filter(Q(talent__alias=tlt) & Q(scope__ref_no=vac))
    int_list = BidInterviewList.objects.filter(Q(talent__alias=tlt) & Q(scope__ref_no=vac))

    #Project Summary
    prj = exp.values_list('project', flat=True).distinct('project')
    prj_set = {}
    prj_count = 0
    for p in prj:
        if p == None:
            pass
        else:
            prj_count +=1
            project_q = prj_qs.filter(pk=p).values_list('name', 'company__name', 'companybranch__name', 'industry__industry')
            info_list=[project_q[0][1], project_q[0][2], project_q[0][3]]
            prj_set[project_q[0][0]] = info_list

    #experience hours on skills required
    vacse_set = {}
    pst = exp.only('skills').values_list('skills', flat=True).distinct('skills')

    for s in skr:
        #populating the keys
        skill_q = skill_qs.filter(pk=s).values_list('skill', flat=True)
        skill_f = skill_q[0]
        vacse_set[skill_f]=float(0)
        if s in pst:
            #populating the values
            d = skill_qs.get(pk=s)
            e = d.experience.filter(talent__alias=tlt)
            e_sum = e.aggregate(sum_t=Sum('hours_worked'))
            sum_float = float(e_sum.get('sum_t'))
            if vacse_set[skill_f]:
                new = vacse_set[skill_f]+sum_float
                vacse_set[skill_f]=new
            else:
                vacse_set[skill_f] = sum_float
        else:
            pass

    #Training hours on skills required
    vacst_set = {}
    edt = exp.only('topic__skills').values_list('topic__skills', flat=True).distinct('topic__skills')
    edc = exp.only('topic').values_list('topic', flat=True).distinct('topic')
    #populating the keys
    for s in skr:
        #populating the set
        skill_q = skill_qs.filter(pk=s).values_list('skill', flat=True)
        skill_f = skill_q[0]
        vacst_set[skill_f]=float(0)
        if s in edt:
            #populating the values
            for t in edc:
                d = skill_qs.get(pk=s)
                e = d.topic_set.filter(topic=t)
                e_sum = e.aggregate(sum_t=Sum('hours'))
                sum_float = e_sum.get('sum_t')
                if sum_float is None:
                    sum_float = float(0)
                else:
                    sum_float = float(sum_float)
                if vacst_set[skill_f]:
                    new = vacst_set[skill_f]+sum_float
                    vacst_set[skill_f]=new
                else:
                    vacst_set[skill_f] = sum_float
        else:
            pass

    object_viewed_signal.send(pfl.__class__, instance=pfl, request=request)


    template = 'talenttrack/active_profile_view.html'
    context = {
        'bch': bch, 'pfl': pfl, 'padd': padd,'vacse_set': vacse_set, 'vacst_set': vacst_set, 'exp': exp, 'bkl': bkl, 'edtexp': edtexp, 'bkl_count': bkl_count, 'prj_set': prj_set, 'prj_count': prj_count, 'bid_qs': bid_qs, 'achievement_qs': achievement_qs, 'language_qs': language_qs, 'membership_qs': membership_qs, 'bslist_qs': bslist_qs, 'vacancy': vacancy, 'int_list': int_list, 'als': als,
        }
    return render(request, template, context)


@login_required()
def profile_view(request, tlt):
    '''View for profile without reference to a vacancy. Used for the seach feature'''
    #caching
    bch = BriefCareerHistory.objects.filter(talent__alias=tlt).order_by('-date_from')
    pfl = Profile.objects.filter(alias=tlt).first()
    als = get_object_or_404(Profile, alias=tlt)
    padd = PhysicalAddress.objects.only('country', 'region', 'city').get(talent__alias=tlt)
    skill_qs = SkillTag.objects.all()
    exp = WorkExperience.objects.filter(talent__alias=tlt).select_related('topic', 'course', 'project')
    edtexp = exp.filter(edt=True).order_by('-date_from')
    bkl = ReadBy.objects.filter(talent__alias=tlt).select_related('book', 'type')[:6]
    bkl_count = bkl.count()
    prj_qs = ProjectData.objects.all()
    achievement_qs = Achievements.objects.filter(talent__alias=tlt).order_by('-date_achieved')
    language_qs = LanguageTrack.objects.filter(talent__alias=tlt).order_by('-language')
    membership_qs = LicenseCertification.objects.filter(talent__alias=tlt).order_by('-issue_date')

    #Project Summary
    prj = exp.values_list('project', flat=True).distinct('project')
    prj_set = {}
    prj_count = 0
    for p in prj:
        if p == None:
            pass
        else:
            prj_count +=1
            project_q = prj_qs.filter(pk=p).values_list('name', 'company__name', 'companybranch__name', 'industry__industry')
            info_list=[project_q[0][1], project_q[0][2], project_q[0][3]]
            prj_set[project_q[0][0]] = info_list

    object_viewed_signal.send(pfl.__class__, instance=pfl, request=request)


    template = 'talenttrack/active_profile_view_light.html'
    context = {
        'bch': bch, 'pfl': pfl, 'padd': padd, 'exp': exp, 'bkl': bkl, 'edtexp': edtexp, 'bkl_count': bkl_count, 'prj_set': prj_set, 'prj_count': prj_count, 'achievement_qs': achievement_qs, 'language_qs': language_qs, 'membership_qs': membership_qs, 'als': als
        }
    return render(request, template, context)



def LCMFullView(request, tlt):
    '''View to show all licenses and certifications for a person.'''
    #tlt = Profile.objects.get(alias=tlt)
    lcm_qs = LicenseCertification.objects.filter(talent__alias=tlt).order_by('-issue_date')

    template = 'talenttrack/lcm_full_view.html'
    context = {
        'lcm_qs': lcm_qs, 'tlt': tlt,
        }
    return render(request, template, context)


def SkillProfileDetailView(request, tlt):
    '''A list of all hours logged against a skill for experience and training'''
    tlt_p = Profile.objects.get(alias=tlt)
    skill_qs = SkillTag.objects.all()
    exp = WorkExperience.objects.filter(talent__alias = tlt).select_related('topic')

    exp_s = exp.values_list('skills', flat=True).distinct('skills')
    exp_t = exp.order_by('topic__skills').values_list('topic__skills', flat=True).distinct('topic__skills')
    edt_topic = exp.values_list('topic', flat=True).distinct('topic')

    tlt = tlt

    #gathering all experience hours per topic
    exp_set = {}
    for s in exp_s:
        if s == None:
            pass
        else:
            b = skill_qs.get(pk=s)
            c = b.experience.filter(talent__alias=tlt)
            cnt = c.count()
            sum = c.aggregate(sum_s=Sum('hours_worked'))
            sum_float = float(sum.get('sum_s'))
            info_set = {}
            info_set['count']=cnt
            info_set['sum']=sum_float
            skill_q = skill_qs.filter(pk=s).values_list('skill', flat=True)
            skill_f = skill_q[0]
            exp_set[skill_f] = info_set

    #gathering all training hours per topic
    edt_set = {}
    for c in edt_topic:
        #populating the keys
        for t in exp_t:
            if t == None:
                pass
            else:
                skill_q = skill_qs.filter(pk=t).values_list('skill', flat=True)
                skill_f = skill_q[0]
                edt_set[skill_f]=float(0)

        #populating the values
        for t in exp_t:
            if t == None:
                pass
            else:
                d = skill_qs.get(pk=t)
                e = exp.filter(topic__skills=d)
                e_sum = e.aggregate(sum_t=Sum('topic__hours'))
                sum_float = float(e_sum.get('sum_t'))
                skill_q = skill_qs.filter(pk=t).values_list('skill', flat=True)
                skill_f = skill_q[0]
                if edt_set[skill_f]:
                    new = edt_t[skill_f]+sum_float
                    d[skill_f]=new
                else:
                    edt_set[skill_f] = sum_float

    template = 'talenttrack/talent_detail_summary.html'
    context = {
        'edt_set': edt_set, 'exp_set': exp_set, 'tlt_p': tlt_p, 'tlt': tlt,
    }
    return render(request, template, context)


def SumAllExperienceView(request, tlt):
    '''A list of all hours logged against a skill for experience and training'''
    talent = request.user.id
    tlt_p = Profile.objects.get(alias=tlt)
    skill_qs = SkillTag.objects.all()
    exp = WorkExperience.objects.filter(talent__alias = tlt).select_related('topic')
    tlt = tlt

    exp_s = exp.values_list('skills', flat=True).distinct('skills')
    exp_t = exp.order_by('topic__skills').values_list('topic__skills', flat=True).distinct('topic__skills')
    edt_topic = exp.values_list('topic', flat=True).distinct('topic')

    #gathering all experience hours per topic
    exp_set = {}
    for s in exp_s:
        if s == None:
            pass
        else:
            b = skill_qs.get(pk=s)
            c = b.experience.filter(talent__alias=tlt)
            cnt = c.count()
            sum = c.aggregate(sum_s=Sum('hours_worked'))
            sum_float = float(sum.get('sum_s'))
            info_set = {}
            info_set['count']=cnt
            info_set['sum']=sum_float
            skill_q = skill_qs.filter(pk=s).values_list('skill', flat=True)
            skill_f = skill_q[0]
            exp_set[skill_f] = info_set

    #gathering all training hours per topic
    edt_set = {}
    for c in edt_topic:
        #populating the keys
        for t in exp_t:
            if t == None:
                pass
            else:
                skill_q = skill_qs.filter(pk=t).values_list('skill', flat=True)
                skill_f = skill_q[0]
                edt_set[skill_f]=float(0)

        #populating the values
        for t in exp_t:
            if t == None:
                pass
            else:
                d = skill_qs.get(pk=t)
                e = exp.filter(topic__skills=d)
                e_sum = e.aggregate(sum_t=Sum('topic__hours'))
                sum_float = float(e_sum.get('sum_t'))
                skill_q = skill_qs.filter(pk=t).values_list('skill', flat=True)
                skill_f = skill_q[0]
                if edt_set[skill_f]:
                    new = edt_t[skill_f]+sum_float
                    d[skill_f]=new
                else:
                    edt_set[skill_f] = sum_float

    template = 'talenttrack/talent_detail_summary.html'
    context = {
        'edt_set': edt_set, 'tlt': tlt, 'exp_set': exp_set, 'tlt_p': tlt_p
    }
    return render(request, template, context)


def DPC_SummaryView(request, tlt):
    '''View for Designation, Project and Company hours logged'''
    #caching
    exp = WorkExperience.objects.filter(talent__alias = tlt).select_related('designation')
    designation_qs = Designation.objects.all()
    companybranch_qs = Branch.objects.all()
    project_qs = ProjectData.objects.all()
    tlt = tlt

    #Designation Summary
    dgn = exp.values_list('designation', flat=True).distinct('designation')

    dgn_set = {}
    for d in dgn:
        if d == None:
            pass
        else:
            a = designation_qs.get(pk=d)
            b = a.workexperience_set.all()
            cnt = b.count()
            sum = b.aggregate(sum_d=Sum('hours_worked'))
            sum_float = float(sum.get('sum_d'))
            info_set = {}
            info_set['count']=cnt
            info_set['sum']=sum_float
            designation_q = designation_qs.filter(pk=d).values_list('name', flat=True)
            designation_f = designation_q[0]
            dgn_set[designation_f] = info_set


    #Company Summary - Listed Per Branch
    cmp = exp.values_list('companybranch', flat=True).distinct('companybranch')
    cmp_set = {}
    for c in cmp:
        if c == None:
            pass
        else:
            a = companybranch_qs.get(pk=c)
            b = a.workexperience_set.all()
            cnt = b.count()
            sum = b.aggregate(sum_d=Sum('hours_worked'))
            sum_float = float(sum.get('sum_d'))
            info_set = {}
            info_set['count']=cnt
            info_set['sum']=sum_float
            companybranch_q = companybranch_qs.filter(pk=c).values_list('company__name', 'name', 'city__city')
            companybranch_f = f'{companybranch_q[0][0]}: {companybranch_q[0][1]} ({companybranch_q[0][2]})'
            cmp_set[companybranch_f] = info_set

    #Project Summary
    prj = exp.values_list('project', flat=True).distinct('project')
    prj_set = {}
    for p in prj:
        if p == None:
            pass
        else:
            a = project_qs.get(pk=p)
            b = a.workexperience_set.all()
            cnt = b.count()
            sum = b.aggregate(sum_d=Sum('hours_worked'))
            sum_float = float(sum.get('sum_d'))
            info_set = {}
            info_set['count']=cnt
            info_set['sum']=sum_float
            project_q = project_qs.filter(pk=p).values_list('name', 'company__name', 'companybranch__name')
            project_f = f'{project_q[0][0]}: {project_q[0][1]} ({project_q[0][2]})'
            prj_set[project_f] = info_set

    template = 'talenttrack/talent_dpc_summary.html'
    context = {
        'dgn_set': dgn_set, 'tlt': tlt, 'cmp_set': cmp_set, 'prj_set': prj_set,
    }
    return render(request, template, context)


@login_required()
@csp_exempt
def PreLoggedExperienceCaptureView(request):
    form = PreLoggedExperienceForm(request.POST or None, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.prelog = True
            new.save()
            form.save_m2m()
            response = redirect(reverse('Talent:ColleagueSelect', kwargs={'pk': new.id}))
            response.delete_cookie("confirm")
            return response
        else:
            template = 'talenttrack/prelogged_capture.html'
            context = {'form': form}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/prelogged_capture.html'
        context = {'form': form}
        response = render(request, template, context)
        response.set_cookie("confirm","PC")
        return response


@login_required()
def PreLoggedExperienceDeleteView(request, ple_pk):
    info = WorkExperience.objects.get(pk=ple_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:Home')+'#headingThree')
    else:
        raise PermissionDenied


@login_required()
def PreLoggedExperienceDeleteFullView(request, ple_pk):
    info = WorkExperience.objects.get(pk=ple_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:PreExperienceList'))
    else:
        raise PermissionDenied


@login_required()
def PreLogDetailView(request, tex):
    check = WorkExperience.objects.get(slug=tex, prelog=True)
    if check.talent == request.user:
        sum = WorkExperience.objects.filter(talent=request.user, prelog=True)
        sum_company = sum.filter(company=check.company).aggregate(co_sum=Sum('hours_worked'))
        sum_project = sum.filter(project=check.project).aggregate(p_sum=Sum('hours_worked'))
        list = WorkExperience.objects.filter(slug=tex)
        confirmed_clg = WorkColleague.objects.filter(experience__slug=tex)
        confirmed_sup = Superior.objects.filter(experience__slug=tex)
        confirmed_clr = WorkCollaborator.objects.filter(experience__slug=tex)
        confirmed_cnt = WorkClient.objects.filter(experience__slug=tex)

        template = 'talenttrack/experience_detail.html'
        context = {
            'check': check, 'confirmed_clg': confirmed_clg, 'confirmed_sup': confirmed_sup, 'confirmed_clr': confirmed_clr, 'confirmed_cnt': confirmed_cnt, 'list': list, 'sum_company': sum_company, 'sum_project': sum_project
            }

        return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def ClientSelectView(request, pk):
    score = client_score
    instance = WorkExperience.objects.get(pk=pk)
    #>>>Create a set of users to exclude
    colleague_excl = set(WorkColleague.objects.filter(experience=pk).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience=pk).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience=pk).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience=pk).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    form = WorkClientSelectForm(request.POST or None, pwd=filt)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:ClientSelect', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect('Talent:Home')
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/experience_client_select.html'
            context = {'instance': instance, 'form': form, 'score': score,}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_client_select.html'
        context = {'instance': instance, 'form': form, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","WT", "check",pk)
        return response


@login_required()
@csp_exempt
def ClientAddView(request, tex):
    score = client_score
    instance = get_object_or_404(WorkExperience, slug=tex)
    tex = tex
    #>>>Create a set of users to exclude
    colleague_excl = set(WorkColleague.objects.filter(experience__slug=tex).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience__slug=tex).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience__slug=tex).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience__slug=tex).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    form = WorkClientSelectForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:ClientAdd', kwargs={'tex':tex}))
                response.delete_cookie("confirm")
                return response

            elif 'done' in request.POST:
                response = redirect(reverse('Talent:ExperienceDetail', kwargs={'tex': tex}))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/experience_client_add.html'
            context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
            response =  render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_client_add.html'
        context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
        response =  render(request, template, context)
        response.set_cookie("confirm","WT")
        return response


@login_required()
def ClientResponseView(request, wkc):
    check = WorkClient.objects.get(slug=wkc)
    if check.experience.talent == request.user:
        form = WorkClientResponseForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/experience_client_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def CollaboratorSelectView(request, pk):
    score = collaborator_score
    instance = WorkExperience.objects.get(pk=pk)

    colleague_excl = set(WorkColleague.objects.filter(experience=pk).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience=pk).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience=pk).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience=pk).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    form = WorkCollaboratorSelectForm(request.POST or None, pwd=filt)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:CollaboratorSelect', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response

            elif 'done' in request.POST:
                response = redirect(reverse('Talent:ClientSelect', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/experience_collaborator_select.html'
            context = {'instance': instance, 'form': form, 'score': score,}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_collaborator_select.html'
        context = {'instance': instance, 'form': form, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","WL")
        return response


@login_required()
@csp_exempt
def CollaboratorAddView(request, tex):
    score = collaborator_score
    instance = get_object_or_404(WorkExperience, slug=tex)
    tex = tex

    colleague_excl = set(WorkColleague.objects.filter(experience__slug=tex).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience__slug=tex).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience__slug=tex).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience__slug=tex).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    form = WorkCollaboratorSelectForm(request.POST or None, pwd=filt)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:CollaboratorAdd', kwargs={'tex':tex}))
                response.delete_cookie("confirm")
                return response

            elif 'done' in request.POST:
                response = redirect(reverse('Talent:ExperienceDetail', kwargs={'tex': tex}))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/experience_collaborator_add.html'
            context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_collaborator_add.html'
        context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","WL")
        return response


@login_required()
def CollaboratorResponseView(request, clb):
    check = WorkCollaborator.objects.get(slug=clb)
    if check.experience.talent == request.user:
        form = WorkCollaboratorResponseForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/experience_collaborator_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def SuperiorSelectView(request, pk):
    score = superior_score
    instance = WorkExperience.objects.get(pk=pk)

    colleague_excl = set(WorkColleague.objects.filter(experience=pk).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience=pk).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience=pk).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience=pk).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    form = SuperiorSelectForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:SuperiorSelect', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:CollaboratorSelect', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/experience_superior_select.html'
            context = {'instance': instance, 'form': form, 'score': score,}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_superior_select.html'
        context = {'instance': instance, 'form': form, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","WS")
        return response


@login_required()
@csp_exempt
def SuperiorAddView(request, tex):
    score = superior_score
    instance = get_object_or_404(WorkExperience, slug=tex)
    tex = tex

    colleague_excl = set(WorkColleague.objects.filter(experience__slug=tex).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience__slug=tex).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience__slug=tex).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience__slug=tex).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    form = SuperiorSelectForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect('Talent:SuperiorAdd', kwargs={'tex':tex})
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:ExperienceDetail', kwargs={'tex': tex}))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/experience_superior_add.html'
            context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_superior_add.html'
        context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","WS")
        return response


@login_required()
def SuperiorResponseView(request, spr):
    check = Superior.objects.get(slug=spr)
    if check.experience.talent == request.user:
        form = WorkColleagueResponseForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/experience_superior_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def ColleagueSelectView(request, pk):
    score = colleague_score
    instance = WorkExperience.objects.get(pk=pk)
    tex = instance.slug

    colleague_excl = set(WorkColleague.objects.filter(experience__slug=tex).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience__slug=tex).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience__slug=tex).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience__slug=tex).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    form = WorkColleagueSelectForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:ColleagueSelect', kwargs={'pk':pk}))
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:SuperiorSelect', kwargs={'pk':instance.id}))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/experience_colleague_select.html'
            context = {'instance': instance, 'form': form, 'score': score,}
            response =  render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_colleague_select.html'
        context = {'instance': instance, 'form': form, 'score': score,}
        response =  render(request, template, context)
        response.set_cookie("confirm","WC")
        return response


@login_required()
@csp_exempt
def ColleagueAddView(request, tex):
    score = colleague_score
    instance = get_object_or_404(WorkExperience, slug=tex)

    colleague_excl = set(WorkColleague.objects.filter(experience__slug=tex).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience__slug=tex).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience__slug=tex).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience__slug=tex).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    form = WorkColleagueSelectForm(request.POST or None, pwd=filt)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:ColleagueAdd', kwargs={'tex':tex}))
                response.delete_cookie("confirm")
                return response

            elif 'done' in request.POST:
                response = redirect(reverse('Talent:ExperienceDetail', kwargs={'tex':tex}))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/experience_colleague_add.html'
            context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
            response = render(request, template, context)
            return response

    else:
        template = 'talenttrack/experience_colleague_add.html'
        context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","WC")
        return response


@login_required()
def ColleagueResponseView(request, clg):
    check = WorkColleague.objects.get(slug=clg)
    if check.experience.talent == request.user:
        form = WorkColleagueResponseForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/experience_colleague_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def ExperienceDetailView(request, tex):
    check = WorkExperience.objects.get(slug=tex, wexp=True)
    if check.talent == request.user:
        sum = WorkExperience.objects.filter(talent=request.user, wexp=True)
        sum_company = sum.filter(company=check.company).aggregate(co_sum=Sum('hours_worked'))
        sum_project = sum.filter(project=check.project).aggregate(p_sum=Sum('hours_worked'))
        list = WorkExperience.objects.filter(slug=tex)
        confirmed_clg = WorkColleague.objects.filter(experience__slug=tex)
        confirmed_sup = Superior.objects.filter(experience__slug=tex)
        confirmed_clr = WorkCollaborator.objects.filter(experience__slug=tex)
        confirmed_cnt = WorkClient.objects.filter(experience__slug=tex)

        template = 'talenttrack/experience_detail.html'
        context = {'check': check, 'confirmed_clg': confirmed_clg, 'confirmed_sup': confirmed_sup, 'confirmed_clr': confirmed_clr, 'confirmed_cnt': confirmed_cnt, 'list': list, 'sum_company': sum_company, 'sum_project': sum_project}
        return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def WorkExperienceCaptureView(request):
    form = WorkExperienceForm(request.POST or None, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.wexp = True
            new.save()
            form.save_m2m()
            return redirect(reverse('Talent:ColleagueSelect', kwargs={'pk': new.id}))
        else:
            template = 'talenttrack/experience_capture.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        template = 'talenttrack/experience_capture.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
def WorkExperienceDeleteView(request, we_pk):
    info = WorkExperience.objects.get(pk=we_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:Home')+'#headingThree')
    else:
        raise PermissionDenied


@login_required()
def WorkExperienceDeleteFullView(request, we_pk):
    info = WorkExperience.objects.get(pk=we_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:ExperienceList'))
    else:
        raise PermissionDenied


@login_required()
def EducationDetail(request, tex):
    check = WorkExperience.objects.get(slug=tex, edt=True)
    if check.talent == request.user:
        confirmed_l = Lecturer.objects.filter(education__slug=tex)
        confirmed_cm = ClassMates.objects.filter(education__slug=tex)
        template = 'talenttrack/education_detail.html'
        context = {'check': check, 'confirmed_l': confirmed_l, 'confirmed_cm': confirmed_cm}
        return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def LecturerResponse(request, lct):
    check = Lecturer.objects.get(slug=lct)
    if check.education.talent == request.user:
        form = LecturerRespondForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/education_lecturer_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def ClassMatesResponse(request, cmt):
    check = ClassMates.objects.get(slug=cmt)
    if check.education.talent == request.user:
        form = ClassMatesRespondForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/education_classmates_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def LecturerSelectView(request):
    score = lecturer_score
    instance = WorkExperience.objects.filter(talent=request.user, edt=True).latest('date_captured')
    tex = instance.slug

    lecturer_excl = set(Lecturer.objects.filter(education__slug=tex).values_list('lecturer', flat=True))
    colleague_excl = set(ClassMates.objects.filter(education__slug=tex).values_list('colleague', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = lecturer_excl | colleague_excl | myself
    print('view: ', filt)
    form = LecturerSelectForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.save()
            if 'another' in request.POST:
                response = redirect('Talent:LecturerSelect')
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect('Talent:ClassMatesSelect')
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/education_lecturer_select.html'
            context = {'instance': instance, 'form': form, 'score': score,}
            response = render(request, template, context)
            response.set_cookie("confirm","LR")
            return response
    else:
        template = 'talenttrack/education_lecturer_select.html'
        context = {'instance': instance, 'form': form, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","LR")
        return response


@login_required()
@csp_exempt
def LecturerAddView(request, tex):
    score = lecturer_score
    instance = get_object_or_404(WorkExperience, slug=tex)
    tex = tex

    lecturer_excl = set(Lecturer.objects.filter(education__slug=tex).values_list('lecturer', flat=True))
    colleague_excl = set(ClassMates.objects.filter(education__slug=tex).values_list('colleague', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = lecturer_excl | colleague_excl | myself

    form = LecturerSelectForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:LecturerAdd', kwargs={'tex': tex}))
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:EducationDetail', kwargs={'tex': tex}))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/education_lecturer_add.html'
            context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
            response = render(request, template, context)
            response.set_cookie("confirm","LR")
            return response
    else:
        template = 'talenttrack/education_lecturer_add.html'
        context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","LR")
        return response


@login_required()
@csp_exempt
def ClassMateSelectView(request):
    score = classmate_score
    instance = WorkExperience.objects.filter(talent=request.user, edt=True).latest('date_captured')
    tex = instance.slug

    lecturer_excl = set(Lecturer.objects.filter(education__slug=tex).values_list('lecturer', flat=True))
    colleague_excl = set(ClassMates.objects.filter(education__slug=tex).values_list('colleague', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = lecturer_excl | colleague_excl | myself

    form = ClassMatesSelectForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.save()
            if 'another' in request.POST:
                reponse = redirect('Talent:ClassMatesSelect')
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:Home'))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/education_classmate_select.html'
            context = {'instance': instance, 'form': form, 'score': score,}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/education_classmate_select.html'
        context = {'instance': instance, 'form': form, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","CM")
        return response


@login_required()
@csp_exempt
def ClassMateAddView(request, tex):
    score = classmate_score
    instance = get_object_or_404(WorkExperience, slug=tex)

    instance = WorkExperience.objects.filter(talent=request.user,edt=True).latest('date_captured')
    tex = instance.slug

    lecturer_excl = set(Lecturer.objects.filter(education__slug=tex).values_list('lecturer', flat=True))
    colleague_excl = set(ClassMates.objects.filter(education__slug=tex).values_list('colleague', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = lecturer_excl | colleague_excl | myself

    form = ClassMatesSelectForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:ClassMatesAdd', kwargs={'tex': tex}))
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:EducationDetail', kwargs={'tex': tex}))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/education_classmate_add.html'
            context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
            response = render(request, template, context)
            response.set_cookie("confirm","CM")
            return response
    else:
        template = 'talenttrack/education_classmate_add.html'
        context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","CM")
        return response


@login_required()
@csp_exempt
def EducationCaptureView(request):
    form = EducationForm(request.POST or None, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.edt = True
            new.save()
            form.save_m2m()
            return redirect(reverse('Talent:LecturerSelect'))
        else:
            template = 'talenttrack/education_capture.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        template = 'talenttrack/education_capture.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
def EducationDeleteView(request, edt_pk):
    info = WorkExperience.objects.get(pk=edt_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:Home')+'#headingOne')
    else:
        raise PermissionDenied


@login_required()
def EducationDeleteFullView(request, edt_pk):
    info = WorkExperience.objects.get(pk=edt_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:TrainingList'))
    else:
        raise PermissionDenied


#>>>Course Popup
@login_required()
@csp_exempt
def CourseAddPopup(request):
    form = CourseForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_course");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'talenttrack/course_popup.html'
            return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'talenttrack/course_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_course_id(request):
    if request.is_ajax():
        course = request.Get['course']
        course_id = Course.objects.get(name = course).id
        data = {'course_id':course_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Course Popup

#>>>CourseType Popup
@login_required()
@csp_exempt
def CourseTypeAddPopup(request):
    form = CourseTypeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_course_type");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'talenttrack/course_type_popup.html'
            return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'talenttrack/course_type_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_coursetype_id(request):
    if request.is_ajax():
        coursetype = request.Get['coursetype']
        coursetype_id = CourseType.objects.get(type = coursetype).id
        data = {'coursetype_id':coursetype_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< CourseType Popup

#>>>Result Popup
@login_required()
@csp_exempt
def ResultAddPopup(request):
    form = ResultForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_certification");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'talenttrack/result_popup.html'
            return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'talenttrack/result_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_result_id(request):
    if request.is_ajax():
        result = request.Get['result']
        result_id = Result.objects.get(type = result).id
        data = {'result_id':result_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Result Popup

#>>>Topic Popup
@login_required()
@csp_exempt
def TopicAddPopup(request):
    form = TopicPopForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            form.save_m2m()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_topic");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'talenttrack/topic_popup.html'
            return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'talenttrack/topic_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_topic_id(request):
    if request.is_ajax():
        topic = request.Get['topic']
        topic_id = Topic.objects.get(topic = topic).id
        data = {'topic_id':topic_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Topic Popup


#>>>Designation Popup
@login_required()
@csp_exempt
def DesignationAddPopup(request):
    form = DesignationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_designation");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'talenttrack/designation_popup.html'
            return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'talenttrack/designation_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_designation_id(request):
    if request.is_ajax():
        designation = request.Get['designation']
        designation_id = Designation.objects.get(name = designation).id
        data = {'designation_id':designation_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Designation Popup
