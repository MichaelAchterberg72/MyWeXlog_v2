from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum, F, Q, Avg, Max, Min
from dateutil.relativedelta import relativedelta
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
import json

from django.views.generic import (
        TemplateView
    )

from itertools import chain
from operator import attrgetter

from csp.decorators import csp_exempt
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.conf import settings

from django_select2.views import AutoResponseView

from WeXlog.app_config import (
    skill_pass_score, locked_age, client_score, lecturer_score, classmate_score,    colleague_score, pre_colleague_score, collaborator_score, superior_score
)

from locations.models import Region
from .models import *
from Profile.models import Profile
from talenttrack.models import WorkExperience
from enterprises.models import Enterprise, Branch
from users.models import CustomUser
from db_flatten.models import SkillTag

from .forms import ProjectAddForm, ProjectAddHome, ProjectSearchForm, ProjectForm, ProjectPersonalDetailsForm, AddProjectPersonalDetailsForm, ProjectFullAddForm

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required()
def ProjectDashboard(request):
    tlt = request.user
    projects_qs = ProjectPersonalDetails.objects.filter(talent=tlt)
    pp_count = projects_qs.count()
    pp_list = projects_qs.annotate(
                                   sum=Sum('workexperience__hours_worked')
                                   ).order_by('-sum')[:5]

    p_qs = ProjectData.objects.filter(
                                      Q(workexperience__score__gte=3)
                                      & Q(workexperience__hours_worked__gte=0))
    pcount = p_qs.count()

    projecthours = p_qs.annotate(
                                 sum=Sum('workexperience__hours_worked'),
                                 count=Count('workexperience__company'),
                                 people=Count('workexperience__talent')
                                 ).order_by('-sum')[0:5]

    template_name = 'project/project_dashboard.html'
    context = {'pp_count': pp_count, 'pp_list': pp_list, 'pcount': pcount, 'projecthours': projecthours}
    return render(request, template_name, context)


@login_required()
def ProjectHome(request):
    tlt = request.user
    projects_qs = ProjectPersonalDetails.objects.filter(talent=tlt).annotate(sum=Sum('workexperience__hours_worked'))

    pcount = projects_qs.count()


    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(projects_qs, 20)

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

    template_name = 'project/personal_projects_a.html'
    context = {'pcount': pcount, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template_name, context)


@login_required()
def ProjectPersonalDetailsView(request, prj, co, bch):
    project = ProjectData.objects.get(slug=prj)
    pr_c_i = Enterprise.objects.get(slug=co)
    pr_b_i = Branch.objects.get(slug=bch)

    instance, _ = ProjectPersonalDetails.objects.get_or_create(
            talent=request.user,
            project=project,
            company=pr_c_i,
            companybranch=pr_b_i)

    if request.method == 'POST':
        form = ProjectPersonalDetailsForm(request.POST, instance=instance)
        if form.is_valid():
            new = form.save(commit=False)
#            new.talent = request.user
#            new.project.slug = prj
            new.save()
            return redirect(reverse('Project:ProjectHome'))
    else:
        form = ProjectPersonalDetailsForm(instance=instance)
        template_name = 'project/personal_detail.html'
        context = {'form': form, 'instance': instance, 'project': project}
        return render(request, template_name, context)


@login_required()
def PersonalProejctDeleteView(request, ppj):
    talent=request.user
    instance = ProjectPersonalDetails.objects.get(id=ppj)

    if instance.talent == request.user:
        if request.method =='POST':
            instance.delete()
            return redirect(reverse('Project:ProjectDashboard')+'#personalprojects')
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def ProjectPersonalDetailsAddView(request):
    tlt = CustomUser.objects.get(alias=request.user.alias)
    if request.method =='POST':
        form = AddProjectPersonalDetailsForm(request.POST or None)
        if form.is_valid():
            new = form.save(commit=False)
            new.talent=request.user
            new.save()
            return redirect(reverse('Project:ProjectHome'))
    else:
        form = AddProjectPersonalDetailsForm()

    template = 'project/project_personal_details_add.html'
    context = {'form': form}
    return render(request, template, context)

#>>> Personal Project Popup
@login_required()
@csp_exempt
def ProjectPersonalDetailsAddPopupView(request):
    form = AddProjectPersonalDetailsForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.talent=request.user
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_project_data");</script>' % (instance.pk, instance))

        else:
            context = {'form':form,}
            template = 'project/project_personal_details_add_popup.html'
            return render(request, template, context)
    else:
        context = {'form':form,}
        template = 'project/project_personal_details_add_popup.html'
        return render(request, template, context)

@csrf_exempt
def get_p_project_id(request):
    if request.is_ajax():
        project = request.Get['project']
        project_id = PersonalProjectDetails.objects.get(project = project).id
        data = {'project_id':project_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#Personal Project Popup <<<


class ProjectDataJsonView(AutoResponseView):
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            raise Http404
        return qs.filter(talent=self.request.user)


@login_required()
def ProjectListHome(request):
<<<<<<< HEAD
    projects = ProjectData.objects.all().annotate(
                                  sum=Sum('workexperience__hours_worked'),
                                  count=Count('workexperience__company'),
                                  people=Count('workexperience__talent'))

    pcount = projects.aggregate(sum_p=Count('name'))

=======
    pcount = ProjectData.objects.all().aggregate(sum_p=Count('name'))
    projects = ProjectData.objects.all().order_by('company')
>>>>>>> origin/2021-08-Mike

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(projects, 20)

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

    template_name = 'project/project_full_list.html'
    context = {'pcount': pcount, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template_name, context)


@login_required()
def HelpProjectHomeView(request):
    template_name = 'project/help_project_home.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpProjectAddView(request):
    template_name = 'project/help_project_add.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpProjectSearchView(request):
    template_name = 'project/help_project_search.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpProjectDetailView(request):
    template_name = 'project/help_project_detail.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def ProjectList(request, profile_id=None):
    profile_id = request.user
    pcount = WorkExperience.objects.filter(talent=profile_id).aggregate(sum_p=Count('company'))
    projects = WorkExperience.objects.filter(talent=profile_id).order_by('date_to')

    template_name = 'project/project_home.html'
    context = {'pcount': pcount, 'projects': projects,}
    return render(request, template_name, context)


@login_required()
def ProjectDetailView(request, prj):
    info = get_object_or_404(ProjectData, slug=prj)
    detail = ProjectData.objects.filter(slug=prj)
    cache = WorkExperience.objects.filter(project__slug=prj)
    hr = cache.aggregate(sum_t=Sum('hours_worked'))
    ppl = cache.distinct('talent').count()

    talent = request.user.id
    tlt_p = info
    skill_qs = SkillTag.objects.all()
    #Full list experience
    exp = WorkExperience.objects.filter(project=info)
    # Validated Experience
    val_exp = exp.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score))

    exp_s = val_exp.values_list('skills', flat=True).distinct('skills')
    exp_t = val_exp.order_by('topic__skills').values_list('topic__skills', flat=True).distinct('topic__skills')
    edt_topic = val_exp.values_list('topic', flat=True).distinct('topic')


    exp_s_skill = val_exp.values_list('skills__skill', flat=True).distinct('skills')
    exp_t_skill = val_exp.order_by('topic__skills__skill').values_list('topic__skills__skill', flat=True).distinct('topic__skills__skill')

    exp_s_list = list(exp_s_skill)
    exp_t_list = list(exp_t_skill)
    skills_list = list(exp_s_list + exp_t_list)

    skills_list_set=[]
    for x in skills_list:
        skills_list_set.append(x)
    skills_list_n = [x for x in skills_list_set if x is not None]

    skills_list_set_set = set(skills_list_n)
    ordered_skills_list = sorted(skills_list_set_set, reverse=False)

    skills_list_Labels = ordered_skills_list

    prj_id = [info.id]

    #Hours Experience per skill chart
    val_skills_hours_skill_data = []
    for s in ordered_skills_list:
        shwe = val_exp.filter(Q(skills__skill=s, edt=False) | Q(topic__skills__skill=s, edt=True))
        skills_hours=[]
        for i in prj_id:
            aw_exp = shwe.filter(project__id=i, edt=False).aggregate(awet=Sum('hours_worked'))
            awetv = aw_exp.get('awet')
            if awetv == None:
                awetv = 0
            else:
                awetv = awetv

            at_exp = shwe.filter(project__id=i, edt=True).aggregate(tet=Sum('topic__hours'))
            atetv = at_exp.get('tet')
            if atetv == None:
                atetv = 0
            else:
                atetv = atetv

            t_exp = awetv + atetv

            result={'t_exp': t_exp}

            skills_hours.append(result)

        skills_list=[float(x['t_exp']) for x in skills_hours]
        sum_shwe = sum(skills_list)

        val_skills_hours_skill_data.append(sum_shwe)

    #Hours Training Experience per skill chart
    training_skills_hours_skill_data = []
    for s in ordered_skills_list:
        shwt = val_exp.filter(Q(topic__skills__skill=s, edt=True))
        training_skills_hours=[]
        for i in prj_id:

            at_exp = shwt.filter(project__id=i, edt=True).aggregate(tet=Sum('topic__hours'))
            atetv = at_exp.get('tet')
            if atetv == None:
                atetv = 0
            else:
                atetv = atetv

            result={'t_exp': atetv}

            training_skills_hours.append(result)

        training_skills_list=[float(x['t_exp']) for x in training_skills_hours]
        sum_shwt = sum(training_skills_list)

        training_skills_hours_skill_data.append(sum_shwt)

    dept_skills_link = SkillTag.objects.filter(skill__in=ordered_skills_list).order_by('skill')

    skills_count = len(ordered_skills_list)

    template_name = 'project/project_detail.html'
    context = {'detail': detail, 'info': info, 'hr': hr, 'ppl': ppl, 'prj': prj,
        'skills_list_Labels': skills_list_Labels,
        'val_skills_hours_skill_data': val_skills_hours_skill_data,
        'training_skills_hours_skill_data': training_skills_hours_skill_data,
        'skills_count': skills_count,
        'dept_skills_link': dept_skills_link,}
    return render(request, template_name, context)


@login_required()
def project_associated_skill_stats(request, prj, skl):
    '''The view for the project associated skill overview and stats'''
    info = get_object_or_404(ProjectData, slug=prj)
    skill = SkillTag.objects.get(id=skl)
    prj_id = [info.id]
    today = timezone.now().date()

    we = WorkExperience.objects.filter(project__slug=prj)
    val_we = we.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score))

    #Skills associated with skill - includes all skills not just validated ones
    skill_we =  val_we.filter(skills__skill=skill.skill, edt=False)
    skills_assoc_qs = skill_we.values_list('pk', flat=True)

    skills_list_qs = val_we.filter(pk__in=skills_assoc_qs)
    skills_list_qs_count = skills_list_qs.count()

    skills_list = skills_list_qs.values_list('skills__skill', flat=True).distinct()

    skills_list_set_all = [x for x in skills_list if x is not None]

    skills_list_set = [x for x in skills_list_set_all if x is not f'{skill.skill}']

    dept_skills_link = SkillTag.objects.filter(skill__in=skills_list_set).order_by('skill')

    skills_instance_count = []
    skill_list_labels = []
    skill_percentage_data = []
    for skill_item in skills_list_set:
        skill_count = 0
        tlt_we_skill = skills_list_qs.filter(skills__skill=skill_item).values_list('skills__skill', flat=True)

        for we_instance in tlt_we_skill:
            skill_count +=1
        skill_percentage = int(format(skill_count / skills_list_qs_count * 100, '.0f'))

        result={'skill': skill_item, 'skill_count': skill_count, 'skill_percentage': skill_percentage}

        skills_instance_count.append(result)

        skill_list_labels.append(skill_item)
        skill_percentage_data.append(skill_percentage)

    skill_list_labels_count = skills_list.count()

    orderd_skills_instance_count = sorted(skills_instance_count, key=lambda kv: kv['skill_percentage'], reverse=True)


    val_we_skill = val_we.filter(Q(skills__skill=skill.skill, edt=False) | Q(topic__skills__skill=skill.skill, edt=True))

    # Total Work Experience Skill Sum Experience by Year
    val_we_skills_used_year_range_data = []
    val_we_skills_age_range=[]
    for i in prj_id:
        we_qs = val_we_skill.filter(project__id=i, edt=False)
        for wet in we_qs:
            swewd = wet.date_to
            we_skill_age=relativedelta(today, swewd).years

            aw_exp = wet.hours_worked
            if aw_exp == None:
                awetv = 0
            else:
                awetv = aw_exp

            result={'we_skill_age': we_skill_age, 'awetv': awetv}

            val_we_skills_age_range.append(result)

    # Total hours experience in year range
    val_we_skill_age_range_0_1=[float(x['awetv']) for x in val_we_skills_age_range if x['we_skill_age'] in range(0, 1)]
    val_we_skill_age_range_1_2=[float(x['awetv']) for x in val_we_skills_age_range if x['we_skill_age'] in range(1, 2)]
    val_we_skill_age_range_2_3=[float(x['awetv']) for x in val_we_skills_age_range if x['we_skill_age'] in range(2, 3)]
    val_we_skill_age_range_3_4=[float(x['awetv']) for x in val_we_skills_age_range if x['we_skill_age'] in range(3, 4)]
    val_we_skill_age_range_4_5=[float(x['awetv']) for x in val_we_skills_age_range if x['we_skill_age'] in range(4, 5)]
    val_we_skill_age_range_5_6=[float(x['awetv']) for x in val_we_skills_age_range if x['we_skill_age'] in range(5, 6)]
    val_we_skill_age_range_6_7=[float(x['awetv']) for x in val_we_skills_age_range if x['we_skill_age'] in range(6, 7)]
    val_we_skill_age_range_7_8=[float(x['awetv']) for x in val_we_skills_age_range if x['we_skill_age'] in range(7, 8)]
    val_we_skill_age_range_8_9=[float(x['awetv']) for x in val_we_skills_age_range if x['we_skill_age'] in range(8, 9)]
    val_we_skill_age_range_9_10=[float(x['awetv']) for x in val_we_skills_age_range if x['we_skill_age'] in range(9, 10)]

    total_val_we_skill_age=[float(x['awetv']) for x in val_we_skills_age_range if x['we_skill_age'] in range(0, 100)]
    total_val_sum_we = sum(total_val_we_skill_age)

    sum_val_we_range_0_1 = sum(val_we_skill_age_range_0_1)
    sum_val_we_range_1_2 = sum(val_we_skill_age_range_1_2)
    sum_val_we_range_2_3 = sum(val_we_skill_age_range_2_3)
    sum_val_we_range_3_4 = sum(val_we_skill_age_range_3_4)
    sum_val_we_range_4_5 = sum(val_we_skill_age_range_4_5)
    sum_val_we_range_5_6 = sum(val_we_skill_age_range_5_6)
    sum_val_we_range_6_7 = sum(val_we_skill_age_range_6_7)
    sum_val_we_range_7_8 = sum(val_we_skill_age_range_7_8)
    sum_val_we_range_8_9 = sum(val_we_skill_age_range_8_9)
    sum_val_we_range_9_10 = sum(val_we_skill_age_range_9_10)

    val_we_skills_used_year_range_data.append(sum_val_we_range_9_10)
    val_we_skills_used_year_range_data.append(sum_val_we_range_8_9)
    val_we_skills_used_year_range_data.append(sum_val_we_range_7_8)
    val_we_skills_used_year_range_data.append(sum_val_we_range_6_7)
    val_we_skills_used_year_range_data.append(sum_val_we_range_5_6)
    val_we_skills_used_year_range_data.append(sum_val_we_range_4_5)
    val_we_skills_used_year_range_data.append(sum_val_we_range_3_4)
    val_we_skills_used_year_range_data.append(sum_val_we_range_2_3)
    val_we_skills_used_year_range_data.append(sum_val_we_range_1_2)
    val_we_skills_used_year_range_data.append(sum_val_we_range_0_1)

    # Training Validated Experience Skill Sum Experience by Year
    t_val_we_skills_used_year_range_data = []
    t_val_we_skills_age_range=[]
    for i in prj_id:
        t_we_qs = val_we_skill.filter(project__id=i, edt=True)
        for wet in t_we_qs:
            swewd = wet.date_to
            we_skill_age=relativedelta(today, swewd).years

            aw_exp = wet.topic.hours
            if aw_exp == None:
                awetv = 0
            else:
                awetv = aw_exp

            t_result={'we_skill_age': we_skill_age, 'awetv': awetv}

            t_val_we_skills_age_range.append(t_result)

    # Total Validated hours experience in year range
    t_val_we_skill_age_range_0_1=[float(x['awetv']) for x in t_val_we_skills_age_range if x['we_skill_age'] in range(0, 1)]
    t_val_we_skill_age_range_1_2=[float(x['awetv']) for x in t_val_we_skills_age_range if x['we_skill_age'] in range(1, 2)]
    t_val_we_skill_age_range_2_3=[float(x['awetv']) for x in t_val_we_skills_age_range if x['we_skill_age'] in range(2, 3)]
    t_val_we_skill_age_range_3_4=[float(x['awetv']) for x in t_val_we_skills_age_range if x['we_skill_age'] in range(3, 4)]
    t_val_we_skill_age_range_4_5=[float(x['awetv']) for x in t_val_we_skills_age_range if x['we_skill_age'] in range(4, 5)]
    t_val_we_skill_age_range_5_6=[float(x['awetv']) for x in t_val_we_skills_age_range if x['we_skill_age'] in range(5, 6)]
    t_val_we_skill_age_range_6_7=[float(x['awetv']) for x in t_val_we_skills_age_range if x['we_skill_age'] in range(6, 7)]
    t_val_we_skill_age_range_7_8=[float(x['awetv']) for x in t_val_we_skills_age_range if x['we_skill_age'] in range(7, 8)]
    t_val_we_skill_age_range_8_9=[float(x['awetv']) for x in t_val_we_skills_age_range if x['we_skill_age'] in range(8, 9)]
    t_val_we_skill_age_range_9_10=[float(x['awetv']) for x in t_val_we_skills_age_range if x['we_skill_age'] in range(9, 10)]

    total_t_val_we_skill_age=[float(x['awetv']) for x in t_val_we_skills_age_range if x['we_skill_age'] in range(0, 100)]
    total_val_sum_t_we = sum(total_t_val_we_skill_age)

    sum_t_val_we_range_0_1 = sum(t_val_we_skill_age_range_0_1)
    sum_t_val_we_range_1_2 = sum(t_val_we_skill_age_range_1_2)
    sum_t_val_we_range_2_3 = sum(t_val_we_skill_age_range_2_3)
    sum_t_val_we_range_3_4 = sum(t_val_we_skill_age_range_3_4)
    sum_t_val_we_range_4_5 = sum(t_val_we_skill_age_range_4_5)
    sum_t_val_we_range_5_6 = sum(t_val_we_skill_age_range_5_6)
    sum_t_val_we_range_6_7 = sum(t_val_we_skill_age_range_6_7)
    sum_t_val_we_range_7_8 = sum(t_val_we_skill_age_range_7_8)
    sum_t_val_we_range_8_9 = sum(t_val_we_skill_age_range_8_9)
    sum_t_val_we_range_9_10 = sum(t_val_we_skill_age_range_9_10)

    t_val_we_skills_used_year_range_data.append(sum_t_val_we_range_9_10)
    t_val_we_skills_used_year_range_data.append(sum_t_val_we_range_8_9)
    t_val_we_skills_used_year_range_data.append(sum_t_val_we_range_7_8)
    t_val_we_skills_used_year_range_data.append(sum_t_val_we_range_6_7)
    t_val_we_skills_used_year_range_data.append(sum_t_val_we_range_5_6)
    t_val_we_skills_used_year_range_data.append(sum_t_val_we_range_4_5)
    t_val_we_skills_used_year_range_data.append(sum_t_val_we_range_3_4)
    t_val_we_skills_used_year_range_data.append(sum_t_val_we_range_2_3)
    t_val_we_skills_used_year_range_data.append(sum_t_val_we_range_1_2)
    t_val_we_skills_used_year_range_data.append(sum_t_val_we_range_0_1)

    skills_used_year_range_labels = [10, 9, 8, 7, 6, 5, 4, 3, 'last year', 'This year']

    template = 'project/project_associated_skills_stats_overview.html'
    context = {
            'prj': prj,
            'skl': skl,
            'skill': skill,
            'skills_list_qs_count': skills_list_qs_count,
            'skill_list_labels_count': skill_list_labels_count,
            'skill_list_labels': skill_list_labels,
            'skill_percentage_data': skill_percentage_data,
            'dept_skills_link': dept_skills_link,
            'skills_used_year_range_labels': skills_used_year_range_labels,
            'total_val_sum_t_we': total_val_sum_t_we,
            'total_val_sum_we': total_val_sum_we,
            't_val_we_skills_used_year_range_data': t_val_we_skills_used_year_range_data,
            'val_we_skills_used_year_range_data': val_we_skills_used_year_range_data,
    }
    return render(request, template, context)


@login_required()
def ProjectEditView(request, prj):
    instance = get_object_or_404(ProjectData, slug=prj)
    form = ProjectForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
        return redirect(reverse('Project:ProjectDetail', kwargs={'prj':prj}))

    else:
        template = 'project/project_add.html'
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


@login_required()
@csp_exempt
def ProjectAddView(request):
    if request.method =='POST':
        form = ProjectAddHome(request.POST or None)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return redirect(reverse('Project:ProjectList'))
    else:
        form = ProjectAddHome()

    template = 'project/project_add.html'
    context = {'form': form}
    return render(request, template, context)


@login_required()
def ProjectListView(request):
    list = ProjectData.objects.all().order_by('name')
    template_name = 'project/projects_list.html'
    paginate_by = 10  # if pagination is desired'
    context = {
            'list': list,
    }
    return render(request, template_name, context)


@login_required()
def ProjectSearch(request):
    form = ProjectSearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = ProjectSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = ProjectData.objects.annotate(
                search=SearchVector('name__icontains',
                                    'company__branch__icontains',
                                    'industry__industry__icontains',
                                    'country__icontains',
                                    'region__region__icontains',
                                    'city__city__icontains'),
            ).filter(search=query).order_by('company__ename')

    template_name= 'project/project_search.html'
    context = {
            'form': form,
            'query': query,
            'results': results
    }
    return render(request, template_name, context)


@login_required()
def HoursWorkedOnProject(request, prj):
    projectdata = get_object_or_404(ProjectData, slug=prj)
    wk_qs = WorkExperience.objects.filter(project__slug=prj)
    hr = wk_qs.aggregate(sum_t=Sum('hours_worked'))
    comp_qs = wk_qs.values_list('company__slug', flat=True).distinct()
    comp = list(comp_qs)

    hours = []
    for c in comp:
        company = Enterprise.objects.get(slug=c).ename
        info = wk_qs.filter(Q(company__slug=c) & Q(project__slug=prj)).aggregate(sum_t=Sum('hours_worked'))
        date = wk_qs.filter(Q(company__slug=c) & Q(project__slug=prj)).aggregate(Max('date_to'))

        result={'company': company, 'slug': c, 'prj': prj, 'hours_worked': info['sum_t'], 'date_to': date['date_to__max']}

        hours.append(result)


    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(hours, 20)

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

    template_name = 'project/hours_worked_on_project.html'
    context = {
            'projectdata': projectdata,
            'hr': hr,
            'pageitems': pageitems,
            'page_range': page_range,
    }
    return render(request, template_name, context)


@login_required()
def EmployeesOnProject(request, prj, corp):
    projectdata = get_object_or_404(ProjectData, slug=prj)
    wk_qs = WorkExperience.objects.filter(Q(project__slug=prj) & Q(company__slug=corp))
    hr = wk_qs.aggregate(sum_t=Sum('hours_worked'))
    talent_qs = wk_qs.values_list('talent__alias', flat=True).distinct()
    talent = list(talent_qs)

    hours = []
    for t in talent:
        info = wk_qs.filter(Q(talent__alias=t) & Q(project__slug=prj)).aggregate(sum_t=Sum('hours_worked'))
        date_from = wk_qs.filter(Q(talent__alias=t) & Q(project__slug=prj)).aggregate(Min('date_from'))
        date_to = wk_qs.filter(Q(talent__alias=t) & Q(project__slug=prj)).aggregate(Max('date_to'))

        result={'talent': t, 'hours_worked': info['sum_t'], 'date_from': date_from['date_from__min'], 'date_to': date_to['date_to__max']}

        hours.append(result)

        hours = sorted(hours, key=lambda kv: kv['date_to'], reverse=True)

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(hours, 20)

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

    template_name = 'project/employees_worked_on_project.html'
    context = {
            'projectdata': projectdata,
            'prj': prj,
            'hr': hr,
            'pageitems': pageitems,
            'page_range': page_range,
    }
    return render(request, template_name, context)


@login_required()
def WorkExperienceDetail(request, prj):
    info = get_object_or_404(WorkExperience, slug=prj)
    detail = WorkExperience.objects.filter(project__slug=prj)

    template_name = 'project/work_experience_detail.html'
    context = {
            'detail': detail,
            'info': info,
    }
    return render(request, template_name, context)


def on_backbutton_clicked(self, widget):
    self.webview.go_back()


#>>>Project Popup
@login_required()
@csp_exempt
def ProjectAddPopup(request):
    exist_project = set(ProjectData.objects.filter().values_list('name', flat=True))

    filt = exist_project
#    data = json.loads(request.COOKIES['branch'])
#    qs = Branch.objects.get(id=data)

    print(qs, qs.company)
    form = ProjectAddForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.companybranch = qs
            instance.company = qs.company
            instance.save()
            response = HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_project");</script>' % (instance.pk, instance))
            response.delete_cookie('branch')
            return response
        else:
            context = {'form':form, 'qs':qs}
            template = 'project/project_add_popup.html'
            return render(request, template, context)
    else:
        context = {'form':form, 'qs':qs}
        template = 'project/project_add_popup.html'
        return render(request, template, context)


@login_required()
@csp_exempt
def ProjectFullAddPopup(request):
    form = ProjectFullAddForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            response = HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_project");</script>' % (instance.pk, instance))
            return response
        else:
            context = {'form':form,}
            template = 'project/project_full_add_popup.html'
            return render(request, template, context)
    else:
        context = {'form':form,}
        template = 'project/project_full_add_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_project_id(request):
    if request.is_ajax():
        project = request.Get['project']
        project_id = ProjectData.objects.get(name = project).id
        data = {'project_id':project_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Project Popup


@login_required()
def AutofillMessage(request, pk):
    from django.contrib.auth import get_user_model
    from users.models import CustomUser
    AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
    #user = get_user_model()
    User = CustomUser

    info = get_object_or_404(User, pk=pk)
#    info2 = get_object_or_404(AUTH_USER_MODEL, pk=pk)
    form = ComposeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.recipient = info
            new.sender = request.User
            new.save()
            return redirect('Project:DetailExperienceOnProject')
    else:
        context = {'info':info, 'form':form,}
        template = 'django_messages/compose.html'
        return render(request, template, context)
