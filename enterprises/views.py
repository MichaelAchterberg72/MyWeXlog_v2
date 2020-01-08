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


@login_required()
def EnterpriseHome(request):
    ecount = Enterprise.objects.all().aggregate(sum_e=Count('name'))
    bcount = Branch.objects.all().aggregate(sum_b=Count('name'))
    company = Enterprise.objects.all()

    template = 'enterprises/enterprise_home.html'
    context = {'ecount': ecount, 'bcount': bcount, 'company': company,}
    return render(request, template, context)


@login_required()
def BranchListView(request, c_id):
    list = Branch.objects.filter(company=c_id).order_by('name')
    detail = get_object_or_404(Enterprise, pk=c_id)
    template = 'enterprises/branch_list.html'
    context = {'list': list, 'detail': detail}
    return render(request, template, context)


@login_required()
def BranchDetailView(request, branch_id):
    info = get_object_or_404(Branch, pk=branch_id)
    detail = Branch.objects.filter(pk=branch_id)

    template = 'enterprises/branch_detail.html'
    context = {'detail': detail, 'info': info}
    return render(request, template, context)


@login_required()
@csp_exempt
#this view autopopulated the ebterprise field with the id in e_id
def BranchAddView(request, e_id):
    form = BranchForm(request.POST or None)
    if request.method == 'POST':

        info = get_object_or_404(Enterprise, pk=e_id)
        next_url=request.POST.get('next','/')
        if form.is_valid():
            #response = redirect(reverse('Enterprise:BranchList', kwargs={'e_id':e_id}))
            #response = redirect('Enterprise:EnterpriseHome')
            new = form.save(commit=False)
            new.company = info
            new.save()
            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Enterprise:BranchList', kwargs={'e_id':e_id})
            response = HttpResponseRedirect(next_url)
            #response._csp_exempt = True
            #return redirect(reverse('Enterprise:BranchList', kwargs={'e_id':e_id}),)
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
            response = HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_companybranch");</script>' % (instance.pk, instance))
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
def BranchEditView(request, e_id):
    info2 = Branch.objects.get(pk=e_id)
    form = BranchForm(request.POST or None, instance=info2)
    if request.method == 'POST':
        next_url=request.POST.get('next','/')
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = redirect(reverse('Profile:ProfileView', kwargs={'e_id':e_id}))
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
