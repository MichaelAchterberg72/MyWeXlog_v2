from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db.models import Count, Sum, F, Q, Avg, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User

from django.views.generic import (
        TemplateView
    )

from itertools import chain
from operator import attrgetter

from csp.decorators import csp_exempt
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.conf import settings

from locations.models import Region
from .models import *
from Profile.models import Profile
from talenttrack.models import WorkExperience
from enterprises.models import Enterprise, Branch

from .forms import (
    ProjectAddForm, ProjectSearchForm, ProjectForm, ProjectPersonalDetailsForm, ProjectPersonalDetailsTaskForm, ProjectPersonalDetailsTaskBillingForm, EditProjectTaskBillingForm
)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required()
def ProjectHome(request):
    tlt = request.user
    projects_qs = WorkExperience.objects.filter(talent=tlt).values('project', 'companybranch')
    prj_list = [dict(t) for t in {tuple(d.items()) for d in projects_qs}]

    tlt_prj_list=[]
    for item in prj_list:
        prj_pk = item['project']
        cob_pk = item['companybranch']
        if prj_pk == None:
            pass
        else:
            prj_qs = ProjectData.objects.get(pk=prj_pk)
            prj = prj_qs.name
            prj_slug = prj_qs.slug
            brch_qs = Branch.objects.get(pk=cob_pk)
            bch = brch_qs.name
            bch_slug = brch_qs.slug
            co = brch_qs.company.ename
            co_slug = brch_qs.company.slug
            industry = prj_qs.industry.industry
            city = prj_qs.city.city

            result={'project': prj, 'prj_slug': prj_slug, 'company': co, 'co_slug': co_slug, 'branch': bch, 'bch_slug': bch_slug, 'industry': industry, 'city': city}
            tlt_prj_list.append(result)

            pcount = len(tlt_prj_list)


    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(tlt_prj_list, 20)

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

    template_name = 'project/personal_projects.html'
    context = {'pcount': pcount, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template_name, context)


@login_required()
def ProjectPersonalDetailsView(request, prj, co, bch):
    project = ProjectData.objects.get(slug=prj)
    pr_c_i = Enterprise.objects.get(slug=co)
    pr_b_i = Branch.objects.get(slug=bch)

    p_instance, _ = ProjectPersonalDetails.objects.get_or_create(
            talent=request.user,
            project=project,
            company=pr_c_i,
            companybranch=pr_b_i)

    ptl = ProjectTaskBilling.objects.filter(ppdt__ppd=p_instance, ppdt__current=True, current=True).order_by('date_start')

    if request.method == 'POST':
        form = ProjectPersonalDetailsForm(request.POST, instance=p_instance)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return redirect(reverse('Project:ProjectHome'))
    else:
        form = ProjectPersonalDetailsForm(instance=p_instance)
        template_name = 'project/personal_detail.html'
        context = {'form': form, 'project': project, 'pr_c_i': pr_c_i, 'pr_b_i': pr_b_i, 'ptl': ptl, 'instance': p_instance, 'prj': prj, 'co': co, 'bch': bch}
        return render(request, template_name, context)


login_required()
def not_current_task(request, pb, prj, co, bch):
    '''Make a project task not current'''
    pb_qs = ProjectTaskBilling.objects.get(pk=pb)
    pt_pk = pb_qs.ppdt.pk
    pt_qs = ProjectPersonalDetailsTask.objects.get(pk=pt_pk)

    if request.method =='POST':
        if 'yes' in request.POST:
            pt_qs.current=True
            pt_qs.date_end=None
            pb_qs.date_end=None
            pt_qs.save()
            pb_qs.save()
        elif 'no' in request.POST:
            pt_qs.current=False
            pt_qs.date_end=timezone.now()
            pb_qs.date_end=timezone.now()
            pt_qs.save()
            pb_qs.save()

        return redirect(reverse('Project:ProjectPersonal', kwargs={'prj': prj, 'co': co, 'bch': bch}))


@login_required
def edit_billing_rate_pd(request, pb, ppdts, prj, co, bch):
    pb_qs = ProjectTaskBilling.objects.get(pk=pb)
    ppdt_qs = ProjectPersonalDetailsTask.objects.get(slug=ppdts)

    form = ProjectPersonalDetailsTaskBillingForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.ppdt = ppdt_qs
            query = new.cleaned_data['date_start']
            pb_qs.current = False
            pb_qs.date_end = query - datetime.timedelta(days=1)
            new.save()
            pb_qs.save()
            return redirect(reverse('Project:ProjectPersonal', kwargs={'prj': prj, 'co': co, 'bch': bch}))
        else:
            template_name = 'project/edit_project_task_billing.html'
            context = {'form': form, 'prj': prj, 'co': co, 'bch': bch}
            return render(request, template_name, context)
    else:
        template_name = 'project/edit_project_task_billing.html'
        context = {'form': form, 'prj': prj, 'co': co, 'bch': bch}
        return render(request, template_name, context)


@login_required
def edit_billing_rate_fl(request, pb, ppds, ppdts, prj, co, bch):
    pb_qs = ProjectTaskBilling.objects.get(pk=pb)
    ppdt_qs = ProjectPersonalDetailsTask.objects.get(slug=ppds)

    form = ProjectPersonalDetailsTaskBillingForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.ppdt = ppdt_qs
            query = new.cleaned_data['date_start']
            pb_qs.current = False
            pb_qs.date_end = query - datetime.timedelta(days=1)
            new.save()
            pb_qs.save()
            return redirect(reverse('Project:ProjectTaskList', kwargs={'ppds': ppdts, 'prj': prj, 'co': co, 'bch': bch}))
        else:
            template_name = 'project/edit_project_task_billing.html'
            context = {'form': form, 'prj': prj, 'co': co, 'bch': bch}
            return render(request, template_name, context)
    else:
        template_name = 'project/edit_project_task_billing.html'
        context = {'form': form, 'prj': prj, 'co': co, 'bch': bch}
        return render(request, template_name, context)


@login_required
def action_project_tasks(request, ppds, prj, co, bch):
    """View to activate or deactivate project tasks"""
    ptl = ProjectTaskBilling.objects.filter(ppdt__ppd__slug=ppds,  current=True).order_by('-date_start')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(ptl, 20)

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

    template_name = 'project/action_project_task.html'
    context = {'pageitems': pageitems, 'page_range': page_range, 'ppds': ppds,  'prj': prj, 'co': co, 'bch': bch}
    return render(request, template_name, context)


login_required()
def action_current_task(request, pb, ppds, prj, co, bch):
    '''action a project task for current or not current'''
    pb_qs = ProjectTaskBilling.objects.get(pk=pb)
    pt_pk = pb_qs.ppdt.pk
    pt_qs = ProjectPersonalDetailsTask.objects.get(pk=pt_pk)

    if request.method =='POST':
        if 'yes' in request.POST:
            pt_qs.current=True
            pt_qs.date_end=None
            pb_qs.date_end=None
            pt_qs.save()
            pb_qs.save()
        elif 'no' in request.POST:
            pt_qs.current=False
            pt_qs.date_end=timezone.now()
            pb_qs.date_end=timezone.now()
            pt_qs.save()
            pb_qs.save()

        return redirect(reverse('Project:ProjectTaskList', kwargs={'ppds': ppds, 'prj': prj, 'co': co, 'bch': bch}))


@login_required()
def ProjectListHome(request):
    pcount = ProjectData.objects.all().aggregate(sum_p=Count('name'))
    projects = ProjectData.objects.all().order_by('-company')

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

    template_name = 'project/project_home.html'
    context = {'pcount': pcount, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template_name, context)


@login_required()
def HelpProjectHomeView(request):
    template_name = 'project/help_project_home.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpProjectOverviewView(request):
    template_name = 'project/help_projects_overview.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpPersonalProjectView(request):
    template_name = 'project/help_personal_projects.html'
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

    template_name = 'project/project_detail.html'
    context = {'detail': detail, 'info': info, 'hr': hr, 'ppl': ppl}
    return render(request, template_name, context)


@login_required()
@csp_exempt
def ProjectEditView(request, prj):
    info2 = ProjectData.objects.get(slug=prj)
    form = ProjectForm(request.POST or None, instance=info2)
    if request.method == 'POST':
        next_url=request.POST.get('next','/')
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = redirect(reverse('Project:ProjectHome', kwargs={'prj':prj}))
            return HttpResponseRedirect(next_url)
    else:
        context = {'form': form}
        template_name = 'project/project_add.html'
        return render(request, template_name, context)


@login_required()
@csp_exempt
def ProjectAddView(request):
    if request.method =='POST':
        form = ProjectAddForm(request.POST or None)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return redirect(reverse('Project:ProjectHome'))
    else:
        form = ProjectAddForm()

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
                search=SearchVector('name',
                                    'company__branch',
                                    'industry__industry',
                                    'country',
                                    'region__region',
                                    'city__city'),
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

    form = ProjectAddForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_project");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'project/project_add_popup.html'
            return render(request, template, context)
    else:
        context = {'form':form,}
        template = 'project/project_add_popup.html'
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


@login_required()
@csp_exempt
def ProjectTaskAddView(request, ppd):
    qs = ProjectPersonalDetails.objects.get(slug=ppd)
    prj = qs.project.slug
    co = qs.companybranch.slug
    bch = qs.companybranch.company.slug

    form = ProjectPersonalDetailsTaskForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.talent = request.user
            instance.ppd = qs
            instance.company = qs.companybranch
            instance.save()
            ppdt=instance.slug
            return redirect(reverse('Project:AddProjectTaskBilling', kwargs={'ppdt':ppdt}))
        else:
            context = {'form': form, 'qs': qs, 'prj': prj, 'co': co, 'bch': bch}
            template = 'project/project_task.html'
            return render(request, template, context)
    else:
        context = {'form': form, 'qs': qs, 'prj': prj, 'co': co, 'bch': bch}
        template = 'project/project_task.html'
        return render(request, template, context)


@login_required()
@csp_exempt
def ProjectTaskBillingAddView(request, ppdt):
    qs = ProjectPersonalDetailsTask.objects.get(slug=ppdt)
    prj = qs.ppd.project.slug
    co = qs.ppd.companybranch.company.slug
    bch = qs.ppd.companybranch.slug

    form = ProjectPersonalDetailsTaskBillingForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.talent=request.user
            instance.ppdt=qs
            instance_start = instance.cleaned_data['start_date']
            instance_end = instance.cleaned_data['end_date']
            instance.save()
            qs.start_date=instance_start
            qs.end_date=instance_end
            qs.save()
            return redirect(reverse('Project:ProjectPersonal', kwargs={'prj': prj, 'co': co, 'bch': bch}))
        else:
            context = {'form': form, 'qs': qs, 'prj': prj, 'co': co, 'bch': bch}
            template = 'project/task_billing.html'
            return render(request, template, context)
    else:
        context = {'form': form, 'qs': qs, 'prj': prj, 'co': co, 'bch': bch}
        template = 'project/task_billing.html'
        return render(request, template, context)
