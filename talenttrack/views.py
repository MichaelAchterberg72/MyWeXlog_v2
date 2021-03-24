from django.shortcuts import(
    render, get_object_or_404, redirect, render_to_response
    )
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import is_safe_url
from django.template.loader import get_template, render_to_string
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import PermissionDenied
import json
from django.db.models import Count, Sum, F, Q, Avg
from dateutil.relativedelta import relativedelta
from django.db.models.functions import Greatest
from decimal import Decimal
from django.contrib.postgres.search import SearchVector, TrigramSimilarity
import math
from .widgets import ListTextWidget

import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Subject, To, ReplyTo, SendAt, Content, From, CustomArg, Header)
from django.utils.html import strip_tags

from csp.decorators import csp_exempt
from core.decorators import subscription, corp_permission
from WeXlog.app_config import(
        client_score, lecturer_score, classmate_score, colleague_score, pre_colleague_score, collaborator_score, superior_score
        )


from .forms import (
        TopicForm, ResultForm, CourseTypeForm, CourseForm, DesignationForm, ClassMatesSelectForm, ClassMatesConfirmForm, LecturerSelectForm, LecturerConfirmForm, EducationForm, WorkExperienceForm, WorkColleagueSelectForm, WorkColleagueConfirmForm, WorkColleagueResponseForm, ClassMatesResponseForm, LecturerResponseForm, SuperiorSelectForm, WorkCollaboratorResponseForm, WorkCollaboratorConfirmForm, WorkCollaboratorSelectForm, WorkClientResponseForm, WorkClientConfirmForm, WorkClientSelectForm, PreLoggedExperienceForm, TopicPopForm, LecturerRespondForm, ClassMatesRespondForm, AchievementsForm, AwardsForm, PublicationsForm, LicenseCertificationForm, ProfileSearchForm, EmailFormModal, SiteSkillStatsFilter, SiteDemandSkillStatsFilter
)

from .models import (
        Lecturer, Course, ClassMates, WorkExperience, Superior, WorkCollaborator, WorkClient, WorkColleague, Designation, Achievements, Awards, Publications, LicenseCertification,
)

from db_flatten.models import SkillTag
from marketplace.models import(
    SkillLevel, SkillRequired, WorkBid, BidShortList, TalentRequired, BidInterviewList,
)
from enterprises.models import Branch, Industry
from locations.models import Region, City
from project.models import ProjectData
from Profile.models import (
        BriefCareerHistory, Profile, LanguageTrack, PhysicalAddress, WillingToRelocate
)
from booklist.models import ReadBy
from users.models import CustomUser
from mod_corporate.models import CorporateStaff
from invitations.models import Invitation

from WeXlog.app_config import (
    skill_pass_score, locked_age, client_score, lecturer_score, classmate_score,    colleague_score, pre_colleague_score, collaborator_score, superior_score
)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from analytics.signals import object_viewed_signal


@login_required()
def site_demand_skill_stats(request, skl):
    '''The view for the site wide skill demand overview and stats'''
    skill = SkillTag.objects.get(id=skl)
    tlt_instance = request.user
    today = timezone.now().date()


    val_we = TalentRequired.objects.all()
    skills_rec = SkillRequired.objects.all()

    #Skills associated with skill for datalist filter - includes all skills not just validated ones
    f_vac_id = val_we.values_list('pk')
    f_skill_we =  skills_rec.filter(Q(scope__pk__in=f_vac_id) & Q(skills__skill=skill.skill))
    f_skills_assoc_qs = f_skill_we.values_list('scope__pk', flat=True).distinct()

    f_vac_list_qs = val_we.filter(pk__in=f_skills_assoc_qs)
    f_vac_list_qs_id = f_vac_list_qs.values_list('pk').distinct()

    f_skill_des = val_we.filter(skillrequired__skills__pk=skl).values_list('designation__pk', flat=True).distinct()
    print(f_skill_des)

    form = SiteDemandSkillStatsFilter()
    form.fields['title'].widget = ListTextWidget(data_list=TalentRequired.objects.filter(pk__in=f_vac_list_qs_id).values_list('title', flat=True).distinct(), name='title-list')
    form.fields['designation'].widget = ListTextWidget(data_list=Designation.objects.filter(pk__in=f_skill_des).only('name'), name='designation-list')

    title_query = request.GET.get('title')
    designation_query = request.GET.get('designation')
    date_entered_query = request.GET.get('date_entered')
    date_to_query = request.GET.get('date_to')
    country_query = request.GET.get('country')
    worklocation_query = request.GET.get('worklocation')
    experience_level_query = request.GET.get('experience_level')

    if title_query != '' and title_query is not None:
        val_we = val_we.filter(title__icontains=title_query)

    if designation_query != '' and designation_query is not None:
        val_we = val_we.filter(designation__name__icontains=designation_query)

    if date_entered_query != '' and date_entered_query is not None:
        val_we = val_we.filter(date_entered__gte=date_entered_query)

    if date_to_query != '' and date_to_query is not None:
        val_we = val_we.filter(date_deadline__lte=date_to_query)

    if country_query != '' and country_query is not None:
        region = Region.objects.filter(country__icontains=country_query).values_list('pk', flat=True)
        city = City.objects.filter(region__pk__in=region).values_list('pk', flat=True)
        val_we = val_we.filter(city__pk__in=city)

    if worklocation_query != '' and worklocation_query is not None:
        val_we = val_we.filter(worklocation__type__icontains=worklocation_query)

    if experience_level_query != '' and experience_level_query is not None:
        val_we = val_we.filter(experience_level__level__icontains=experience_level_query)

    #Skills associated with skill - includes all skills not just validated ones
    vac_id = val_we.values_list('pk')
    skill_we =  skills_rec.filter(Q(scope__pk__in=vac_id) & Q(skills__skill=skill.skill))
    skills_assoc_qs = skill_we.values_list('scope__pk', flat=True).distinct()

    vac_list_qs = val_we.filter(pk__in=skills_assoc_qs)
    vac_list_qs_id = vac_list_qs.values_list('pk').distinct()
    vac_list_qs_count = vac_list_qs.count()

    skills_list = skills_rec.filter(scope__pk__in=vac_list_qs_id).values_list('skills__skill', flat=True).distinct()

    skills_list_set_all = [x for x in skills_list if x is not None]

    skills_list_set = [x for x in skills_list_set_all if x is not f'{skill.skill}']

    dept_skills_link = SkillTag.objects.filter(skill__in=skills_list_set).order_by('skill')

    skills_instance_count = []
    skill_list_labels = []
    skill_percentage_data = []
    for skill_item in skills_list_set:
        skill_count = 0
        vac_skills = skills_rec.filter(skills__skill=skill_item).values_list('scope__pk', flat=True)
        vac_skill = vac_list_qs.filter(pk__in=vac_skills)

        for vac_instance in vac_skill:
            skill_count +=1
        skill_percentage = int(format(skill_count / vac_list_qs_count * 100, '.0f'))

        result={'skill': skill_item, 'skill_count': skill_count, 'skill_percentage': skill_percentage}

        skills_instance_count.append(result)

        skill_list_labels.append(skill_item)
        skill_percentage_data.append(skill_percentage)

    skill_list_labels_count = skills_list.count()

    orderd_skills_instance_count = sorted(skills_instance_count, key=lambda kv: kv['skill_percentage'], reverse=True)

    template = 'talenttrack/site_demand_skill_stats.html'
    context = {
            'skl': skl,
            'skill': skill,
            'form': form,
            'vac_list_qs_count': vac_list_qs_count,
            'skill_list_labels_count': skill_list_labels_count,
            'skill_list_labels': skill_list_labels,
            'skill_percentage_data': skill_percentage_data,
            'dept_skills_link': dept_skills_link,
    }
    return render(request, template, context)


@login_required()
def site_skill_stats(request, skl):
    '''The view for the site wide skill overview and stats'''
    skill = SkillTag.objects.get(id=skl)
    tlt_instance = request.user
    today = timezone.now().date()


    val_we = WorkExperience.objects.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score))

    #Industries associated with skill for datalist filter - includes all skills not just validated ones
    f_skill_ind = val_we.filter(skills__pk=skl).values_list('industry__pk', flat=True).distinct()
    f_skill_des = val_we.filter(skills__pk=skl).values_list('designation__pk', flat=True).distinct()
    f_skill_region = val_we.filter(skills__pk=skl).values_list('talent__physicaladdress__region__pk', flat=True).distinct()


    form = SiteSkillStatsFilter()
    form.fields['industry'].widget = ListTextWidget(data_list=Industry.objects.filter(pk__in=f_skill_ind).only('industry'), name='industry-list')
    form.fields['designation'].widget = ListTextWidget(data_list=Designation.objects.filter(pk__in=f_skill_des).only('name'), name='designation-list')
    form.fields['region'].widget = ListTextWidget(data_list=Region.objects.filter(pk__in=f_skill_region).only('region'), name='region-list')

    industry_query = request.GET.get('industry')
    designation_query = request.GET.get('designation')
    date_from_query = request.GET.get('date_from')
    date_to_query = request.GET.get('date_to')
    country_query = request.GET.get('country')
    region_query = request.GET.get('region')

    if industry_query != '' and industry_query is not None:
        val_we = val_we.filter(industry__industry__icontains=industry_query)

    if designation_query != '' and designation_query is not None:
        val_we = val_we.filter(designation__name__icontains=designation_query)

    if date_from_query != '' and date_from_query is not None:
        val_we = val_we.filter(date_from__gte=date_from_query)

    if date_to_query != '' and date_to_query is not None:
        val_we = val_we.filter(date_to__lte=date_to_query)

    if country_query != '' and country_query is not None:
        country_profiles = PhysicalAddress.objects.filter(country__icontains=country_query).values_list('talent__id')
        val_we = val_we.filter(talent__id__in=country_profiles)

    if region_query != '' and region_query is not None:
        region_profiles = PhysicalAddress.objects.filter(region__region__icontains=region_query).values_list('talent__id')
        val_we = val_we.filter(talent__id__in=region_profiles)

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
#    print(orderd_skills_instance_count['skill'])

    template = 'talenttrack/site_skill_stats.html'
    context = {
            'skl': skl,
            'skill': skill,
            'form': form,
            'skills_list_qs_count': skills_list_qs_count,
            'skill_list_labels_count': skill_list_labels_count,
            'skill_list_labels': skill_list_labels,
            'skill_percentage_data': skill_percentage_data,
            'dept_skills_link': dept_skills_link,
    }
    return render(request, template, context)


@login_required()
def profile_skill_stats(request, skl):
    '''The view for the individual skill overview and stats'''
    skill = SkillTag.objects.get(id=skl)
    tlt_instance = request.user
    tlt = tlt_instance.alias
    tlt_id = [tlt_instance.id]
    today = timezone.now().date()

    we = WorkExperience.objects.filter(talent__alias=tlt)
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

#    print(skill_list_labels)
#    print(skill_percentage_data)
    orderd_skills_instance_count = sorted(skills_instance_count, key=lambda kv: kv['skill_percentage'], reverse=True)
#    print(orderd_skills_instance_count['skill'])



    we_skill = we.filter(Q(skills__skill=skill.skill, edt=False) | Q(topic__skills__skill=skill.skill, edt=True))
    val_we_skill = val_we.filter(Q(skills__skill=skill.skill, edt=False) | Q(topic__skills__skill=skill.skill, edt=True))



    # Total Work Experience Skill Sum Experience by Year
    val_we_skills_used_year_range_data = []
    val_we_skills_age_range=[]
    for i in tlt_id:
        we_qs = val_we_skill.filter(talent=i, edt=False)
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
    for i in tlt_id:
        t_we_qs = val_we_skill.filter(talent=i, edt=True)
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

    template = 'talenttrack/profile_skill_stats.html'
    context = {
            'tlt': tlt,
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
def skill_stats(request, skl):
    '''The view for the individual skill overview and stats'''
    skill = SkillTag.objects.get(id=skl)
    tlt_instance = request.user
    tlt = tlt_instance.alias
    tlt_id = [tlt_instance.id]
    today = timezone.now().date()

    we = WorkExperience.objects.filter(talent__alias=tlt)
    val_we = we.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score))

    #Skills associated with skill - includes all skills not just validated ones
    skill_we =  we.filter(skills__skill=skill.skill, edt=False)
    skills_assoc_qs = skill_we.values_list('pk', flat=True)

    skills_list_qs = we.filter(pk__in=skills_assoc_qs)
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

#    print(skill_list_labels)
#    print(skill_percentage_data)
    orderd_skills_instance_count = sorted(skills_instance_count, key=lambda kv: kv['skill_percentage'], reverse=True)
#    print(orderd_skills_instance_count['skill'])



    #work experience not validated
    n_val_we = we.filter(Q(skills__skill=skill.skill, edt=False) | Q(topic__skills__skill=skill.skill, edt=True))
    n_val_we_slug = n_val_we.values_list('slug', flat=True)

    wc_lt = Lecturer.objects.filter(Q(education__slug__in=n_val_we_slug) & Q(confirm='S')).values_list('lecturer__alias', flat=True).distinct('lecturer__alias')
    wc_ct = ClassMates.objects.filter(Q(education__slug__in=n_val_we_slug) & Q(confirm='S')).values_list('colleague__alias', flat=True).distinct('colleague__alias')
    wc_we = WorkColleague.objects.filter(Q(experience__slug__in=n_val_we_slug) & Q(confirm='S')).values_list('colleague_name__alias', flat=True).distinct('colleague_name__alias')
    wc_se = Superior.objects.filter(Q(experience__slug__in=n_val_we_slug) & Q(confirm='S')).values_list('superior_name__alias', flat=True).distinct('superior_name__alias')
    wc_wce = WorkCollaborator.objects.filter(Q(experience__slug__in=n_val_we_slug) & Q(confirm='S')).values_list('collaborator_name__alias', flat=True).distinct('collaborator_name__alias')
    wc_wcle = WorkClient.objects.filter(Q(experience__slug__in=n_val_we_slug) & Q(confirm='S')).values_list('client_name__alias', flat=True).distinct('client_name__alias')

    wc_lt_l = list(wc_lt)
    wc_ct_l = list(wc_ct)
    wc_we_l = list(wc_we)
    wc_se_l = list(wc_se)
    wc_wce_l = list(wc_wce)
    wc_wcle_l = list(wc_wcle)

    we_tn_l = list(wc_lt_l + wc_ct_l + wc_we_l + wc_se_l + wc_wce_l + wc_wcle_l)

    profile_slug_list_set=[]
    for x in we_tn_l:
        profile_slug_list_set.append(x)
    we_nvs_list_n = [x for x in profile_slug_list_set if x is not None]

    we_nvs_list = set(we_nvs_list_n)

    we_tbc_p_l = Profile.objects.filter(alias__in=we_nvs_list)
    we_tbc_p = we_tbc_p_l[:6]
    we_tbc_p_l_count = we_tbc_p_l.count()

    val_we_lts = n_val_we.filter(Q(talent__subscription__gte=1) & Q(score__lt=skill_pass_score))
    #Traing experience without sufficient pass score
    nsps_te_l = val_we_lts.select_related('topic').filter(edt=True).order_by('-date_from')
    nsps_te_l_count = nsps_te_l.count()
    nsps_te = nsps_te_l[:6]

    #Work experience without sufficient pass score
    nsps_we_l = val_we_lts.select_related('topic').filter(wexp=True).order_by('-date_from')
    nsps_we_l_count = nsps_we_l.count()
    nsps_we = nsps_we_l[:6]

    we_skill = we.filter(Q(skills__skill=skill.skill, edt=False) | Q(topic__skills__skill=skill.skill, edt=True))
    val_we_skill = val_we.filter(Q(skills__skill=skill.skill, edt=False) | Q(topic__skills__skill=skill.skill, edt=True))

    # Colleagues invited but not registered list
    invitation_sent = Invitation.objects.filter(Q(invited_by=tlt_instance) & Q(accpeted=False)).order_by('-date_invited')[:6]

    invitation_sent_count = invitation_sent.count()

    # Total Work Experience Skill Sum Experience by Year
    we_skills_used_year_range_data = []
    we_skills_age_range=[]
    for i in tlt_id:
        we_qs = we_skill.filter(talent=i, edt=False)
        for wet in we_qs:
            swewd = wet.date_to
            we_skill_age=relativedelta(today, swewd).years

            aw_exp = wet.hours_worked
            if aw_exp == None:
                awetv = 0
            else:
                awetv = aw_exp

            result={'we_skill_age': we_skill_age, 'awetv': awetv}

            we_skills_age_range.append(result)

    # Total hours experience in year range
    we_skill_age_range_0_1=[float(x['awetv']) for x in we_skills_age_range if x['we_skill_age'] in range(0, 1)]
    we_skill_age_range_1_2=[float(x['awetv']) for x in we_skills_age_range if x['we_skill_age'] in range(1, 2)]
    we_skill_age_range_2_3=[float(x['awetv']) for x in we_skills_age_range if x['we_skill_age'] in range(2, 3)]
    we_skill_age_range_3_4=[float(x['awetv']) for x in we_skills_age_range if x['we_skill_age'] in range(3, 4)]
    we_skill_age_range_4_5=[float(x['awetv']) for x in we_skills_age_range if x['we_skill_age'] in range(4, 5)]
    we_skill_age_range_5_6=[float(x['awetv']) for x in we_skills_age_range if x['we_skill_age'] in range(5, 6)]
    we_skill_age_range_6_7=[float(x['awetv']) for x in we_skills_age_range if x['we_skill_age'] in range(6, 7)]
    we_skill_age_range_7_8=[float(x['awetv']) for x in we_skills_age_range if x['we_skill_age'] in range(7, 8)]
    we_skill_age_range_8_9=[float(x['awetv']) for x in we_skills_age_range if x['we_skill_age'] in range(8, 9)]
    we_skill_age_range_9_10=[float(x['awetv']) for x in we_skills_age_range if x['we_skill_age'] in range(9, 10)]

    total_we_skill_age=[float(x['awetv']) for x in we_skills_age_range if x['we_skill_age'] in range(0, 100)]
    total_sum_we = sum(total_we_skill_age)

    sum_we_range_0_1 = sum(we_skill_age_range_0_1)
    sum_we_range_1_2 = sum(we_skill_age_range_1_2)
    sum_we_range_2_3 = sum(we_skill_age_range_2_3)
    sum_we_range_3_4 = sum(we_skill_age_range_3_4)
    sum_we_range_4_5 = sum(we_skill_age_range_4_5)
    sum_we_range_5_6 = sum(we_skill_age_range_5_6)
    sum_we_range_6_7 = sum(we_skill_age_range_6_7)
    sum_we_range_7_8 = sum(we_skill_age_range_7_8)
    sum_we_range_8_9 = sum(we_skill_age_range_8_9)
    sum_we_range_9_10 = sum(we_skill_age_range_9_10)

    we_skills_used_year_range_data.append(sum_we_range_9_10)
    we_skills_used_year_range_data.append(sum_we_range_8_9)
    we_skills_used_year_range_data.append(sum_we_range_7_8)
    we_skills_used_year_range_data.append(sum_we_range_6_7)
    we_skills_used_year_range_data.append(sum_we_range_5_6)
    we_skills_used_year_range_data.append(sum_we_range_4_5)
    we_skills_used_year_range_data.append(sum_we_range_3_4)
    we_skills_used_year_range_data.append(sum_we_range_2_3)
    we_skills_used_year_range_data.append(sum_we_range_1_2)
    we_skills_used_year_range_data.append(sum_we_range_0_1)

    # Total Work Experience Skill Sum Experience by Year
    val_we_skills_used_year_range_data = []
    val_we_skills_age_range=[]
    for i in tlt_id:
        we_qs = val_we_skill.filter(talent=i, edt=False)
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

    # Training Experience Skill Sum Experience by Year
    t_we_skills_used_year_range_data = []
    t_we_skills_age_range=[]
    for i in tlt_id:
        t_we_qs = we_skill.filter(talent=i, edt=True)
        for wet in t_we_qs:
            swewd = wet.date_to
            we_skill_age=relativedelta(today, swewd).years

            aw_exp = wet.topic.hours
            if aw_exp == None:
                awetv = 0
            else:
                awetv = aw_exp

            t_result={'we_skill_age': we_skill_age, 'awetv': awetv}

            t_we_skills_age_range.append(t_result)

    # Total hours experience in year range
    t_we_skill_age_range_0_1=[float(x['awetv']) for x in t_we_skills_age_range if x['we_skill_age'] in range(0, 1)]
    t_we_skill_age_range_1_2=[float(x['awetv']) for x in t_we_skills_age_range if x['we_skill_age'] in range(1, 2)]
    t_we_skill_age_range_2_3=[float(x['awetv']) for x in t_we_skills_age_range if x['we_skill_age'] in range(2, 3)]
    t_we_skill_age_range_3_4=[float(x['awetv']) for x in t_we_skills_age_range if x['we_skill_age'] in range(3, 4)]
    t_we_skill_age_range_4_5=[float(x['awetv']) for x in t_we_skills_age_range if x['we_skill_age'] in range(4, 5)]
    t_we_skill_age_range_5_6=[float(x['awetv']) for x in t_we_skills_age_range if x['we_skill_age'] in range(5, 6)]
    t_we_skill_age_range_6_7=[float(x['awetv']) for x in t_we_skills_age_range if x['we_skill_age'] in range(6, 7)]
    t_we_skill_age_range_7_8=[float(x['awetv']) for x in t_we_skills_age_range if x['we_skill_age'] in range(7, 8)]
    t_we_skill_age_range_8_9=[float(x['awetv']) for x in t_we_skills_age_range if x['we_skill_age'] in range(8, 9)]
    t_we_skill_age_range_9_10=[float(x['awetv']) for x in t_we_skills_age_range if x['we_skill_age'] in range(9, 10)]

    total_t_we_skill_age=[float(x['awetv']) for x in t_we_skills_age_range if x['we_skill_age'] in range(0, 100)]
    total_sum_t_we = sum(total_t_we_skill_age)

    sum_t_we_range_0_1 = sum(t_we_skill_age_range_0_1)
    sum_t_we_range_1_2 = sum(t_we_skill_age_range_1_2)
    sum_t_we_range_2_3 = sum(t_we_skill_age_range_2_3)
    sum_t_we_range_3_4 = sum(t_we_skill_age_range_3_4)
    sum_t_we_range_4_5 = sum(t_we_skill_age_range_4_5)
    sum_t_we_range_5_6 = sum(t_we_skill_age_range_5_6)
    sum_t_we_range_6_7 = sum(t_we_skill_age_range_6_7)
    sum_t_we_range_7_8 = sum(t_we_skill_age_range_7_8)
    sum_t_we_range_8_9 = sum(t_we_skill_age_range_8_9)
    sum_t_we_range_9_10 = sum(t_we_skill_age_range_9_10)

    t_we_skills_used_year_range_data.append(sum_t_we_range_9_10)
    t_we_skills_used_year_range_data.append(sum_t_we_range_8_9)
    t_we_skills_used_year_range_data.append(sum_t_we_range_7_8)
    t_we_skills_used_year_range_data.append(sum_t_we_range_6_7)
    t_we_skills_used_year_range_data.append(sum_t_we_range_5_6)
    t_we_skills_used_year_range_data.append(sum_t_we_range_4_5)
    t_we_skills_used_year_range_data.append(sum_t_we_range_3_4)
    t_we_skills_used_year_range_data.append(sum_t_we_range_2_3)
    t_we_skills_used_year_range_data.append(sum_t_we_range_1_2)
    t_we_skills_used_year_range_data.append(sum_t_we_range_0_1)

    # Training Validated Experience Skill Sum Experience by Year
    t_val_we_skills_used_year_range_data = []
    t_val_we_skills_age_range=[]
    for i in tlt_id:
        t_we_qs = val_we_skill.filter(talent=i, edt=True)
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

    template = 'talenttrack/skill_stats.html'
    context = {
            'tlt': tlt,
            'skl': skl,
            'skill': skill,
            'skills_list_qs_count': skills_list_qs_count,
            'skill_list_labels_count': skill_list_labels_count,
            'skill_list_labels': skill_list_labels,
            'skill_percentage_data': skill_percentage_data,
            'dept_skills_link': dept_skills_link,
            'nsps_te': nsps_te,
            'nsps_te_l_count': nsps_te_l_count,
            'nsps_we': nsps_we,
            'nsps_we_l_count': nsps_we_l_count,
            'skills_used_year_range_labels': skills_used_year_range_labels,
            'total_sum_t_we': total_sum_t_we,
            'total_val_sum_t_we': total_val_sum_t_we,
            'total_val_sum_we': total_val_sum_we,
            't_we_skills_used_year_range_data': t_we_skills_used_year_range_data,
            't_val_we_skills_used_year_range_data': t_val_we_skills_used_year_range_data,
            'total_sum_we': total_sum_we,
            'we_skills_used_year_range_data': we_skills_used_year_range_data,
            'val_we_skills_used_year_range_data': val_we_skills_used_year_range_data,
            'we_tbc_p': we_tbc_p,
            'we_tbc_p_l_count': we_tbc_p_l_count,
            'invitation_sent': invitation_sent,
            'invitation_sent_count': invitation_sent_count,
    }
    return render(request, template, context)


@login_required()
def skill_training_list_view(request, skl):
    skill = SkillTag.objects.get(id=skl)
    tlt = request.user.alias
    we = WorkExperience.objects.filter(talent__alias=tlt)
    n_val_we = we.filter(Q(topic__skills__skill=skill.skill, edt=True))
    val_we_lts = n_val_we.filter(Q(talent__subscription__gte=1) & Q(score__lt=skill_pass_score))
    #Traing experience without sufficient pass score
    nsps_we_l = val_we_lts.select_related('topic').order_by('-date_from')
    train_sum = nsps_we_l.aggregate(Edu_sum=Sum('topic__hours'))
    train_count = nsps_we_l.count()

    t_sum = train_sum.get('Edu_sum')

    if t_sum:
        t_sum = t_sum
    else:
        t_sum=0

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(nsps_we_l, 20)

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

    template = 'talenttrack/training_skill_list.html'
    context = {
        'skl': skl,
        'train_sum': train_sum,
        'train_count': train_count,
        'pageitems': pageitems,
        'page_range': page_range
    }
    return render(request, template, context)


@login_required()
def skill_work_experience_list_view(request, skl):
    skill = SkillTag.objects.get(id=skl)
    tlt = request.user.alias
    we = WorkExperience.objects.filter(talent__alias=tlt)
    n_val_we = we.filter(Q(skills__skill=skill.skill, wexp=True))
    val_we_lts = n_val_we.filter(Q(talent__subscription__gte=1) & Q(score__lt=skill_pass_score))
    #Traing experience without sufficient pass score
    nsps_we_l = val_we_lts.select_related('topic').order_by('-date_from')
    exp_sum = nsps_we_l.aggregate(we_sum=Sum('hours_worked'))
    exp_count = nsps_we_l.count()

    e_sum = exp_sum.get('we_sum')

    if e_sum:
        e_sum = e_sum
    else:
        e_sum = 0

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(nsps_we_l, 20)

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

    template = 'talenttrack/experience_skill_list.html'
    context = {
        'skl': skl,
        'exp_sum': exp_sum,
        'exp_count': exp_count,
        'pageitems': pageitems,
        'page_range': page_range
    }
    return render(request, template, context)


@login_required()
def skill_validate_list(request, skl):
    tlt = request.user.alias
    tlt_id = [request.user.id]
    skill = SkillTag.objects.get(id=skl)

    we = WorkExperience.objects.filter(talent__alias=tlt)
    val_we = we.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score))

    #work experience not validated
    n_val_we = we.filter(Q(skills__skill=skill.skill, edt=False) | Q(topic__skills__skill=skill.skill, edt=True) & Q(score__lt=skill_pass_score))
    n_val_we_slug = n_val_we.values_list('slug', flat=True)

    wc_lt = Lecturer.objects.filter(Q(education__slug__in=n_val_we_slug) & Q(confirm='S')).values_list('lecturer__alias', flat=True).distinct('lecturer__alias')
    wc_ct = ClassMates.objects.filter(Q(education__slug__in=n_val_we_slug) & Q(confirm='S')).values_list('colleague__alias', flat=True).distinct('colleague__alias')
    wc_we = WorkColleague.objects.filter(Q(experience__slug__in=n_val_we_slug) & Q(confirm='S')).values_list('colleague_name__alias', flat=True).distinct('colleague_name__alias')
    wc_se = Superior.objects.filter(Q(experience__slug__in=n_val_we_slug) & Q(confirm='S')).values_list('superior_name__alias', flat=True).distinct('superior_name__alias')
    wc_wce = WorkCollaborator.objects.filter(Q(experience__slug__in=n_val_we_slug) & Q(confirm='S')).values_list('collaborator_name__alias', flat=True).distinct('collaborator_name__alias')
    wc_wcle = WorkClient.objects.filter(Q(experience__slug__in=n_val_we_slug) & Q(confirm='S')).values_list('client_name__alias', flat=True).distinct('client_name__alias')

    wc_lt_l = list(wc_lt)
    wc_ct_l = list(wc_ct)
    wc_we_l = list(wc_we)
    wc_se_l = list(wc_se)
    wc_wce_l = list(wc_wce)
    wc_wcle_l = list(wc_wcle)

    we_tn_l = list(wc_lt_l + wc_ct_l + wc_we_l + wc_se_l + wc_wce_l + wc_wcle_l)

    profile_slug_list_set=[]
    for x in we_tn_l:
        profile_slug_list_set.append(x)
    we_nvs_list_n = [x for x in profile_slug_list_set if x is not None]

    we_nvs_list = set(we_nvs_list_n)

    we_tbc_p_l = Profile.objects.filter(alias__in=we_nvs_list)

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(we_tbc_p_l, 20)

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

    template = 'talenttrack/skill_not_validated_list.html'
    context = {'skl': skl, 'tlt': tlt, 'skill': skill, 'pageitems': pageitems,  'page_range': page_range}
    return render(request, template, context)


@login_required()
def email_reminder_validate(request, skl, tlt):
    '''The view to email member to remind them to validate a tlt experience'''
    current_user = request.user
    invitee = current_user.email

    recipient = CustomUser.objects.get(alias=tlt)

    form = EmailFormModal(request.POST or None, initial={
                    'subject': "Please Confirm MyWeXlog Experience",
                    'message': f"Hi { recipient.first_name }, I have sent you a validation request and was hoping you would be able log in to MyWeXlog and confirm it for me."})

    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.sender = current_user
            new.recipient = recipient
            new.save()
            cd = form.cleaned_data

            subject = cd['subject']
            message = cd['message']

            email_subject = f"{ subject }"
            context = {'form': form, 'sender': current_user, 'recipient': recipient, 'user_email': invitee }
            html_message = render_to_string('invitations/validate_request.html', context)

            message = Mail(
                from_email = (settings.SENDGRID_FROM_EMAIL, f"{current_user.first_name} {current_user.last_name}"),
                to_emails = invitee,
                subject = email_subject,
                plain_text_content = strip_tags(html_message),
                html_content = html_message)

            try:
                sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)

            except Exception as e:
                print(e)

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Talent:SkillsStats', kwargs={'skl': skl})
            response = HttpResponseRedirect(next_url)
            return response
        else:
            template = 'talenttrack/request_validate_email.html'
            context = {'form': form, 'skl': skl}
            return render(request, template, context)
    else:
        template = 'talenttrack/request_validate_email.html'
        context = {'form': form, 'skl': skl}
        return render(request, template, context)


@login_required()
def email_reminder_validate_list(request, skl, tlt):
    '''The view to email member to remind them to validate a tlt experience'''
    current_user = request.user
    invitee = current_user.email

    recipient = CustomUser.objects.get(alias=tlt)

    form = EmailFormModal(request.POST or None, initial={
                    'subject': "Please Confirm MyWeXlog Experience",
                    'message': f"Hi { recipient.first_name }, I have sent you a validation request and was hopeing you would be able log in to MyWeXlog and confirm it for me."})

    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.sender = current_user
            new.recipient = recipient
            new.save()
            cd = form.cleaned_data

            subject = cd['subject']
            message = cd['message']

            email_subject = f"{ subject }"
            context = {'form': form, 'sender': current_user, 'recipient': recipient, 'user_email': invitee }
            html_message = render_to_string('invitations/validate_request.html', context)

            message = Mail(
                from_email = (settings.SENDGRID_FROM_EMAIL, f"{current_user.first_name} {current_user.last_name}"),
                to_emails = invitee,
                subject = email_subject,
                plain_text_content = strip_tags(html_message),
                html_content = html_message)

            try:
                sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)

            except Exception as e:
                print(e)

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Talent:SkillValidationList', kwargs={'skl': skl})
            response = HttpResponseRedirect(next_url)
            return response
        else:
            template = 'talenttrack/request_validate_email_list.html'
            context = {'form': form, 'skl': skl}
            return render(request, template, context)
    else:
        template = 'talenttrack/request_validate_email_list.html'
        context = {'form': form, 'skl': skl}
        return render(request, template, context)


@login_required()
def ExperienceHome(request):
    '''The view for the main page for Talenttrack app'''
    #>>>Step 1
    basequery = WorkExperience.objects.filter(talent=request.user).select_related('topic')
    skills = SkillTag.objects.all()
    sl = SkillLevel.objects.all()
    we_c = basequery.filter(score__gte=skill_pass_score)
    #<<<Step 1

    talent = request.user
    tlt = talent.alias

    #>>>Step 2
    #unconfirmed
    train_base = basequery.filter(Q(edt=True)).order_by('-date_from')
    train_sum = train_base.aggregate(Edu_sum=Sum('topic__hours'))
    train_count = train_base.count()
    train = train_base[:5]
    #Confirmed
    train_c = train_base.filter(Q(score__gte=skill_pass_score))
    train_sum_c = train_c.aggregate(Edu_sumc=Sum('topic__hours'))
    train_count_c = train_c.count()

    #unconfirmed
    exp_base = basequery.filter(wexp=True).order_by('-date_from')
    exp_sum = exp_base.aggregate(we_sum=Sum('hours_worked'))
    exp_count = exp_base.count()
    experience = exp_base[:5]
    #Confirmed
    exp_c = exp_base.filter(Q(score__gte=skill_pass_score))
    exp_sum_c = exp_c.aggregate(we_sumc=Sum('hours_worked'))
    exp_count_c = exp_c.count()

    #unconfirmed
    pre_base = basequery.filter(prelog=True).order_by('-date_from')
    prelog = pre_base[:5]
    pre_sum = pre_base.aggregate(p_sum=Sum('hours_worked'))
    pre_count = pre_base.count()
    #Confirmed
    pre_c = pre_base.filter(Q(score__gte=skill_pass_score))
    pre_sum_c = pre_c.aggregate(p_sumc=Sum('hours_worked'))
    pre_count_c = pre_c.count()

    #UNCONFIRMED
    t_sum = train_sum.get('Edu_sum')
    e_sum = exp_sum.get('we_sum')
    p_sum= pre_sum.get('p_sum')


    if t_sum:
        t_sum = t_sum
    else:
        t_sum=0

    if e_sum:
        e_sum = e_sum
    else:
        e_sum = 0

    if p_sum:
        p_sum = p_sum
    else:
        p_sum = 0

    tot_sum = t_sum + e_sum + p_sum

    #CONFIRMED
    t_sum_c = train_sum_c.get('Edu_sumc')
    e_sum_c = exp_sum_c.get('we_sumc')
    p_sum_c= pre_sum_c.get('p_sumc')


    if t_sum_c:
        t_sum_c = t_sum_c
    else:
        t_sum_c=0

    if e_sum_c:
        e_sum_c = e_sum_c
    else:
        e_sum_c = 0

    if p_sum_c:
        p_sum_c = p_sum_c
    else:
        p_sum_c = 0

    tot_sum_c = t_sum_c + e_sum_c + p_sum_c
    exp_lvls = [Decimal(e_sum_c + p_sum_c)]

    std = list(sl.filter(level__exact=0).values_list('min_hours', flat=True))
    grd = list(sl.filter(level__exact=1).values_list('min_hours', flat=True))
    jnr = list(sl.filter(level__exact=2).values_list('min_hours', flat=True))
    int = list(sl.filter(level__exact=3).values_list('min_hours', flat=True))
    snr = list(sl.filter(level__exact=4).values_list('min_hours', flat=True))
    lead = list(sl.filter(level__exact=5).values_list('min_hours', flat=True))

    if exp_lvls < std:
        iama = 0
    elif exp_lvls >= std and exp_lvls < grd:
        iama = 1
    elif exp_lvls >= grd and exp_lvls < jnr:
        iama = 2
    elif exp_lvls >= jnr and exp_lvls < int:
        iama = 3
    elif exp_lvls >= int and exp_lvls < snr:
        iama = 4
    elif exp_lvls >= snr:
        iama = 5

    level = sl.get(level=iama)

    Profile.objects.filter(talent=request.user.id).update(exp_lvl=level)

    #<<<Step 2

    #>>>Step 3
    e_skill = basequery.filter(edt=True).values_list('topic__skills', flat=True)
    l_skill = basequery.filter(edt=False).values_list('skills', flat=True)

    e_skill_l = list(e_skill)
    l_skill_l = list(l_skill)

    skill_list = e_skill_l + l_skill_l
    skill_set = set(skill_list)
    skill_count = len(skill_set)


    skill_name = skills.none()

    for ls in skill_set:
        b = skills.filter(pk=ls).values_list('skill', flat=True)

        skill_name = skill_name | b
    #<<< Step 3

    #>>> Summary of confirmation activity
    #>>> As Confirmer
    edu_lect = Lecturer.objects.filter(lecturer=talent)
    edu_lect_r = edu_lect.filter(confirm="R").count()
    edu_lect_c = edu_lect.filter(confirm="C").count()
    edu_lect_s = edu_lect.filter(confirm="S").count()
    edu_lect_y = edu_lect.filter(confirm="Y").count()

    edu_cm = ClassMates.objects.filter(colleague=talent)
    edu_cm_r = edu_cm.filter(confirm="R").count()
    edu_cm_c = edu_cm.filter(confirm="C").count()
    edu_cm_s = edu_cm.filter(confirm="S").count()
    edu_cm_y = edu_cm.filter(confirm="Y").count()

    exp_clg = WorkColleague.objects.filter(colleague_name=talent)
    exp_clg_r = exp_clg.filter(confirm="R").count()
    exp_clg_c = exp_clg.filter(confirm="C").count()
    exp_clg_s = exp_clg.filter(confirm="S").count()
    exp_clg_y = exp_clg.filter(confirm="Y").count()

    exp_sup = Superior.objects.filter(superior_name=talent)
    exp_sup_r = exp_sup.filter(confirm="R").count()
    exp_sup_c = exp_sup.filter(confirm="C").count()
    exp_sup_s = exp_sup.filter(confirm="S").count()
    exp_sup_y = exp_sup.filter(confirm="Y").count()

    exp_clt = WorkClient.objects.filter(client_name=talent)
    exp_clt_r = exp_clt.filter(confirm="R").count()
    exp_clt_c = exp_clt.filter(confirm="C").count()
    exp_clt_s = exp_clt.filter(confirm="S").count()
    exp_clt_y = exp_clt.filter(confirm="Y").count()

    exp_cbr = WorkCollaborator.objects.filter(collaborator_name=talent)
    exp_cbr_r = exp_cbr.filter(confirm="R").count()
    exp_cbr_c = exp_cbr.filter(confirm="C").count()
    exp_cbr_s = exp_cbr.filter(confirm="S").count()
    exp_cbr_y = exp_cbr.filter(confirm="Y").count()
    #As Confirmer<<<

    #>>>As Requestioner
    edu_req_lect = Lecturer.objects.filter(education__talent=talent)
    edu_req_lect_r = edu_req_lect.filter(confirm="R").count()
    edu_req_lect_c = edu_req_lect.filter(confirm="C").count()
    edu_req_lect_s = edu_req_lect.filter(confirm="S").count()
    edu_req_lect_y = edu_req_lect.filter(confirm="Y").count()

    edu_req_cm = ClassMates.objects.filter(education__talent=talent)
    edu_req_cm_r = edu_req_cm.filter(confirm="R").count()
    edu_req_cm_c = edu_req_cm.filter(confirm="C").count()
    edu_req_cm_s = edu_req_cm.filter(confirm="S").count()
    edu_req_cm_y = edu_req_cm.filter(confirm="Y").count()

    exp_req_clg = WorkColleague.objects.filter(experience__talent=talent)
    exp_req_clg_r = exp_req_clg.filter(confirm="R").count()
    exp_req_clg_c = exp_req_clg.filter(confirm="C").count()
    exp_req_clg_s = exp_req_clg.filter(confirm="S").count()
    exp_req_clg_y = exp_req_clg.filter(confirm="Y").count()

    exp_req_sup = Superior.objects.filter(experience__talent=talent)
    exp_req_sup_r = exp_req_sup.filter(confirm="R").count()
    exp_req_sup_c = exp_req_sup.filter(confirm="C").count()
    exp_req_sup_s = exp_req_sup.filter(confirm="S").count()
    exp_req_sup_y = exp_req_sup.filter(confirm="Y").count()

    exp_req_clt = WorkClient.objects.filter(experience__talent=talent)
    exp_req_clt_r = exp_req_clt.filter(confirm="R").count()
    exp_req_clt_c = exp_req_clt.filter(confirm="C").count()
    exp_req_clt_s = exp_req_clt.filter(confirm="S").count()
    exp_req_clt_y = exp_req_clt.filter(confirm="Y").count()

    exp_req_cbr = WorkCollaborator.objects.filter(experience__talent=talent)
    exp_req_cbr_r = exp_req_cbr.filter(confirm="R").count()
    exp_req_cbr_c = exp_req_cbr.filter(confirm="C").count()
    exp_req_cbr_s = exp_req_cbr.filter(confirm="S").count()
    exp_req_cbr_y = exp_req_cbr.filter(confirm="Y").count()
    #As Requestioner<<<
    #Summary of confirmation activity<<<


    template = 'talenttrack/track_home.html'
    context = {
        'tlt': tlt,
        'train': train,
        'train_sum': train_sum,
        'train_sum_c': train_sum_c,
        'train_count_c': train_count_c,
        'train_count': train_count,
        'experience': experience,
        'exp_sum': exp_sum,
        'exp_sum_c': exp_sum_c,
        'exp_count': exp_count,
        'exp_count_c': exp_count_c,
        'prelog': prelog,
        'pre_sum': pre_sum,
        'pre_count': pre_count,
        'pre_sum_c': pre_sum_c,
        'pre_count_c': pre_count_c,
        'tot_sum': tot_sum,
        'tot_sum_c': tot_sum_c,
        'skill_name': skill_name,
        'skill_count': skill_count,
        'level': level,
        'edu_lect': edu_lect, 'edu_lect_r': edu_lect_r, 'edu_lect_c': edu_lect_c, 'edu_lect_s': edu_lect_s, 'edu_lect_y': edu_lect_y,
        'edu_cm': edu_cm, 'edu_cm_r': edu_cm_r, 'edu_cm_c': edu_cm_c, 'edu_cm_s': edu_cm_s, 'edu_cm_y': edu_cm_y,
        'exp_clg': exp_clg, 'exp_clg_c': exp_clg_c, 'exp_clg_r': exp_clg_r, 'exp_clg_s': exp_clg_s, 'exp_clg_y': exp_clg_y,
        'exp_sup': exp_sup, 'exp_sup_c': exp_sup_c, 'exp_sup_r': exp_sup_r, 'exp_sup_s': exp_sup_s, 'exp_sup_y': exp_sup_y,
        'exp_clt': exp_clt, 'exp_clt_c': exp_clt_c, 'exp_clt_r': exp_clt_r, 'exp_clt_s': exp_clt_s, 'exp_clt_y': exp_clt_y,
        'exp_cbr': exp_cbr, 'exp_cbr_c': exp_cbr_c, 'exp_cbr_r': exp_cbr_r, 'exp_cbr_s': exp_cbr_s, 'exp_cbr_y': exp_cbr_y,
        'edu_req_lect': edu_req_lect, 'edu_req_lect_r': edu_req_lect_r, 'edu_req_lect_c': edu_req_lect_c, 'edu_req_lect_s': edu_req_lect_s, 'edu_req_lect_y': edu_req_lect_y,
        'edu_req_cm': edu_req_cm, 'edu_req_cm_r': edu_req_cm_r, 'edu_req_cm_c': edu_req_cm_c, 'edu_req_cm_s': edu_req_cm_s, 'edu_req_cm_y': edu_req_cm_y,
        'exp_req_clg': exp_req_clg, 'exp_req_clg_c': exp_req_clg_c, 'exp_req_clg_r': exp_req_clg_r, 'exp_req_clg_s': exp_req_clg_s, 'exp_req_clg_y': exp_req_clg_y,
        'exp_req_sup': exp_req_sup, 'exp_req_sup_c': exp_req_sup_c, 'exp_req_sup_r': exp_req_sup_r, 'exp_req_sup_s': exp_req_sup_s, 'exp_req_sup_y': exp_req_sup_y,
        'exp_req_clt': exp_req_clt, 'exp_req_clt_c': exp_req_clt_c, 'exp_req_clt_r': exp_req_clt_r, 'exp_req_clt_s': exp_req_clt_s, 'exp_req_clt_y': exp_req_clt_y,
        'exp_req_cbr': exp_req_cbr, 'exp_req_cbr_c': exp_req_cbr_c, 'exp_req_cbr_r': exp_req_cbr_r, 'exp_req_cbr_s': exp_req_cbr_s, 'exp_req_cbr_y': exp_req_cbr_y,
    }
    return render(request, template, context)


@login_required()
@subscription(2)
def profile_search(request):
    form = ProfileSearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = ProfileSearchForm(request.GET)
        if form.is_valid():
            query=form.cleaned_data['query']
            results = Profile.objects.annotate(similarity=Greatest(
                TrigramSimilarity('alias', query),
                TrigramSimilarity('f_name', query),
                TrigramSimilarity('l_name', query),
                )).filter(similarity__gt=0.3).order_by('-similarity')

    template = 'talenttrack/profile_search_results.html'
    context = {'form': form, 'query': query, 'results': results,}
    return render(request, template, context)


@login_required()
def lecturer_conf_summary_list(request):
    '''Confirmations the logged-in user has received'''
    tlt = request.user
    lect_qs = Lecturer.objects.filter(lecturer=tlt)
    lect_qs_unlocked = lect_qs.filter(Q(locked=False) & ~Q(confirm="S"))

    today = timezone.now().date()

    for item in lect_qs_unlocked:
        age = (today - item.date_confirmed).days
        if age > locked_age:
            item.locked = True
            item.save()
        else:
            pass
    lect_qs = Lecturer.objects.filter(lecturer=tlt).order_by('-date_confirmed').order_by('-confirm')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(lect_qs, 20)

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

    template = 'talenttrack/confirm_edu_lect_list.html'
    context = {'lect_qs': lect_qs, 'age': locked_age, 'pageitems': pageitems,  'page_range': page_range}
    return render(request, template, context)


@login_required()
def classmate_conf_summary_list(request):
    '''Confirmations the logged-in user has received'''
    tlt = request.user
    cm_qs = ClassMates.objects.filter(colleague=tlt)
    cm_qs_unlocked = cm_qs.filter(Q(locked=False) & ~Q(confirm="S"))

    today = timezone.now().date()

    for item in cm_qs_unlocked:
        age = (today - item.date_confirmed).days
        if age > locked_age:
            item.locked = True
            item.save()
        else:
            pass

    cm_qs = ClassMates.objects.filter(colleague=tlt).order_by('-date_confirmed').order_by('-confirm')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(cm_qs, 20)

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

    template = 'talenttrack/confirm_edu_cm_list.html'
    context = {'cm_qs': cm_qs, 'age': locked_age, 'pageitems': pageitems,  'page_range': page_range}
    return render(request, template, context)


@login_required()
def colleague_conf_summary_list(request):
    '''Confirmations the logged-in user has received'''
    tlt = request.user
    clg_c_qs = WorkColleague.objects.filter(colleague_name=tlt)
    clg_c_qs_unlocked = clg_c_qs.filter(Q(locked=False) & ~Q(confirm="S"))

    today = timezone.now().date()

    for item in clg_c_qs_unlocked:
        age = (today - item.date_confirmed).days
        if age > locked_age:
            item.locked = True
            item.save()
        else:
            pass

    clg_c_qs = WorkColleague.objects.filter(colleague_name=tlt).order_by('-date_confirmed').order_by('-confirm')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(clg_c_qs, 20)

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

    template = 'talenttrack/confirm_exp_clg_list.html'
    context = {'clg_c_qs': clg_c_qs, 'age': locked_age, 'pageitems': pageitems,  'page_range': page_range}
    return render(request, template, context)


@login_required()
def superior_conf_summary_list(request):
    '''Confirmations the logged-in user has received'''
    tlt = request.user
    sup_c_qs = Superior.objects.filter(superior_name=tlt)
    sup_c_qs_unlocked = sup_c_qs.filter(Q(locked=False) & ~Q(confirm="S"))

    today = timezone.now().date()

    for item in sup_c_qs_unlocked:
        age = (today - item.date_confirmed).days
        if age > locked_age:
            item.locked = True
            item.save()
        else:
            pass

    sup_c_qs = Superior.objects.filter(superior_name=tlt).order_by('-date_confirmed').order_by('-confirm')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(sup_c_qs, 20)

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

    template = 'talenttrack/confirm_exp_sup_list.html'
    context = {'sup_c_qs': sup_c_qs, 'age': locked_age, 'pageitems': pageitems,  'page_range': page_range}
    return render(request, template, context)


@login_required()
def collaborator_conf_summary_list(request):
    '''Confirmations the logged-in user has received'''
    tlt = request.user
    clb_c_qs = WorkCollaborator.objects.filter(collaborator_name=tlt)
    clb_c_qs_unlocked = clb_c_qs.filter(Q(locked=False) & ~Q(confirm="S"))

    today = timezone.now().date()

    for item in clb_c_qs_unlocked:
        age = (today - item.date_confirmed).days
        if age > locked_age:
            item.locked = True
            item.save()
        else:
            pass

    clb_c_qs = WorkCollaborator.objects.filter(collaborator_name=tlt).order_by('-date_confirmed').order_by('-confirm')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(clb_c_qs, 20)

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

    template = 'talenttrack/confirm_exp_clb_list.html'
    context = {'clb_c_qs': clb_c_qs, 'age': locked_age, 'pageitems': pageitems,  'page_range': page_range}
    return render(request, template, context)


@login_required()
def client_conf_summary_list(request):
    '''Confirmations the logged-in user has received'''
    tlt = request.user
    clt_c_qs = WorkClient.objects.filter(client_name=tlt)
    clt_c_qs_unlocked = clt_c_qs.filter(Q(locked=False) & ~Q(confirm="S"))

    today = timezone.now().date()

    for item in clt_c_qs_unlocked:
        age = (today - item.date_confirmed).days
        if age > locked_age:
            item.locked = True
            item.save()
        else:
            pass

    clt_c_qs = WorkClient.objects.filter(client_name=tlt).order_by('-date_confirmed').order_by('-confirm')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(clt_c_qs, 20)

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

    template = 'talenttrack/confirm_exp_clt_list.html'
    context = {'clt_c_qs': clt_c_qs, 'age': locked_age, 'pageitems': pageitems,  'page_range': page_range}
    return render(request, template, context)


@login_required()
def lect_req_list(request):
    '''Filters for the view where all requests for lecturer are listed'''
    talent = request.user
    edu_req_lect = Lecturer.objects.filter(education__talent=talent).order_by('-date_confirmed').order_by('-confirm')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(edu_req_lect, 20)

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

    template = 'talenttrack/request_lect_list.html'
    context = {'edu_req_lect': edu_req_lect, 'pageitems': pageitems,  'page_range': page_range}
    return render(request, template, context)


@login_required()
def cm_req_list(request):
    '''Filters for the view where all requests for classmate are listed'''
    talent = request.user
    edu_req_cm = ClassMates.objects.filter(education__talent=talent).order_by('-date_confirmed').order_by('-confirm')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(edu_req_cm, 20)

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

    template = 'talenttrack/request_cm_list.html'
    context = {'edu_req_cm': edu_req_cm, 'pageitems': pageitems,  'page_range': page_range}
    return render(request, template, context)


@login_required()
def clg_req_list(request):
    '''Filters for the view where all requests to colleagues are listed'''
    talent = request.user
    exp_req_clg = WorkColleague.objects.filter(experience__talent=talent).order_by('-date_confirmed').order_by('-confirm')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(exp_req_clg, 20)

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

    template = 'talenttrack/request_clg_list.html'
    context = {'exp_req_clg': exp_req_clg, 'pageitems': pageitems,  'page_range': page_range}
    return render(request, template, context)


@login_required()
def sup_req_list(request):
    '''Filters for the view where all requests to superiors are listed'''
    talent = request.user
    exp_req_sup = Superior.objects.filter(experience__talent=talent).order_by('-date_confirmed').order_by('-confirm')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(exp_req_sup, 20)

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

    template = 'talenttrack/request_sup_list.html'
    context = {'exp_req_sup': exp_req_sup, 'pageitems': pageitems,  'page_range': page_range}
    return render(request, template, context)


@login_required()
def clt_req_list(request):
    '''Filters for the view where all requests to clients are listed'''
    talent = request.user
    exp_req_clt = WorkClient.objects.filter(experience__talent=talent).order_by('-date_confirmed').order_by('-confirm')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(exp_req_clt, 20)

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

    template = 'talenttrack/request_clt_list.html'
    context = {'exp_req_clt': exp_req_clt, 'pageitems': pageitems,  'page_range': page_range}
    return render(request, template, context)


@login_required()
def clb_req_list(request):
    '''Filters for the view where all requests to collaborators are listed'''
    talent = request.user
    exp_req_clb = WorkCollaborator.objects.filter(experience__talent=talent).order_by('-date_confirmed').order_by('-confirm')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(exp_req_clb, 20)

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

    template = 'talenttrack/request_clb_list.html'
    context = {'exp_req_clb': exp_req_clb, 'pageitems': pageitems,  'page_range': page_range}
    return render(request, template, context)


@login_required()
def HelpExperienceHomeView(request):
    template_name = 'talenttrack/help_experience_home.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpExperienceEducationView(request):
    template_name = 'talenttrack/help_experience_education.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpExperienceExperienceView(request):
    template_name = 'talenttrack/help_experience_experience.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpExperiencePreExperienceView(request):
    template_name = 'talenttrack/help_experience_pre_experience.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpCaptrueEducationView(request):
    template_name = 'talenttrack/help_capture_education.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpCaptrueExperienceView(request):
    template_name = 'talenttrack/help_capture_experience.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpHowCaptrueSkillsView(request):
    template_name = 'talenttrack/help_how_to_capture_skills.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def TrainingListView(request):
    basequery = WorkExperience.objects.select_related('topic').filter(talent=request.user)

    train = basequery.filter(edt=True).order_by('-date_from')
    train_sum = train.aggregate(Edu_sum=Sum('topic__hours'))
    train_count = train.count()

    t_sum = train_sum.get('Edu_sum')

    if t_sum:
        t_sum = t_sum
    else:
        t_sum=0

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(train, 20)

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

    template = 'talenttrack/training_list.html'
    context = {
        'train_sum': train_sum,
        'train_count': train_count,
        'pageitems': pageitems,
        'page_range': page_range
    }
    return render(request, template, context)


@login_required()
def PreExperienceListView(request):
    basequery = WorkExperience.objects.select_related('topic').filter(talent=request.user)

    prelog = basequery.filter(prelog=True).order_by('-date_from')
    pre_sum = prelog.aggregate(p_sum=Sum('hours_worked'))
    pre_count = prelog.count()

    p_sum= pre_sum.get('p_sum')

    if p_sum:
        p_sum = p_sum
    else:
        p_sum = 0

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(prelog, 20)

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

    template = 'talenttrack/pre_experience_list.html'
    context = {
        'pre_sum': pre_sum,
        'pre_count': pre_count,
        'pageitems': pageitems,
        'page_range': page_range
    }
    return render(request, template, context)


@login_required()
def WorkExperienceListView(request):
    basequery = WorkExperience.objects.select_related('topic').filter(talent=request.user)

    experience = basequery.filter(wexp=True).order_by('-date_from')
    exp_sum = experience.aggregate(we_sum=Sum('hours_worked'))
    exp_count = experience.count()

    e_sum = exp_sum.get('we_sum')

    if e_sum:
        e_sum = e_sum
    else:
        e_sum = 0

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(experience, 20)

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

    template = 'talenttrack/experience_list.html'
    context = {
        'exp_sum': exp_sum,
        'exp_count': exp_count,
        'pageitems': pageitems,
        'page_range': page_range
    }
    return render(request, template, context)


@login_required()
def CaptureAchievementView(request):
    pfl = get_object_or_404(CustomUser, pk=request.user.id)

    if request.method == 'POST':
        form = AchievementsForm(request.POST, request.FILES)
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = pfl
            new.save()
            return redirect(reverse('Profile:ProfileView')+'#achievements')
        else:
            template = 'talenttrack/achievement_capture.html'
            context = {'form': form,}
            return render(request, template, context)
    else:
        form = AchievementsForm()
        template = 'talenttrack/achievement_capture.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def EditAchievementView(request, ach):
    instance = get_object_or_404(Achievements, slug=ach)

    if request.method == 'POST':
        form = AchievementsForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return redirect(reverse('Profile:ProfileView')+'#achievements')
        else:
            template = 'talenttrack/achievement_capture.html'
            context = {'form': form,}
            return render(request, template, context)
    else:
        form = AchievementsForm(instance=instance)
        template = 'talenttrack/achievement_capture.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def DeleteAchievementView(request, ach_i, tlt):
    info = Achievements.objects.get(pk=ach_i)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Profile:ProfileView')+'#achievements')
    else:
        raise PermissionDenied


@login_required()
def CaptureAwardView(request):
    pfl = get_object_or_404(CustomUser, pk=request.user.id)

    if request.method == 'POST':
        form = AwardsForm(request.POST, request.FILES)
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = pfl
            new.save()
            form.save_m2m()
            return redirect(reverse('Profile:ProfileView')+'#awards')
        else:
            template = 'talenttrack/award_capture.html'
            context = {'form': form,}
            return render(request, template, context)
    else:
        form = AwardsForm()
        template = 'talenttrack/award_capture.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def EditAwardView(request, awd):
    instance = get_object_or_404(Awards, slug=awd)

    if request.method == 'POST':
        form = AwardsForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
            return redirect(reverse('Profile:ProfileView')+'#awards')
        else:
            template = 'talenttrack/award_capture.html'
            context = {'form': form,}
            return render(request, template, context)
    else:
        form = AwardsForm(instance=instance)
        template = 'talenttrack/award_capture.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def DeleteAwardView(request, awd_i, tlt):
    info = Awards.objects.get(pk=awd_i)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Profile:ProfileView')+'#awards')
    else:
        raise PermissionDenied


@login_required()
def CapturePublicationView(request):
    pfl = get_object_or_404(CustomUser, pk=request.user.id)

    if request.method == 'POST':
        form = PublicationsForm(request.POST, request.FILES)
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = pfl
            new.save()
            form.save_m2m()
            return redirect(reverse('Profile:ProfileView')+'#publications')
        else:
            template = 'talenttrack/publication_capture.html'
            context = {'form': form,}
            return render(request, template, context)
    else:
        form = PublicationsForm()
        template = 'talenttrack/publication_capture.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def EditPublicationView(request, pub):
    instance = get_object_or_404(Publications, slug=pub)

    if request.method == 'POST':
        form = PublicationsForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
            return redirect(reverse('Profile:ProfileView')+'#publications')
        else:
            template = 'talenttrack/publication_capture.html'
            context = {'form': form,}
            return render(request, template, context)
    else:
        form = PublicationsForm(instance=instance)
        template = 'talenttrack/publication_capture.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def DeletePublicationView(request, pub_i, tlt):
    info = Publications.objects.get(pk=pub_i)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Profile:ProfileView')+'#publications')
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def LicenseCertificationCaptureView(request):
    tlt_i = get_object_or_404(CustomUser, pk=request.user.id)
    form = LicenseCertificationForm(request.POST or None, request.FILES)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = tlt_i
            new.save()
            return redirect(reverse ('Profile:ProfileView')+'#memberships')
    else:
        template = 'talenttrack/membership_view.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
@csp_exempt
def LicenseCertificationEditView(request, lcm):
    lcm_i = LicenseCertification.objects.get(slug=lcm)


    if request.method == 'POST':
        form = LicenseCertificationForm(request.POST, request.FILES, instance=lcm_i)
        if form.is_valid():
            edit = form.save(commit=False)
            edit.save()
            return redirect(reverse ('Profile:ProfileView')+'#memberships')
        else:
            form = LicenseCertificationForm(instance=lcm_i)
            template = 'talenttrack/membership_view.html'
            context = {'form': form,}
            return render(request, template, context)
    else:
        form = LicenseCertificationForm(instance=lcm_i)
        template = 'talenttrack/membership_view.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def LicenseCertificationDeleteView(request, pk, tlt):
    lcm = LicenseCertification.objects.get(pk=pk)
    if lcm.talent == request.user:
        if request.method =='POST':
            lcm.delete()
            return redirect(reverse('Profile:ProfileView')+'#memberships')
    else:
        raise PermissionDenied


def TltRatingDetailView(request, tlt):
    pfl = Profile.objects.get(alias=tlt)

    r_1 = pfl.rate_1/100
    r_2 = pfl.rate_2/100
    r_3 = pfl.rate_3/100

    template = 'talenttrack/rating_detail_tlt.html'
    context = {'pfl': pfl, 'r_1': r_1, 'r_2': r_2, 'r_3': r_3,}
    return render(request, template, context)


@login_required()
def ActiveProfileView(request, tlt, vac):
    '''View for profile and skills for specified vacancy'''
    #caching
    bch_qs = BriefCareerHistory.objects.filter(talent__alias=tlt).order_by('-date_from')
    bch = bch_qs[:6]
    bch_count = bch_qs.count()
    pfl = Profile.objects.filter(alias=tlt).first()
    als = get_object_or_404(Profile, alias=tlt)
    padd = PhysicalAddress.objects.only('country', 'region', 'city').get(talent__alias=tlt)
    vacancy = TalentRequired.objects.filter(ref_no=vac)
    skr = SkillRequired.objects.filter(scope__ref_no=vac).values_list('skills', flat=True).distinct('skills')
    skill_qs = SkillTag.objects.all()
    exp = WorkExperience.objects.filter(talent__alias=tlt).select_related('topic', 'course', 'project')
    edtexp = exp.filter(edt=True).order_by('-date_from')[:6]
    edtexp_count = edtexp.count()
    bkl_qs = ReadBy.objects.filter(talent__alias=tlt).select_related('book', 'type')
    bkl = bkl_qs[:8]
    bkl_count = bkl.count()
    prj_qs = ProjectData.objects.all()
    bid_qs = WorkBid.objects.filter(Q(talent__alias=tlt) & Q(work__ref_no=vac))
    achievement_qs = Achievements.objects.filter(talent__alias=tlt).order_by('-date_achieved')
    achievement = achievement_qs[:6]
    achievement_qs_count = achievement_qs.count()
    award_qs = Awards.objects.filter(talent__alias=tlt).order_by('-date_achieved')
    award = award_qs[:6]
    award_qs_count = award.count()
    publication_qs = Publications.objects.filter(talent__alias=tlt).order_by('-date_published')
    publication = publication_qs[:6]
    publication_qs_count = publication_qs.count()
    language_qs = LanguageTrack.objects.filter(talent__alias=tlt).order_by('-language')
    membership_qs = LicenseCertification.objects.filter(talent__alias=tlt).order_by('-issue_date')
    membership = membership_qs[:12]
    membership_qs_count = membership_qs.count()
    bslist_qs = BidShortList.objects.filter(Q(talent__alias=tlt) & Q(scope__ref_no=vac))
    int_list = BidInterviewList.objects.filter(Q(talent__alias=tlt) & Q(scope__ref_no=vac))
    wtr_qs = WillingToRelocate.objects.filter(talent__alias=tlt)

    #Project Summary
    prj = exp.values_list('project', flat=True).distinct('project')
    prj_set = {}
    prj_count = 0
    for p in prj:
        if p == None:
            pass
        else:
            prj_count +=1
            project_q = prj_qs.filter(pk=p).values_list('name', 'company__ename', 'companybranch__name', 'industry__industry', 'country')
            cache = WorkExperience.objects.filter(project__pk=p)
            hr = cache.aggregate(sum_t=Sum('hours_worked'))
            ppl = cache.distinct('talent').count()
            info_list=[project_q[0][1], project_q[0][2], project_q[0][3], project_q[0][4], hr['sum_t'], ppl]
            prj_set[project_q[0][0]] = info_list

    #experience hours on skills required
    vacse_set = {}
    pst = exp.only('skills').values_list('skills', flat=True).distinct('skills')

    for s in skr:
        #populating the keys
        skill_q = skill_qs.filter(pk=s).values_list('skill', flat=True)
        skill_f = skill_q[0]
        vacse_set[skill_f]=float(0)
        if s in pst:
            #populating the values
            d = skill_qs.get(pk=s)
            e = d.experience.filter(talent__alias=tlt)
            e_sum = e.aggregate(sum_t=Sum('hours_worked'))
            sum_float = float(e_sum.get('sum_t'))
            if vacse_set[skill_f]:
                new = vacse_set[skill_f]+sum_float
                vacse_set[skill_f]=new
            else:
                vacse_set[skill_f] = sum_float
        else:
            pass

    #Training hours on skills required
    vacst_set = {}
    edt = exp.only('topic__skills').values_list('topic__skills', flat=True).distinct('topic__skills')
    edc = exp.only('topic').values_list('topic', flat=True).distinct('topic')
    #populating the keys
    for s in skr:
        #populating the set
        skill_q = skill_qs.filter(pk=s).values_list('skill', flat=True)
        skill_f = skill_q[0]
        vacst_set[skill_f]=float(0)
        if s in edt:
            #populating the values
            for t in edc:
                d = skill_qs.get(pk=s)
                e = d.topic_set.filter(topic=t)
                e_sum = e.aggregate(sum_t=Sum('hours'))
                sum_float = e_sum.get('sum_t')
                if sum_float is None:
                    sum_float = float(0)
                else:
                    sum_float = float(sum_float)
                if vacst_set[skill_f]:
                    new = vacst_set[skill_f]+sum_float
                    vacst_set[skill_f]=new
                else:
                    vacst_set[skill_f] = sum_float
        else:
            pass

    object_viewed_signal.send(pfl.__class__, instance=pfl, request=request)


    template = 'talenttrack/active_profile_view.html'
    context = {
        'tlt': tlt, 'bch': bch, 'bch_count': bch_count, 'pfl': pfl, 'padd': padd,'vacse_set': vacse_set, 'vacst_set': vacst_set, 'exp': exp, 'bkl': bkl, 'edtexp': edtexp, 'edtexp_count': edtexp_count, 'bkl_count': bkl_count, 'prj_set': prj_set, 'prj_count': prj_count, 'bid_qs': bid_qs, 'achievement': achievement, 'achievement_qs_count': achievement_qs_count, 'award': award, 'award_qs_count': award_qs_count, 'publication': publication, 'publication_qs_count': publication_qs_count, 'language_qs': language_qs, 'membership': membership, 'membership_qs_count': membership_qs_count, 'bslist_qs': bslist_qs, 'vacancy': vacancy, 'int_list': int_list, 'als': als, 'vac': vac, 'wtr_qs': wtr_qs,
        }
    return render(request, template, context)


def LCMFVView(request, tlt, vac):

    membership_qs = LicenseCertification.objects.filter(talent__alias=tlt).order_by('-issue_date')
    membership_qs_count = membership_qs.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(membership_qs, 20)

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

    template = 'talenttrack/apv_lcm.html'
    context = {'tlt': tlt, 'vac': vac, 'membership_qs_count': membership_qs_count, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


def BCHView(request, tlt, vac):

    bch = BriefCareerHistory.objects.filter(talent__alias=tlt).order_by('-date_from')
    bch_count = bch.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(bch, 20)

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

    template = 'talenttrack/apv_bch.html'
    context = {'tlt': tlt, 'vac': vac, 'bch_count': bch_count, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


def AchievementsFVView(request, tlt, vac):

    achievements_qs = Achievements.objects.filter(talent__alias=tlt).order_by('-date_achieved')
    achievements_qs_count = achievements_qs.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(achievements_qs, 21)

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

    template = 'talenttrack/apv_ach.html'
    context = {'tlt': tlt, 'vac': vac, 'achievements_qs_count': achievements_qs_count, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


def AwardsFVView(request, tlt, vac):

    awards_qs = Awards.objects.filter(talent__alias=tlt).order_by('-date_achieved')
    awards_qs_count = awards_qs.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(awards_qs, 21)

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

    template = 'talenttrack/apv_awd.html'
    context = {'tlt': tlt, 'vac': vac, 'awards_qs_count': awards_qs_count, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


def PublicationsFVView(request, tlt, vac):

    publications_qs = Publications.objects.filter(talent__alias=tlt).order_by('-date_published')
    publications_qs_count = publications_qs.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(publications_qs, 21)

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

    template = 'talenttrack/apv_pub.html'
    context = {'tlt': tlt, 'vac': vac, 'publications_qs_count': publications_qs_count, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


def ProjectsFVView(request, tlt, vac):

    exp = WorkExperience.objects.filter(talent__alias=tlt).select_related('topic', 'course', 'project')
    prj_qs = ProjectData.objects.all()
    #Project Summary
    prj = exp.values_list('project', flat=True).distinct('project')
    prj_set = {}
    prj_count = 0
    for p in prj:
        if p == None:
            pass
        else:
            prj_count +=1
            project_q = prj_qs.filter(pk=p).values_list('name', 'company__ename', 'companybranch__name', 'industry__industry', 'country')
            cache = WorkExperience.objects.filter(project__pk=p)
            hr = cache.aggregate(sum_t=Sum('hours_worked'))
            ppl = cache.distinct('talent').count()
            info_list=[project_q[0][1], project_q[0][2], project_q[0][3], project_q[0][4], hr['sum_t'], ppl]
            prj_set[project_q[0][0]] = info_list

    t = tuple(prj_set.items())

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(t, 21)

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

    template = 'talenttrack/apv_projects.html'
    context = {'tlt': tlt, 'vac': vac, 'prj_count': prj_count, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


def EduFVView(request, tlt, vac):

    exp = WorkExperience.objects.filter(talent__alias=tlt).select_related('topic', 'course', 'project')
    edtexp = exp.filter(edt=True).order_by('-date_from')
    edtexp_count = edtexp.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(edtexp, 21)

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

    template = 'talenttrack/apv_edu.html'
    context = {'tlt': tlt, 'vac': vac, 'edtexp_count': edtexp_count, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


def LCMFullView(request, tlt):
    '''View to show all licenses and certifications for a person.'''
    #tlt = Profile.objects.get(alias=tlt)
    lcm_qs = LicenseCertification.objects.filter(talent__alias=tlt).order_by('-issue_date')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(lcm_qs, 20)

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

    template = 'talenttrack/lcm_full_view.html'
    context = {
        'tlt': tlt, 'pageitems': pageitems, 'page_range': page_range
        }
    return render(request, template, context)


@login_required()
def profile_view(request, tlt):
    '''View for profile without reference to a vacancy. Used for the search feature'''
    #caching
    vac = '1ad9t2'
    bch_qs = BriefCareerHistory.objects.filter(talent__alias=tlt).order_by('-date_from')
    bch = bch_qs[:6]
    bch_count = bch_qs.count()
    pfl = Profile.objects.filter(alias=tlt).first()
    als = get_object_or_404(Profile, alias=tlt)
    padd = PhysicalAddress.objects.only('country', 'region', 'city').get(talent__alias=tlt)
    #vacancy = TalentRequired.objects.filter(ref_no=vac)
    #skr = SkillRequired.objects.filter(scope__ref_no=vac).values_list('skills', flat=True).distinct('skills')
    skill_qs = SkillTag.objects.all()
    exp = WorkExperience.objects.filter(talent__alias=tlt).select_related('topic', 'course', 'project')
    edtexp = exp.filter(edt=True).order_by('-date_from')
    edtexp_count = edtexp.count()
    bkl_qs = ReadBy.objects.filter(talent__alias=tlt).select_related('book', 'type')
    bkl = bkl_qs[:8]
    bkl_count = bkl_qs.count()
    prj_qs = ProjectData.objects.all()
    #bid_qs = WorkBid.objects.filter(Q(talent__alias=tlt) & Q(work__ref_no=vac))
    achievement_qs = Achievements.objects.filter(talent__alias=tlt).order_by('-date_achieved')
    achievement = achievement_qs[:6]
    achievement_qs_count = achievement_qs.count()
    award_qs = Awards.objects.filter(talent__alias=tlt).order_by('-date_achieved')
    award = award_qs[:6]
    award_qs_count = award.count()
    publication_qs = Publications.objects.filter(talent__alias=tlt).order_by('-date_published')
    publication = publication_qs[:6]
    publication_qs_count = publication_qs.count()
    language_qs = LanguageTrack.objects.filter(talent__alias=tlt).order_by('-language')
    membership_qs = LicenseCertification.objects.filter(talent__alias=tlt).order_by('-issue_date')
    membership = membership_qs[:12]
    membership_qs_count = membership_qs.count()
    wtr_qs = WillingToRelocate.objects.filter(talent__alias=tlt)

    #Project Summary
    prj = exp.values_list('project', flat=True).distinct('project')
    prj_set = {}
    prj_count = 0
    for p in prj:
        if p == None:
            pass
        else:
            prj_count +=1
            project_q = prj_qs.filter(pk=p).values_list('name', 'company__ename', 'companybranch__name', 'industry__industry', 'country')
            cache = WorkExperience.objects.filter(project__pk=p)
            hr = cache.aggregate(sum_t=Sum('hours_worked'))
            ppl = cache.distinct('talent').count()
            info_list=[project_q[0][1], project_q[0][2], project_q[0][3], project_q[0][4], hr['sum_t'], ppl]
            prj_set[project_q[0][0]] = info_list

    object_viewed_signal.send(pfl.__class__, instance=pfl, request=request)


    template = 'talenttrack/active_profile_view_light.html'
    context = {
        'tlt': tlt, 'bch': bch, 'bch_count': bch_count, 'pfl': pfl, 'padd': padd, 'exp': exp, 'bkl': bkl, 'edtexp': edtexp, 'edtexp_count': edtexp_count, 'bkl_count': bkl_count, 'prj_set': prj_set, 'prj_count': prj_count, 'achievement': achievement, 'achievement_qs_count': achievement_qs_count, 'award': award, 'award_qs_count': award_qs_count, 'publication': publication, 'publication_qs_count': publication_qs_count, 'language_qs': language_qs, 'membership': membership, 'membership_qs_count': membership_qs_count, 'als': als, 'vac': vac, 'wtr_qs': wtr_qs,
        }
    return render(request, template, context)


@login_required()
@corp_permission(1)
def profile_view_corp(request, cor, tlt):
    '''View for profile without reference to a vacancy. Used for the corporate feature'''
    #caching
    vac = '1ad9t2'
    bch_qs = BriefCareerHistory.objects.filter(talent__alias=tlt).order_by('-date_from')
    bch = bch_qs[:6]
    corp_info = CorporateStaff.objects.get(Q(talent__alias=tlt) & Q(corporate__slug=cor))
    bch_count = bch_qs.count()
    pfl = Profile.objects.filter(alias=tlt)
    als = get_object_or_404(Profile, alias=tlt)
    padd = PhysicalAddress.objects.only('country', 'region', 'city').get(talent__alias=tlt)
    skill_qs = SkillTag.objects.all()
    exp = WorkExperience.objects.filter(talent__alias=tlt).select_related('topic', 'course', 'project')
    edtexp = exp.filter(edt=True).order_by('-date_from')
    edtexp_count = edtexp.count()
    bkl_qs = ReadBy.objects.filter(talent__alias=tlt).select_related('book', 'type')
    bkl = bkl_qs[:8]
    bkl_count = bkl_qs.count()
    prj_qs = ProjectData.objects.all()
    #bid_qs = WorkBid.objects.filter(Q(talent__alias=tlt) & Q(work__ref_no=vac))
    achievement_qs = Achievements.objects.filter(talent__alias=tlt).order_by('-date_achieved')
    achievement = achievement_qs[:6]
    achievement_qs_count = achievement_qs.count()
    award_qs = Awards.objects.filter(talent__alias=tlt).order_by('-date_achieved')
    award = award_qs[:6]
    award_qs_count = award.count()
    publication_qs = Publications.objects.filter(talent__alias=tlt).order_by('-date_published')
    publication = publication_qs[:6]
    publication_qs_count = publication_qs.count()
    language_qs = LanguageTrack.objects.filter(talent__alias=tlt).order_by('-language')
    membership_qs = LicenseCertification.objects.filter(talent__alias=tlt).order_by('-issue_date')
    membership = membership_qs[:6]
    membership_qs_count = membership_qs.count()
    wtr_qs = WillingToRelocate.objects.filter(talent__alias=tlt)

    #Project Summary
    prj = exp.values_list('project', flat=True).distinct('project')
    prj_set = {}
    prj_count = 0
    for p in prj:
        if p == None:
            pass
        else:
            prj_count +=1
            project_q = prj_qs.filter(pk=p).values_list('name', 'company__ename', 'companybranch__name', 'industry__industry', 'country')
            cache = WorkExperience.objects.filter(project__pk=p)
            hr = cache.aggregate(sum_t=Sum('hours_worked'))
            ppl = cache.distinct('talent').count()
            info_list=[project_q[0][1], project_q[0][2], project_q[0][3], project_q[0][4], hr['sum_t'], ppl]
            prj_set[project_q[0][0]] = info_list

    #object_viewed_signal.send(pfl.__class__, instance=pfl, request=request)


    template = 'talenttrack/active_profile_view_corp.html'
    context = {
        'tlt': tlt, 'bch': bch, 'bch_count': bch_count, 'pfl': pfl, 'padd': padd, 'exp': exp, 'bkl': bkl, 'edtexp': edtexp, 'edtexp_count': edtexp_count, 'bkl_count': bkl_count, 'prj_set': prj_set, 'prj_count': prj_count, 'achievement': achievement, 'achievement_qs_count': achievement_qs_count, 'award': award, 'award_qs_count': award_qs_count, 'publication': publication, 'publication_qs_count': publication_qs_count, 'language_qs': language_qs, 'membership': membership, 'membership_qs_count': membership_qs_count, 'als': als, 'vac': vac, 'wtr_qs': wtr_qs, 'corp_info': corp_info
        }
    return render(request, template, context)


def BCHLView(request, tlt):

    bch = BriefCareerHistory.objects.filter(talent__alias=tlt).order_by('-date_from')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(bch, 20)

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

    template = 'talenttrack/apv_l_bch.html'
    context = {'tlt': tlt, 'vac': vac, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


def AchievementsLView(request, tlt):

    achievement_qs = Achievements.objects.filter(talent__alias=tlt).order_by('-date_achieved')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(achievement_qs, 20)

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

    template = 'talenttrack/apv_l_ach.html'
    context = {'tlt': tlt, 'vac': vac, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


def ProjectsLFVView(request, tlt):

    exp = WorkExperience.objects.filter(talent__alias=tlt).select_related('topic', 'course', 'project')
    prj_qs = ProjectData.objects.all()
    #Project Summary
    prj = exp.values_list('project', flat=True).distinct('project')
    prj_set = {}
    prj_count = 0
    for p in prj:
        if p == None:
            pass
        else:
            prj_count +=1
            project_q = prj_qs.filter(pk=p).values_list('name', 'company__ename', 'companybranch__name', 'industry__industry')
            info_list=[project_q[0][1], project_q[0][2], project_q[0][3]]
            prj_set[project_q[0][0]] = info_list

    t = tuple(prj_set.items())

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(t, 20)

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

    template = 'talenttrack/apv_l_projects.html'
    context = {'tlt': tlt, 'vac': vac, 'prj_count': prj_count, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


def EduLFVView(request, tlt):

    exp = WorkExperience.objects.filter(talent__alias=tlt).select_related('topic', 'course', 'project')
    edtexp = exp.filter(edt=True).order_by('-date_from')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(edtexp, 20)

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

    template = 'talenttrack/apv_l_edu.html'
    context = {'tlt': tlt, 'vac': vac, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


def LCMFullView(request, tlt):
    '''View to show all licenses and certifications for a person.'''
    #tlt = Profile.objects.get(alias=tlt)
    lcm_qs = LicenseCertification.objects.filter(talent__alias=tlt).order_by('-issue_date')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(lcm_qs, 20)

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

    template = 'talenttrack/lcm_full_view.html'
    context = {
        'tlt': tlt, 'pageitems': pageitems, 'page_range': page_range
        }
    return render(request, template, context)


def SkillProfileDetailView(request, tlt):
    '''A list of all hours logged against a skill (for an individual) for experience and training'''
    tlt_p = Profile.objects.get(talent__alias=tlt)
    skill_qs = SkillTag.objects.all()
    exp = WorkExperience.objects.filter(talent__alias=tlt).select_related('topic')
    tlt_filter=tlt
    exp_skills = exp.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score))

    exp_s = exp_skills.values_list('skills', flat=True).distinct('skills')
    exp_t = exp_skills.order_by('topic__skills').values_list('topic__skills', flat=True).distinct('topic__skills')
    edt_topic = exp_skills.values_list('topic', flat=True).distinct('topic')

    exp_s_skill = exp_skills.values_list('skills__skill', flat=True).distinct('skills')
    exp_t_skill = exp_skills.order_by('topic__skills__skill').values_list('topic__skills__skill', flat=True).distinct('topic__skills__skill')

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

    tlt_id = [tlt_p.id]

    #Hours Experience per skill chart
    skills_hours_skill_data = []
    for s in ordered_skills_list:
        shwe = exp_skills.filter(Q(skills__skill=s, edt=False) | Q(topic__skills__skill=s, edt=True))
        skills_hours=[]
        for i in tlt_id:

            aw_exp = shwe.filter(talent=i, edt=False).aggregate(awet=Sum('hours_worked'))
            awetv = aw_exp.get('awet')
            if awetv == None:
                awetv = 0
            else:
                awetv = awetv

            at_exp = shwe.filter(talent=i, edt=True).aggregate(tet=Sum('topic__hours'))
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

        skills_hours_skill_data.append(sum_shwe)

    #Hours Training Experience per skill chart
    training_skills_hours_skill_data = []
    for s in ordered_skills_list:
        shwt = exp_skills.filter(Q(topic__skills__skill=s, edt=True))
        training_skills_hours=[]
        for i in tlt_id:

            at_exp = shwt.filter(talent=i, edt=True).aggregate(tet=Sum('topic__hours'))
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
    #gathering all experience hours per topic-this not working again
    exp_set = {}
    for s in exp_s:
        if s == None:
            pass
        else:
            b = skill_qs.get(pk=s)
            c = b.experience.filter(Q(talent__alias=tlt_filter) & Q(score__gte=skill_pass_score))
            #cnt = c.count()
            sum_h = c.aggregate(sum_s=Sum('hours_worked'))
            if sum_h.get('sum_s')==None:
                sum_float=0
            else:
                sum_float = float(sum_h.get('sum_s'))
            info_set = {}
            #info_set['count']=cnt
            info_set['sum']=sum_float
            skill_q = skill_qs.filter(pk=s).values_list('skill', flat=True)
            skill_f = skill_q[0]
            exp_set[skill_f] = info_set

    #gathering all training hours per topic
    edt_set = {}
    for c in edt_topic:
        #populating the keys
        for t in exp_t:
            if t == None:
                pass
            else:
                skill_q = skill_qs.filter(pk=t).values_list('skill', flat=True)
                skill_f = skill_q[0]
                edt_set[skill_f]=float(0)

        #populating the values
        for t in exp_t:
            if t == None:
                pass
            else:
                d = skill_qs.get(pk=t)
                e = exp_skills.filter(topic__skills=d)
                e_sum = e.aggregate(sum_t=Sum('topic__hours'))
                sum_float = float(e_sum.get('sum_t'))
                skill_q = skill_qs.filter(pk=t).values_list('skill', flat=True)
                skill_f = skill_q[0]
                if edt_set[skill_f]:
                    new = edt_t[skill_f]+sum_float
                    d[skill_f]=new
                else:
                    edt_set[skill_f] = sum_float

    template = 'talenttrack/talent_profile_detail_summary.html'
    context = {
        'skills_list_Labels': skills_list_Labels,
        'skills_hours_skill_data': skills_hours_skill_data,
        'training_skills_hours_skill_data': training_skills_hours_skill_data,
        'skills_count': skills_count,
        'dept_skills_link': dept_skills_link,
        'edt_set': edt_set, 'exp_set': exp_set, 'tlt_p': tlt_p, 'tlt': tlt,
    }
    return render(request, template, context)


def SumAllExperienceView(request, tlt):
    '''A list of all hours logged against a skill for experience and training'''
    talent = request.user.id
    tlt_p = Profile.objects.get(alias=tlt)
    skill_qs = SkillTag.objects.all()
    #Full list experience
    exp = WorkExperience.objects.filter(talent__alias=tlt).select_related('topic')
    # Validated Experience
    val_exp_skills = exp.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score))

    exp_s = exp.values_list('skills', flat=True).distinct('skills')
    exp_t = exp.order_by('topic__skills').values_list('topic__skills', flat=True).distinct('topic__skills')
    edt_topic = exp.values_list('topic', flat=True).distinct('topic')


    exp_s_skill = exp.values_list('skills__skill', flat=True).distinct('skills')
    exp_t_skill = exp.order_by('topic__skills__skill').values_list('topic__skills__skill', flat=True).distinct('topic__skills__skill')

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

    tlt_id = [tlt_p.id]

    #Hours Experience per skill chart
    skills_hours_skill_data = []
    for s in ordered_skills_list:
        shwe = exp.filter(Q(skills__skill=s, edt=False) | Q(topic__skills__skill=s, edt=True))
        skills_hours=[]
        for i in tlt_id:
            aw_exp = shwe.filter(talent=i, edt=False).aggregate(awet=Sum('hours_worked'))
            awetv = aw_exp.get('awet')
            if awetv == None:
                awetv = 0
            else:
                awetv = awetv

            at_exp = shwe.filter(talent=i, edt=True).aggregate(tet=Sum('topic__hours'))
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

        skills_hours_skill_data.append(sum_shwe)

    #Hours Validated Experience per skill chart
    val_skills_hours_skill_data = []
    for s in ordered_skills_list:
        shwe = val_exp_skills.filter(Q(skills__skill=s, edt=False) | Q(topic__skills__skill=s, edt=True))
        skills_hours=[]
        for i in tlt_id:
            aw_exp = shwe.filter(talent=i, edt=False).aggregate(awet=Sum('hours_worked'))
            awetv = aw_exp.get('awet')
            if awetv == None:
                awetv = 0
            else:
                awetv = awetv

            at_exp = shwe.filter(talent=i, edt=True).aggregate(tet=Sum('topic__hours'))
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
        shwt = exp.filter(Q(topic__skills__skill=s, edt=True))
        training_skills_hours=[]
        for i in tlt_id:

            at_exp = shwt.filter(talent=i, edt=True).aggregate(tet=Sum('topic__hours'))
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

    #gathering all experience hours per topic
    exp_set = {}
    for s in exp_s:
        if s == None:
            pass
        else:
            b = skill_qs.get(pk=s)
            c = b.experience.filter(talent__alias=tlt)
            cnt = c.count()
            s_sum = c.aggregate(sum_s=Sum('hours_worked'))
            sum_float = float(s_sum.get('sum_s'))
            info_set = {}
            info_set['count']=cnt
            info_set['sum']=sum_float
            skill_q = skill_qs.filter(pk=s).values_list('skill', flat=True)
            skill_f = skill_q[0]
            exp_set[skill_f] = info_set

    #gathering all training hours per topic
    edt_set = {}
    for c in edt_topic:
        #populating the keys
        for t in exp_t:
            if t == None:
                pass
            else:
                skill_q = skill_qs.filter(pk=t).values_list('skill', flat=True)
                skill_f = skill_q[0]
                edt_set[skill_f]=float(0)

        #populating the values
        for t in exp_t:
            if t == None:
                pass
            else:
                d = skill_qs.get(pk=t)
                e = exp.filter(topic__skills=d)
                e_sum = e.aggregate(sum_t=Sum('topic__hours'))
                sum_float = float(e_sum.get('sum_t'))
                skill_q = skill_qs.filter(pk=t).values_list('skill', flat=True)
                skill_f = skill_q[0]
                if edt_set[skill_f]:
                    new = edt_t[skill_f]+sum_float
                    d[skill_f]=new
                else:
                    edt_set[skill_f] = sum_float

    template = 'talenttrack/talent_detail_summary.html'
    context = {
        'skills_list_Labels': skills_list_Labels,
        'skills_hours_skill_data': skills_hours_skill_data,
        'val_skills_hours_skill_data': val_skills_hours_skill_data,
        'training_skills_hours_skill_data': training_skills_hours_skill_data,
        'skills_count': skills_count,
        'dept_skills_link': dept_skills_link,
        'edt_set': edt_set, 'tlt': tlt, 'exp_set': exp_set, 'tlt_p': tlt_p, 'talent': talent,
    }
    return render(request, template, context)


def DPC_SummaryView(request, tlt):
    '''View for Designation, Project and Company hours logged'''
    #caching
    exp = WorkExperience.objects.filter(talent__alias = tlt).select_related('designation')
    designation_qs = Designation.objects.all()
    companybranch_qs = Branch.objects.all()
    project_qs = ProjectData.objects.all()
    tlt = tlt

    #Designation Summary
    dgn = exp.values_list('designation', flat=True).distinct('designation')

    dgn_set = {}
    for d in dgn:
        if d == None:
            pass
        else:
            a = designation_qs.get(pk=d)
            b = a.workexperience_set.all()

            sum = b.aggregate(sum_d=Sum('hours_worked'))
            sum_float = float(sum.get('sum_d'))

            confirmed = b.filter(score__gte=skill_pass_score)
            confirmed_s = confirmed.aggregate(sum_dc=Sum('hours_worked'))

            cnt = b.count()
            cnt_c = confirmed.count()
            unconfirmed_count = cnt-cnt_c

            sum_c = confirmed_s.get('sum_dc')
            if sum_c is None:
                sum_float_c = 0
            else:
                sum_float_c = float(sum_c)

            info_set = {}
            info_set['confirmed']=sum_float_c
            info_set['cnt_u']=unconfirmed_count
            info_set['sum']=sum_float

            designation_q = designation_qs.filter(pk=d).values_list('name', flat=True)
            designation_f = designation_q[0]
            dgn_set[designation_f] = info_set


    #Company Summary - Listed Per Branch
    cmp = exp.values_list('companybranch', flat=True).distinct('companybranch')
    cmp_set = {}
    for c in cmp:
        if c == None:
            pass
        else:
            a = companybranch_qs.get(pk=c)
            b = a.workexperience_set.all()

            sum = b.aggregate(sum_d=Sum('hours_worked'))
            sum_float = float(sum.get('sum_d'))

            confirmed = b.filter(score__gte=skill_pass_score)
            confirmed_s = confirmed.aggregate(sum_dc=Sum('hours_worked'))

            cnt = b.count()
            cnt_c = confirmed.count()
            unconfirmed_count = cnt-cnt_c

            sum_c = confirmed_s.get('sum_dc')
            if sum_c is None:
                sum_float_c = 0
            else:
                sum_float_c = float(sum_c)

            info_set = {}
            info_set['confirmed']=sum_float_c
            info_set['cnt_u']=unconfirmed_count
            info_set['sum']=sum_float

            companybranch_q = companybranch_qs.filter(pk=c).values_list('company__ename', 'name', 'city__city')
            companybranch_f = f'{companybranch_q[0][0]}: {companybranch_q[0][1]} ({companybranch_q[0][2]})'
            cmp_set[companybranch_f] = info_set

    #Project Summary
    prj = exp.values_list('project', flat=True).distinct('project')
    prj_set = {}
    for p in prj:
        if p == None:
            pass
        else:
            a = project_qs.get(pk=p)
            b = a.workexperience_set.all()

            sum = b.aggregate(sum_d=Sum('hours_worked'))
            sum_float = float(sum.get('sum_d'))

            confirmed = b.filter(score__gte=skill_pass_score)
            confirmed_s = confirmed.aggregate(sum_dc=Sum('hours_worked'))

            cnt = b.count()
            cnt_c = confirmed.count()
            unconfirmed_count = cnt-cnt_c

            sum_c = confirmed_s.get('sum_dc')
            if sum_c is None:
                sum_float_c = 0
            else:
                sum_float_c = float(sum_c)

            info_set = {}
            info_set['confirmed']=sum_float_c
            info_set['cnt_u']=unconfirmed_count
            info_set['sum']=sum_float

            project_q = project_qs.filter(pk=p).values_list('name', 'company__ename', 'companybranch__name')
            project_f = f'{project_q[0][0]}: {project_q[0][1]} ({project_q[0][2]})'
            prj_set[project_f] = info_set

    template = 'talenttrack/talent_dpc_summary.html'
    context = {
        'dgn_set': dgn_set, 'tlt': tlt, 'cmp_set': cmp_set, 'prj_set': prj_set,
    }
    return render(request, template, context)


def DPCP_SummaryView(request, tlt):
    '''View for Designation, Project and Company hours logged'''
    #caching
    exp = WorkExperience.objects.filter(talent__alias = tlt).select_related('designation')
    designation_qs = Designation.objects.all()
    companybranch_qs = Branch.objects.all()
    project_qs = ProjectData.objects.all()
    tlt = tlt

    #Designation Summary
    dgn = exp.values_list('designation', flat=True).distinct('designation')

    dgn_set = {}
    for d in dgn:
        if d == None:
            pass
        else:
            a = designation_qs.get(pk=d)
            b = a.workexperience_set.all()

            sum = b.aggregate(sum_d=Sum('hours_worked'))
            sum_float = float(sum.get('sum_d'))

            confirmed = b.filter(score__gte=skill_pass_score)
            confirmed_s = confirmed.aggregate(sum_dc=Sum('hours_worked'))

            cnt = b.count()
            cnt_c = confirmed.count()
            unconfirmed_count = cnt-cnt_c



            sum_c = confirmed_s.get('sum_dc')
            if sum_c is None:
                sum_float_c = 0
            else:
                sum_float_c = float(sum_c)

            info_set = {}
            info_set['sum']=sum_float
            info_set['confirmed']=sum_float_c
            info_set['cnt_u']=unconfirmed_count
            designation_q = designation_qs.filter(pk=d).values_list('name', flat=True)
            designation_f = designation_q[0]
            dgn_set[designation_f] = info_set


    #Company Summary - Listed Per Branch
    cmp = exp.values_list('companybranch', flat=True).distinct('companybranch')
    cmp_set = {}
    for c in cmp:
        if c == None:
            pass
        else:
            a = companybranch_qs.get(pk=c)
            b = a.workexperience_set.all()

            sum = b.aggregate(sum_d=Sum('hours_worked'))
            sum_float = float(sum.get('sum_d'))

            confirmed = b.filter(score__gte=skill_pass_score)
            confirmed_s = confirmed.aggregate(sum_dc=Sum('hours_worked'))

            sum_c = confirmed_s.get('sum_dc')
            if sum_c is None:
                confirmed_float = 0
            else:
                confirmed_float = float(sum_c)

            cnt = b.count()
            cnt_c = confirmed.count()
            unconfirmed_count = cnt-cnt_c

            info_set = {}
            info_set['confirmed']=confirmed_float
            info_set['sum']=sum_float
            info_set['cnt_u']=unconfirmed_count

            companybranch_q = companybranch_qs.filter(pk=c).values_list('company__ename', 'name', 'city__city')
            companybranch_f = f'{companybranch_q[0][0]}: {companybranch_q[0][1]} ({companybranch_q[0][2]})'
            cmp_set[companybranch_f] = info_set

    #Project Summary
    prj = exp.values_list('project', flat=True).distinct('project')
    prj_set = {}
    for p in prj:
        if p == None:
            pass
        else:
            a = project_qs.get(pk=p)
            b = a.workexperience_set.all()
            sum = b.aggregate(sum_d=Sum('hours_worked'))
            sum_float = float(sum.get('sum_d'))

            confirmed = b.filter(score__gte=skill_pass_score)
            confirmed_s = confirmed.aggregate(sum_dc=Sum('hours_worked'))

            sum_c = confirmed_s.get('sum_dc')
            if sum_c is None:
                confirmed_float = 0
            else:
                confirmed_float = float(sum_c)

            cnt = b.count()
            cnt_c = confirmed.count()
            unconfirmed_count = cnt-cnt_c

            info_set = {}
            info_set['confirmed']=confirmed_float
            info_set['sum']=sum_float
            info_set['cnt_u']=unconfirmed_count

            project_q = project_qs.filter(pk=p).values_list('name', 'company__ename', 'companybranch__name')
            project_f = f'{project_q[0][0]}: {project_q[0][1]} ({project_q[0][2]})'
            prj_set[project_f] = info_set

    template = 'talenttrack/talent_dpcp_summary.html'
    context = {
        'dgn_set': dgn_set, 'tlt': tlt, 'cmp_set': cmp_set, 'prj_set': prj_set,
    }
    return render(request, template, context)


@login_required()
@csp_exempt
def PreLoggedExperienceCaptureView(request):
    form = PreLoggedExperienceForm(request.POST or None, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.prelog = True
            new.save()
            form.save_m2m()
            response = redirect(reverse('Talent:ColleagueSelect', kwargs={'pk': new.id}))
            response.delete_cookie("confirm")
            return response
        else:
            template = 'talenttrack/prelogged_capture.html'
            context = {'form': form}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/prelogged_capture.html'
        context = {'form': form}
        response = render(request, template, context)
        response.set_cookie("confirm","PC")
        return response


@login_required()
def PreLoggedExperienceDeleteView(request, ple_pk):
    info = WorkExperience.objects.get(pk=ple_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:Home')+'#headingThree')
    else:
        raise PermissionDenied


@login_required()
def PreLoggedExperienceDeleteFullView(request, ple_pk):
    info = WorkExperience.objects.get(pk=ple_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:PreExperienceList'))
    else:
        raise PermissionDenied


@login_required()
def PreLogDetailView(request, tex):
    check = WorkExperience.objects.get(slug=tex, prelog=True)
    if check.talent == request.user:
        sum = WorkExperience.objects.filter(talent=request.user, prelog=True)
        sum_company = sum.filter(company=check.company).aggregate(co_sum=Sum('hours_worked'))
        sum_project = sum.filter(project=check.project).aggregate(p_sum=Sum('hours_worked'))
        list = WorkExperience.objects.filter(slug=tex)
        confirmed_clg = WorkColleague.objects.filter(experience__slug=tex)
        confirmed_sup = Superior.objects.filter(experience__slug=tex)
        confirmed_clr = WorkCollaborator.objects.filter(experience__slug=tex)
        confirmed_cnt = WorkClient.objects.filter(experience__slug=tex)

        template = 'talenttrack/prelogged_experience_detail.html'
        context = {
            'check': check, 'confirmed_clg': confirmed_clg, 'confirmed_sup': confirmed_sup, 'confirmed_clr': confirmed_clr, 'confirmed_cnt': confirmed_cnt, 'list': list, 'sum_company': sum_company, 'sum_project': sum_project, 'client_score': client_score, 'colleague_score': colleague_score, 'pre_colleague_score': pre_colleague_score, 'collaborator_score': collaborator_score, 'superior_score': superior_score
            }

        return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def ClientSelectView(request, pk):
    score = client_score
    instance = WorkExperience.objects.get(pk=pk)
    #>>>Create a set of users to exclude
    colleague_excl = set(WorkColleague.objects.filter(experience=pk).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience=pk).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience=pk).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience=pk).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    if request.is_ajax():
        qry = request.GET.get('term')
        people = CustomUser.objects.filter(~Q(id__in=filt)).filter(Q(first_name__icontains=qry) | Q(last_name__icontains=qry) | Q(email__icontains=qry) | Q(display_text__icontains=qry)).order_by('last_name')
        response_content = list(people.values('id','display_text'))

        return JsonResponse(response_content, safe=False)

    form = WorkClientSelectForm(request.POST or None, pwd=filt)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:ClientSelect', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect('Talent:Home')
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/experience_client_select.html'
            context = {'instance': instance, 'form': form, 'score': score,}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_client_select.html'
        context = {'instance': instance, 'form': form, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","WT", "check",pk)
        return response


@login_required()
@csp_exempt
def ClientAddView(request, tex):
    score = client_score
    instance = get_object_or_404(WorkExperience, slug=tex)
    tex = tex
    #>>>Create a set of users to exclude
    colleague_excl = set(WorkColleague.objects.filter(experience__slug=tex).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience__slug=tex).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience__slug=tex).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience__slug=tex).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    if request.is_ajax():
        qry = request.GET.get('term')
        people = CustomUser.objects.filter(~Q(id__in=filt)).filter(Q(first_name__icontains=qry) | Q(last_name__icontains=qry) | Q(email__icontains=qry) | Q(display_text__icontains=qry)).order_by('last_name')
        response_content = list(people.values('id','display_text'))

        return JsonResponse(response_content, safe=False)

    form = WorkClientSelectForm(request.POST or None, pwd=filt)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            response = redirect(reverse('Talent:ExperienceDetail', kwargs={'tex': tex}))
            response.delete_cookie("confirm")
            return response
        else:
            template = 'talenttrack/experience_client_add.html'
            context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
            response =  render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_client_add.html'
        context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
        response =  render(request, template, context)
        response.set_cookie("confirm","WT")
        return response


@login_required()
def ClientResponseView(request, wkc):
    check = WorkClient.objects.get(slug=wkc)
    if check.experience.talent == request.user:
        form = WorkClientResponseForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/experience_client_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def ClientPreResponseView(request, wkc):
    check = WorkClient.objects.get(slug=wkc)
    if check.experience.talent == request.user:
        form = WorkClientResponseForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/prelogged_experience_client_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def CollaboratorSelectView(request, pk):
    score = collaborator_score
    instance = WorkExperience.objects.get(pk=pk)

    colleague_excl = set(WorkColleague.objects.filter(experience=pk).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience=pk).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience=pk).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience=pk).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    if request.is_ajax():
        qry = request.GET.get('term')
        people = CustomUser.objects.filter(~Q(id__in=filt)).filter(Q(first_name__icontains=qry) | Q(last_name__icontains=qry) | Q(email__icontains=qry) | Q(display_text__icontains=qry)).order_by('last_name')
        response_content = list(people.values('id','display_text'))

        return JsonResponse(response_content, safe=False)

    form = WorkCollaboratorSelectForm(request.POST or None, pwd=filt)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:CollaboratorSelect', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response

            elif 'done' in request.POST:
                response = redirect(reverse('Talent:ClientSelect', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/experience_collaborator_select.html'
            context = {'instance': instance, 'form': form, 'score': score,}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_collaborator_select.html'
        context = {'instance': instance, 'form': form, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","WL")
        return response


@login_required()
@csp_exempt
def CollaboratorAddView(request, tex):
    score = collaborator_score
    instance = get_object_or_404(WorkExperience, slug=tex)
    tex = tex

    colleague_excl = set(WorkColleague.objects.filter(experience__slug=tex).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience__slug=tex).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience__slug=tex).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience__slug=tex).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    if request.is_ajax():
        qry = request.GET.get('term')
        people = CustomUser.objects.filter(~Q(id__in=filt)).filter(Q(first_name__icontains=qry) | Q(last_name__icontains=qry) | Q(email__icontains=qry) | Q(display_text__icontains=qry)).order_by('last_name')
        response_content = list(people.values('id','display_text'))

        return JsonResponse(response_content, safe=False)

    form = WorkCollaboratorSelectForm(request.POST or None, pwd=filt)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            response = redirect(reverse('Talent:ExperienceDetail', kwargs={'tex': tex}))
            response.delete_cookie("confirm")
            return response
        else:
            template = 'talenttrack/experience_collaborator_add.html'
            context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_collaborator_add.html'
        context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","WL")
        return response


@login_required()
def CollaboratorResponseView(request, clb):
    check = WorkCollaborator.objects.get(slug=clb)
    if check.experience.talent == request.user:
        form = WorkCollaboratorResponseForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/experience_collaborator_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def CollaboratorPreResponseView(request, clb):
    check = WorkCollaborator.objects.get(slug=clb)
    if check.experience.talent == request.user:
        form = WorkCollaboratorResponseForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/prelogged_experience_collaborator_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def SuperiorSelectView(request, pk):
    score = superior_score
    instance = WorkExperience.objects.get(pk=pk)

    colleague_excl = set(WorkColleague.objects.filter(experience=pk).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience=pk).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience=pk).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience=pk).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    if request.is_ajax():
        qry = request.GET.get('term')
        people = CustomUser.objects.filter(~Q(id__in=filt)).filter(Q(first_name__icontains=qry) | Q(last_name__icontains=qry) | Q(email__icontains=qry) | Q(display_text__icontains=qry)).order_by('last_name')
        response_content = list(people.values('id','display_text'))

        return JsonResponse(response_content, safe=False)

    form = SuperiorSelectForm(request.POST or None, pwd=filt)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:SuperiorSelect', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:CollaboratorSelect', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/experience_superior_select.html'
            context = {'instance': instance, 'form': form, 'score': score,}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_superior_select.html'
        context = {'instance': instance, 'form': form, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","WS")
        return response


@login_required()
@csp_exempt
def SuperiorAddView(request, tex):
    score = superior_score
    instance = get_object_or_404(WorkExperience, slug=tex)
    tex = tex

    colleague_excl = set(WorkColleague.objects.filter(experience__slug=tex).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience__slug=tex).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience__slug=tex).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience__slug=tex).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    if request.is_ajax():
        qry = request.GET.get('term')
        people = CustomUser.objects.all().filter(~Q(id__in=filt)).filter(Q(first_name__icontains=qry) | Q(last_name__icontains=qry) | Q(email__icontains=qry) | Q(display_text__icontains=qry)).order_by('last_name')
        response_content = list(people.values('id','display_text'))

        return JsonResponse(response_content, safe=False)

    form = SuperiorSelectForm(request.POST or None, pwd=filt)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            response = redirect(reverse('Talent:ExperienceDetail', kwargs={'tex': tex}))
            response.delete_cookie("confirm")
            return response
        else:
            template = 'talenttrack/experience_superior_add.html'
            context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_superior_add.html'
        context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","WS")
        return response


@login_required()
def SuperiorResponseView(request, spr):
    check = Superior.objects.get(slug=spr)
    if check.experience.talent == request.user:
        form = WorkColleagueResponseForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/experience_superior_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def SuperiorPreResponseView(request, spr):
    check = Superior.objects.get(slug=spr)
    if check.experience.talent == request.user:
        form = WorkColleagueResponseForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/prelogged_experience_superior_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def ColleagueSelectView(request, pk):
    score = colleague_score
    instance = WorkExperience.objects.get(pk=pk)
    tex = instance.slug

    colleague_excl = set(WorkColleague.objects.filter(experience__slug=tex).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience__slug=tex).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience__slug=tex).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience__slug=tex).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    if request.is_ajax():
        qry = request.GET.get('term')
        people = CustomUser.objects.all().filter(~Q(id__in=filt)).filter(Q(first_name__icontains=qry) | Q(last_name__icontains=qry) | Q(email__icontains=qry) | Q(display_text__icontains=qry)).order_by('last_name')
        response_content = list(people.values('id','display_text'))

        return JsonResponse(response_content, safe=False)

    form = WorkColleagueSelectForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:ColleagueSelect', kwargs={'pk':pk}))
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:SuperiorSelect', kwargs={'pk':instance.id}))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/experience_colleague_select.html'
            context = {'instance': instance, 'form': form, 'score': score,}
            response =  render(request, template, context)
            return response
    else:
        template = 'talenttrack/experience_colleague_select.html'
        context = {'instance': instance, 'form': form, 'score': score,}
        response =  render(request, template, context)
        response.set_cookie("confirm","WC")
        return response


@login_required()
@csp_exempt
def ColleagueAddView(request, tex):
    score = colleague_score
    instance = get_object_or_404(WorkExperience, slug=tex)

    colleague_excl = set(WorkColleague.objects.filter(experience__slug=tex).values_list('colleague_name', flat=True))
    superior_excl = set(Superior.objects.filter(experience__slug=tex).values_list('superior_name', flat=True))
    collab_excl = set(WorkCollaborator.objects.filter(experience__slug=tex).values_list('collaborator_name', flat=True))
    client_excl = set(WorkClient.objects.filter(experience__slug=tex).values_list('client_name', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = colleague_excl | superior_excl | collab_excl | client_excl | myself

    if request.is_ajax():
        qry = request.GET.get('term')
        people = CustomUser.objects.all().filter(~Q(id__in=filt)).filter(Q(first_name__icontains=qry) | Q(last_name__icontains=qry) | Q(email__icontains=qry) | Q(display_text__icontains=qry)).order_by('last_name')
        response_content = list(people.values('id','display_text'))

        return JsonResponse(response_content, safe=False)

    form = WorkColleagueSelectForm(request.POST or None, pwd=filt)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            response = redirect(reverse('Talent:ExperienceDetail', kwargs={'tex':tex}))
            response.delete_cookie("confirm")
            return response
        else:
            template = 'talenttrack/experience_colleague_add.html'
            context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
            response = render(request, template, context)
            return response

    else:
        template = 'talenttrack/experience_colleague_add.html'
        context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","WC")
        return response


@login_required()
def ColleagueResponseView(request, clg):
    check = WorkColleague.objects.get(slug=clg)
    if check.experience.talent == request.user:
        form = WorkColleagueResponseForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/experience_colleague_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def ColleaguePreResponseView(request, clg):
    check = WorkColleague.objects.get(slug=clg)
    if check.experience.talent == request.user:
        form = WorkColleagueResponseForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/prelogged_experience_colleague_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def ExperienceDetailView(request, tex):
    check = WorkExperience.objects.get(slug=tex)
    if check.talent == request.user:
        sum = WorkExperience.objects.filter(talent=request.user, wexp=True)
        sum_company = sum.filter(company=check.company).aggregate(co_sum=Sum('hours_worked'))
        sum_project = sum.filter(project=check.project).aggregate(p_sum=Sum('hours_worked'))
        list = WorkExperience.objects.filter(slug=tex)
        confirmed_clg = WorkColleague.objects.filter(experience__slug=tex)
        confirmed_sup = Superior.objects.filter(experience__slug=tex)
        confirmed_clr = WorkCollaborator.objects.filter(experience__slug=tex)
        confirmed_cnt = WorkClient.objects.filter(experience__slug=tex)

        template = 'talenttrack/experience_detail.html'
        context = {'check': check, 'confirmed_clg': confirmed_clg, 'confirmed_sup': confirmed_sup, 'confirmed_clr': confirmed_clr, 'confirmed_cnt': confirmed_cnt, 'list': list, 'sum_company': sum_company, 'sum_project': sum_project, 'client_score': client_score, 'colleague_score': colleague_score, 'pre_colleague_score': pre_colleague_score, 'collaborator_score': collaborator_score, 'superior_score': superior_score}
        return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def ExperienceDeleteView(request, pk):
    info = WorkExperience.objects.get(pk=pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:Home')+'#experience')
        else:
            return redirect(reverse('Talent:Home')+'#experience')
    else:
        raise PermissionDenied


@login_required()
def EducationDetailDeleteView(request, pk):
    info = WorkExperience.objects.get(pk=pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:Home')+'#education')
        else:
            return redirect(reverse('Talent:Home')+'#education')
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def WorkExperienceCaptureView(request):
    form = WorkExperienceForm(request.POST or None, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.wexp = True
            new.save()
            form.save_m2m()
            return redirect(reverse('Talent:ColleagueSelect', kwargs={'pk': new.id}))
        else:
            template = 'talenttrack/experience_capture.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        template = 'talenttrack/experience_capture.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
@csp_exempt
def WorkExperienceEditView(request, we_slug):
    instance = get_object_or_404(WorkExperience, slug=we_slug)
    form = WorkExperienceForm(request.POST or None, request.FILES, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.wexp = True
            new.save()
            form.save_m2m()
            return redirect(reverse('Talent:ColleagueSelect', kwargs={'pk': new.id}))
        else:
            template = 'talenttrack/experience_capture.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        template = 'talenttrack/experience_capture.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
def WorkExperienceDeleteView(request, we_pk):
    info = WorkExperience.objects.get(pk=we_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:Home')+'#headingThree')
    else:
        raise PermissionDenied


@login_required()
def WorkExperienceDeleteFullView(request, we_pk):
    info = WorkExperience.objects.get(pk=we_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:ExperienceList'))
    else:
        raise PermissionDenied


@login_required()
def WorkExperienceDeleteSkillView(request, we_pk, skl):
    info = WorkExperience.objects.get(pk=we_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:SkillsStats', kwargs={'skl': skl}))
    else:
        raise PermissionDenied


@login_required()
def WorkExperienceDeleteSkillFullView(request, we_pk, skl):
    info = WorkExperience.objects.get(pk=we_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:SkillWorkExperienceList', kwargs={'skl':skl}))
    else:
        raise PermissionDenied


@login_required()
def EducationDetail(request, tex):
    check = WorkExperience.objects.get(slug=tex, edt=True)
    if check.talent == request.user:
        confirmed_l = Lecturer.objects.filter(education__slug=tex)
        confirmed_cm = ClassMates.objects.filter(education__slug=tex)
        template = 'talenttrack/education_detail.html'
        context = {'check': check, 'confirmed_l': confirmed_l, 'confirmed_cm': confirmed_cm, 'classmate_score': classmate_score, 'lecturer_score': lecturer_score}
        return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def LecturerResponse(request, lct):
    check = Lecturer.objects.get(slug=lct)
    if check.education.talent == request.user:
        form = LecturerRespondForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/education_lecturer_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def ClassMatesResponse(request, cmt):
    check = ClassMates.objects.get(slug=cmt)
    if check.education.talent == request.user:
        form = ClassMatesRespondForm(request.POST or None, instance=check)
        if request.method =='POST':
            next_url=request.POST.get('next', '/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Talent:Home')
                return HttpResponseRedirect(next_url)
        else:
            template = 'talenttrack/education_classmates_respond.html'
            context = {'check': check, 'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def LecturerSelectView(request, tex):
    score = lecturer_score
    instance = WorkExperience.objects.get(slug=tex)

    lecturer_excl = set(Lecturer.objects.filter(education__slug=tex).values_list('lecturer', flat=True))
    colleague_excl = set(ClassMates.objects.filter(education__slug=tex).values_list('colleague', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = lecturer_excl | colleague_excl | myself

    if request.is_ajax():
        qry = request.GET.get('term')
        people = CustomUser.objects.all().filter(~Q(id__in=filt)).filter(Q(first_name__icontains=qry) | Q(last_name__icontains=qry) | Q(email__icontains=qry) | Q(display_text__icontains=qry)).order_by('last_name')
        response_content = list(people.values('id','display_text'))

        return JsonResponse(response_content, safe=False)

    form = LecturerSelectForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.topic = instance.topic
            new.save()
            if 'another' in request.POST:
                return redirect(reverse('Talent:LecturerSelect', kwargs={'tex': tex}))
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:ClassMatesSelect', kwargs={'tex': tex}))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/education_lecturer_select.html'
            context = {'instance': instance, 'form': form, 'score': score,}
            response = render(request, template, context)
            response.set_cookie("confirm","LR")
            return response
    else:
        template = 'talenttrack/education_lecturer_select.html'
        context = {'instance': instance, 'form': form, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","LR")
        return response


@login_required()
@csp_exempt
def LecturerAddView(request, tex):
    score = lecturer_score
    instance = get_object_or_404(WorkExperience, slug=tex)
    tex = tex

    lecturer_excl = set(Lecturer.objects.filter(education__slug=tex).values_list('lecturer', flat=True))
    colleague_excl = set(ClassMates.objects.filter(education__slug=tex).values_list('colleague', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = lecturer_excl | colleague_excl | myself

    if request.is_ajax():
        qry = request.GET.get('term')
        people = CustomUser.objects.all().filter(~Q(id__in=filt)).filter(Q(first_name__icontains=qry) | Q(last_name__icontains=qry) | Q(email__icontains=qry) | Q(display_text__icontains=qry)).order_by('last_name')
        response_content = list(people.values('id','display_text'))

        return JsonResponse(response_content, safe=False)

    form = LecturerSelectForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.course = instance.course
            new.topic = instance.topic
            new.save()
            response = redirect(reverse('Talent:EducationDetail', kwargs={'tex': tex}))
            response.delete_cookie("confirm")
            return response
        else:
            template = 'talenttrack/education_lecturer_add.html'
            context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
            response = render(request, template, context)
            response.set_cookie("confirm","LR")
            return response
    else:
        template = 'talenttrack/education_lecturer_add.html'
        context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","LR")
        return response


@login_required()
@csp_exempt
def ClassMateSelectView(request, tex):
    score = classmate_score
    instance = WorkExperience.objects.get(slug=tex)

    lecturer_excl = set(Lecturer.objects.filter(education__slug=tex).values_list('lecturer', flat=True))
    colleague_excl = set(ClassMates.objects.filter(education__slug=tex).values_list('colleague', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = lecturer_excl | colleague_excl | myself

    if request.is_ajax():
        qry = request.GET.get('term')
        people = CustomUser.objects.all().filter(~Q(id__in=filt)).filter(Q(first_name__icontains=qry) | Q(last_name__icontains=qry) | Q(email__icontains=qry) | Q(display_text__icontains=qry)).order_by('last_name')
        response_content = list(people.values('id','display_text'))
        return JsonResponse(response_content, safe=False)

    form = ClassMatesSelectForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.course = instance.course
            new.topic = instance.topic
            new.save()
            if 'another' in request.POST:
                return redirect(reverse('Talent:ClassMatesSelect', kwargs={'tex': tex}))
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:Home'))
                response.delete_cookie("confirm")
                return response
        else:
            template = 'talenttrack/education_classmate_select.html'
            context = {'instance': instance, 'form': form, 'score': score,}
            response = render(request, template, context)
            return response
    else:
        template = 'talenttrack/education_classmate_select.html'
        context = {'instance': instance, 'form': form, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","CM")
        return response


@login_required()
@csp_exempt
def ClassMateAddView(request, tex):
    score = classmate_score
    instance = get_object_or_404(WorkExperience, slug=tex)

    lecturer_excl = set(Lecturer.objects.filter(education__slug=tex).values_list('lecturer', flat=True))
    colleague_excl = set(ClassMates.objects.filter(education__slug=tex).values_list('colleague', flat=True))
    myself = set(Profile.objects.filter(talent=request.user).values_list('talent', flat=True))

    filt = lecturer_excl | colleague_excl | myself

    if request.is_ajax():
        qry = request.GET.get('term')
        people = CustomUser.objects.all().filter(~Q(id__in=filt)).filter(Q(first_name__icontains=qry) | Q(last_name__icontains=qry) | Q(email__icontains=qry) | Q(display_text__icontains=qry)).order_by('last_name')
        response_content = list(people.values('id','display_text'))

        return JsonResponse(response_content, safe=False)

    form = ClassMatesSelectForm(request.POST or None, pwd=filt)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.course = instance.course
            new.topic = instance.topic
            new.save()
            response = redirect(reverse('Talent:EducationDetail', kwargs={'tex': tex}))
            response.delete_cookie("confirm")
            return response
        else:
            template = 'talenttrack/education_classmate_add.html'
            context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
            response = render(request, template, context)
            response.set_cookie("confirm","CM")
            return response
    else:
        template = 'talenttrack/education_classmate_add.html'
        context = {'instance': instance, 'form': form, 'tex': tex, 'score': score,}
        response = render(request, template, context)
        response.set_cookie("confirm","CM")
        return response


@login_required()
@csp_exempt
def EducationCaptureView(request):
    form = EducationForm(request.POST or None, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.edt = True
            new.save()
            form.save_m2m()
            return redirect(reverse('Talent:LecturerSelect', kwargs={'tex': new.slug}))
        else:
            template = 'talenttrack/education_capture.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        template = 'talenttrack/education_capture.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
@csp_exempt
def EducationEditView(request, edt_slug):
    instance = get_object_or_404(WorkExperience, slug=edt_slug)
    form = EducationForm(request.POST or None, request.FILES, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.edt = True
            new.save()
            form.save_m2m()
            return redirect(reverse('Talent:LecturerSelect', kwargs={'tex': new.slug}))
        else:
            template = 'talenttrack/education_capture.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        template = 'talenttrack/education_capture.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
def EducationDeleteView(request, edt_pk):
    info = WorkExperience.objects.get(pk=edt_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:Home')+'#heading1')
    else:
        raise PermissionDenied


@login_required()
def EducationDeleteFullView(request, edt_pk):
    info = WorkExperience.objects.get(pk=edt_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:TrainingList'))
    else:
        raise PermissionDenied


@login_required()
def EducationDeleteSkillView(request, edt_pk, skl):
    info = WorkExperience.objects.get(pk=edt_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:SkillsStats', kwargs={'skl': skl}))
    else:
        raise PermissionDenied


@login_required()
def EducationDeleteSkillFullView(request, edt_pk, skl):
    info = WorkExperience.objects.get(pk=edt_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Talent:SkillEducationList', kwargs={'skl': skl}))
    else:
        raise PermissionDenied


#>>>Course Popup
@login_required()
@csp_exempt
def CourseAddPopup(request):
    form = CourseForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_course");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'talenttrack/course_popup.html'
            return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'talenttrack/course_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_course_id(request):
    if request.is_ajax():
        course = request.Get['course']
        course_id = Course.objects.get(name = course).id
        data = {'course_id':course_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Course Popup

#>>>CourseType Popup
@login_required()
@csp_exempt
def CourseTypeAddPopup(request):
    form = CourseTypeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_course_type");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'talenttrack/course_type_popup.html'
            return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'talenttrack/course_type_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_coursetype_id(request):
    if request.is_ajax():
        coursetype = request.Get['coursetype']
        coursetype_id = CourseType.objects.get(type = coursetype).id
        data = {'coursetype_id':coursetype_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< CourseType Popup

#>>>Result Popup
@login_required()
@csp_exempt
def ResultAddPopup(request):
    form = ResultForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_certification");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'talenttrack/result_popup.html'
            return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'talenttrack/result_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_result_id(request):
    if request.is_ajax():
        result = request.Get['result']
        result_id = Result.objects.get(type = result).id
        data = {'result_id':result_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Result Popup

#>>>Topic Popup
@login_required()
@csp_exempt
def TopicAddPopup(request):
    form = TopicPopForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            form.save_m2m()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_topic");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'talenttrack/topic_popup.html'
            return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'talenttrack/topic_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_topic_id(request):
    if request.is_ajax():
        topic = request.Get['topic']
        topic_id = Topic.objects.get(topic = topic).id
        data = {'topic_id':topic_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Topic Popup


#>>>Designation Popup
@login_required()
@csp_exempt
def DesignationAddPopup(request):
    cap_des = set(Designation.objects.all().values_list('name', flat=True))
    filt = cap_des

    form = DesignationForm(request.POST or None, pwd=filt)

    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_designation");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'talenttrack/designation_popup.html'
            return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'talenttrack/designation_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_designation_id(request):
    if request.is_ajax():
        designation = request.Get['designation']
        designation_id = Designation.objects.get(name = designation).id
        data = {'designation_id':designation_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Designation Popup
