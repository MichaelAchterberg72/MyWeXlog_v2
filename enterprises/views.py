from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from django.views.generic import (
        TemplateView
)

from csp.decorators import csp_exempt
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from locations.models import Region
from .models import *
from .forms import *

# Create your views here.
class EnterpriseHomeView(TemplateView):
    template_name = 'enterprises/home.html'


@login_required
@csp_exempt
def EnterpriseCreatePopupView(request):
    form = EnterpriseAddForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance=form.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_enterprise");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template_name = 'enterprises/create_new_enterprise_popup.html'
        return render(request, template_name, context)


@login_required
@csp_exempt
def BranchTypeCreatePopupView(request):
    form = BranchTypeAddForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance=form.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_type");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template_name = 'enterprises/create_new_enterprise_popup.html'
        return render(request, template_name, context)


@login_required
@csp_exempt
def IndustryCreatePopupView(request):
    form = IndustryAddForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance=form.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_industry");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template_name = 'enterprises/create_new_industry_popup.html'
        return render(request, template_name, context)


@login_required
def EnterpriseListView(request):
    list = Enterprise.objects.all().order_by('name')
    template_name = 'enterprises/enterprises_list.html'
    paginate_by = 10  # if pagination is desired'
    context = {
            'list': list,
    }
    return render(request, template_name, context)


@login_required()
@csp_exempt
def BranchAddView(request):
    if request.method =='POST':
        form = BranchAddForm(request.POST or None)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return redirect(reverse('Enterprise:EnterpriseHome'))
    else:
        form = BranchAddForm()

    template_name = 'enterprises/branch_add.html'
    context = {'form': form}
    return render(request, template_name, context)


def EnterpriseSearch(request):
    form = EnterpriseSearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = EnterpriseSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Enterprise.objects.annotate(
                search=SearchVector('name', 'description', 'website',),
            ).filter(search=query)

    template_name= 'enterprises/enterprise_search.html'
    context = {
            'form': form,
            'query': query,
            'results': results
    }
    return render(request, template_name, context)


def BranchSearch(request):
    form = BranchSearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = BranchSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Branch.objects.annotate(
                search=SearchVector('enterprise', 'name', 'type', 'country', 'region', 'city', 'suburb', 'industry',),
            ).filter(search=query)

    template_name= 'enterprises/branch_search.html'
    context = {
            'form': form,
            'query': query,
            'results': results
    }
    return render(request, template_name, context)
