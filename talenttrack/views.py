from django.shortcuts import(
    render, get_object_or_404, redirect, render_to_response
    )
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
import json
from django.db.models import Count, Sum, Q, F
from decimal import Decimal


from csp.decorators import csp_exempt
from core.decorators import subscription


from .forms import (
        TopicForm, ResultForm, CourseTypeForm, CourseForm, DesignationForm, ClassMatesSelectForm, ClassMatesConfirmForm, LecturerSelectForm, LecturerConfirmForm, EducationForm, WorkExperienceForm, WorkColleagueSelectForm, WorkColleagueConfirmForm, WorkColleagueResponseForm, ClassMatesResponseForm, LecturerResponseForm, SuperiorSelectForm, WorkCollaboratorResponseForm, WorkCollaboratorConfirmForm, WorkCollaboratorSelectForm, WorkClientResponseForm, WorkClientConfirmForm, WorkClientSelectForm, PreLoggedExperienceForm, TopicPopForm, LecturerRespondForm, ClassMatesRespondForm, WorkColleagueSelectForm, SuperiorSelectForm, WorkCollaboratorSelectForm, AchievementsForm, LicenseCertificationForm,
)

from .models import (
        Lecturer, Course, ClassMates, WorkExperience, Superior, WorkCollaborator, WorkClient, WorkColleague, Designation, Achievements, LicenseCertification,
)

from db_flatten.models import SkillTag
from marketplace.models import(
    SkillLevel, SkillRequired, WorkBid, BidShortList, TalentRequired, BidInterviewList,
)
from enterprises.models import Branch
from project.models import ProjectData
from Profile.models import (
        BriefCareerHistory, Profile, LanguageTrack, PhysicalAddress
)
from booklist.models import ReadBy
from users.models import CustomUser


@login_required()
def ExperienceHome(request):
        #>>>Step 1
        basequery = WorkExperience.objects.select_related('topic').filter(talent=request.user)
        skills = SkillTag.objects.all()
        sl = SkillLevel.objects.all()
        #<<<Step 1

        #>>>Step 2
        train = basequery.filter(edt=True).order_by('-date_from')
        train_sum = train.aggregate(Edu_sum=Sum('topic__hours'))

        experience = basequery.filter(wexp=True).order_by('-date_from')
        exp_sum = experience.aggregate(we_sum=Sum('hours_worked'))

        prelog = basequery.filter(prelog=True).order_by('-date_from')
        pre_sum = prelog.aggregate(p_sum=Sum('hours_worked'))

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
        exp_lvls = [Decimal(e_sum+p_sum)]

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

        template = 'talenttrack/track_home.html'
        context = {
            'train': train, 'train_sum': train_sum, 'experience': experience, 'exp_sum': exp_sum, 'prelog': prelog, 'pre_sum': pre_sum, 'tot_sum': tot_sum, 'skill_name': skill_name, 'skill_count': skill_count, 'level': level,
            }
        return render(request, template, context)


@login_required()
def CaptureAchievementView(request):
    pfl = get_object_or_404(CustomUser, pk=request.user.id)
    form = AchievementsForm(request.POST or None)

    if request.method == 'POST':
        new = form.save(commit=False)
        new.talent = pfl
        new.save()
        return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':pfl.id})+'#achievements')
    else:
        template = 'talenttrack/achievement_capture.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def EditAchievementView(request, ach_pk):
    instance = get_object_or_404(Achievements, pk=ach_pk)

    form = AchievementsForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        new = form.save(commit=False)
        new.save()
        return redirect(reverse('Profile:ProfileView')+'#achievements')
    else:
        template = 'talenttrack/achievement_capture.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def DeleteAchievementView(request, ach_pk):
    info = Achievements.objects.get(pk=ach_pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Profile:ProfileView', kwargs={'profile_id':info.talent.id})+'#achievements')
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def LicenseCertificationCaptureView(request):
    tlt_i = get_object_or_404(CustomUser, pk=request.user.id)
    form = LicenseCertificationForm(request.POST or None)

    if form.is_valid():
        new = form.save(commit=False)
        new.talent = tlt_i
        new.save()
        return redirect(reverse ('Profile:ProfileView', kwargs={'tlt':tlt_i.alias})+'#memberships')
    else:
        template = 'talenttrack/membership_view.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
@csp_exempt
def LicenseCertificationEditView(request, lcm):
    lcm_i = LicenseCertification.objects.get(slug=lcm)
    form = LicenseCertificationForm(request.POST or None, instance=lcm_i)

    if form.is_valid():
        edit = form.save(commit=False)
        edit.save()
        return redirect(reverse ('Profile:ProfileView', kwargs={'tlt':lcm_i.talent.alias})+'#memberships')
    else:
        template = 'talenttrack/membership_view.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def LicenseCertificationDeleteView(request, pk, tlt):
    lcm = LicenseCertification.objects.get(pk=pk)
    if lcm.talent == request.user:
        if request.method =='POST':
            lcm.delete()
            return redirect(reverse('Profile:ProfileView', kwargs={'tlt':tlt})+'#memberships')
    else:
        raise PermissionDenied


@login_required()
@subscription(2)
def ActiveProfileView(request, tlt, vac):
    #caching
    bch = BriefCareerHistory.objects.filter(talent__alias=tlt).order_by('-date_from')
    pfl = Profile.objects.only('id','background', 'alias', 'mentor', 'motivation', 'std_rate', 'currency').filter(alias=tlt)
    print('tlt:', tlt, 'pfl:', pfl)
    als = get_object_or_404(Profile, alias=tlt)
    padd = PhysicalAddress.objects.only('country', 'region', 'city').filter(talent__alias=tlt)
    vacancy = TalentRequired.objects.filter(ref_no=vac)
    skr = SkillRequired.objects.filter(scope__ref_no=vac).values_list('skills', flat=True).distinct('skills')
    skill_qs = SkillTag.objects.all()
    exp = WorkExperience.objects.filter(talent__alias=tlt).select_related('topic', 'course', 'project')
    edtexp = exp.filter(edt=True).order_by('-date_from')
    bkl = ReadBy.objects.filter(talent__alias=tlt).select_related('book', 'type')[:6]
    bkl_count = bkl.count()
    prj_qs = ProjectData.objects.all()
    bid_qs = WorkBid.objects.filter(Q(talent__alias=tlt) & Q(work__ref_no=vac))
    achievement_qs = Achievements.objects.filter(talent__alias=tlt).order_by('-date_achieved')
    language_qs = LanguageTrack.objects.filter(talent__alias=tlt).order_by('-language')
    membership_qs = LicenseCertification.objects.filter(talent__alias=tlt).order_by('-issue_date')
    bslist_qs = BidShortList.objects.filter(Q(talent__alias=tlt) & Q(scope__ref_no=vac))
    int_list = BidInterviewList.objects.filter(Q(talent__alias=tlt) & Q(scope__ref_no=vac))

    #Project Summary
    prj = exp.values_list('project', flat=True).distinct('project')
    prj_set = {}
    prj_count = 0
    for p in prj:
        if p == None:
            pass
        else:
            prj_count +=1
            project_q = prj_qs.filter(pk=p).values_list('name', 'company__name', 'branch__name', 'industry__industry')
            info_list=[project_q[0][1], project_q[0][2], project_q[0][3]]
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
            e = d.experience.all()
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
    #populating the keys
    for s in skr:
        #populating the set
        skill_q = skill_qs.filter(pk=s).values_list('skill', flat=True)
        skill_f = skill_q[0]
        vacst_set[skill_f]=float(0)
        if s in edt:
            #populating the values
            d = skill_qs.get(pk=s)
            e = d.topic_set.all()
            e_sum = e.aggregate(sum_t=Sum('hours'))
            sum_float = float(e_sum.get('sum_t'))
            if vacst_set[skill_f]:
                new = vacst_set[skill_f]+sum_float
                vacst_set[skill_f]=new
            else:
                vacst_set[skill_f] = sum_float
        else:
            pass

    template = 'talenttrack/active_profile_view.html'
    context = {
        'bch': bch,'pfl': pfl, 'padd': padd,'vacse_set': vacse_set, 'vacst_set': vacst_set, 'exp': exp, 'bkl': bkl, 'edtexp': edtexp, 'bkl_count': bkl_count, 'prj_set': prj_set, 'prj_count': prj_count, 'bid_qs': bid_qs, 'achievement_qs': achievement_qs, 'language_qs': language_qs, 'membership_qs': membership_qs, 'bslist_qs': bslist_qs, 'vacancy': vacancy, 'int_list': int_list, 'als': als
        }
    return render(request, template, context)


@login_required()
@subscription(1)
def LCMFullView(request, tlt):
    tlt = Profile.objects.get(alias=tlt)
    lcm_qs = LicenseCertification.objects.filter(talent__alias=tlt).order_by('-issue_date')

    template = 'talenttrack/lcm_full_view.html'
    context = {
        'lcm_qs': lcm_qs, 'tlt': tlt,
        }
    return render(request, template, context)


@login_required()
@subscription(2)
def SkillProfileDetailView(request, tlt):
    tlt_p = Profile.objects.get(alias=tlt)
    skill_qs = SkillTag.objects.all()
    exp = WorkExperience.objects.filter(
        talent__alias = tlt).select_related('topic')

    exp_s = exp.values_list('skills', flat=True).distinct('skills')
    exp_t = exp.order_by('topic__skills').values_list('topic__skills', flat=True).distinct('topic__skills')
    edt_topic = exp.values_list('topic', flat=True).distinct('topic')

    #gathering all experience hours per topic
    exp_set = {}
    for s in exp_s:
        if s == None:
            pass
        else:
            b = skill_qs.get(pk=s)
            c = b.experience.all()
            cnt = c.count()
            sum = c.aggregate(sum_s=Sum('hours_worked'))
            sum_float = float(sum.get('sum_s'))
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
                e = d.topic_set.all()
                e_sum = e.aggregate(sum_t=Sum('hours'))
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
        'edt_set': edt_set, 'exp_set': exp_set, 'tlt_p': tlt_p,
    }
    return render(request, template, context)


@login_required()
def SumAllExperienceView(request):
    tlt_p = Profile.objects.get(pk=request.user.id)
    skill_qs = SkillTag.objects.all()
    exp = WorkExperience.objects.filter(
        talent = request.user.id).select_related('topic')

    exp_s = exp.values_list('skills', flat=True).distinct('skills')
    exp_t = exp.order_by('topic__skills').values_list('topic__skills', flat=True).distinct('topic__skills')
    edt_topic = exp.values_list('topic', flat=True).distinct('topic')

    #gathering all experience hours per topic
    exp_set = {}
    for s in exp_s:
        if s == None:
            pass
        else:
            b = skill_qs.get(pk=s)
            c = b.experience.all()
            cnt = c.count()
            sum = c.aggregate(sum_s=Sum('hours_worked'))
            sum_float = float(sum.get('sum_s'))
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
                e = d.topic_set.all()
                e_sum = e.aggregate(sum_t=Sum('hours'))
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
        'edt_set': edt_set, 'exp_set': exp_set, 'tlt_p': tlt_p
    }
    return render(request, template, context)


@login_required()
def DPC_SummaryView(request):
    #caching
    exp = WorkExperience.objects.filter(
        talent = request.user.id).select_related('designation')
    designation_qs = Designation.objects.all()
    companybranch_qs = Branch.objects.all()
    project_qs = ProjectData.objects.all()

    #Designation Summary
    dgn = exp.values_list('designation', flat=True).distinct('designation')

    dgn_set = {}
    for d in dgn:
        if d == None:
            pass
        else:
            a = designation_qs.get(pk=d)
            b = a.workexperience_set.all()
            cnt = b.count()
            sum = b.aggregate(sum_d=Sum('hours_worked'))
            sum_float = float(sum.get('sum_d'))
            info_set = {}
            info_set['count']=cnt
            info_set['sum']=sum_float
            designation_q = designation_qs.filter(pk=d).values_list('name', flat=True)
            designation_f = designation_q[0]
            dgn_set[designation_f] = info_set


    #Company Summary - Listed Per Branch
    cmp = exp.values_list('branch', flat=True).distinct('branch')
    cmp_set = {}
    for c in cmp:
        if c == None:
            pass
        else:
            a = companybranch_qs.get(pk=c)
            b = a.workexperience_set.all()
            cnt = b.count()
            sum = b.aggregate(sum_d=Sum('hours_worked'))
            sum_float = float(sum.get('sum_d'))
            info_set = {}
            info_set['count']=cnt
            info_set['sum']=sum_float
            companybranch_q = companybranch_qs.filter(pk=c).values_list('company__name', 'name', 'city__city')
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
            cnt = b.count()
            sum = b.aggregate(sum_d=Sum('hours_worked'))
            sum_float = float(sum.get('sum_d'))
            info_set = {}
            info_set['count']=cnt
            info_set['sum']=sum_float
            project_q = project_qs.filter(pk=p).values_list('name', 'company__name', 'branch__name')
            project_f = f'{project_q[0][0]}: {project_q[0][1]} ({project_q[0][2]})'
            prj_set[project_f] = info_set

    template = 'talenttrack/talent_dpc_summary.html'
    context = {
        'dgn_set': dgn_set, 'cmp_set': cmp_set, 'prj_set': prj_set,
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
            response = redirect('Talent:ColleagueSelect')
            response.delete_cookie("confirm")
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
def PreLogDetailView(request, pre_id):
    check = WorkExperience.objects.get(pk=pre_id, prelog=True)
    if check.talent == request.user:
        sum = WorkExperience.objects.filter(talent=request.user, prelog=True)
        sum_company = sum.filter(company=check.company).aggregate(co_sum=Sum('hours_worked'))
        sum_project = sum.filter(project=check.project).aggregate(p_sum=Sum('hours_worked'))
        list = WorkExperience.objects.filter(pk=pre_id)
        confirmed_clg = WorkColleague.objects.filter(experience=pre_id)
        confirmed_sup = Superior.objects.filter(experience=pre_id)
        confirmed_clr = WorkCollaborator.objects.filter(experience=pre_id)
        confirmed_cnt = WorkClient.objects.filter(experience=pre_id)

        template = 'talenttrack/experience_detail.html'
        context = {
            'check': check, 'confirmed_clg': confirmed_clg, 'confirmed_sup': confirmed_sup, 'confirmed_clr': confirmed_clr, 'confirmed_cnt': confirmed_cnt, 'list': list, 'sum_company': sum_company, 'sum_project': sum_project
            }

        return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def ClientSelectView(request, pk):
    instance = WorkExperience.objects.get(pk=pk)
    form = WorkClientSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect('Talent:ClientSelect', kwargs={'pk':pk})
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect('Talent:Home')
                response.delete_cookie("confirm")
                return response
    else:

        template = 'talenttrack/experience_client_select.html'
        context = {'instance': instance, 'form': form}
        response = render(request, template, context)
        response.set_cookie("confirm","WT")
        return response


@login_required()
@csp_exempt
def ClientAddView(request, pk):
    instance = get_object_or_404(WorkExperience, pk=pk)
    form = WorkClientSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:ClientAdd', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response

            elif 'done' in request.POST:
                response = redirect(reverse('Talent:ExperienceDetail', kwargs={'exp_id': instance.id}))
                response.delete_cookie("confirm")
                return response
    else:
        template = 'talenttrack/experience_client_add.html'
        context = {'instance': instance, 'form': form}
        response =  render(request, template, context)
        response.set_cookie("confirm","WT")
        return response


@login_required()
def ClientResponseView(request, pk):
    check = WorkClient.objects.get(pk=pk)
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
@csp_exempt
def CollaboratorSelectView(request, pk):
    instance = WorkExperience.objects.get(pk=pk)
    form = WorkCollaboratorSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect('Talent:CollaboratorSelect', kwargs={'pk':pk})
                response.delete_cookie("confirm")
                return response

            elif 'done' in request.POST:
                response = redirect(reverse('Talent:ClientSelect', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response
    else:
        template = 'talenttrack/experience_collaborator_select.html'
        context = {'instance': instance, 'form': form}
        response = render(request, template, context)
        response.set_cookie("confirm","WL")
        return response


@login_required()
@csp_exempt
def CollaboratorAddView(request, pk):
    instance = get_object_or_404(WorkExperience, pk=pk)
    form = WorkCollaboratorSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:CollaboratorAdd', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response

            elif 'done' in request.POST:
                response = redirect(reverse('Talent:ExperienceDetail', kwargs={'exp_id': instance.id}))
                response.delete_cookie("confirm")
                return response
    else:
        template = 'talenttrack/experience_collaborator_add.html'
        context = {'instance': instance, 'form': form}
        response = render(request, template, context)
        response.set_cookie("confirm","WL")
        return response


@login_required()
def CollaboratorResponseView(request, pk):
    check = WorkCollaborator.objects.get(pk=pk)
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
@csp_exempt
def SuperiorSelectView(request, pk):
    instance = WorkExperience.objects.get(pk=pk)
    form = SuperiorSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect('Talent:SuperiorSelect', kwargs={'pk':pk})
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:CollaboratorSelect', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response
    else:
        template = 'talenttrack/experience_superior_select.html'
        context = {'instance': instance, 'form': form}
        response = render(request, template, context)
        response.set_cookie("confirm","WS")
        return response


@login_required()
@csp_exempt
def SuperiorAddView(request, pk):
    instance = get_object_or_404(WorkExperience, pk=pk)
    form = SuperiorSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect('Talent:SuperiorAdd', kwargs={'pk':pk})
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:ExperienceDetail', kwargs={'exp_id': instance.id}))
                response.delete_cookie("confirm")
                return response
    else:
        template = 'talenttrack/experience_superior_add.html'
        context = {'instance': instance, 'form': form}
        response = render(request, template, context)
        response.set_cookie("confirm","WS")
        return response


@login_required()
def SuperiorResponseView(request, pk):
    check = Superior.objects.get(pk=pk)
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
@csp_exempt
def ColleagueSelectView(request):
    instance = WorkExperience.objects.filter(talent=request.user).latest('date_captured')
    form = WorkColleagueSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect('Talent:ColleagueSelect')
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:SuperiorSelect', kwargs={'pk':instance.id}))
                response.delete_cookie("confirm")
                return response
    else:
        template = 'talenttrack/experience_colleague_select.html'
        context = {'instance': instance, 'form': form}
        response =  render(request, template, context)
        response.set_cookie("confirm","WC")
        return response


@login_required()
@csp_exempt
def ColleagueAddView(request, pk):
    instance = get_object_or_404(WorkExperience, pk=pk)
    form = WorkColleagueSelectForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:ColleagueAdd', kwargs={'pk':pk}))
                response.delete_cookie("confirm")
                return response

            elif 'done' in request.POST:

                response = redirect(reverse('Talent:ExperienceDetail', kwargs={'exp_id':instance.id}))
                response.delete_cookie("confirm")
                return response

    else:
        template = 'talenttrack/experience_colleague_add.html'
        context = {'instance': instance, 'form': form}
        response = render(request, template, context)
        response.set_cookie("confirm","WC")
        return response


@login_required()
def ColleagueResponseView(request, pk):
    check = WorkColleague.objects.get(pk=pk)
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
def ExperienceDetailView(request, exp_id):
    check = WorkExperience.objects.get(pk=exp_id, wexp=True)
    if check.talent == request.user:
        sum = WorkExperience.objects.filter(talent=request.user, wexp=True)
        sum_company = sum.filter(company=check.company).aggregate(co_sum=Sum('hours_worked'))
        sum_project = sum.filter(project=check.project).aggregate(p_sum=Sum('hours_worked'))
        list = WorkExperience.objects.filter(pk=exp_id)
        confirmed_clg = WorkColleague.objects.filter(experience=exp_id)
        confirmed_sup = Superior.objects.filter(experience=exp_id)
        confirmed_clr = WorkCollaborator.objects.filter(experience=exp_id)
        confirmed_cnt = WorkClient.objects.filter(experience=exp_id)
        template = 'talenttrack/experience_detail.html'
        context = {'check': check, 'confirmed_clg': confirmed_clg, 'confirmed_sup': confirmed_sup, 'confirmed_clr': confirmed_clr, 'confirmed_cnt': confirmed_cnt, 'list': list, 'sum_company': sum_company, 'sum_project': sum_project}
        return render(request, template, context)
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
            return redirect('Talent:ColleagueSelect')
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
def EducationDetail(request, edu_id):
    check = WorkExperience.objects.get(pk=edu_id, edt=True)
    if check.talent == request.user:
        confirmed_l = Lecturer.objects.filter(education=edu_id)
        confirmed_cm = ClassMates.objects.filter(education=edu_id)
        template = 'talenttrack/education_detail.html'
        context = {'check': check, 'confirmed_l': confirmed_l, 'confirmed_cm': confirmed_cm}
        return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def LecturerResponse(request, pk):
    check = Lecturer.objects.get(pk=pk)
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
def ClassMatesResponse(request, pk):
    check = ClassMates.objects.get(pk=pk)
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
def LecturerSelectView(request):
    instance = WorkExperience.objects.filter(talent=request.user, edt=True).latest('date_captured')
    form = LecturerSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.save()
            if 'another' in request.POST:
                response = redirect('Talent:LecturerSelect')
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect('Talent:ClassMatesSelect')
                response.delete_cookie("confirm")
                return response
    else:
        template = 'talenttrack/education_lecturer_select.html'
        context = {'instance': instance, 'form': form}
        response = render(request, template, context)
        response.set_cookie("confirm","LR")
        return response


@login_required()
@csp_exempt
def LecturerAddView(request, pk):
    instance = get_object_or_404(WorkExperience, pk=pk)
    form = LecturerSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.save()
            if 'another' in request.POST:
                response = redirect('Talent:LecturerAdd', kwargs={'pk': pk})
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:EducationDetail', kwargs={'edu_id': instance.id}))
                response.delete_cookie("confirm")
                return response
    else:
        template = 'talenttrack/education_lecturer_select.html'
        context = {'instance': instance, 'form': form}
        response = render(request, template, context)
        response.set_cookie("confirm","LR")
        return response


@login_required()
@csp_exempt
def ClassMateSelectView(request):
    instance = WorkExperience.objects.filter(talent=request.user,edt=True).latest('date_captured')
    form = ClassMatesSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.save()
            if 'another' in request.POST:
                reponse = redirect('Talent:ClassMatesSelect')
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:Home'))
                response.delete_cookie("confirm")
                return response
    else:
        template = 'talenttrack/education_classmate_select.html'
        context = {'instance': instance, 'form': form}
        response = render(request, template, context)
        response.set_cookie("confirm","CM")
        return response


@login_required()
@csp_exempt
def ClassMateAddView(request, pk):
    instance = get_object_or_404(WorkExperience, pk=pk)
    form = ClassMatesSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.save()
            if 'another' in request.POST:
                response = redirect(reverse('Talent:ClassMatesAdd', kwargs={'pk': pk}))
                response.delete_cookie("confirm")
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Talent:EducationDetail', kwargs={'edu_id': instance.id}))
                response.delete_cookie("confirm")
                return response
    else:
        template = 'talenttrack/education_classmate_select.html'
        context = {'instance': instance, 'form': form}
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
            return redirect(reverse('Talent:LecturerSelect'))
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
            return redirect(reverse('Talent:Home')+'#headingOne')
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
    form = DesignationForm(request.POST or None)
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
