from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone, dateformat
from django.db.models import Count, Sum, F, Q, Avg
from dateutil.relativedelta import relativedelta
from django.utils.http import is_safe_url

import math
import json

from datetime import datetime


from core.decorators import corp_permission, subscription
from django.contrib.postgres.search import SearchVector, TrigramSimilarity
from django.db.models.functions import Greatest

from .models import (
    CorporateStaff, OrgStructure
    )
from .forms import (
    OrgStructureForm, AddStaffForm, StaffSearchForm, AdminTypeForm
)

from AppControl.models import (
    CorporateHR
)

from Profile.models import (
    BriefCareerHistory,
)

from marketplace.models import WorkLocation
from Profile.models import Profile
from talenttrack.models import WorkExperience


from WeXlog.app_config import (
    skill_pass_score, locked_age,
)


@login_required()
@corp_permission(1)
def org_department_dashboard(request, cor, dept):
    usr = request.user
    corp = CorporateStaff.objects.get(talent=usr)
    company = corp.corporate
    structure = OrgStructure.objects.filter(Q(corporate__slug=cor) & Q(level_name=dept))

    template = 'mod_corporate/dashboard_department.html'
    context = {'dept': dept}
    return render(request, template, context)

@login_required()
@corp_permission(1)
def staff_search(request, cor):
    '''Search in the staff_current.html'''
    qs = CorporateStaff.objects.filter(
        Q(corporate__slug=cor)
        ).select_related('talent')

    tlt = request.user

    l2 = qs.get(talent = tlt)

    if l2.corp_access >= 2:
        perm = 'granted'
    else:
        perm = 'denied'

    locked = qs.filter(unlocked=False)

    today = timezone.now().date()
    '''at least 1 month billed for each added user'''
    for ind in locked:
        age = (today - ind.date_modified).days
        if age > 32:
            ind.unlocked = True
            ind.save()
        else:
            pass

    form = StaffSearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = StaffSearchForm(request.GET)
        if form.is_valid():
            query=form.cleaned_data['query']
            results = qs.annotate(similarity=Greatest(
                TrigramSimilarity('talent__first_name', query),
                TrigramSimilarity('talent__last_name', query),
                )).filter(similarity__gt=0.3).order_by('-similarity')

    template = 'mod_corporate/staff_search.html'
    context = {'form': form, 'query': query, 'results': results, 'access': perm,}
    return render(request, template, context)


@login_required()
@corp_permission(1)
def dashboard_corporate(request):
    usr = request.user
    corp = CorporateStaff.objects.get(talent=usr)
    company = corp.corporate
    structure = OrgStructure.objects.filter(corporate=company)

    departments_link={}
    for item in structure:
        cor = item.corporate.slug
        dept = item.level_name
        departments_link[item]={'cor': cor, 'dept': dept}

    department_labels=[]
    for d in structure:
        dept = d.level_name
        department=[f'{dept}']
        department_labels.append(department)

    dpt_staff_data=[]
    for d in structure:
        staff = CorporateStaff.objects.filter(Q(corporate=company) & Q(department=d))
        current_staff = staff.values_list('talent__id', flat=True)
        if current_staff.count() >= 1:
            current_count = current_staff.count()
        else:
            current_count = 1
        staff = Profile.objects.filter(talent__id__in=current_staff)
        today = timezone.now().date()
        age={}
        for i in staff:
            staff_age=relativedelta(today, i.birth_date).years
            age={'staff_age': staff_age}
        total_age = sum(age.values())
        ave_age = total_age / current_count
        dpt_staff=ave_age
        dpt_staff_data.append(dpt_staff)

    staff = CorporateStaff.objects.filter(corporate=company)
    current_staff = staff.values_list('talent__id', flat=True)
    current_count = current_staff.count()

    staff = Profile.objects.filter(talent__id__in=current_staff)
    today = timezone.now().date()

    age={}
    for i in staff:
        staff_age=relativedelta(today, i.birth_date).years
        age={'staff_age': staff_age}

    total_age = sum(age.values())
    ave_age = [total_age / current_count]


    potential = BriefCareerHistory.objects.exclude(talent__id__in=current_staff).filter(Q(companybranch__company=company.company) & Q(date_to__isnull=True)).count()

    template = 'mod_corporate/dashboard_corporate.html'
    context = {
        'corp': corp,
        'potential': potential,
        'current_count': current_count,
        'department_labels': department_labels,
        'dpt_staff_data': dpt_staff_data,
        'departments_link': departments_link,
        'ave_age': ave_age,
        }
    return render(request, template, context)


@login_required()
@corp_permission(1)
def org_structure_view(request):
    '''A view of the levels in the corporate structure'''
    usr = request.user
    corp = CorporateStaff.objects.filter(talent=usr)

    corp_charts = {}
    for item in corp:
        chart = []
        pr = item.corporate
        structure = OrgStructure.objects.filter(corporate=pr).order_by('parent')
        for d in structure:
            dept = d.level_name
            if d.parent == None:
                parent = ''
            else:
                parent = d.parent
            tp = ''
            department=[f'{dept}', f'{parent}', f'{tp}']
            chart.append(department)

        corp_charts[item] = {'co': pr, 'chart': chart}

    template = 'mod_corporate/org_structure_view.html'
    context = {'structure': structure, 'corp_charts': corp_charts}
    return render(request, template, context)


@login_required()
@corp_permission(2)
def org_structure_add(request, cor):
    '''View to capture the company structure - only corporate administrators can edit the structure '''
    corp = get_object_or_404(CorporateHR, slug=cor)

    form = OrgStructureForm(request.POST or None, fil=corp)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.corporate = corp
            new.save()
            return redirect(reverse('Corporate:DashCorp'))
        else:
            template = 'mod_corporate/org_structure_add.html'
            context = {'form': form, 'corp': corp,}
            return render(request, template, context)
    else:
        template = 'mod_corporate/org_structure_add.html'
        context = {'form': form, 'corp': corp,}
        return render(request, template, context)


@login_required()
@corp_permission(1)
def staff_manage(request, cor):
    '''View the people who have listed the company as an employer, but have not been identified as staff'''
    #logit to test if limited to a companybranch
    staff = CorporateStaff.objects.filter(corporate__slug=cor).select_related('talent')

    staff_id = staff.values_list('talent__id', flat=True)

    corp = CorporateHR.objects.get(slug=cor)
    potential = BriefCareerHistory.objects.filter(Q(companybranch__company=corp.company) & Q(date_to__isnull=True)).order_by('talent__last_name')

    type = list(WorkLocation.objects.all().values_list('type', flat=True))

    template = 'mod_corporate/staff_manage.html'
    context = {'potential': potential, 'corp': corp, 'staff': staff, 'type': type, 'staff_id': staff_id,}

    return render(request, template, context)

@login_required()
@corp_permission(1)
def staff_include(request, cor, tlt):
    '''Add people to the company staff'''
    corp = get_object_or_404(CorporateHR,slug=cor)
    staff = get_object_or_404(Profile, alias=tlt)


    form = AddStaffForm(request.POST or None)
    template = 'mod_corporate/staff_include.html'
    context = {'form': form, 'staff': staff,}

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = staff.talent
            new.corporate = corp
            new.save()
            return redirect(reverse('Corporate:StaffManage',kwargs={'cor':cor,}))
        else:
            return render(request, template, context)
    else:
        return render(request, template, context)


@login_required()
@corp_permission(1)
def staff_actions(request):
    '''Actions from the Staff Admin template'''
    data = json.loads(request.body)
    staffSlug = data['staffSlug']
    action = data['action']

    staff_qs = CorporateStaff.objects.get(slug=staffSlug)

    if action == 'remove':
        staff_qs.resigned=True
        staff_qs.hide=True
        staff_qs.status=False

    elif action == 'admin':
        staff_qs.status=True

    staff_qs.save()

    return JsonResponse('Action Processed', safe=False)


@login_required()
@corp_permission(1)
def staff_current(request, cor):
    '''Lists the current staff members'''
    corp = get_object_or_404(CorporateHR, slug=cor)
    staff = CorporateStaff.objects.filter(corporate__slug=cor).filter(Q(hide=False) | Q(resigned=False)).select_related('talent').order_by('talent__last_name')
    staff_id = staff.values_list('talent__id')
    staff_c = staff.count()

    current = BriefCareerHistory.objects.filter(Q(companybranch__company=corp.company) & Q(talent__id__in=staff_id) & Q(date_to__isnull=True)).select_related('talent').order_by('talent__last_name')

    template = 'mod_corporate/staff_current.html'
    context = {'current': current, 'corp': corp, 'staff_c': staff_c,}
    return render(request, template, context)


@login_required()
@corp_permission(1)
def staff_admin(request, cor):
    '''Manages the staff (make admin, remove from staff, etc.)'''
    tlt = request.user
    corp = CorporateHR.objects.get(slug=cor)

    staff_qs = CorporateStaff.objects.filter(corporate__slug=cor).filter(Q(hide=False) | Q(resigned=False)).select_related('talent').order_by('talent__last_name')

    l2 = staff_qs.get(talent = tlt)

    if l2.corp_access >= 2:
        perm = 'granted'
    else:
        perm = 'denied'

    locked = staff_qs.filter(unlocked=False)

    today = timezone.now().date()
    '''at least 1 month billed for each added user'''
    for ind in locked:
        age = (today - ind.date_modified).days
        if age > 32:
            ind.unlocked = True
            ind.save()
        else:
            pass

    template = 'mod_corporate/staff_admin.html'
    context = {'staff_qs':staff_qs, 'access': perm, 'corp': corp,}
    return render(request, template, context)


@login_required()
@corp_permission(1)
def admin_staff(request, cor):
    corp = CorporateHR.objects.get(slug=cor)
    staff_qs = CorporateStaff.objects.filter(Q(corporate=corp) & Q(resigned=False) & Q(hide = False)).select_related('talent').order_by('talent__last_name')
    staff_c = staff_qs.count()
    usr = request.user
    usr_permission = staff_qs.get(talent=usr).corp_access
    #number of administrators determined by number of staff
    if staff_c <= 100:
        no_admin = 2
        no_cont = 1
    elif staff_c > 100 and staff_c < 2000:
        no_admin = 3
        no_cont = 2
    elif staff_c >=2000:
        no_admin = 2 + math.floor((staff_c-2000) / 5000)
        no_cont = 2 + math.floor((staff_c-2000) / 1500)
        if no_admin > 5:
            no_admin = 5
        if no_cont > 20:
            no_cont = 20

    admin_qs = staff_qs.filter(status=True)
    admin_c = admin_qs.filter(corp_access = 2).count()
    cont_c = admin_qs.filter(corp_access = 1).count()

    template = 'mod_corporate/admin_manage.html'
    context = {
        'admin_qs': admin_qs, 'admin_c': admin_c, 'cont_c': cont_c, 'no_admin': no_admin, 'no_cont': no_cont, 'staff_c': staff_c, 'usr_permission': usr_permission, 'corp': corp,
        }
    return render(request, template, context)


@login_required()
@corp_permission(2)
def admin_permission(request):

    data = json.loads(request.body)
    staffSlug = data['staffSlug']
    action = data['action']

    staff = CorporateStaff.objects.get(slug=staffSlug)

    if action == 'up':
        if staff.corp_access < 2:
            staff.corp_access += 1

    elif action == 'down':
        if staff.corp_access > 0:
            staff.corp_access -= 1

    elif action == 'remove':
        staff.corp_access = 0
        staff.status = False

    staff.save()

    return JsonResponse('Action Processed', safe=False)


@login_required()
@corp_permission(1)
def talent_hidden(request, cor):
    '''Lists the hidden/ignored users'''
    corp = get_object_or_404(CorporateHR, slug=cor)
    user = CorporateStaff.objects.filter(corporate__slug=cor).filter(Q(hide=True) | Q(resigned=True)).select_related('talent')
    user_id = user.values_list('talent__id')
    hidden_c = user.count()

    hidden = BriefCareerHistory.objects.filter(Q(companybranch__company=corp.company) & Q(talent__id__in=user_id) & Q(date_to__isnull=True)).select_related('talent').order_by('-date_from')


    template = 'mod_corporate/talent_hidden.html'
    context = {'hidden': hidden, 'corp': corp, 'hidden_c': hidden_c,}
    return render(request, template, context)


@login_required()
@corp_permission(1)
def hidden_actions(request):

    data = json.loads(request.body)
    tltAlias = data['tltAlias']
    action = data['action']

    staff = CorporateStaff.objects.get(talent__alias=tltAlias)

    if action == 'reinstate':
        staff.hide = False
        staff.resigned = False
        staff.unlicked = False

    staff.save()

    return JsonResponse('Action Processed', safe=False)


def experience_dashboard(request, cor):
    staff_qs = CorporateStaff.objects.filter(Q(corporate__slug=cor) & Q(hide=False)).select_related('talent')

    staff_list = staff_qs.values_list('talent__id', flat=True)
    we_qs = WorkExperience.objects.filter(Q(talent__id__in=staff_list) & Q(score__gte=skill_pass_score))

    #total experience and training hours (confirmed)
    corp_ehrs = we_qs.filter(edt=False).aggregate(exp_sum = Sum('hours_worked'))
    corp_thrs = we_qs.filter(edt=True).aggregate(trn_sum = Sum('topic__hours'))

    #count staff at each experience level

    #list all skills
    #count skills
    #sum hours for each skill
    #see skill age (possibly have a barchart with different colours for age)

    #list projects staff members have worked on.
    #sum the number of hours worked on the project.
