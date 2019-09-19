from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db.models import Count, Sum
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
from talenttrack.models import WorkExperience, PreLoggedExperience
from django_messages.models import Message

from .forms import ProjectAddForm, ProjectSearchForm, ProjectForm
from django_messages.forms import ComposeForm

# Create your views here.
@login_required
def ProjectListHome(request):
    pcount = ProjectData.objects.all().aggregate(sum_p=Count('name'))
    projects = ProjectData.objects.all().order_by('-company')

    template_name = 'project/project_home.html'
    context = {'pcount': pcount, 'projects': projects}
    return render(request, template_name, context)


@login_required
def ProjectList(request, profile_id=None):
    profile_id = request.user
    pcount = WorkExperience.objects.filter(talent=profile_id).aggregate(sum_p=Count('company'))
    projects = WorkExperience.objects.filter(talent=profile_id).order_by('date_to')

    template_name = 'project/project_home.html'
    context = {'pcount': pcount, 'projects': projects,}
    return render(request, template_name, context)


@login_required()
def ProjectDetailView(request, project_id):
    info = get_object_or_404(ProjectData, pk=project_id)
    detail = ProjectData.objects.filter(pk=project_id)
    hr = WorkExperience.objects.filter(project=project_id).aggregate(sum_t=Sum('hours_worked'))

    template_name = 'project/project_detail.html'
    context = {'detail': detail, 'info': info, 'hr': hr,}
    return render(request, template_name, context)


@login_required()
@csp_exempt
def ProjectEditView(request, e_id):
    info2 = ProjectData.objects.get(pk=e_id)
    form = ProjectForm(request.POST or None, instance=info2)
    if request.method == 'POST':
        next_url=request.POST.get('next','/')
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = redirect(reverse('Project:ProjectHome', kwargs={'e_id':e_id}))
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

    template_name = 'Project/project_add.html'
    context = {'form': form}
    return render(request, template_name, context)


@login_required
def ProjectListView(request):
    list = ProjectData.objects.all().order_by('name')
    template_name = 'project/projects_list.html'
    paginate_by = 10  # if pagination is desired'
    context = {
            'list': list,
    }
    return render(request, template_name, context)


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
                                    'company__name',
                                    'industry__industry',
                                    'country',
                                    'region__region',
                                    'city__city'),
            ).filter(search=query)

    template_name= 'project/project_search.html'
    context = {
            'form': form,
            'query': query,
            'results': results
    }
    return render(request, template_name, context)


@login_required
def HoursWorkedOnProject(request, project_id):
    projectdata = get_object_or_404(ProjectData, pk=project_id)
    info = WorkExperience.objects.filter(project=project_id).annotate(sum_hours=Sum('hours_worked')).order_by('date_to')
    hr = WorkExperience.objects.filter(project=project_id).aggregate(sum_t=Sum('hours_worked'))

    template_name = 'project/hours_worked_on_project.html'
    context = {
            'projectdata': projectdata,
            'info': info,
            'hr': hr,
    }
    return render(request, template_name, context)

"""
@login_required
def HoursWorkedOnProject(request, project_id):
    projectdata = get_object_or_404(ProjectData, pk=project_id)
    info = WorkExperience.objects.filter(project=project_id).annotate(sum_hours=Sum('hours_worked')).order_by('date_to')
    info2 = PreLoggedExperience.objects.filter(project=project_id).annotate(sum_hours=Sum('hours_worked')).order_by('date_to')
    hr = WorkExperience.objects.filter(project=project_id).aggregate(sum_t=Sum('hours_worked'))
    hr2 = PreLoggedExperience.objects.filter(project=project_id).aggregate(sum_t2=Sum('hours_worked'))
    infocombined = sorted(list(chain(info, info2)),)
    combined = sorted(list(chain(hr, hr2)))
#    total_sum = hr + hr2

    template_name = 'project/hours_worked_on_project.html'
    context = {
            'projectdata': projectdata,
            'info': info,
            'info2': info2,
            'hr': hr,
            'hr2': hr2,
            'combined': combined,
            'infocombined': infocombined
    }
    return render(request, template_name, context)
"""

@login_required
def EmployeesOnProject(request, workexperience_id):
    projectdata = get_object_or_404(ProjectData, pk=project_id)
    info = WorkExperience.objects.filter(project=project_id).annotate('talent').order_by('talent')
    employee = Users.objects.filter(project=project_id)

    template_name = 'project/employees_worked_on_project.html'
    context = {
            'projectdata': projectdata,
            'info': info,
            'employee': employee
    }
    return render(request, template_name, context)


@login_required
def WorkExperienceDetail(request, workexperience_id):
    info = get_object_or_404(WorkExperience, pk=workexperience_id)
    detail = WorkExperience.objects.filter(pk=workexperience_id)

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


@csrf_exempt
def get_project_id(request):
    if request.is_ajax():
        project = request.Get['project']
        project_id = ProjectData.objects.get(name = project).id
        data = {'project_id':project_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Project Popup


def AutofillMessage(request, pk):
    info = get_object_or_404(settings.AUTH_USER_MODEL, pk=pk)
    form = ComposeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.recipient = info
            new.sender = request.user
            new.save()
            return redirect('Project:DetailExperienceOnProject')
    else:
        context = {'info':info, 'form':form,}
        template = 'django_messages/compose.html'
        return render(request, template, context)
