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
from django.utils import timezone
from statistics import mean
from users.models import CustomUser

from core.decorators import corp_permission, subscription
from django.contrib.postgres.search import SearchVector, TrigramSimilarity
from django.db.models.functions import Greatest

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import (
    CorporateStaff, OrgStructure
    )
from .forms import (
    OrgStructureForm, AddStaffForm, StaffSearchForm, AdminTypeForm, AddNewStaffForm
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
from db_flatten.models import SkillTag


from WeXlog.app_config import (
    skill_pass_score, locked_age,
)


@login_required()
@corp_permission(1)
def dept_skill_dashboard(request, cor, dept, skl):
    skill = SkillTag.objects.get(id=skl)

    structure = OrgStructure.objects.filter(Q(corporate__slug=cor) & Q(level_name=dept))
    # Full Staff List
    staff_list = CorporateStaff.objects.filter(Q(corporate__slug=cor) & Q(department__level_name=dept) & Q(date_to__isnull=True))

    current_staff = staff_list.values_list('talent__id', flat=True)

    today = timezone.now().date()

    staff_id = Profile.objects.filter(talent__id__in=current_staff).values_list('id', flat=True)

    we = WorkExperience.objects.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score))

    we_skill = we.filter(Q(skills__skill=skill.skill, edt=False) | Q(topic__skills__skill=skill.skill, edt=True))

    staff_skills_id = we_skill.filter(talent__id__in=current_staff).values_list('talent__id', flat=True)

    staff_skill = Profile.objects.filter(talent__id__in=staff_skills_id)
    staff_skill_id = staff_skill.values_list('id', flat=True).distinct()

    # Freelance Staff List
    freelance_staff_list = staff_list.filter(Q(type__type__icontains='freelance'))

    freelance_current_staff = freelance_staff_list.values_list('talent__id', flat=True)

    freelance_staff_id = Profile.objects.filter(talent__id__in=freelance_current_staff).values_list('id', flat=True)

    freelance_staff_skills_id = we_skill.filter(talent__id__in=freelance_current_staff).values_list('talent__id', flat=True)

    freelance_staff_skill = Profile.objects.filter(talent__id__in=freelance_staff_skills_id)
    freelance_staff_skill_id = freelance_staff_skill.values_list('id', flat=True).distinct()

    #Current staff for skill list
    current_staff_skill_l = CorporateStaff.objects.filter(Q(talent__id__in=staff_skill_id) & Q(date_to__isnull=True) & Q(corporate__slug=cor) & Q(department__level_name=dept))

    current_staff_skill_count = current_staff_skill_l.count()
    current_staff_skill = current_staff_skill_l[:10]

    #Past staff for skill list
    past_staff_skill_l = CorporateStaff.objects.filter(Q(talent__id__in=staff_skill_id) & Q(date_to__isnull=False) & Q(corporate__slug=cor) & Q(department__level_name=dept)).order_by('-date_to')
    past_staff_skill_count = past_staff_skill_l.count()
    past_staff_skill = past_staff_skill_l[:10]

    today = timezone.now().date()

    #Full Staff for skill by age bracket
    age=[]
    for i in staff_skill:
        staff_age=relativedelta(today, i.birth_date).years
        age.append(staff_age)

    age_range_18_25 = []
    for i in age:
        if i in range(18, 25):
            staff_age = {'staff_age': i}
            age_range_18_25.append(staff_age)

    age_range_26_35 = []
    for i in age:
        if i in range(26, 35):
            staff_age = {'staff_age': i}
            age_range_26_35.append(staff_age)

    age_range_36_45 = []
    for i in age:
        if i in range(36, 45):
            staff_age = {'staff_age': i}
            age_range_36_45.append(staff_age)

    age_range_46_55 = []
    for i in age:
        if i in range(46, 55):
            staff_age = {'staff_age': i}
            age_range_46_55.append(staff_age)

    age_range_56_65 = []
    for i in age:
        if i in range(56, 65):
            staff_age = {'staff_age': i}
            age_range_56_65.append(staff_age)

    age_range_66_100 = []
    for i in age:
        if i in range(66, 100):
            staff_age = {'staff_age': i}
            age_range_66_100.append(staff_age)

    sum_age_range_18_25 = len(age_range_18_25)
    sum_age_range_26_35 = len(age_range_26_35)
    sum_age_range_36_45 = len(age_range_36_45)
    sum_age_range_46_55 = len(age_range_46_55)
    sum_age_range_56_65 = len(age_range_56_65)
    sum_age_range_66_100 = len(age_range_66_100)

    number_age_brackets_data = [sum_age_range_18_25, sum_age_range_26_35, sum_age_range_36_45, sum_age_range_46_55, sum_age_range_56_65, sum_age_range_66_100]

    #Freelance Staff for skill by age bracket
    freelance_age=[]
    for i in freelance_staff_skill:
        staff_age=relativedelta(today, i.birth_date).years
        freelance_age.append(staff_age)

    freelance_age_range_18_25 = []
    for i in freelance_age:
        if i in range(18, 25):
            staff_age = {'staff_age': i}
            freelance_age_range_18_25.append(staff_age)

    freelance_age_range_26_35 = []
    for i in freelance_age:
        if i in range(26, 35):
            staff_age = {'staff_age': i}
            freelance_age_range_26_35.append(staff_age)

    freelance_age_range_36_45 = []
    for i in freelance_age:
        if i in range(36, 45):
            staff_age = {'staff_age': i}
            freelance_age_range_36_45.append(staff_age)

    freelance_age_range_46_55 = []
    for i in freelance_age:
        if i in range(46, 55):
            staff_age = {'staff_age': i}
            freelance_age_range_46_55.append(staff_age)

    freelance_age_range_56_65 = []
    for i in freelance_age:
        if i in range(56, 65):
            staff_age = {'staff_age': i}
            freelance_age_range_56_65.append(staff_age)

    freelance_age_range_66_100 = []
    for i in freelance_age:
        if i in range(66, 100):
            staff_age = {'staff_age': i}
            freelance_age_range_66_100.append(staff_age)

    freelance_sum_age_range_18_25 = len(freelance_age_range_18_25)
    freelance_sum_age_range_26_35 = len(freelance_age_range_26_35)
    freelance_sum_age_range_36_45 = len(freelance_age_range_36_45)
    freelance_sum_age_range_46_55 = len(freelance_age_range_46_55)
    freelance_sum_age_range_56_65 = len(freelance_age_range_56_65)
    freelance_sum_age_range_66_100 = len(freelance_age_range_66_100)

    freelance_number_age_brackets_data = [freelance_sum_age_range_18_25, freelance_sum_age_range_26_35, freelance_sum_age_range_36_45, freelance_sum_age_range_46_55, freelance_sum_age_range_56_65, freelance_sum_age_range_66_100]

    # Number of staff with skill per age bracket
    skills_age=[]
    for i in staff_skill_id:
        tlt = Profile.objects.get(talent=i)
        staff_age=relativedelta(today, tlt.birth_date).years

        talent_skill_l = we_skill.filter(talent=i, edt=False)
        talent_skillt_l = we_skill.filter(talent=i, edt=True)

        aw_exp = talent_skill_l.filter(talent=i, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        if awetv == None:
            awetv = 0
        else:
            awetv = awetv

        at_exp = talent_skillt_l.filter(talent=i, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        if atetv == None:
            atetv = 0
        else:
            atetv = atetv

        t_exp = awetv + atetv

        result={'staff_age': staff_age, 't_exp': t_exp}

        skills_age.append(result)

    # Total hours experience
    he_list_age_range_18_25=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(18, 25)]
    he_list_age_range_26_35=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(26, 35)]
    he_list_age_range_36_45=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(36, 45)]
    he_list_age_range_46_55=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(46, 55)]
    he_list_age_range_56_65=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(56, 65)]
    he_list_age_range_66_100=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(66, 100)]

    sum_he_range_18_25 = sum(he_list_age_range_18_25)
    sum_he_range_26_35 = sum(he_list_age_range_26_35)
    sum_he_range_36_45 = sum(he_list_age_range_36_45)
    sum_he_range_46_55 = sum(he_list_age_range_46_55)
    sum_he_range_56_65 = sum(he_list_age_range_56_65)
    sum_he_range_66_100 = sum(he_list_age_range_66_100)

    hours_experience_age_brackets_data = [sum_he_range_18_25, sum_he_range_26_35, sum_he_range_36_45, sum_he_range_46_55, sum_he_range_56_65, sum_he_range_66_100]

    # Volume freelance staff experience with skill per age bracket
    freelance_skills_age=[]
    for i in freelance_staff_skill_id:
        tlt = Profile.objects.get(talent=i)
        staff_age=relativedelta(today, tlt.birth_date).years

        talent_skill_l = we_skill.filter(talent=i, edt=False)
        talent_skillt_l = we_skill.filter(talent=i, edt=True)

        aw_exp = talent_skill_l.filter(talent=i, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        if awetv == None:
            awetv = 0
        else:
            awetv = awetv

        at_exp = talent_skillt_l.filter(talent=i, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        if atetv == None:
            atetv = 0
        else:
            atetv = atetv

        t_exp = awetv + atetv

        result={'staff_age': staff_age, 't_exp': t_exp}

        freelance_skills_age.append(result)

    # Total hours experience
    freelance_he_list_age_range_18_25=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(18, 25)]
    freelance_he_list_age_range_26_35=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(26, 35)]
    freelance_he_list_age_range_36_45=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(36, 45)]
    freelance_he_list_age_range_46_55=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(46, 55)]
    freelance_he_list_age_range_56_65=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(56, 65)]
    freelance_he_list_age_range_66_100=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(66, 100)]

    freelance_sum_he_range_18_25 = sum(freelance_he_list_age_range_18_25)
    freelance_sum_he_range_26_35 = sum(freelance_he_list_age_range_26_35)
    freelance_sum_he_range_36_45 = sum(freelance_he_list_age_range_36_45)
    freelance_sum_he_range_46_55 = sum(freelance_he_list_age_range_46_55)
    freelance_sum_he_range_56_65 = sum(freelance_he_list_age_range_56_65)
    freelance_sum_he_range_66_100 = sum(freelance_he_list_age_range_66_100)

    freelance_hours_experience_age_brackets_data = [freelance_sum_he_range_18_25, freelance_sum_he_range_26_35, freelance_sum_he_range_36_45, freelance_sum_he_range_46_55, freelance_sum_he_range_56_65, freelance_sum_he_range_66_100]

    age_bracket_labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '66 & up']

    skills_used_year_range_labels = [10,9,8,7,6,5,4,3,'last year', 'this tear']

    # Work Experience Skill Sum Experience by Year
    we_skills_used_year_range_data = []
    we_skills_age_range=[]
    for i in staff_skill_id:
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

    # Freelance Work Experience Skill Sum Experience by Year
    f_we_skills_used_year_range_data = []
    f_we_skills_age_range=[]
    for i in freelance_staff_skill_id:
        f_we_qs = we_skill.filter(talent=i, edt=False)
        for wet in f_we_qs:
            swewd = wet.date_to
            we_skill_age=relativedelta(today, swewd).years

            aw_exp = wet.hours_worked
            if aw_exp == None:
                awetv = 0
            else:
                awetv = aw_exp

            f_result={'we_skill_age': we_skill_age, 'awetv': awetv}

            f_we_skills_age_range.append(f_result)

    # Total hours experience in year range
    f_we_skill_age_range_0_1=[float(x['awetv']) for x in f_we_skills_age_range if x['we_skill_age'] in range(0, 1)]
    f_we_skill_age_range_1_2=[float(x['awetv']) for x in f_we_skills_age_range if x['we_skill_age'] in range(1, 2)]
    f_we_skill_age_range_2_3=[float(x['awetv']) for x in f_we_skills_age_range if x['we_skill_age'] in range(2, 3)]
    f_we_skill_age_range_3_4=[float(x['awetv']) for x in f_we_skills_age_range if x['we_skill_age'] in range(3, 4)]
    f_we_skill_age_range_4_5=[float(x['awetv']) for x in f_we_skills_age_range if x['we_skill_age'] in range(4, 5)]
    f_we_skill_age_range_5_6=[float(x['awetv']) for x in f_we_skills_age_range if x['we_skill_age'] in range(5, 6)]
    f_we_skill_age_range_6_7=[float(x['awetv']) for x in f_we_skills_age_range if x['we_skill_age'] in range(6, 7)]
    f_we_skill_age_range_7_8=[float(x['awetv']) for x in f_we_skills_age_range if x['we_skill_age'] in range(7, 8)]
    f_we_skill_age_range_8_9=[float(x['awetv']) for x in f_we_skills_age_range if x['we_skill_age'] in range(8, 9)]
    f_we_skill_age_range_9_10=[float(x['awetv']) for x in f_we_skills_age_range if x['we_skill_age'] in range(9, 10)]

    total_f_we_skill_age=[float(x['awetv']) for x in f_we_skills_age_range if x['we_skill_age'] in range(0, 100)]
    total_sum_f_we = sum(total_f_we_skill_age)

    sum_f_we_range_0_1 = sum(f_we_skill_age_range_0_1)
    sum_f_we_range_1_2 = sum(f_we_skill_age_range_1_2)
    sum_f_we_range_2_3 = sum(f_we_skill_age_range_2_3)
    sum_f_we_range_3_4 = sum(f_we_skill_age_range_3_4)
    sum_f_we_range_4_5 = sum(f_we_skill_age_range_4_5)
    sum_f_we_range_5_6 = sum(f_we_skill_age_range_5_6)
    sum_f_we_range_6_7 = sum(f_we_skill_age_range_6_7)
    sum_f_we_range_7_8 = sum(f_we_skill_age_range_7_8)
    sum_f_we_range_8_9 = sum(f_we_skill_age_range_8_9)
    sum_f_we_range_9_10 = sum(f_we_skill_age_range_9_10)

    f_we_skills_used_year_range_data.append(sum_f_we_range_9_10)
    f_we_skills_used_year_range_data.append(sum_f_we_range_8_9)
    f_we_skills_used_year_range_data.append(sum_f_we_range_7_8)
    f_we_skills_used_year_range_data.append(sum_f_we_range_6_7)
    f_we_skills_used_year_range_data.append(sum_f_we_range_5_6)
    f_we_skills_used_year_range_data.append(sum_f_we_range_4_5)
    f_we_skills_used_year_range_data.append(sum_f_we_range_3_4)
    f_we_skills_used_year_range_data.append(sum_f_we_range_2_3)
    f_we_skills_used_year_range_data.append(sum_f_we_range_1_2)
    f_we_skills_used_year_range_data.append(sum_f_we_range_0_1)

    # Training Experience Skill Sum Experience by Year
    t_we_skills_used_year_range_data = []
    t_we_skills_age_range=[]
    for i in staff_skill_id:
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

    # Freelance Training Work Experience Skill Sum Experience by Year
    ft_we_skills_used_year_range_data = []
    ft_we_skills_age_range=[]
    for i in freelance_staff_skill_id:
        ft_we_qs = we_skill.filter(talent=i, edt=True)
        for wet in ft_we_qs:
            swewd = wet.date_to
            we_skill_age=relativedelta(today, swewd).years

            aw_exp = wet.topic.hours
            if aw_exp == None:
                awetv = 0
            else:
                awetv = aw_exp

            ft_result={'we_skill_age': we_skill_age, 'awetv': awetv}

            ft_we_skills_age_range.append(ft_result)

    # Total hours experience in year range
    ft_we_skill_age_range_0_1=[float(x['awetv']) for x in ft_we_skills_age_range if x['we_skill_age'] in range(0, 1)]
    ft_we_skill_age_range_1_2=[float(x['awetv']) for x in ft_we_skills_age_range if x['we_skill_age'] in range(1, 2)]
    ft_we_skill_age_range_2_3=[float(x['awetv']) for x in ft_we_skills_age_range if x['we_skill_age'] in range(2, 3)]
    ft_we_skill_age_range_3_4=[float(x['awetv']) for x in ft_we_skills_age_range if x['we_skill_age'] in range(3, 4)]
    ft_we_skill_age_range_4_5=[float(x['awetv']) for x in ft_we_skills_age_range if x['we_skill_age'] in range(4, 5)]
    ft_we_skill_age_range_5_6=[float(x['awetv']) for x in ft_we_skills_age_range if x['we_skill_age'] in range(5, 6)]
    ft_we_skill_age_range_6_7=[float(x['awetv']) for x in ft_we_skills_age_range if x['we_skill_age'] in range(6, 7)]
    ft_we_skill_age_range_7_8=[float(x['awetv']) for x in ft_we_skills_age_range if x['we_skill_age'] in range(7, 8)]
    ft_we_skill_age_range_8_9=[float(x['awetv']) for x in ft_we_skills_age_range if x['we_skill_age'] in range(8, 9)]
    ft_we_skill_age_range_9_10=[float(x['awetv']) for x in ft_we_skills_age_range if x['we_skill_age'] in range(9, 10)]

    total_ft_we_skill_age=[float(x['awetv']) for x in ft_we_skills_age_range if x['we_skill_age'] in range(0, 100)]
    total_sum_ft_we = sum(total_ft_we_skill_age)

    sum_ft_we_range_0_1 = sum(ft_we_skill_age_range_0_1)
    sum_ft_we_range_1_2 = sum(ft_we_skill_age_range_1_2)
    sum_ft_we_range_2_3 = sum(ft_we_skill_age_range_2_3)
    sum_ft_we_range_3_4 = sum(ft_we_skill_age_range_3_4)
    sum_ft_we_range_4_5 = sum(ft_we_skill_age_range_4_5)
    sum_ft_we_range_5_6 = sum(ft_we_skill_age_range_5_6)
    sum_ft_we_range_6_7 = sum(ft_we_skill_age_range_6_7)
    sum_ft_we_range_7_8 = sum(ft_we_skill_age_range_7_8)
    sum_ft_we_range_8_9 = sum(ft_we_skill_age_range_8_9)
    sum_ft_we_range_9_10 = sum(ft_we_skill_age_range_9_10)

    ft_we_skills_used_year_range_data.append(sum_ft_we_range_9_10)
    ft_we_skills_used_year_range_data.append(sum_ft_we_range_8_9)
    ft_we_skills_used_year_range_data.append(sum_ft_we_range_7_8)
    ft_we_skills_used_year_range_data.append(sum_ft_we_range_6_7)
    ft_we_skills_used_year_range_data.append(sum_ft_we_range_5_6)
    ft_we_skills_used_year_range_data.append(sum_ft_we_range_4_5)
    ft_we_skills_used_year_range_data.append(sum_ft_we_range_3_4)
    ft_we_skills_used_year_range_data.append(sum_ft_we_range_2_3)
    ft_we_skills_used_year_range_data.append(sum_ft_we_range_1_2)
    ft_we_skills_used_year_range_data.append(sum_ft_we_range_0_1)

    experience_lost_labels = [6, 5, 4, 3, 'last year', 'this year']

    hours_experience_lost_month_labels = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 'last month', 'This month']

    # Volume skill lost by Year Range
    past_staff_list = CorporateStaff.objects.filter(Q(corporate__slug=cor) & Q(department__level_name=dept) & Q(date_to__isnull=False))

    past_staff_id = past_staff_list.values_list('talent__id', flat=True)

    skills_lost_age=[]
    for i in past_staff_id:
        tlt = CorporateStaff.objects.filter(talent__id=i).order_by('-date_to')[:0]
        staff_resigned_age = relativedelta(today, tlt.date_to).years
        staff_resigned_months = relativedelta(today, tlt.date_to).months

        talent_skill_l = we_skill.filter(talent=i, edt=False)
        talent_skillt_l = we_skill.filter(talent=i, edt=True)

        aw_exp = talent_skill_l.filter(talent=i, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        if awetv == None:
            awetv = 0
        else:
            awetv = awetv

        at_exp = talent_skillt_l.filter(talent=i, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        if atetv == None:
            atetv = 0
        else:
            atetv = atetv

        t_exp = awetv + atetv

        result={'staff_resigned_age': staff_resigned_age, 'staff_resigned_months': staff_resigned_months, 't_exp': t_exp}

        skills_lost_age.append(result)

    # Total hours experience by year past
    he_list_year_range_0_1=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_age'] in range(0, 1)]
    he_list_year_range_1_2=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_age'] in range(1, 2)]
    he_list_year_range_2_3=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_age'] in range(2, 3)]
    he_list_year_range_3_4=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_age'] in range(3, 4)]
    he_list_year_range_4_5=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_age'] in range(4, 5)]
    he_list_year_range_5_6=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_age'] in range(5, 6)]

    sum_he_range_0_1 = sum(he_list_year_range_0_1)
    sum_he_range_1_2 = sum(he_list_year_range_1_2)
    sum_he_range_2_3 = sum(he_list_year_range_2_3)
    sum_he_range_3_4 = sum(he_list_year_range_3_4)
    sum_he_range_4_5 = sum(he_list_year_range_4_5)
    sum_he_range_5_6 = sum(he_list_year_range_5_6)

    hours_experience_lost_year_brackets_data = [sum_he_range_5_6, sum_he_range_4_5, sum_he_range_3_4, sum_he_range_2_3, sum_he_range_1_2, sum_he_range_0_1]

    # Total hours experience by month past year
    he_list_month_range_0_1=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_months'] in range(0, 1)]
    he_list_month_range_1_2=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_months'] in range(1, 2)]
    he_list_month_range_2_3=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_months'] in range(2, 3)]
    he_list_month_range_3_4=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_months'] in range(3, 4)]
    he_list_month_range_4_5=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_months'] in range(4, 5)]
    he_list_month_range_5_6=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_months'] in range(5, 6)]
    he_list_month_range_6_7=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_months'] in range(6, 7)]
    he_list_month_range_7_8=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_months'] in range(7, 8)]
    he_list_month_range_8_9=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_months'] in range(8, 9)]
    he_list_month_range_9_10=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_months'] in range(9, 10)]
    he_list_month_range_10_11=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_months'] in range(10, 11)]
    he_list_month_range_11_12=[float(x['t_exp']) for x in skills_lost_age if x['staff_resigned_months'] in range(11, 12)]

    sum_he_month_range_0_1 = sum(he_list_month_range_0_1)
    sum_he_month_range_1_2 = sum(he_list_month_range_1_2)
    sum_he_month_range_2_3 = sum(he_list_month_range_2_3)
    sum_he_month_range_3_4 = sum(he_list_month_range_3_4)
    sum_he_month_range_4_5 = sum(he_list_month_range_4_5)
    sum_he_month_range_5_6 = sum(he_list_month_range_5_6)
    sum_he_month_range_6_7 = sum(he_list_month_range_6_7)
    sum_he_month_range_7_8 = sum(he_list_month_range_7_8)
    sum_he_month_range_8_9 = sum(he_list_month_range_8_9)
    sum_he_month_range_9_10 = sum(he_list_month_range_9_10)
    sum_he_month_range_10_11 = sum(he_list_month_range_10_11)
    sum_he_month_range_11_12 = sum(he_list_month_range_11_12)

    hours_experience_lost_month_brackets_data = [sum_he_month_range_11_12, sum_he_month_range_10_11, sum_he_month_range_9_10, sum_he_month_range_8_9, sum_he_month_range_7_8, sum_he_month_range_6_7, sum_he_month_range_5_6, sum_he_month_range_4_5, sum_he_month_range_3_4, sum_he_month_range_2_3, sum_he_month_range_1_2, sum_he_month_range_0_1]

    # Volume freelance skill lost by Year Range
    freelance_past_staff_list = CorporateStaff.objects.filter(Q(corporate__slug=cor) & Q(department__level_name=dept) & Q(date_to__isnull=False) & Q(type__type__icontains='freelance'))

    freelance_past_staff_id = freelance_past_staff_list.values_list('talent__id', flat=True)

    freelance_skills_lost_age=[]
    for i in freelance_past_staff_id:
        tlt = CorporateStaff.objects.filter(talent__id=i).order_by('-date_to')[:0]
        staff_resigned_age = relativedelta(today, tlt.date_to).years
        staff_resigned_months = relativedelta(today, tlt.date_to).months

        talent_skill_l = we_skill.filter(talent=i, edt=False)
        talent_skillt_l = we_skill.filter(talent=i, edt=True)

        aw_exp = talent_skill_l.filter(talent=i, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        if awetv == None:
            awetv = 0
        else:
            awetv = awetv

        at_exp = talent_skillt_l.filter(talent=i, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        if atetv == None:
            atetv = 0
        else:
            atetv = atetv

        t_exp = awetv + atetv

        result={'staff_resigned_age': staff_resigned_age, 'staff_resigned_months': staff_resigned_months, 't_exp': t_exp}

        freelance_skills_lost_age.append(result)

    # Total hours experience by year past
    freelance_he_list_year_range_0_1=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_age'] in range(0, 1)]
    freelance_he_list_year_range_1_2=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_age'] in range(1, 2)]
    freelance_he_list_year_range_2_3=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_age'] in range(2, 3)]
    freelance_he_list_year_range_3_4=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_age'] in range(3, 4)]
    freelance_he_list_year_range_4_5=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_age'] in range(4, 5)]
    freelance_he_list_year_range_5_6=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_age'] in range(5, 6)]

    freelance_sum_he_range_0_1 = sum(freelance_he_list_year_range_0_1)
    freelance_sum_he_range_1_2 = sum(freelance_he_list_year_range_1_2)
    freelance_sum_he_range_2_3 = sum(freelance_he_list_year_range_2_3)
    freelance_sum_he_range_3_4 = sum(freelance_he_list_year_range_3_4)
    freelance_sum_he_range_4_5 = sum(freelance_he_list_year_range_4_5)
    freelance_sum_he_range_5_6 = sum(freelance_he_list_year_range_5_6)

    freelance_hours_experience_lost_year_brackets_data = [freelance_sum_he_range_5_6, freelance_sum_he_range_4_5, freelance_sum_he_range_3_4, freelance_sum_he_range_2_3, freelance_sum_he_range_1_2, freelance_sum_he_range_0_1]

    # Total hours freelance experience by month past year
    freelance_he_list_month_range_0_1=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_months'] in range(0, 1)]
    freelance_he_list_month_range_1_2=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_months'] in range(1, 2)]
    freelance_he_list_month_range_2_3=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_months'] in range(2, 3)]
    freelance_he_list_month_range_3_4=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_months'] in range(3, 4)]
    freelance_he_list_month_range_4_5=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_months'] in range(4, 5)]
    freelance_he_list_month_range_5_6=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_months'] in range(5, 6)]
    freelance_he_list_month_range_6_7=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_months'] in range(6, 7)]
    freelance_he_list_month_range_7_8=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_months'] in range(7, 8)]
    freelance_he_list_month_range_8_9=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_months'] in range(8, 9)]
    freelance_he_list_month_range_9_10=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_months'] in range(9, 10)]
    freelance_he_list_month_range_10_11=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_months'] in range(10, 11)]
    freelance_he_list_month_range_11_12=[float(x['t_exp']) for x in freelance_skills_lost_age if x['staff_resigned_months'] in range(11, 12)]

    freelance_sum_he_month_range_0_1 = sum(freelance_he_list_month_range_0_1)
    freelance_sum_he_month_range_1_2 = sum(freelance_he_list_month_range_1_2)
    freelance_sum_he_month_range_2_3 = sum(freelance_he_list_month_range_2_3)
    freelance_sum_he_month_range_3_4 = sum(freelance_he_list_month_range_3_4)
    freelance_sum_he_month_range_4_5 = sum(freelance_he_list_month_range_4_5)
    freelance_sum_he_month_range_5_6 = sum(freelance_he_list_month_range_5_6)
    freelance_sum_he_month_range_6_7 = sum(freelance_he_list_month_range_6_7)
    freelance_sum_he_month_range_7_8 = sum(freelance_he_list_month_range_7_8)
    freelance_sum_he_month_range_8_9 = sum(freelance_he_list_month_range_8_9)
    freelance_sum_he_month_range_9_10 = sum(freelance_he_list_month_range_9_10)
    freelance_sum_he_month_range_10_11 = sum(freelance_he_list_month_range_10_11)
    freelance_sum_he_month_range_11_12 = sum(freelance_he_list_month_range_11_12)

    hours_freelance_experience_lost_month_brackets_data = [freelance_sum_he_month_range_11_12, freelance_sum_he_month_range_10_11, freelance_sum_he_month_range_9_10, freelance_sum_he_month_range_8_9, freelance_sum_he_month_range_7_8, freelance_sum_he_month_range_6_7, freelance_sum_he_month_range_5_6, freelance_sum_he_month_range_4_5, freelance_sum_he_month_range_3_4, freelance_sum_he_month_range_2_3, freelance_sum_he_month_range_1_2, freelance_sum_he_month_range_0_1]

    template = 'mod_corporate/dept_skill_dashboard.html'
    context = {
        'cor': cor,
        'dept': dept,
        'skl': skl,
        'skill': skill,
        'current_staff_skill': current_staff_skill,
        'current_staff_skill_count': current_staff_skill_count,
        'past_staff_skill': past_staff_skill,
        'past_staff_skill_count': past_staff_skill_count,
        'age_bracket_labels': age_bracket_labels,
        'number_age_brackets_data': number_age_brackets_data,
        'freelance_number_age_brackets_data': freelance_number_age_brackets_data,
        'hours_experience_age_brackets_data': hours_experience_age_brackets_data,
        'freelance_hours_experience_age_brackets_data': freelance_hours_experience_age_brackets_data,
        'total_sum_we': total_sum_we,
        'total_sum_f_we': total_sum_f_we,
        'total_sum_t_we': total_sum_t_we,
        'total_sum_ft_we': total_sum_ft_we,
        'skills_age': skills_age,
        'skills_used_year_range_labels': skills_used_year_range_labels,
        'we_skills_used_year_range_data': we_skills_used_year_range_data,
        'f_we_skills_used_year_range_data': f_we_skills_used_year_range_data,
        't_we_skills_used_year_range_data': t_we_skills_used_year_range_data,
        'ft_we_skills_used_year_range_data': ft_we_skills_used_year_range_data,
        'experience_lost_labels': experience_lost_labels,
        'hours_experience_lost_year_brackets_data': hours_experience_lost_year_brackets_data,
        'freelance_hours_experience_lost_year_brackets_data': freelance_hours_experience_lost_year_brackets_data,
        'hours_experience_lost_month_labels': hours_experience_lost_month_labels,
        'hours_experience_lost_month_brackets_data': hours_experience_lost_month_brackets_data,
        'hours_freelance_experience_lost_month_brackets_data': hours_freelance_experience_lost_month_brackets_data,
    }
    return render(request, template, context)


@login_required()
@corp_permission(1)
def dept_skill_current_staff(request, cor, dept, skl):
    skill = SkillTag.objects.get(id=skl)

    staff_list = CorporateStaff.objects.filter(Q(corporate__slug=cor) & Q(department__level_name=dept))

    current_staff = staff_list.values_list('talent__id', flat=True)

    we = WorkExperience.objects.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score))

    we_skill = we.filter(Q(skills__skill=skill.skill, edt=False) | Q(topic__skills__skill=skill.skill, edt=True))

    staff_skills_id = we_skill.filter(talent__id__in=current_staff).values_list('talent__id', flat=True)

    staff_skill = Profile.objects.filter(talent__id__in=staff_skills_id)
    staff_skill_id = staff_skill.values_list('id', flat=True).distinct()

    #Current staff for skill list
    current_staff_skill_l = CorporateStaff.objects.filter(Q(talent__id__in=staff_skill_id) & Q(date_to__isnull=True) & Q(corporate__slug=cor) & Q(department__level_name=dept))
    current_staff_count = current_staff_skill_l.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(current_staff_skill_l, 20)

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

    template = 'mod_corporate/dept_skill_current_staff.html'
    context = {
        'cor': cor,
        'dept': dept,
        'skl': skl,
        'skill': skill,
        'current_staff_count': current_staff_count,
        'pageitems': pageitems,
        'page_range': page_range,
    }
    return render(request, template, context)


@login_required()
@corp_permission(1)
def dept_skill_past_staff(request, cor, dept, skl):
    skill = SkillTag.objects.get(id=skl)

    staff_list = CorporateStaff.objects.filter(Q(corporate__slug=cor) & Q(department__level_name=dept))

    current_staff = staff_list.values_list('talent__id', flat=True)

    we = WorkExperience.objects.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score))

    we_skill = we.filter(Q(skills__skill=skill.skill, edt=False) | Q(topic__skills__skill=skill.skill, edt=True))

    staff_skills_id = we_skill.filter(talent__id__in=current_staff).values_list('talent__id', flat=True)

    staff_skill = Profile.objects.filter(talent__id__in=staff_skills_id)
    staff_skill_id = staff_skill.values_list('id', flat=True).distinct()

    #Past staff for skill list
    past_staff_skill_l = CorporateStaff.objects.filter(Q(talent__id__in=staff_skill_id) & Q(date_to__isnull=False) & Q(corporate__slug=cor) & Q(department__level_name=dept)).order_by('-date_to')
    past_staff_count = past_staff_skill_l.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(current_staff_skill_l, 20)

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

    template = 'mod_corporate/dept_skill_past_staff.html'
    context = {
        'cor': cor,
        'dept': dept,
        'skl': skl,
        'skill': skill,
        'past_staff_count': past_staff_count,
        'pageitems': pageitems,
        'page_range': page_range,
    }
    return render(request, template, context)


@login_required()
@corp_permission(1)
def dept_skills_current(request, cor, dept):

    template = 'mod_corporate/dept_skills_current.html'
    context = {}
    return render(request, template, context)


@login_required()
@corp_permission(1)
def dept_skills_resigned(request, cor, dept):

    template = 'mod_corporate/dept_skills_resigned.html'
    context = {}
    return render(request, template, context)


@login_required()
@corp_permission(1)
def dept_skills_freelance(request, cor, dept):

    structure = OrgStructure.objects.filter(Q(corporate__slug=cor) & Q(level_name=dept))

    full_staff_list = CorporateStaff.objects.filter(Q(corporate__slug=cor) & Q(department__level_name=dept))

    staff_list = full_staff_list.filter(Q(date_to__isnull=True))

    freelance_staff_list = staff_list.filter(Q(type__type__icontains='freelance'))

    freelance_current_staff = freelance_staff_list.values_list('talent__id', flat=True)
    freelance_current_count = freelance_current_staff.count()

    freelance_staff = Profile.objects.filter(talent__id__in=freelance_current_staff)
    today = timezone.now().date()

    freelance_age=[]
    for i in freelance_staff:
        freelance_staff_age=relativedelta(today, i.birth_date).years
        freelance_age.append(freelance_staff_age)

    freelance_age_range_18_25 = []
    for i in freelance_age:
        if i in range(18, 25):
            freelance_staff_age = {'staff_age': i}
            freelance_age_range_18_25.append(freelance_staff_age)

    freelance_age_range_26_35 = []
    for i in freelance_age:
        if i in range(26, 35):
            freelance_staff_age = {'staff_age': i}
            freelance_age_range_26_35.append(freelance_staff_age)

    freelance_age_range_36_45 = []
    for i in freelance_age:
        if i in range(36, 45):
            freelance_staff_age = {'staff_age': i}
            freelance_age_range_36_45.append(freelance_staff_age)

    freelance_age_range_46_55 = []
    for i in freelance_age:
        if i in range(46, 55):
            freelance_staff_age = {'staff_age': i}
            freelance_age_range_46_55.append(freelance_staff_age)

    freelance_age_range_56_65 = []
    for i in freelance_age:
        if i in range(56, 65):
            freelance_staff_age = {'staff_age': i}
            freelance_age_range_56_65.append(freelance_staff_age)

    freelance_age_range_66_100 = []
    for i in freelance_age:
        if i in range(66, 100):
            freelance_staff_age = {'staff_age': i}
            freelance_age_range_66_100.append(freelance_staff_age)

    freelance_sum_age_range_18_25 = len(freelance_age_range_18_25)
    freelance_sum_age_range_26_35 = len(freelance_age_range_26_35)
    freelance_sum_age_range_36_45 = len(freelance_age_range_36_45)
    freelance_sum_age_range_46_55 = len(freelance_age_range_46_55)
    freelance_sum_age_range_56_65 = len(freelance_age_range_56_65)
    freelance_sum_age_range_66_100 = len(freelance_age_range_66_100)

    freelance_number_age_brackets_data = [freelance_sum_age_range_18_25, freelance_sum_age_range_26_35, freelance_sum_age_range_36_45, freelance_sum_age_range_46_55, freelance_sum_age_range_56_65, freelance_sum_age_range_66_100]

    age_bracket_labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '66 & up']

    freelance_staff_id = Profile.objects.filter(talent__id__in=freelance_current_staff).values_list('id', flat=True)

    we = WorkExperience.objects.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score))

    # Total Number of freelance skills per age bracket
    freelance_skills_age=[]
    for i in freelance_staff_id:
        tlt = Profile.objects.get(talent=i)
        staff_age=relativedelta(today, tlt.birth_date).years

        talent_skill_l = we.filter(talent=i, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=i, edt=True).values_list('topic__skills__skill', flat=True)

        aw_exp = we.filter(talent=i, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        if awetv == None:
            awetv = 0
        else:
            awetv = awetv

        at_exp = we.filter(talent=i, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        if atetv == None:
            atetv = 0
        else:
            atetv = atetv

        t_exp = awetv + atetv

        atalent_skill = list(talent_skill_l)
        atalent_skillt = list(talent_skillt_l)
        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        result={'staff_age': staff_age, 'askillset': askillset, 'awetv': awetv, 'awetv': awetv, 't_exp': t_exp}

        freelance_skills_age.append(result)

    freelance_skills_list_age_range_18_25=[list(x['askillset']) for x in freelance_skills_age if x['staff_age'] in range(18, 25)]
    freelance_skills_list_age_range_26_35=[list(x['askillset']) for x in freelance_skills_age if x['staff_age'] in range(26, 35)]
    freelance_skills_list_age_range_36_45=[list(x['askillset']) for x in freelance_skills_age if x['staff_age'] in range(36, 45)]
    freelance_skills_list_age_range_46_55=[list(x['askillset']) for x in freelance_skills_age if x['staff_age'] in range(46, 55)]
    freelance_skills_list_age_range_56_65=[list(x['askillset']) for x in freelance_skills_age if x['staff_age'] in range(56, 65)]
    freelance_skills_list_age_range_66_100=[list(x['askillset']) for x in freelance_skills_age if x['staff_age'] in range(66, 100)]

    freelance_global_skills_list_age_range_18_25 =[]
    for sublist in freelance_skills_list_age_range_18_25:
        for item in sublist:
            freelance_global_skills_list_age_range_18_25.append(item)

    freelance_global_skills_list_age_range_26_35 =[]
    for sublist in freelance_skills_list_age_range_26_35:
        for item in sublist:
            freelance_global_skills_list_age_range_26_35.append(item)

    freelance_global_skills_list_age_range_36_45 =[]
    for sublist in freelance_skills_list_age_range_36_45:
        for item in sublist:
            freelance_global_skills_list_age_range_36_45.append(item)

    freelance_global_skills_list_age_range_46_55 =[]
    for sublist in freelance_skills_list_age_range_46_55:
        for item in sublist:
            freelance_global_skills_list_age_range_46_55.append(item)

    freelance_global_skills_list_age_range_56_65 =[]
    for sublist in freelance_skills_list_age_range_56_65:
        for item in sublist:
            freelance_global_skills_list_age_range_56_65.append(item)

    freelance_global_skills_list_age_range_66_100 =[]
    for sublist in freelance_skills_list_age_range_66_100:
        for item in sublist:
            freelance_global_skills_list_age_range_66_100.append(item)

    freelance_skills_list_age_range_18_25 = set(freelance_global_skills_list_age_range_18_25)
    freelance_skills_list_age_range_26_35 = set(freelance_global_skills_list_age_range_26_35)
    freelance_skills_list_age_range_36_45 = set(freelance_global_skills_list_age_range_36_45)
    freelance_skills_list_age_range_46_55 = set(freelance_global_skills_list_age_range_46_55)
    freelance_skills_list_age_range_56_65 = set(freelance_global_skills_list_age_range_56_65)
    freelance_skills_list_age_range_66_100 = set(freelance_global_skills_list_age_range_66_100)

    freelance_sum_skills_range_18_25 = len(freelance_skills_list_age_range_18_25)
    freelance_sum_skills_range_26_35 = len(freelance_skills_list_age_range_26_35)
    freelance_sum_skills_range_36_45 = len(freelance_skills_list_age_range_36_45)
    freelance_sum_skills_range_46_55 = len(freelance_skills_list_age_range_46_55)
    freelance_sum_skills_range_56_65 = len(freelance_skills_list_age_range_56_65)
    freelance_sum_skills_range_66_100 = len(freelance_skills_list_age_range_66_100)

    freelance_number_skills_age_brackets_data = [freelance_sum_skills_range_18_25, freelance_sum_skills_range_26_35, freelance_sum_skills_range_36_45, freelance_sum_skills_range_46_55, freelance_sum_skills_range_56_65, freelance_sum_skills_range_66_100]
    # end number freelance skills per age Bracket

    # Total hours freelance experience
    freelance_he_list_age_range_18_25=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(18, 25)]
    freelance_he_list_age_range_26_35=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(26, 35)]
    freelance_he_list_age_range_36_45=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(36, 45)]
    freelance_he_list_age_range_46_55=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(46, 55)]
    freelance_he_list_age_range_56_65=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(56, 65)]
    freelance_he_list_age_range_66_100=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(66, 100)]

    freelance_sum_he_range_18_25 = sum(freelance_he_list_age_range_18_25)
    freelance_sum_he_range_26_35 = sum(freelance_he_list_age_range_26_35)
    freelance_sum_he_range_36_45 = sum(freelance_he_list_age_range_36_45)
    freelance_sum_he_range_46_55 = sum(freelance_he_list_age_range_46_55)
    freelance_sum_he_range_56_65 = sum(freelance_he_list_age_range_56_65)
    freelance_sum_he_range_66_100 = sum(freelance_he_list_age_range_66_100)

    freelance_hours_experience_age_brackets_data = [freelance_sum_he_range_18_25, freelance_sum_he_range_26_35, freelance_sum_he_range_36_45, freelance_sum_he_range_46_55, freelance_sum_he_range_56_65, freelance_sum_he_range_66_100]

    # List of skills for buttons
    skills_list = [list(x['askillset']) for x in freelance_skills_age]

    global_skills_list =[]
    for sublist in skills_list:
        for item in sublist:
            global_skills_list.append(item)

    skills_list_set_set = set(global_skills_list)

    skills_list_set = sorted(skills_list_set_set, reverse=False)

    skills_list_labels = list(skills_list_set)

    dept_skills_link = SkillTag.objects.filter(skill__in=skills_list_set).order_by('skill')

    sum_skills = len(skills_list_set)

    #Hours Freelance Experience per skill chart
    freelance_skills_hours_skill_data = []
    for s in skills_list_set:
        shwe = we.filter(Q(skills__skill=s, edt=False) | Q(topic__skills__skill=s, edt=True))
        freelance_skills_hours=[]
        for i in freelance_staff_id:
            tlt = Profile.objects.get(talent=i)

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

            freelance_skills_hours.append(result)

        freelance_skills_list=[float(x['t_exp']) for x in freelance_skills_hours]
        sum_fshwe = sum(freelance_skills_list)

        freelance_skills_hours_skill_data.append(sum_fshwe)

    #Current Freelance staff
    current_freelance_staff_l =     staff_list.filter(Q(type__type__icontains='freelance')).order_by('-date_to')
    current_freelance_staff_count = current_freelance_staff_l.count()
    current_freelance_staff = current_freelance_staff_l[:10]

    #Past staff for skill list
    past_freelance_staff_l = full_staff_list.filter(Q(date_to__isnull=False) & Q(type__type__icontains='freelance')).order_by('-date_to')
    past_freelance_staff_count = past_freelance_staff_l.count()
    past_freelance_staff = past_freelance_staff_l[:10]


    template = 'mod_corporate/dept_skills_freelance.html'
    context = {
            'cor': cor,
            'dept': dept,
            'dept_skills_link': dept_skills_link,
            'freelance_number_age_brackets_data': freelance_number_age_brackets_data,
            'age_bracket_labels': age_bracket_labels,
            'freelance_number_skills_age_brackets_data': freelance_number_skills_age_brackets_data,
            'freelance_hours_experience_age_brackets_data': freelance_hours_experience_age_brackets_data,
            'skills_list_set': skills_list_set,
            'skills_list_labels': skills_list_labels,
            'freelance_skills_hours_skill_data': freelance_skills_hours_skill_data,
            'sum_skills': sum_skills,
            'current_freelance_staff': current_freelance_staff,
            'current_freelance_staff_count': current_freelance_staff_count,
            'past_freelance_staff': past_freelance_staff,
            'past_freelance_staff_count': past_freelance_staff_count,
    }
    return render(request, template, context)


@login_required()
@corp_permission(1)
def dept_freelance_current_staff(request, cor, dept):

    full_staff_list = CorporateStaff.objects.filter(Q(corporate__slug=cor) & Q(department__level_name=dept))

    staff_list = full_staff_list.filter(Q(date_to__isnull=True))

    #Current Freelance staff
    current_freelance_staff_l =     staff_list.filter(Q(type__type__icontains='freelance')).order_by('-date_to')
    current_freelance_staff_count = current_freelance_staff_l.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(current_freelance_staff_l, 20)

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

    template = 'mod_corporate/dept_freelance_current_staff.html'
    context = {
            'cor': cor,
            'dept': dept,
            'pageitems': pageitems,
            'page_range': page_range,
    }
    return render(request, template, context)


@login_required()
@corp_permission(1)
def dept_freelance_past_staff(request, cor, dept):

    full_staff_list = CorporateStaff.objects.filter(Q(corporate__slug=cor) & Q(department__level_name=dept))

    #Past staff for skill list
    past_freelance_staff_l = full_staff_list.filter(Q(date_to__isnull=False) & Q(type__type__icontains='freelance')).order_by('-date_to')
    past_freelance_staff_count = past_freelance_staff_l.count()

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(past_freelance_staff_l, 20)

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

    template = 'mod_corporate/dept_freelance_past_staff.html'
    context = {
            'cor': cor,
            'dept': dept,
            'pageitems': pageitems,
            'page_range': page_range,
    }
    return render(request, template, context)


@login_required()
@corp_permission(1)
def dept_skills_not_utilised(request, cor, dept):
    webr = CorporateHR.objects.get(slug=cor)
    webrb = webr.companybranch

    staff_list = CorporateStaff.objects.filter(Q(corporate__slug=cor) & Q(department__level_name=dept) & Q(date_to__isnull=True))

    current_staff = staff_list.values_list('talent__id', flat=True)

    today = timezone.now().date()

    freelance_staff_list = staff_list.filter(Q(type__type__icontains='freelance'))

    freelance_current_staff = freelance_staff_list.values_list('talent__id', flat=True)

    staff_id = Profile.objects.filter(talent__id__in=current_staff).values_list('id', flat=True)

    freelance_staff_id = Profile.objects.filter(talent__id__in=freelance_current_staff).values_list('id', flat=True)

    we = WorkExperience.objects.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score))

    # Total list of skills for company
    skills=[]
    for i in staff_id:
        talent_skill_l = we.filter(talent=i, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=i, edt=True).values_list('topic__skills__skill', flat=True)

        atalent_skill = list(talent_skill_l)
        atalent_skillt = list(talent_skillt_l)
        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)

        result={'askillset': askillset}

        skills.append(result)

    # Total List of skills
    total_skills_list = [list(x['askillset']) for x in skills]

    total_global_skills_list =[]
    for sublist in total_skills_list:
        for item in sublist:
            total_global_skills_list.append(item)

    total_skills_list_set_set = set(total_global_skills_list)


    # List of Skills not used in Company
    wenc = WorkExperience.objects.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score) & Q(companybranch=webrb))

    cor_skills=[]
    for i in staff_id:
        talent_skill_l = wenc.filter(talent=i, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = wenc.filter(talent=i, edt=True).values_list('topic__skills__skill', flat=True)

        atalent_skill = list(talent_skill_l)
        atalent_skillt = list(talent_skillt_l)
        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)

        result={'askillset': askillset}

        cor_skills.append(result)

    # Total not utilised List of skills for buttons
    cor_skills_list = [list(x['askillset']) for x in cor_skills]

    cor_global_skills_list =[]
    for sublist in cor_skills_list:
        for item in sublist:
            cor_global_skills_list.append(item)

    cor_skills_list_set_set = set(cor_global_skills_list)

    nu_skills = total_skills_list_set_set - cor_skills_list_set_set

    skills_list_set = sorted(nu_skills, reverse=False)

    skills_list_labels = list(skills_list_set)

    dept_skills_link = SkillTag.objects.filter(skill__in=skills_list_set).order_by('skill')

    #Hours Experience per skill chart
    skills_hours_skill_data = []
    for s in skills_list_set:
        shwe = we.filter(Q(skills__skill=s, edt=False) | Q(topic__skills__skill=s, edt=True))
        skills_hours=[]
        for i in staff_id:
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

    #Hours Freelance Experience per skill chart
    freelance_skills_hours_skill_data = []
    for s in skills_list_set:
        shwe = we.filter(Q(skills__skill=s, edt=False) | Q(topic__skills__skill=s, edt=True))
        freelance_skills_hours=[]
        for i in freelance_staff_id:
            tlt = Profile.objects.get(talent=i)

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

            freelance_skills_hours.append(result)

        freelance_skills_list=[float(x['t_exp']) for x in freelance_skills_hours]
        sum_fshwe = sum(freelance_skills_list)

        freelance_skills_hours_skill_data.append(sum_fshwe)

    tsul = we.filter(Q(skills__skill__in=skills_list_set, edt=False) | Q(topic__skills__skill__in=skills_list_set, edt=True)).values_list('talent')

    tsus = set(tsul)

#    stus = Profile.objects.filter(talent__id__in=tsus)
#    print(stus)
    template = 'mod_corporate/dept_skills_not_utilised.html'
    context = {
            'cor': cor,
            'dept': dept,
            'dept_skills_link': dept_skills_link,
            'skills_list_set': skills_list_set,
            'skills_list_labels': skills_list_labels,
            'skills_hours_skill_data': skills_hours_skill_data,
            'freelance_skills_hours_skill_data': freelance_skills_hours_skill_data,
    }
    return render(request, template, context)


@login_required()
@corp_permission(1)
def org_department_dashboard(request, cor, dept):
    structure = OrgStructure.objects.filter(Q(corporate__slug=cor) & Q(level_name=dept))

    staff_list = CorporateStaff.objects.filter(Q(corporate__slug=cor) & Q(department__level_name=dept) & Q(date_to__isnull=True))

    freelance_staff_list = staff_list.filter(Q(type__type__icontains='freelance'))

    current_staff = staff_list.values_list('talent__id', flat=True)
    current_count = current_staff.count()

    freelance_current_staff = freelance_staff_list.values_list('talent__id', flat=True)
    freelance_current_count = freelance_current_staff.count()

    staff = Profile.objects.filter(talent__id__in=current_staff)
    freelance_staff = Profile.objects.filter(talent__id__in=freelance_current_staff)
    today = timezone.now().date()

    age=[]
    for i in staff:
        staff_age=relativedelta(today, i.birth_date).years
        age.append(staff_age)

    age_range_18_25 = []
    for i in age:
        if i in range(18, 25):
            staff_age = {'staff_age': i}
            age_range_18_25.append(staff_age)

    age_range_26_35 = []
    for i in age:
        if i in range(26, 35):
            staff_age = {'staff_age': i}
            age_range_26_35.append(staff_age)

    age_range_36_45 = []
    for i in age:
        if i in range(36, 45):
            staff_age = {'staff_age': i}
            age_range_36_45.append(staff_age)

    age_range_46_55 = []
    for i in age:
        if i in range(46, 55):
            staff_age = {'staff_age': i}
            age_range_46_55.append(staff_age)

    age_range_56_65 = []
    for i in age:
        if i in range(56, 65):
            staff_age = {'staff_age': i}
            age_range_56_65.append(staff_age)

    age_range_66_100 = []
    for i in age:
        if i in range(66, 100):
            staff_age = {'staff_age': i}
            age_range_66_100.append(staff_age)

    sum_age_range_18_25 = len(age_range_18_25)
    sum_age_range_26_35 = len(age_range_26_35)
    sum_age_range_36_45 = len(age_range_36_45)
    sum_age_range_46_55 = len(age_range_46_55)
    sum_age_range_56_65 = len(age_range_56_65)
    sum_age_range_66_100 = len(age_range_66_100)

    number_age_brackets_data = [sum_age_range_18_25, sum_age_range_26_35, sum_age_range_36_45, sum_age_range_46_55, sum_age_range_56_65, sum_age_range_66_100]

    freelance_age=[]
    for i in freelance_staff:
        freelance_staff_age=relativedelta(today, i.birth_date).years
        freelance_age.append(freelance_staff_age)

    freelance_age_range_18_25 = []
    for i in freelance_age:
        if i in range(18, 25):
            freelance_staff_age = {'staff_age': i}
            freelance_age_range_18_25.append(freelance_staff_age)

    freelance_age_range_26_35 = []
    for i in freelance_age:
        if i in range(26, 35):
            freelance_staff_age = {'staff_age': i}
            freelance_age_range_26_35.append(freelance_staff_age)

    freelance_age_range_36_45 = []
    for i in freelance_age:
        if i in range(36, 45):
            freelance_staff_age = {'staff_age': i}
            freelance_age_range_36_45.append(freelance_staff_age)

    freelance_age_range_46_55 = []
    for i in freelance_age:
        if i in range(46, 55):
            freelance_staff_age = {'staff_age': i}
            freelance_age_range_46_55.append(freelance_staff_age)

    freelance_age_range_56_65 = []
    for i in freelance_age:
        if i in range(56, 65):
            freelance_staff_age = {'staff_age': i}
            freelance_age_range_56_65.append(freelance_staff_age)

    freelance_age_range_66_100 = []
    for i in freelance_age:
        if i in range(66, 100):
            freelance_staff_age = {'staff_age': i}
            freelance_age_range_66_100.append(freelance_staff_age)

    freelance_sum_age_range_18_25 = len(freelance_age_range_18_25)
    freelance_sum_age_range_26_35 = len(freelance_age_range_26_35)
    freelance_sum_age_range_36_45 = len(freelance_age_range_36_45)
    freelance_sum_age_range_46_55 = len(freelance_age_range_46_55)
    freelance_sum_age_range_56_65 = len(freelance_age_range_56_65)
    freelance_sum_age_range_66_100 = len(freelance_age_range_66_100)

    freelance_number_age_brackets_data = [freelance_sum_age_range_18_25, freelance_sum_age_range_26_35, freelance_sum_age_range_36_45, freelance_sum_age_range_46_55, freelance_sum_age_range_56_65, freelance_sum_age_range_66_100]

    age_bracket_labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '66 & up']

    staff_id = Profile.objects.filter(talent__id__in=current_staff).values_list('id', flat=True)

    freelance_staff_id = Profile.objects.filter(talent__id__in=freelance_current_staff).values_list('id', flat=True)

    we = WorkExperience.objects.filter(Q(talent__subscription__gte=1) & Q(score__gte=skill_pass_score))

    # Total Number of skills per age bracket
    skills_age=[]
    for i in staff_id:
        tlt = Profile.objects.get(talent=i)
        staff_age=relativedelta(today, tlt.birth_date).years

        talent_skill_l = we.filter(talent=i, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=i, edt=True).values_list('topic__skills__skill', flat=True)

        aw_exp = we.filter(talent=i, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        if awetv == None:
            awetv = 0
        else:
            awetv = awetv

        at_exp = we.filter(talent=i, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        if atetv == None:
            atetv = 0
        else:
            atetv = atetv

        t_exp = awetv + atetv

        atalent_skill = list(talent_skill_l)
        atalent_skillt = list(talent_skillt_l)
        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        result={'staff_age': staff_age, 'askillset': askillset, 'awetv': awetv, 'awetv': awetv, 't_exp': t_exp}

        skills_age.append(result)

    skills_list_age_range_18_25=[list(x['askillset']) for x in skills_age if x['staff_age'] in range(18, 25)]
    skills_list_age_range_26_35=[list(x['askillset']) for x in skills_age if x['staff_age'] in range(26, 35)]
    skills_list_age_range_36_45=[list(x['askillset']) for x in skills_age if x['staff_age'] in range(36, 45)]
    skills_list_age_range_46_55=[list(x['askillset']) for x in skills_age if x['staff_age'] in range(46, 55)]
    skills_list_age_range_56_65=[list(x['askillset']) for x in skills_age if x['staff_age'] in range(56, 65)]
    skills_list_age_range_66_100=[list(x['askillset']) for x in skills_age if x['staff_age'] in range(66, 100)]

    global_skills_list_age_range_18_25 =[]
    for sublist in skills_list_age_range_18_25:
        for item in sublist:
            global_skills_list_age_range_18_25.append(item)

    global_skills_list_age_range_26_35 =[]
    for sublist in skills_list_age_range_26_35:
        for item in sublist:
            global_skills_list_age_range_26_35.append(item)

    global_skills_list_age_range_36_45 =[]
    for sublist in skills_list_age_range_36_45:
        for item in sublist:
            global_skills_list_age_range_36_45.append(item)

    global_skills_list_age_range_46_55 =[]
    for sublist in skills_list_age_range_46_55:
        for item in sublist:
            global_skills_list_age_range_46_55.append(item)

    global_skills_list_age_range_56_65 =[]
    for sublist in skills_list_age_range_56_65:
        for item in sublist:
            global_skills_list_age_range_56_65.append(item)

    global_skills_list_age_range_66_100 =[]
    for sublist in skills_list_age_range_66_100:
        for item in sublist:
            global_skills_list_age_range_66_100.append(item)

    skills_list_age_range_18_25 = set(global_skills_list_age_range_18_25)
    skills_list_age_range_26_35 = set(global_skills_list_age_range_26_35)
    skills_list_age_range_36_45 = set(global_skills_list_age_range_36_45)
    skills_list_age_range_46_55 = set(global_skills_list_age_range_46_55)
    skills_list_age_range_56_65 = set(global_skills_list_age_range_56_65)
    skills_list_age_range_66_100 = set(global_skills_list_age_range_66_100)

    sum_skills_range_18_25 = len(skills_list_age_range_18_25)
    sum_skills_range_26_35 = len(skills_list_age_range_26_35)
    sum_skills_range_36_45 = len(skills_list_age_range_36_45)
    sum_skills_range_46_55 = len(skills_list_age_range_46_55)
    sum_skills_range_56_65 = len(skills_list_age_range_56_65)
    sum_skills_range_66_100 = len(skills_list_age_range_66_100)

    number_skills_age_brackets_data = [sum_skills_range_18_25, sum_skills_range_26_35, sum_skills_range_36_45, sum_skills_range_46_55, sum_skills_range_56_65, sum_skills_range_66_100]
    # end number skills per age Bracket

    # Total Number of freelance skills per age bracket
    freelance_skills_age=[]
    for i in freelance_staff_id:
        tlt = Profile.objects.get(talent=i)
        staff_age=relativedelta(today, tlt.birth_date).years

        talent_skill_l = we.filter(talent=i, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=i, edt=True).values_list('topic__skills__skill', flat=True)

        aw_exp = we.filter(talent=i, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        if awetv == None:
            awetv = 0
        else:
            awetv = awetv

        at_exp = we.filter(talent=i, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        if atetv == None:
            atetv = 0
        else:
            atetv = atetv

        t_exp = awetv + atetv

        atalent_skill = list(talent_skill_l)
        atalent_skillt = list(talent_skillt_l)
        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        result={'staff_age': staff_age, 'askillset': askillset, 'awetv': awetv, 'awetv': awetv, 't_exp': t_exp}

        freelance_skills_age.append(result)

    freelance_skills_list_age_range_18_25=[list(x['askillset']) for x in freelance_skills_age if x['staff_age'] in range(18, 25)]
    freelance_skills_list_age_range_26_35=[list(x['askillset']) for x in freelance_skills_age if x['staff_age'] in range(26, 35)]
    freelance_skills_list_age_range_36_45=[list(x['askillset']) for x in freelance_skills_age if x['staff_age'] in range(36, 45)]
    freelance_skills_list_age_range_46_55=[list(x['askillset']) for x in freelance_skills_age if x['staff_age'] in range(46, 55)]
    freelance_skills_list_age_range_56_65=[list(x['askillset']) for x in freelance_skills_age if x['staff_age'] in range(56, 65)]
    freelance_skills_list_age_range_66_100=[list(x['askillset']) for x in freelance_skills_age if x['staff_age'] in range(66, 100)]

    freelance_global_skills_list_age_range_18_25 =[]
    for sublist in freelance_skills_list_age_range_18_25:
        for item in sublist:
            freelance_global_skills_list_age_range_18_25.append(item)

    freelance_global_skills_list_age_range_26_35 =[]
    for sublist in freelance_skills_list_age_range_26_35:
        for item in sublist:
            freelance_global_skills_list_age_range_26_35.append(item)

    freelance_global_skills_list_age_range_36_45 =[]
    for sublist in freelance_skills_list_age_range_36_45:
        for item in sublist:
            freelance_global_skills_list_age_range_36_45.append(item)

    freelance_global_skills_list_age_range_46_55 =[]
    for sublist in freelance_skills_list_age_range_46_55:
        for item in sublist:
            freelance_global_skills_list_age_range_46_55.append(item)

    freelance_global_skills_list_age_range_56_65 =[]
    for sublist in freelance_skills_list_age_range_56_65:
        for item in sublist:
            freelance_global_skills_list_age_range_56_65.append(item)

    freelance_global_skills_list_age_range_66_100 =[]
    for sublist in freelance_skills_list_age_range_66_100:
        for item in sublist:
            freelance_global_skills_list_age_range_66_100.append(item)

    freelance_skills_list_age_range_18_25 = set(freelance_global_skills_list_age_range_18_25)
    freelance_skills_list_age_range_26_35 = set(freelance_global_skills_list_age_range_26_35)
    freelance_skills_list_age_range_36_45 = set(freelance_global_skills_list_age_range_36_45)
    freelance_skills_list_age_range_46_55 = set(freelance_global_skills_list_age_range_46_55)
    freelance_skills_list_age_range_56_65 = set(freelance_global_skills_list_age_range_56_65)
    freelance_skills_list_age_range_66_100 = set(freelance_global_skills_list_age_range_66_100)

    freelance_sum_skills_range_18_25 = len(freelance_skills_list_age_range_18_25)
    freelance_sum_skills_range_26_35 = len(freelance_skills_list_age_range_26_35)
    freelance_sum_skills_range_36_45 = len(freelance_skills_list_age_range_36_45)
    freelance_sum_skills_range_46_55 = len(freelance_skills_list_age_range_46_55)
    freelance_sum_skills_range_56_65 = len(freelance_skills_list_age_range_56_65)
    freelance_sum_skills_range_66_100 = len(freelance_skills_list_age_range_66_100)

    freelance_number_skills_age_brackets_data = [freelance_sum_skills_range_18_25, freelance_sum_skills_range_26_35, freelance_sum_skills_range_36_45, freelance_sum_skills_range_46_55, freelance_sum_skills_range_56_65, freelance_sum_skills_range_66_100]
    # end number freelance skills per age Bracket

    # Total hours experience
    he_list_age_range_18_25=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(18, 25)]
    he_list_age_range_26_35=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(26, 35)]
    he_list_age_range_36_45=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(36, 45)]
    he_list_age_range_46_55=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(46, 55)]
    he_list_age_range_56_65=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(56, 65)]
    he_list_age_range_66_100=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(66, 100)]


    sum_he_range_18_25 = sum(he_list_age_range_18_25)
    sum_he_range_26_35 = sum(he_list_age_range_26_35)
    sum_he_range_36_45 = sum(he_list_age_range_36_45)
    sum_he_range_46_55 = sum(he_list_age_range_46_55)
    sum_he_range_56_65 = sum(he_list_age_range_56_65)
    sum_he_range_66_100 = sum(he_list_age_range_66_100)

    hours_experience_age_brackets_data = [sum_he_range_18_25, sum_he_range_26_35, sum_he_range_36_45, sum_he_range_46_55, sum_he_range_56_65, sum_he_range_66_100]

    # Total hours freelance experience
    freelance_he_list_age_range_18_25=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(18, 25)]
    freelance_he_list_age_range_26_35=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(26, 35)]
    freelance_he_list_age_range_36_45=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(36, 45)]
    freelance_he_list_age_range_46_55=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(46, 55)]
    freelance_he_list_age_range_56_65=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(56, 65)]
    freelance_he_list_age_range_66_100=[float(x['t_exp']) for x in freelance_skills_age if x['staff_age'] in range(66, 100)]

    freelance_sum_he_range_18_25 = sum(freelance_he_list_age_range_18_25)
    freelance_sum_he_range_26_35 = sum(freelance_he_list_age_range_26_35)
    freelance_sum_he_range_36_45 = sum(freelance_he_list_age_range_36_45)
    freelance_sum_he_range_46_55 = sum(freelance_he_list_age_range_46_55)
    freelance_sum_he_range_56_65 = sum(freelance_he_list_age_range_56_65)
    freelance_sum_he_range_66_100 = sum(freelance_he_list_age_range_66_100)

    freelance_hours_experience_age_brackets_data = [freelance_sum_he_range_18_25, freelance_sum_he_range_26_35, freelance_sum_he_range_36_45, freelance_sum_he_range_46_55, freelance_sum_he_range_56_65, freelance_sum_he_range_66_100]

    # List of skills for buttons
    skills_list = [list(x['askillset']) for x in skills_age]

    global_skills_list =[]
    for sublist in skills_list:
        for item in sublist:
            global_skills_list.append(item)

    skills_list_set_set = set(global_skills_list)

    skills_list_set = sorted(skills_list_set_set, reverse=False)

    skills_list_labels = list(skills_list_set)

    dept_skills_link = SkillTag.objects.filter(skill__in=skills_list_set).order_by('skill')

    sum_skills = len(skills_list_set)

    #Hours Experience per skill chart
    skills_hours_skill_data = []
    for s in skills_list_set:
        shwe = we.filter(Q(skills__skill=s, edt=False) | Q(topic__skills__skill=s, edt=True))
        skills_hours=[]
        for i in staff_id:
            tlt = Profile.objects.get(talent=i)

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

    #Hours Freelance Experience per skill chart
    freelance_skills_hours_skill_data = []
    for s in skills_list_set:
        shwe = we.filter(Q(skills__skill=s, edt=False) | Q(topic__skills__skill=s, edt=True))
        freelance_skills_hours=[]
        for i in freelance_staff_id:
            tlt = Profile.objects.get(talent=i)

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

            freelance_skills_hours.append(result)

        freelance_skills_list=[float(x['t_exp']) for x in freelance_skills_hours]
        sum_fshwe = sum(freelance_skills_list)

        freelance_skills_hours_skill_data.append(sum_fshwe)

    template = 'mod_corporate/dashboard_department.html'
    context = {
            'cor': cor,
            'dept': dept,
            'dept_skills_link': dept_skills_link,
            'number_age_brackets_data': number_age_brackets_data,
            'freelance_number_age_brackets_data': freelance_number_age_brackets_data,
            'age_bracket_labels': age_bracket_labels,
            'number_skills_age_brackets_data': number_skills_age_brackets_data,
            'freelance_number_skills_age_brackets_data': freelance_number_skills_age_brackets_data,
            'hours_experience_age_brackets_data': hours_experience_age_brackets_data,
            'freelance_hours_experience_age_brackets_data': freelance_hours_experience_age_brackets_data,
            'skills_list_set': skills_list_set,
            'skills_list_labels': skills_list_labels,
            'skills_hours_skill_data': skills_hours_skill_data,
            'freelance_skills_hours_skill_data': freelance_skills_hours_skill_data,
            'sum_skills': sum_skills,
    }
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
    context = {'form': form, 'cor': cor, 'query': query, 'results': results, 'access': perm,}
    return render(request, template, context)


@login_required()
def corporate_select(request):
    usr = request.user
    corp = CorporateStaff.objects.filter(Q(talent=usr) & Q(corp_access__gte=1))
    corp_c = corp.count()
    if corp_c == 1:
        cor = corp[0].corporate.slug
        response = redirect(reverse('Corporate:DashCorp',kwargs={'cor': cor}))
        response.set_cookie("corp", cor)
        return response
    else:
        template = 'mod_corporate/corp_select.html'
        context = {'corp': corp}
        return render(request, template, context)


@login_required()
@corp_permission(1)
def dashboard_corporate(request, cor):
    usr = request.user
    corp = CorporateStaff.objects.get(Q(talent=usr) & Q(corporate__slug=cor))
    company = corp.corporate
    structure = OrgStructure.objects.filter(corporate__slug=cor)
    bch_qs = BriefCareerHistory.objects.filter(companybranch__company=company.company)

    #>>> Past Staff window
    past_staff = bch_qs.filter(date_to__isnull=False)

    #ps means past staff,
    ps_emp = past_staff.filter(work_configeration=5)
    ps_ctr = past_staff.filter(work_configeration=3)
    ps_fifo = past_staff.filter(work_configeration=6)
    ps_cons = past_staff.filter(work_configeration=4)
    ps_fl = past_staff.filter(work_configeration=2)
    ps_rfl = past_staff.filter(work_configeration=1)

    ps_emp_l = []
    ps_ctr_l = []
    ps_fifo_l = []
    ps_cons_l = []
    ps_fl_l = []
    ps_rfl_l = []

    if ps_emp:
        for person in ps_emp:
            tnr = person.tenure
            ps_emp_l.append(tnr)
    else:
        ps_emp_l.append(0)
    ps_emp_c = len(ps_emp_l)
    ps_emp_m = mean(ps_emp_l)

    if ps_ctr:
        for person in ps_ctr:
            tnr = person.tenure
            ps_ctr_l.append(tnr)
    else:
        ps_ctr_l.append(0)
    ps_ctr_c = len(ps_ctr_l)
    ps_ctr_m = mean(ps_ctr_l)

    if ps_fifo:
        for person in ps_fifo:
            tnr = person.tenure
            ps_fifo_l.append(tnr)
    else:
        ps_fifo_l.append(0)
    ps_fifo_c = len(ps_fifo_l)
    ps_fifo_m = mean(ps_fifo_l)

    if ps_cons:
        for person in ps_cons:
            tnr = person.tenure
            ps_cons_l.append(tnr)
    else:
        ps_cons_l.append(0)
    ps_cons_c = len(ps_cons_l)
    ps_cons_m = mean(ps_cons_l)

    if ps_fl:
        for person in ps_fl:
            tnr = person.tenure
            ps_fl_l.append(tnr)
    else:
        ps_fl_l.append(0)
    ps_fl_c = len(ps_fl_l)
    ps_fl_m = mean(ps_fl_l)

    if ps_rfl:
        for person in ps_rfl:
            tnr = person.tenure
            ps_rfl_l.append(tnr)
    else:
        ps_rfl_l.append(0)
    ps_rfl_c = len(ps_rfl_l)
    ps_rfl_m = mean(ps_rfl_l)


    #Past Staff window<<<
    departments_link={}
    for item in structure:
        cor = item.corporate.slug
        dept = item.level_name
        departments_link[item]={'cor': cor, 'dept': dept}

    chart = []
    for d in structure:
        dept = d.level_name
        if d.parent == None:
            parent = ''
        else:
            parent = d.parent
        tp = ''
        department=[f'{dept}', f'{parent}', f'{tp}']
        chart.append(department)

    department_labels=[]
    for d in structure:
        dept = d.level_name
        department=[f'{dept}']
        department_labels.append(department)

    dpt_staff_data=[]
    for d in structure:
        staff = CorporateStaff.objects.filter(Q(corporate=company) & Q(department=d) & Q(date_to__isnull=True))
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
    current_staff = staff.filter(Q(hide=False) | Q(resigned=False)).values_list('talent__id', flat=True)
    current_count = current_staff.count()

    staff = Profile.objects.filter(talent__id__in=current_staff)
    today = timezone.now().date()

    age=[]
    for i in staff:
        staff_age=relativedelta(today, i.birth_date).years
        age.append(staff_age)

    age_range_18_25 = []
    for i in age:
        if i in range(18, 25):
            staff_age = {'staff_age': i}
            age_range_18_25.append(staff_age)

    age_range_26_35 = []
    for i in age:
        if i in range(26, 35):
            staff_age = {'staff_age': i}
            age_range_26_35.append(staff_age)

    age_range_36_45 = []
    for i in age:
        if i in range(36, 45):
            staff_age = {'staff_age': i}
            age_range_36_45.append(staff_age)

    age_range_46_55 = []
    for i in age:
        if i in range(46, 55):
            staff_age = {'staff_age': i}
            age_range_46_55.append(staff_age)

    age_range_56_65 = []
    for i in age:
        if i in range(56, 65):
            staff_age = {'staff_age': i}
            age_range_56_65.append(staff_age)

    age_range_66_100 = []
    for i in age:
        if i in range(66, 100):
            staff_age = {'staff_age': i}
            age_range_66_100.append(staff_age)

    sum_age_range_18_25 = len(age_range_18_25)
    sum_age_range_26_35 = len(age_range_26_35)
    sum_age_range_36_45 = len(age_range_36_45)
    sum_age_range_46_55 = len(age_range_46_55)
    sum_age_range_56_65 = len(age_range_56_65)
    sum_age_range_66_100 = len(age_range_66_100)

    number_age_brackets_data = [sum_age_range_18_25, sum_age_range_26_35, sum_age_range_36_45, sum_age_range_46_55, sum_age_range_56_65, sum_age_range_66_100]

    age_bracket_labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '66 & up']

#    total_age = sum(age.values())
#    ave_age = [total_age / current_count]

    staff_id = Profile.objects.filter(talent__id__in=current_staff).values_list('id', flat=True)

    we = WorkExperience.objects.filter(Q(talent__subscription__gte=0) & Q(score__gte=skill_pass_score))

    # Number of skills per age bracket
    skills_age=[]
    for i in staff_id:
        tlt = Profile.objects.get(talent=i)
        staff_age=relativedelta(today, tlt.birth_date).years

        talent_skill_l = we.filter(talent=i, edt=False).values_list('skills__skill', flat=True)
        talent_skillt_l = we.filter(talent=i, edt=True).values_list('topic__skills__skill', flat=True)

        aw_exp = we.filter(talent=i, edt=False).aggregate(awet=Sum('hours_worked'))
        awetv = aw_exp.get('awet')
        if awetv == None:
            awetv = 0
        else:
            awetv = awetv

        at_exp = we.filter(talent=i, edt=True).aggregate(tet=Sum('topic__hours'))
        atetv = at_exp.get('tet')
        if atetv == None:
            atetv = 0
        else:
            atetv = atetv

        t_exp = awetv + atetv

        atalent_skill = list(talent_skill_l)
        atalent_skillt = list(talent_skillt_l)
        aslist = atalent_skill + atalent_skillt
        askillset = set(aslist)
        askill_count = len(askillset)

        result={'staff_age': staff_age, 'askillset': askillset, 'awetv': awetv, 'awetv': awetv, 't_exp': t_exp}

        skills_age.append(result)

    skills_list_age_range_18_25=[list(x['askillset']) for x in skills_age if x['staff_age'] in range(18, 25)]
    skills_list_age_range_26_35=[list(x['askillset']) for x in skills_age if x['staff_age'] in range(26, 35)]
    skills_list_age_range_36_45=[list(x['askillset']) for x in skills_age if x['staff_age'] in range(36, 45)]
    skills_list_age_range_46_55=[list(x['askillset']) for x in skills_age if x['staff_age'] in range(46, 55)]
    skills_list_age_range_56_65=[list(x['askillset']) for x in skills_age if x['staff_age'] in range(56, 65)]
    skills_list_age_range_66_100=[list(x['askillset']) for x in skills_age if x['staff_age'] in range(66, 100)]

    global_skills_list_age_range_18_25 =[]
    for sublist in skills_list_age_range_18_25:
        for item in sublist:
            global_skills_list_age_range_18_25.append(item)

    global_skills_list_age_range_26_35 =[]
    for sublist in skills_list_age_range_26_35:
        for item in sublist:
            global_skills_list_age_range_26_35.append(item)

    global_skills_list_age_range_36_45 =[]
    for sublist in skills_list_age_range_36_45:
        for item in sublist:
            global_skills_list_age_range_36_45.append(item)

    global_skills_list_age_range_46_55 =[]
    for sublist in skills_list_age_range_46_55:
        for item in sublist:
            global_skills_list_age_range_46_55.append(item)

    global_skills_list_age_range_56_65 =[]
    for sublist in skills_list_age_range_56_65:
        for item in sublist:
            global_skills_list_age_range_56_65.append(item)

    global_skills_list_age_range_66_100 =[]
    for sublist in skills_list_age_range_66_100:
        for item in sublist:
            global_skills_list_age_range_66_100.append(item)

    skills_list_age_range_18_25 = set(global_skills_list_age_range_18_25)
    skills_list_age_range_26_35 = set(global_skills_list_age_range_26_35)
    skills_list_age_range_36_45 = set(global_skills_list_age_range_36_45)
    skills_list_age_range_46_55 = set(global_skills_list_age_range_46_55)
    skills_list_age_range_56_65 = set(global_skills_list_age_range_56_65)
    skills_list_age_range_66_100 = set(global_skills_list_age_range_66_100)

    sum_skills_range_18_25 = len(skills_list_age_range_18_25)
    sum_skills_range_26_35 = len(skills_list_age_range_26_35)
    sum_skills_range_36_45 = len(skills_list_age_range_36_45)
    sum_skills_range_46_55 = len(skills_list_age_range_46_55)
    sum_skills_range_56_65 = len(skills_list_age_range_56_65)
    sum_skills_range_66_100 = len(skills_list_age_range_66_100)

    number_skills_age_brackets_data = [sum_skills_range_18_25, sum_skills_range_26_35, sum_skills_range_36_45, sum_skills_range_46_55, sum_skills_range_56_65, sum_skills_range_66_100]
    # end number skills per age Bracket

    # Total hours experience
    he_list_age_range_18_25=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(18, 25)]
    he_list_age_range_26_35=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(26, 35)]
    he_list_age_range_36_45=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(36, 45)]
    he_list_age_range_46_55=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(46, 55)]
    he_list_age_range_56_65=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(56, 65)]
    he_list_age_range_66_100=[float(x['t_exp']) for x in skills_age if x['staff_age'] in range(66, 100)]


    sum_he_range_18_25 = sum(he_list_age_range_18_25)
    sum_he_range_26_35 = sum(he_list_age_range_26_35)
    sum_he_range_36_45 = sum(he_list_age_range_36_45)
    sum_he_range_46_55 = sum(he_list_age_range_46_55)
    sum_he_range_56_65 = sum(he_list_age_range_56_65)
    sum_he_range_66_100 = sum(he_list_age_range_66_100)

    hours_experience_age_brackets_data = [sum_he_range_18_25, sum_he_range_26_35, sum_he_range_36_45, sum_he_range_46_55, sum_he_range_56_65, sum_he_range_66_100]

    potential = bch_qs.exclude(talent__id__in=current_staff).filter(date_to__isnull=True).count()

    template = 'mod_corporate/dashboard_corporate.html'
    context = {
        'corp': corp,
        'company': company,
        'potential': potential,
        'chart': chart,
        'current_count': current_count,
        'department_labels': department_labels,
        'dpt_staff_data': dpt_staff_data,
        'number_age_brackets_data': number_age_brackets_data,
        'age_bracket_labels': age_bracket_labels,
        'number_skills_age_brackets_data': number_skills_age_brackets_data,
        'hours_experience_age_brackets_data': hours_experience_age_brackets_data,
        'departments_link': departments_link,
        'ave_age': ave_age,
        'ps_emp_c': ps_emp_c, 'ps_emp_m': ps_emp_m, 'ps_ctr_c': ps_ctr_c, 'ps_ctr_m': ps_ctr_m, 'ps_fifo_c': ps_fifo_c, 'ps_fifo_m': ps_fifo_m, 'ps_cons_c': ps_cons_c, 'ps_cons_m': ps_cons_m, 'ps_fl_c': ps_fl_c, 'ps_fl_m': ps_fl_m, 'ps_rfl_c': ps_rfl_c, 'ps_rfl_m': ps_rfl_m,
        }
    return render(request, template, context)


@login_required()
@corp_permission(2)
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
@corp_permission(3)
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
def help_dash_staff(request):
    '''Help page for the staff card on the corporate dashboard, context not working'''
    context = {}
    template = 'mod_corporate/help_dashboard_staff.html'
    return render(request, template, context)


@login_required()
@corp_permission(2)
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
@corp_permission(2)
def staff_include(request, cor, tlt, bch):
    '''Add people to the company staff'''
    corp = get_object_or_404(CorporateHR,slug=cor)
    staff = get_object_or_404(Profile, alias=tlt)
    bch = get_object_or_404(BriefCareerHistory, slug=bch)


    form = AddStaffForm(request.POST or None)
    template = 'mod_corporate/staff_include.html'
    context = {'form': form, 'staff': staff, 'corp': corp,}
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = staff.talent
            new.corporate = corp
            new.date_from = bch.date_from
            new.type = bch.work_configeration
            if bch.date_to:
                new.date_to = bch.date_to
            new.designation = bch.designation
            new.save()
            return redirect(reverse('Corporate:StaffManage',kwargs={'cor':cor,}))
        else:
            return render(request, template, context)
    else:
        return render(request, template, context)


@login_required()
@corp_permission(2)
def staff_add(request, cor):
    '''Add people to the company staff that have not indicated they work for the company'''
    corp = get_object_or_404(CorporateHR,slug=cor)

    if request.is_ajax():
        qry = request.GET.get('term')
        filt = CorporateStaff.objects.filter(corporate__slug=cor)

        people = CustomUser.objects.all().filter(~Q(id__in=filt)).filter(Q(first_name__icontains=qry) | Q(last_name__icontains=qry) | Q(email__icontains=qry) | Q(display_text__icontains=qry)).order_by('last_name')
        response_content = list(people.values('id','email'))

        return JsonResponse(response_content, safe=False)

    form = AddNewStaffForm(request.POST or None, cor_sg=cor)
    template = 'mod_corporate/staff_add.html'
    context = {'form': form, 'corp': corp,}

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.corporate = corp
            new.save()
            return redirect(reverse('Corporate:StaffManage',kwargs={'cor':cor,}))
        else:
            return render(request, template, context)
    else:
        return render(request, template, context)


@login_required()
@corp_permission(2)
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
@corp_permission(2)
def staff_current(request, cor):
    '''Lists the current staff members'''
    corp = get_object_or_404(CorporateHR, slug=cor)
    current = CorporateStaff.objects.filter(corporate__slug=cor).filter(Q(hide=False) | Q(resigned=False)).select_related('talent').order_by('talent__last_name')

    staff_c = current.count()

    template = 'mod_corporate/staff_current.html'
    context = {'current': current, 'cor': cor, 'corp': corp, 'staff_c': staff_c,}
    return render(request, template, context)


@login_required()
@corp_permission(2)
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
    admin_c = admin_qs.filter(corp_access = 3).count()
    cont_c = admin_qs.filter(corp_access = 2).count()
    hod_c = admin_qs.filter(corp_access = 1).count()

    template = 'mod_corporate/admin_manage.html'
    context = {
        'admin_qs': admin_qs, 'admin_c': admin_c, 'cont_c': cont_c, 'no_admin': no_admin, 'no_cont': no_cont, 'staff_c': staff_c, 'usr_permission': usr_permission, 'corp': corp,
        }
    return render(request, template, context)


@login_required()
@corp_permission(3)
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
@corp_permission(2)
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
@corp_permission(2)
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

@login_required()
@corp_permission(1)
def experience_dashboard(request, cor):
    staff_qs = CorporateStaff.objects.filter(Q(corporate__slug=cor) & Q(hide=False)).select_related('talent')

    staff_list = staff_qs.values_list('talent__id', flat=True)
    we_qs = WorkExperience.objects.filter(Q(talent__id__in=staff_list) & Q(score__gte=skill_pass_score))

    #total experience and training hours (confirmed)
    corp_ehrs = we_qs.filter(edt=False).aggregate(exp_sum = Sum('hours_worked'))
    corp_thrs = we_qs.filter(edt=True).aggregate(trn_sum = Sum('topic__hours'))


@login_required()
@corp_permission(2)
def past_staff(request, cor):
    corp = CorporateHR.objects.get(slug=cor)
    company = corp.company
    print(company)
    past_qs = BriefCareerHistory.objects.filter(Q(companybranch__company=company) & Q(date_to__isnull=False)).select_related('talent').order_by('-date_to')

    template = 'mod_corporate/staff_past.html'
    context = {'past_qs': past_qs, 'cor': cor, 'corp': corp,}
    return render(request, template, context)



    #count staff at each experience level

    #list all skills
    #count skills
    #sum hours for each skill
    #see skill age (possibly have a barchart with different colours for age)
    #at a later stage: skill age, by department, skill last utilised, no longer available (staff left), SKILLS AVAILABLE, BUT NOT UTILISED.

    #list projects staff members have worked on.
    #sum the number of hours worked on the project.
