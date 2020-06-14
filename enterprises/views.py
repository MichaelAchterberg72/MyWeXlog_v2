from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
import json
from django.db.models import Count
from django.contrib import messages

from core.decorators import app_role, subscription
from csp.decorators import csp_exempt


from .models import (
            Industry, Enterprise, BranchType, Branch, PhoneNumber,
            )


from .forms import (
    EnterprisePopupForm, BranchForm, PhoneNumberForm, IndustryPopUpForm, BranchTypePopUpForm, FullBranchForm
)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required()
def EnterpriseHome(request):
    bcount = Branch.objects.all().aggregate(sum_b=Count('name'))
    company = Enterprise.objects.all().order_by('name')
    ecount = company.aggregate(sum_e=Count('name'))

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(company, 20)

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

    template = 'enterprises/enterprise_home.html'
    context = {'ecount': ecount, 'bcount': bcount, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


@login_required()
@subscription(2)
def EmpRatingDetailView(request, bch):
    rte = Branch.objects.get(slug=bch)

    r_1 = rte.rate_1/100
    r_2 = rte.rate_2/100
    r_3 = rte.rate_3/100
    r_4 = rte.rate_4/100

    template = 'enterprises/rating_bch_detail.html'
    context = {'rte': rte, 'r_1': r_1, 'r_2': r_2, 'r_3': r_3, 'r_4': r_4,}
    return render(request, template, context)


@login_required()
def HelpEnterpriseHomeView(request):
    template_name = 'enterprises/help_enterprises_home.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpEnterpriseBranchView(request):
    template_name = 'enterprises/help_enterprises_branch_details.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpEnterpriseBranchListView(request):
    template_name = 'enterprises/help_enterprises_branch_list.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpAddEnterpriseView(request):

    context = {}
    template = 'enterprises/help_add_enterprise.html'
    return render(request, template, context)


@login_required()
def BranchListView(request, cmp):
    branches = Branch.objects.filter(company__slug=cmp).order_by('name')
    detail = get_object_or_404(Enterprise, slug=cmp)


    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(branches, 20)

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

    template = 'enterprises/branch_list.html'
    context = {'detail': detail, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


@login_required()
def BranchDetailView(request, bch):
    info = get_object_or_404(Branch, slug=bch)
    detail = Branch.objects.filter(slug=bch)

    r_a = detail[0].avg_rate
    r_c = detail[0].rate_count
    r_1 = detail[0].rate_1/100
    r_2 = detail[0].rate_2/100
    r_3 = detail[0].rate_3/100
    r_4 = detail[0].rate_4/100

    template = 'enterprises/branch_detail.html'
    context = {'detail': detail, 'info': info, 'r_1': r_1, 'r_2': r_2, 'r_3': r_3, 'r_4': r_4, 'r_a': r_a}
    return render(request, template, context)


@login_required()
@csp_exempt
def BranchEditView(request, bch):
    info2 = Branch.objects.get(slug=bch)
    form = BranchForm(request.POST or None, instance=info2)
    if request.method == 'POST':
        next_url=request.POST.get('next','/')
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = redirect(reverse('Profile:ProfileView', kwargs={'tlt':request.user.alias}))
            return HttpResponseRedirect(next_url)
        else:
            context = {'form': form}
            template = 'enterprises/branch_add.html'
            return render(request, template, context)

    else:
        context = {'form': form}
        template = 'enterprises/branch_add.html'
        return render(request, template, context)


@login_required()
@csp_exempt
#this view autopopulated the ebterprise field with the id in e_id
def BranchAddView(request, cmp):
    form = BranchForm(request.POST or None)
    if request.method == 'POST':

        info = get_object_or_404(Enterprise, slug=cmp)
        next_url=request.POST.get('next','/')
        if form.is_valid():
            new = form.save(commit=False)
            new.company = info
            new.save()
            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Enterprise:BranchList', kwargs={'cmp':cmp})
            response = HttpResponseRedirect(next_url)
            return response
        else:
            context = {'form': form}
            template = 'enterprises/branch_add.html'
            response =  render(request, template, context)
            return response

    else:
        context = {'form': form}
        template = 'enterprises/branch_add.html'
        response =  render(request, template, context)

        return response


#>>> Branch Popup
@login_required()
@csp_exempt
def BranchAddPopView(request):
    form = FullBranchForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            response = HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_branch");</script>' % (instance.pk, instance))
            return response
        else:
            context = {'form': form}
            template = 'enterprises/branch_popup.html'
            response = render(request, template, context)
            return response

    else:
        context = {'form': form}
        template = 'enterprises/branch_popup.html'
        response = render(request, template, context)
        return response


@csrf_exempt
def get_branch_id(request):
    if request.is_ajax():
        new_branch = request.Get['branch']
        branch_id = Branch.objects.get(branch = new_branch).id
        data = {'branch_id':branch_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#Branch Popup <<<


@login_required()
@csp_exempt
def FullBranchAddView(request):
    form = FullBranchForm(request.POST or None)
    if request.method == 'POST':
        next_url=request.POST.get('next','/')
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = redirect(reverse('Enterprise:BranchList'))
            return HttpResponseRedirect(next_url)
        else:
            context = {'form': form}
            template = 'enterprises/full_branch_add.html'
            return render(request, template, context)

    else:
        context = {'form': form}
        template = 'enterprises/full_branch_add.html'
        return render(request, template, context)


@login_required()
@csp_exempt
def EnterpriseAddView(request):
    form = EnterprisePopupForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return redirect('Enterprise:EnterpriseHome')
    else:
        context = {'form':form,}
        template = 'enterprises/enterprise_add.html'
        return render(request, template, context)


#>>>Company Popup
@login_required()
@csp_exempt
def EnterpriseAddPopup(request):
    form = EnterprisePopupForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_company");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'enterprises/enterprise_popup.html'
            return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'enterprises/enterprise_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_enterprise_id(request):
    if request.is_ajax():
        company = request.Get['company']
        company_id = Enterprise.objects.get(name = enterprise).id
        data = {'company_id':company_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Company Popup


#>>>Industry Popup
@login_required()
@csp_exempt
def IndustryAddPopup(request):
    form = IndustryPopUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_industry");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'enterprises/industry_popup.html'
            return render(request, template, context)
    else:
        context = {'form':form,}
        template = 'enterprises/industry_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_industry_id(request):
    if request.is_ajax():
        industry = request.Get['industry']
        industry_id = Industry.objects.get(industry = industry).id
        data = {'industry_id':industry_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Industry Popup


#>>>BranchType Popup
@login_required()
@csp_exempt
def BranchTypeAddPopup(request):
    form = BranchTypePopUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_type");</script>' % (instance.pk, instance))
        else:
                context = {'form':form,}
                template = 'enterprises/branchtype_popup.html'
                return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'enterprises/branchtype_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_branchtype_id(request):
    if request.is_ajax():
        branchtype = request.Get['branchtype']
        branchtype_id = BranchType.objects.get(type = branchtype).id
        data = {'branchtype_id':branchtype_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< BranchType Popup
