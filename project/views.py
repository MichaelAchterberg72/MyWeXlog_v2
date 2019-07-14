from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db.models import Count, Sum
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from django.views.generic import (
        TemplateView
)

from csp.decorators import csp_exempt
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from locations.models import Region
from .models import *
from Profile.models import Profile
from talenttrack.models import WorkExperience

from .forms import ProjectAddForm, ProjectSearchForm, ProjectForm

# Create your views here.
class ProjectHomeView(TemplateView):
    template_name = 'project/home.html'


@login_required
def ProjectListHome(request):
    pcount = ProjectData.objects.all().aggregate(sum_p=Count('name'))
    projects = ProjectData.objects.all().order_by('name')

    template_name = 'project/project_home.html'
    context = {'pcount': pcount, 'projects': projects,}
    return render(request, template_name, context)


@login_required()
def ProjectDetailView(request, project_id):
    info = get_object_or_404(ProjectData, pk=project_id)
    detail = ProjectData.objects.filter(pk=project_id)

    template_name = 'project/project_detail.html'
    context = {'detail': detail, 'info': info}
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


"""
@login_required()
@csp_exempt
def ProjectAdd(request, profile_id):
    detail = Project.objects.get(talent=profile_id)
    if detail.talent == request.user:
        form = ProjectAddForm(request.POST or None)
        if request.method =='POST':
            if form.is_valid():
                new=form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Project:ProjectHome', kwargs={'profile_id':profile_id}))
        else:
            template_name = 'Project/project_add.html'
            context = {'form': form}
            return render(request, template_name, context)
    else:
        raise PermissionDenied
"""

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
                search=SearchVector('name', 'company', 'industry', 'country', 'region', 'city'),
            ).filter(search=query)

    template_name= 'project/project_search.html'
    context = {
            'form': form,
            'query': query,
            'results': results
    }
    return render(request, template_name, context)


@login_required
def EmployeesOnProject(request, project_id):
#    pcount = WorkExperience.objects.filter('owner').aggregate(sum_p=Count('talent'))
#    employees = ProjectData.objects.filter('name').order_by('talent')
    projctdata = ProjectData.objects.all()

    template_name = 'project/employees_on_project.html'
    context = {
#            'pcount': pcount,
#            'employees': employees,
            'people': people
    }
    return render(request, template_name, context)


@login_required
def HoursWorkedOnProject(request, project_id):
    data = ProjectData.objects.get(pk=project_id)
    hr = WorkExperience.objects.filter(project=project_id).aggregate(sumt=Sum('hours_worked'))

    template_name = 'project/hours_worked_on_project0.html'
    context = {
            'data': data,
            'hr': hr
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
