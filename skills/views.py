from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q, Sum, Min, Max
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from core.decorators import subscription

from db_flatten.models import SkillTag
from talenttrack.models import WorkExperience
from users.models import CustomUser
from marketplace.models import SkillRequired
from enterprises.models import Branch
from locations.models import Region
from WeXlog.app_config import skill_pass_score
from Profile.models import PhysicalAddress
from django_countries import countries


from .forms import SkillFilterInputForm


@login_required()
@subscription(1)
def skill_detail(request, skl):
    '''The the top 5 people and companies with the selected skill'''
    skill = SkillTag.objects.get(id=skl)

    qs = CustomUser.objects.filter(workexperience__skills__id=skl,
                                          workexperience__score__gte=3,
                                          workexperience__edt=False)

    hours1 = qs.annotate(sum=Sum('workexperience__hours_worked'),
                       min=Min('workexperience__date_from'),
                       max=Max('workexperience__date_to'))
    hours = hours1[:5]
    tally = hours1.count()
    filter = 'on'

    range = qs.aggregate(range_sum=Sum('workexperience__hours_worked'),
                       range_min=Min('workexperience__date_from'),
                       range_max=Max('workexperience__date_to'),
                      )
    qs_demand = Branch.objects.filter(talentrequired__skillrequired__skills__id=skl).annotate(demand_count=Count('talentrequired'))

    template = 'skills/skill_detail.html'
    context = {'hours': hours, 'skill': skill, 'range': range, 'tally': tally, 'qs_demand': qs_demand, 'filter': filter}
    return render (request, template, context)


@login_required()
@subscription(1)
def skill_detail_full(request, skl):
    '''The full list of all people with the selected skill'''
    skill = SkillTag.objects.get(id=skl)

    qs = CustomUser.objects.filter(workexperience__skills__id=skl,
                                          workexperience__score__gte=3,
                                          workexperience__edt=False)

    hours1 = qs.annotate(sum=Sum('workexperience__hours_worked'),
                       min=Min('workexperience__date_from'),
                       max=Max('workexperience__date_to')).order_by('-sum')
    hours = hours1
    tally = hours1.count()
    filter = 'off'

    range = qs.aggregate(range_sum=Sum('workexperience__hours_worked'),
                       range_min=Min('workexperience__date_from'),
                       range_max=Max('workexperience__date_to'),
                      )

    qs_demand = Branch.objects.filter(talentrequired__skillrequired__skills__id=skl).annotate(demand_count=Count('talentrequired')).order_by('-demand_count')

    template = 'skills/skill_detail.html'
    context = {'hours': hours, 'skill': skill, 'range': range, 'tally': tally, 'qs_demand': qs_demand, 'filter': filter}
    return render (request, template, context)


def is_valid_queryparam(param):
    '''function to check if query fields has a value entered '''
    return param != '' and param is not None

def get_talent(qs_l):
    '''function to filter the talent that lives in a certain country or region before being processed through the skills filter '''

    tlt = qs_l.distinct('talent').values_list('id', flat=True)
    qs_tlt = CustomUser.objects.filter(id__in=tlt)

    return qs_tlt

@login_required()
def skill_form_filter_view(request):
    '''Generating the view for the skills filter form'''
    form = SkillFilterInputForm()

    qs_country = request.GET.get('country')
    qs_region = request.GET.get('region')
    qs_skill1 = request.GET.get('skill1')
    qs_skill2 = request.GET.get('skill2')
    qs_skill3 = request.GET.get('skill3')
    qs_skill4 = request.GET.get('skill4')

    skill_1 = []
    qs_1a = []
    qs_1c = 0
    skill_2 = []
    qs_2a = []
    qs_2c = 0
    skill_3 = []
    qs_3a = []
    qs_3c = 0
    skill_4 = []
    qs_4a = []
    qs_4c = 0
    msg = ''
    region = 1
    country =''


    skills = SkillTag.objects.all()
    if is_valid_queryparam(qs_skill1):
        skill_1 = skills.get(id=qs_skill1)

    if is_valid_queryparam(qs_skill2):
        skill_2 = skills.get(id=qs_skill2)

    if is_valid_queryparam(qs_skill3):
        skill_3 = skills.get(id=qs_skill3)

    if is_valid_queryparam(qs_skill4):
        skill_4 = skills.get(id=qs_skill4)


    if is_valid_queryparam(qs_country):
        qs_l = PhysicalAddress.objects.filter(country__iexact=qs_country)
        country = dict(countries)[qs_country]

        if is_valid_queryparam(qs_region):
            qs_l = qs_l.filter(region__id = qs_region)
            region = Region.objects.get(id=qs_region)

    elif is_valid_queryparam(qs_region):
            qs_l = PhysicalAddress.objects.filter(region__id = qs_region)
            qs_lc = qs_l.count()
            region = Region.objects.get(id=qs_region)

    if is_valid_queryparam(qs_country) or is_valid_queryparam(qs_region):
        if is_valid_queryparam(qs_skill1):
            qs_1 = get_talent(qs_l).filter(Q(workexperience__skills__in=qs_skill1) & Q(workexperience__score__gte=3))
            qs_1a = qs_1.annotate(sum_1=Sum('workexperience__hours_worked'), max_1=Max('workexperience__date_to'), min_1=Min('workexperience__date_from')).order_by('-sum_1')
            qs_1c = qs_1a.count()

            if is_valid_queryparam(qs_skill2):
                qs_2 = qs_1.filter(Q(workexperience__skills__in=qs_skill2) & Q(workexperience__score__gte=3))
                qs_2a = qs_2.annotate(sum_2=Sum('workexperience__hours_worked'), max_2=Max('workexperience__date_to'), min_2=Min('workexperience__date_from')).order_by('-sum_2')
                qs_2c = qs_2a.count()

                if is_valid_queryparam(qs_skill3):
                    qs_3 = qs_2.filter(Q(workexperience__skills__in=qs_skill3) & Q(workexperience__score__gte=3))
                    qs_3a = qs_3.annotate(sum_3=Sum('workexperience__hours_worked'), max_3=Max('workexperience__date_to'), min_3=Min('workexperience__date_from')).order_by('-sum_3')
                    qs_3c = qs_3a.count()

                    if is_valid_queryparam(qs_skill4):
                        qs_4 = qs_3.filter(Q(workexperience__skills__in=qs_skill4) & & Q(workexperience__score__gte=3))
                        qs_4a = qs_4.annotate(sum_4=Sum('workexperience__hours_worked'), max_4=Max('workexperience__date_to'), min_4=Min('workexperience__date_from')).order_by('-sum_4')
                        qs_4c = qs_4a.count()
        else:
            msg = 'Please enter a value for "Skill 1"'
    else:
        if is_valid_queryparam(qs_skill1):
            qs_1 = CustomUser.objects.filter(Q(workexperience__skills__in=qs_skill1) & Q(workexperience__score__gte=3))
            qs_1a = qs_1.annotate(sum_1=Sum('workexperience__hours_worked'), max_1=Max('workexperience__date_to'), min_1=Min('workexperience__date_from')).order_by('-sum_1')
            qs_1c = qs_1a.count()

            if is_valid_queryparam(qs_skill2):
                qs_2 = qs_1.filter(Q(workexperience__skills__in=qs_skill2) & Q(workexperience__score__gte=3))
                qs_2a = qs_2.annotate(sum_2=Sum('workexperience__hours_worked'), max_2=Max('workexperience__date_to'), min_2=Min('workexperience__date_from')).order_by('-sum_2')
                qs_2c = qs_2a.count()

                if is_valid_queryparam(qs_skill3):
                    qs_3 = qs_2.filter(Q(workexperience__skills__in=qs_skill3) & Q(workexperience__score__gte=3))
                    qs_3a = qs_3.annotate(sum_3=Sum('workexperience__hours_worked'), max_3=Max('workexperience__date_to'), min_3=Min('workexperience__date_from')).order_by('-sum_3')
                    qs_3c = qs_3a.count()

                    if is_valid_queryparam(qs_skill4):
                        qs_4 = qs_3.filter(Q(workexperience__skills__in=qs_skill4) & Q(workexperience__score__gte=3))
                        qs_4a = qs_4.annotate(sum_4=Sum('workexperience__hours_worked'), max_4=Max('workexperience__date_to'), min_4=Min('workexperience__date_from')).order_by('-sum_4')
                        qs_4c = qs_4a.count()
        else:
            msg = 'Please enter a value for "Skill 1"'

    template = 'skills/skills_form_filter.html'
    context = {'form': form,
               'skill_1': skill_1, 'qs_1': qs_1a, 'qs_1c': qs_1c,
               'skill_2': skill_2, 'qs_2': qs_2a, 'qs_2c': qs_2c,
               'skill_3': skill_3, 'qs_3': qs_3a, 'qs_3c': qs_3c,
               'skill_4': skill_4, 'qs_4': qs_4a, 'qs_4c': qs_4c,
               'msg': msg, 'country': country, 'region': region
               }
    return render(request, template, context)

@login_required()
def ajax_region_field(request):
    if request.is_ajax():
        qry = request.GET.get('term')
        print(qry)
        region = Region.objects.filter(region__icontains=qry)

        response_content = list(region.values('id', 'region'))

        return JsonResponse(response_content, safe=False)


@login_required()
def ajax_skill_field(request):
    if request.is_ajax():
        qry = request.GET.get('term')
        print(qry)
        skill_qs = SkillTag.objects.filter(skill__icontains=qry)

        response_content = list(skill_qs.values('id', 'skill'))

        return JsonResponse(response_content, safe=False)
