from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db.models import Count
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
                search=SearchVector('name', 'owner', 'industry', 'country', 'region', 'city'),
            ).filter(search=query)

    template_name= 'project/project_search.html'
    context = {
            'form': form,
            'query': query,
            'results': results
    }
    return render(request, template_name, context)
