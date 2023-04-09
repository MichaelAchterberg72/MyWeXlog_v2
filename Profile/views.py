import datetime as dt
import json
import os
from datetime import datetime, timedelta

import pytz
import sendgrid
from csp.decorators import csp_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
#email
from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Count, F, Q, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.utils import dateformat, timezone
from django.utils.html import strip_tags
from django.utils.http import is_safe_url
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from pinax.referrals.models import Referral
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Content, CustomArg, From, Header, Mail,
                                   ReplyTo, SendAt, Subject, To)
from treebeard.mp_tree import MP_Node

from analytics.models import ObjectViewed
from core.decorators import subscription
from enterprises.models import Branch, Enterprise
from db_flatten.models import SkillTag
from locations.models import Region
from marketplace.forms import (AssignmentClarifyForm,
                               AssignmentDeclineReasonsForm, TalentRateForm,
                               VacancyRateForm)
from marketplace.models import (BidInterviewList, BidShortList, TalentRate,
                                TalentRequired, VacancyRate, WorkBid,
                                WorkIssuedTo)
from nestedsettree.models import NtWk
from talenttrack.forms import (ClassMatesCommentForm, LecturerCommentForm,
                               SuperiorConfirmForm, WorkClientConfirmForm,
                               WorkCollaboratorConfirmForm,
                               WorkColleagueConfirmForm)
from talenttrack.models import (Achievements, Awards, ClassMates, Lecturer,
                                LicenseCertification, Publications, Superior,
                                WorkClient, WorkCollaborator, WorkColleague,
                                WorkExperience)
from users.models import CustomUser, ExpandedView
from WeXlog import app_config
from WeXlog.app_config import (classmate_score, client_score,
                               collaborator_score, colleague_score,
                               lecturer_score, pre_colleague_score,
                               superior_score)

from .forms import (BriefCareerHistoryForm, CustomUserUpdateForm, EmailForm,
                    EmailStatusForm, ExpandedIntroWalkthroughForm,
                    FileUploadForm, IdentificationDetailForm, IdTypeForm,
                    LanguageListForm, LanguageTrackForm, OnlineProfileForm,
                    PassportDetailForm, PhoneNumberForm, PhysicalAddressForm,
                    PostalAddressForm, ProfileBackgroundForm, ProfileForm,
                    ProfileMotivationForm, ProfileTypeForm,
                    PublicProfileIntroForm, PublicProfileNameForm,
                    ResignedForm, UploadProfileBackgroundPicForm,
                    UploadProfilePicForm, UserUpdateForm,
                    WillingToRelocateForm)
from .models import (BriefCareerHistory, Email, FileUpload,
                     IdentificationDetail, IdType, LanguageTrack,
                     OnlineRegistrations, PassportDetail, PhoneNumber,
                     PhysicalAddress, PostalAddress, Profile, ProfileImages,
                     SiteName, WillingToRelocate)


def willing_to_relocate(request):
    talent = request.user

    form = WillingToRelocateForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = talent
            new.save()

            return redirect(reverse('Profile:ProfileView')+'#WTR')
        else:
            template = 'Profile/willing_to_relocate.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        template = 'Profile/willing_to_relocate.html'
        context = {'form': form}
        return render(request, template, context)


def copy_phy_address(request):
    talent = request.user
    qs_addr = PhysicalAddress.objects.get(talent=talent)
    qs_post = PostalAddress.objects.filter(talent=talent)
    qs_post.update(
        line1=qs_addr.line1,
        line2=qs_addr.line2,
        country=qs_addr.country,
        region=qs_addr.region,
        city=qs_addr.city,
        code=qs_addr.code,
        )

    return redirect(reverse('Profile:ProfileView')+'#phone')


def ProfileViewedReport(request):
    tlt = request.user
    tlt_id = tlt.id
    qs = ObjectViewed.objects.filter(object_id=tlt_id).exclude(user=tlt)
    pvr = qs.filter(content_type__app_label="Profile").order_by('-timestamp')
    vbm = WorkBid.objects.filter(talent=tlt).order_by('-date_applied')
    pvr_p = pvr.values_list('user__alias', flat=True).distinct()
    pvr_p_count = pvr_p.count()
    pvr_count = pvr.count()
    pvr_s = pvr[:5]

    referral_code = Referral.objects.get(user=tlt)
    alias = tlt.alias

    date = timezone.now()
    d1 = date - timedelta(days=7)
    d2 = d1 - timedelta(days=7)
    d3 = d2 - timedelta(days=7)
    d4 = d3 - timedelta(days=7)
    d5 = d4 - timedelta(days=7)
    d6 = d5 - timedelta(days=7)
    d7 = d6 - timedelta(days=7)
    d8 = d7 - timedelta(days=7)
    d9 = d8 - timedelta(days=7)

    monday1 = (d1 - timedelta(days=d1.weekday()))
    monday2 = (d2 - timedelta(days=d2.weekday()))
    monday3 = (d3 - timedelta(days=d3.weekday()))
    monday4 = (d4 - timedelta(days=d4.weekday()))
    monday5 = (d5 - timedelta(days=d5.weekday()))
    monday6 = (d6 - timedelta(days=d6.weekday()))
    monday7 = (d7 - timedelta(days=d7.weekday()))
    monday8 = (d8 - timedelta(days=d8.weekday()))
    monday9 = (d9 - timedelta(days=d9.weekday()))

    week3_date = dateformat.format(monday2, "d-M")
    week4_date = dateformat.format(monday3, "d-M")
    week5_date = dateformat.format(monday4, "d-M")
    week6_date = dateformat.format(monday5, "d-M")
    week7_date = dateformat.format(monday6, "d-M")
    week8_date = dateformat.format(monday7, "d-M")

    week1 = pvr.filter(timestamp__range=(monday1, date)).count()
    week2 = pvr.filter(timestamp__range=(monday2, monday1)).count()
    week3 = pvr.filter(timestamp__range=(monday3, monday2)).count()
    week4 = pvr.filter(timestamp__range=(monday4, monday3)).count()
    week5 = pvr.filter(timestamp__range=(monday5, monday4)).count()
    week6 = pvr.filter(timestamp__range=(monday6, monday5)).count()
    week7 = pvr.filter(timestamp__range=(monday7, monday6)).count()
    week8 = pvr.filter(timestamp__range=(monday8, monday7)).count()

    week1_u = pvr_p.filter(timestamp__range=(monday1, date)).count()
    week2_u = pvr_p.filter(timestamp__range=(monday2, monday1)).count()
    week3_u = pvr_p.filter(timestamp__range=(monday3, monday2)).count()
    week4_u = pvr_p.filter(timestamp__range=(monday4, monday3)).count()
    week5_u = pvr_p.filter(timestamp__range=(monday5, monday4)).count()
    week6_u = pvr_p.filter(timestamp__range=(monday6, monday5)).count()
    week7_u = pvr_p.filter(timestamp__range=(monday7, monday6)).count()
    week8_u = pvr_p.filter(timestamp__range=(monday8, monday7)).count()

    week1_b = vbm.filter(date_applied__range=(monday1, date)).count()
    week2_b = vbm.filter(date_applied__range=(monday2, monday1)).count()
    week3_b = vbm.filter(date_applied__range=(monday3, monday2)).count()
    week4_b = vbm.filter(date_applied__range=(monday4, monday3)).count()
    week5_b = vbm.filter(date_applied__range=(monday5, monday4)).count()
    week6_b = vbm.filter(date_applied__range=(monday6, monday5)).count()
    week7_b = vbm.filter(date_applied__range=(monday7, monday6)).count()
    week8_b = vbm.filter(date_applied__range=(monday8, monday7)).count()

    report_views_labels = [week8_date, week7_date, week6_date, week5_date, week4_date, week3_date, 'Last Week', 'This Week']

    report_views_data = [week8, week7, week6, week5, week4, week3, week2, week1]

    user_views_data = [week8_u, week7_u, week6_u, week5_u, week4_u, week3_u, week2_u, week1_u,]

    vacancy_bids_views_data = [week8_b, week7_b, week6_b, week5_b, week4_b, week3_b, week2_b, week1_b,]

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(pvr, 20)

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

    template = 'Profile/profile_viewed_report.html'
    context = {
            'pvr': pvr,
            'pvr_s': pvr_s,
            'pvr_count': pvr_count,
            'pvr_p': pvr_p,
            'pvr_p_count': pvr_p_count,
            'tlt': tlt,
            'alias': alias,
            'referral_code': referral_code,
            'report_views_data': report_views_data,
            'user_views_data': user_views_data,
            'vacancy_bids_views_data': vacancy_bids_views_data,
            'report_views_labels': report_views_labels,
            'pageitems': pageitems,
            'page_range': page_range
    }
    return render(request, template, context)


@login_required()
def IntroIntroductionView(request):

    template = 'Profile/intro_introduction.html'
    context = {}
    return render(request, template, context)


@login_required()
def IntroValidatingView(request):

    template = 'Profile/intro_validating.html'
    context = {}
    return render(request, template, context)


@login_required()
def IntroProfileView(request):

    template = 'Profile/intro_profile.html'
    context = {}
    return render(request, template, context)


@login_required()
def IntroCaptureExpreienceView(request):

    template = 'Profile/intro_capture_experience.html'
    context = {}
    return render(request, template, context)


@login_required()
def IntroCaptureSkillsView(request):

    template = 'Profile/intro_capture_skills.html'
    context = {}
    return render(request, template, context)


@login_required()
def IntroVacancyView(request):

    template = 'Profile/intro_vacancy.html'
    context = {}
    return render(request, template, context)


@login_required()
def IntroShortlistingView(request):

    template = 'Profile/intro_shortlisting.html'
    context = {}
    return render(request, template, context)


@login_required()
def IntroAssigningView(request):

    template = 'Profile/intro_assigning.html'
    context = {}
    return render(request, template, context)


@login_required()
def IntroPublicProfileView(request):

    template = 'Profile/intro_public_profile.html'
    context = {}
    return render(request, template, context)


@login_required()
def IntroManagingAccountView(request):

    template = 'Profile/intro_managing_account.html'
    context = {}
    return render(request, template, context)

@login_required()
def IntroBEPView(request):

    template = 'Profile/intro_bep.html'
    context = {}
    return render(request, template, context)

#>>>Contact details view for Assigned vacancies and interviews
@login_required()
@subscription(1)
def ContactDetailView(request, tlt, vac):
    pfl_qs = Profile.objects.get(alias = tlt)
    vac_qs = TalentRequired.objects.get(ref_no=vac)

    template = 'Profile/contact_details.html'
    context = {'pfl_qs': pfl_qs, 'vac_qs': vac_qs}
    return render(request, template, context)
#Contact details view for Assigned vacancies and interviews<<<


#>>> Workshop view for Talent
@login_required()
@subscription(1)
def TltWorkshopView(request):
    tlt=request.user
    wit_qs = WorkIssuedTo.objects.filter(talent=tlt).order_by('-date_create')
    #declined Vacancies
    wit_qsd = wit_qs.filter(Q(tlt_response='D'))
    #pending Vacancies
    wit_qsp = wit_qs.filter(Q(tlt_response='P') | Q(tlt_response='C'))
    #Accepted Vacancies
    wit_qsa = wit_qs.filter(Q(tlt_response='A'))
    wit_qsao = wit_qsa.filter(Q(assignment_complete_tlt=False) | Q(assignment_complete_emp=False))
    wit_qsac = wit_qsa.filter(Q(assignment_complete_tlt=True) | Q(assignment_complete_emp=True))

    template = 'Profile/workshop_tlt.html'
    context = {
        'wit_qsao': wit_qsao, 'wit_qsac': wit_qsac, 'wit_qsp': wit_qsp, 'wit_qsd': wit_qsd,
        }
    return render(request, template, context)


@login_required()
def TltVacancyComplete(request, wit):
    wit_qs = WorkIssuedTo.objects.filter(slug=wit)

    wit_qs.update(assignment_complete_tlt=True)

    return redirect(reverse('Profile:WorkshopTlt'))


@login_required()
def TltUpdateStatusRate(request, wit):
    wit_qs = get_object_or_404(WorkIssuedTo, slug=wit)
    ref = wit_qs.work.ref_no
    form = TalentRateForm(request.POST or None)

    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.vacancy = wit_qs.work
            new.talent = wit_qs.talent
            new.complete = True
            new.save()

            #average for company as a whole
            cmp_id = wit_qs.work.companybranch.company.id
            cmp = Enterprise.objects.get(id=cmp_id)
            cmpu = Enterprise.objects.filter(id=cmp_id)

            tctr = TalentRate.objects.filter(vacancy__companybranch__company=cmp)

            avg_1 = tctr.aggregate(c1=Avg('rate_1'))
            c1 = avg_1.get('c1')*100

            avg_2 = tctr.aggregate(c2=Avg('rate_2'))
            c2 = avg_2.get('c2')*100

            avg_3 = tctr.aggregate(c3=Avg('rate_3'))
            c3 = avg_3.get('c3')*100

            avg_4 = tctr.aggregate(c4=Avg('payment_time'))
            c4 = avg_4.get('c4')*100

            cnt = tctr.count()

            cmpu.update(rate_1=c1, rate_2=c2, rate_3=c3, rate_4=c4, rate_count=cnt)

            #average branch rating
            bch_id = wit_qs.work.companybranch.id
            bch = Branch.objects.get(id=bch_id)
            bchu = Branch.objects.filter(id=bch_id)

            trt = TalentRate.objects.filter(vacancy__companybranch=bch)

            avg_1 = trt.aggregate(a1=Avg('rate_1'))
            a1 = avg_1.get('a1')*100

            avg_2 = trt.aggregate(a2=Avg('rate_2'))
            a2 = avg_2.get('a2')*100

            avg_3 = trt.aggregate(a3=Avg('rate_3'))
            a3 = avg_3.get('a3')*100

            avg_4 = trt.aggregate(a4=Avg('payment_time'))
            a4 = avg_4.get('a4')*100

            cnt = trt.count()

            bchu.update(rate_1=a1, rate_2=a2, rate_3=a3, rate_4=a4, rate_count=cnt)

            wit_qs.tlt_rated=True
            wit_qs.save()

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Profile:WorkshopEmp')
            return HttpResponseRedirect(next_url)
    else:
        template = 'marketplace/rate_by_talent.html'
        context={'form': form, 'wit_qs': wit_qs,}
        return render(request, template, context)


@login_required()
def TltRatingView(request, wit):
    wit_qs = get_object_or_404(WorkIssuedTo,slug=wit)
    ref = wit_qs.work.ref_no
    tlt_qs = TalentRate.objects.get(vacancy__ref_no=ref)

    if wit_qs.emp_rated == True:
        emp_qs = VacancyRate.objects.get(vacancy__ref_no=ref)
    else:
        emp_qs = 'To be submitted'

    template = 'marketplace/rated_by_talent.html'
    context={'emp_qs': emp_qs, 'tlt_qs': tlt_qs,}
    return render(request, template, context)
#Workshop view for Talent<<<


#>>>Office view for Employer
@login_required()
@subscription(2)
def EmpWorkshopView(request):
    tlt=request.user
    wit_qs = WorkIssuedTo.objects.filter(work__requested_by=tlt).order_by('-date_create')
    #pending Vacancies
    wit_qsp = wit_qs.filter(Q(tlt_response='P') | Q(tlt_response='C'))
    #Accepted Vacancies
    wit_qsa = wit_qs.filter(Q(tlt_response='A'))
    wit_qsao = wit_qsa.filter(Q(assignment_complete_tlt=False) | Q(assignment_complete_emp=False))
    wit_qsac = wit_qsa.filter(Q(assignment_complete_tlt=True) | Q(assignment_complete_emp=True))

    template = 'Profile/workshop_emp.html'
    context = {
        'wit_qsao': wit_qsao, 'wit_qsac': wit_qsac, 'wit_qsp': wit_qsp,
        }
    return render(request, template, context)


@login_required()
def EmpVacancyComplete(request, wit):
    wit_qs = WorkIssuedTo.objects.filter(slug=wit)

    wit_qs.update(assignment_complete_emp=True)

    return redirect(reverse('Profile:WorkshopEmp'))


@login_required()
def EmpUpdateStatusRate(request, wit):
    wit_qs = get_object_or_404(WorkIssuedTo,slug=wit)
    ref = wit_qs.work.ref_no
    form = VacancyRateForm(request.POST or None)

    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.vacancy = wit_qs.work
            new.talent = wit_qs.talent
            new.complete = True
            new.save()

            #injecting average rating into profile table
            tlt = wit_qs.talent
            vrm = VacancyRate.objects.filter(talent=tlt)
            pfl = Profile.objects.filter(talent=tlt)

            avg_1 = vrm.aggregate(a1=Avg('rate_1'))
            a1 = avg_1.get('a1')*100

            avg_2 = vrm.aggregate(a2=Avg('rate_2'))
            a2 = avg_2.get('a2')*100

            avg_3 = vrm.aggregate(a3=Avg('rate_3'))
            a3 = avg_3.get('a3')*100

            cnt = vrm.count()

            pfl.update(rate_1=a1, rate_2=a2, rate_3=a3, rate_count=cnt)

            wit_qs.emp_rated=True
            wit_qs.save()

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Profile:WorkshopEmp')
            return HttpResponseRedirect(next_url)
    else:
        template = 'marketplace/rate_by_employer.html'
        context={'form': form, 'wit_qs': wit_qs,}
        return render(request, template, context)


@login_required()
def EmpRatingView(request, wit):
    wit_qs = get_object_or_404(WorkIssuedTo,slug=wit)
    ref = wit_qs.work.ref_no
    emp_qs = VacancyRate.objects.get(vacancy__ref_no=ref)

    if wit_qs.tlt_rated == True:
        tlt_qs = TalentRate.objects.get(vacancy__ref_no=ref)
    else:
        tlt_qs = 0

    template = 'marketplace/rated_by_employer.html'
    context={'emp_qs': emp_qs, 'tlt_qs': tlt_qs,}
    return render(request, template, context)
#Office view for Employer<<<


#This is the Dashboard view...
@login_required()
def ProfileHome(request):
    #>>>NetworkCard
    node = NtWk.objects.get(talent=request.user)
    get = lambda node_id: NtWk.objects.get(pk=node_id)
    list = NtWk.get_annotated_list(node, 5)
    tl = request.user
    tlt = tl.alias

    tlt_id = tl.id
    qs = ObjectViewed.objects.filter(object_id=tlt_id).exclude(user=tl)
    pvr_count = qs.filter(content_type__app_label="Profile").count()

    list_length = len(list)
    n=0
    lvl_1=0
    lvl_2=0
    lvl_3=0
    lvl_4=0
    lvl_5=0
    lvl_6=0

    for n in range(0,list_length):
        lvl = list[n][1]['level']
        if lvl == 0:
            pass
        elif lvl == 1:
            lvl_1 += 1
        elif lvl == 2:
            lvl_2 += 1
        elif lvl == 3:
            lvl_3 += 1
        elif lvl == 4:
            lvl_4 += 1
        elif lvl == 5:
            lvl_5 += 1
        n += 1

    tot = lvl_1 + lvl_2 + lvl_3 + lvl_4 + lvl_5
    #NetworkCard<<<

    #>>>WorkFlow Card
    talent = request.user
    if app_config.switch_confirmation == 'on':
        wf1 = Lecturer.objects.filter(Q(lecturer=talent) & Q(confirm__exact='S')).count()
        cm1 = ClassMates.objects.filter(Q(colleague=talent) & Q(confirm__exact='S')).count()
        wk1 = WorkColleague.objects.filter(Q(colleague_name=talent) & Q(confirm__exact='S')).count()
        spr1 = Superior.objects.filter(Q(superior_name=talent) & Q(confirm__exact='S')).count()
        wclr1 = WorkCollaborator.objects.filter(Q(collaborator_name=talent) & Q(confirm__exact='S')).count()
        wc1 = WorkClient.objects.filter(Q(client_name=talent) & Q(confirm__exact='S')).count()
    else:
        wf1 = Lecturer.objects.filter(confirm__exact='S').count()
        cm1 = ClassMates.objects.filter(confirm__exact='S').count()
        wk1 = WorkColleague.objects.filter(confirm__exact='S').count()
        spr1 = Superior.objects.filter(confirm__exact='S').count()
        wclr1 = WorkCollaborator.objects.filter(confirm__exact='S').count()
        wc1 = WorkClient.objects.filter(confirm__exact='S').count()

    total = wf1 + cm1 + wk1 + spr1 + wclr1 + wc1

    interview_qs = BidInterviewList.objects.all().select_related('scope')

    interviews_tlt = interview_qs.filter(Q(talent=talent) & Q(tlt_intcomplete=False) & ~Q(tlt_response='R'))

    interviews_tltc = interviews_tlt.count()

    interviews_emp = interview_qs.filter(Q(scope__requested_by=talent) & Q(emp_intcomplete=False))

    interviews_empc = interviews_emp.count()

    assigned_tlt_qs = WorkIssuedTo.objects.filter(Q(talent=talent))
    assigned_tlt = assigned_tlt_qs.filter(Q(tlt_response='P') | Q(tlt_response='C'))
    assigned_tltc = assigned_tlt.count()

    assigned_emp = WorkIssuedTo.objects.filter(Q(work__requested_by=talent) & Q(assignment_complete_emp=False))
    assigned_empc = assigned_emp.count()

    open_assignments_tltc = assigned_tlt_qs.filter(Q(tlt_response='A') & Q(assignment_complete_tlt=False)).count()

    open_assignments_empc = assigned_emp.filter(Q(tlt_response='A')).count()


    #talent interview information
    tlt_bil_qs = BidInterviewList.objects.filter(talent=talent)
    tlt_bil_qs_p = tlt_bil_qs.filter(Q(tlt_response='P') & Q(outcome='I')).count()
    tlt_bil_qs_a = tlt_bil_qs.filter(Q(tlt_response='A') &  Q(tlt_intcomplete=False)).count()
    tlt_bil_qs_d = tlt_bil_qs.filter(tlt_response='D').count()
    tlt_bil_qs_i = tlt_bil_qs.filter(tlt_intcomplete=True).count()

    #employer interview information
    emp_bil_qs = BidInterviewList.objects.filter(scope__requested_by=talent)
    emp_bil_qs_p = emp_bil_qs.filter(Q(tlt_response='P') & Q(outcome='I')).count()
    emp_bil_qs_a = emp_bil_qs.filter(Q(tlt_response='A') & Q(emp_intcomplete=False)).count()
    emp_bil_qs_d = emp_bil_qs.filter(tlt_response='D').count()
    emp_bil_qs_i = emp_bil_qs.filter(emp_intcomplete=True).count()

    #Employer assignments
    emp_wit = WorkIssuedTo.objects.filter(work__requested_by=talent)
    emp_wit_p = emp_wit.filter(tlt_response='P').count()
    emp_wit_a = emp_wit.filter(Q(tlt_response='A')).filter(Q(assignment_complete_emp=False)|Q(assignment_complete_emp=True)).filter(Q(assignment_complete_tlt=False)|Q(assignment_complete_tlt=True)).count()
    emp_wit_d = emp_wit.filter(tlt_response='D').count()
    emp_wit_c = emp_wit.filter(tlt_response='C').count()
    emp_wit_s = emp_wit.filter(Q(tlt_response='A') & Q(assignment_complete_emp=True) & Q(assignment_complete_tlt=True)).count()

    #Talent assignments
    tlt_wit = WorkIssuedTo.objects.filter(talent=talent)
    tlt_wit_p = tlt_wit.filter(tlt_response='P').count()
    tlt_wit_a = tlt_wit.filter(Q(tlt_response='A')).filter(Q(assignment_complete_emp=False)|Q(assignment_complete_emp=True)).filter(Q(assignment_complete_tlt=False)|Q(assignment_complete_tlt=True)).count()
    tlt_wit_d = tlt_wit.filter(tlt_response='D').count()
    tlt_wit_c = tlt_wit.filter(tlt_response='C').count()
    tlt_wit_s = tlt_wit.filter(Q(tlt_response='A') & Q(assignment_complete_tlt=True) & Q(assignment_complete_emp=True)).count()


    #WorkFlow Card<<<

    #>>>QuickAccess card
    pfl = Profile.objects.get(talent=talent)
    referral_code = Referral.objects.get(user=talent)

    #>>> Confirmation Summary
    #>>>As Confirmer
    conf_tot_c = int(0)
    conf_tot_r = int(0)
    conf_tot_y = int(0)
    conf_tot_s = int(0)
    conf_tot_y = int(0)

    edu_lect = Lecturer.objects.filter(lecturer=talent)

    edu_lect_r = edu_lect.filter(confirm="R").count()
    if edu_lect_r is not None:
        conf_tot_r += edu_lect_r

    edu_lect_y = edu_lect.filter(confirm="Y").count()
    if edu_lect_y is not None:
        conf_tot_y += edu_lect_y

    edu_lect_c = edu_lect.filter(confirm="C").count()
    if edu_lect_c is not None:
        conf_tot_c += edu_lect_c

    edu_lect_s = edu_lect.filter(confirm="S").count()
    if edu_lect_s is not None:
        conf_tot_s += edu_lect_s

    edu_lect_y = edu_lect.filter(confirm="Y").count()
    if edu_lect_y is not None:
        conf_tot_y += edu_lect_y

    edu_cm = ClassMates.objects.filter(colleague=talent)
    edu_cm_r = edu_cm.filter(confirm="R").count()
    if edu_cm_r is not None:
        conf_tot_r += edu_cm_r

    edu_cm_y = edu_cm.filter(confirm="Y").count()
    if edu_cm_y is not None:
        conf_tot_y += edu_cm_y

    edu_cm_c = edu_cm.filter(confirm="C").count()
    if edu_cm_c is not None:
        conf_tot_c += edu_cm_c

    edu_cm_s = edu_cm.filter(confirm="S").count()
    if edu_cm_s is not None:
        conf_tot_s += edu_cm_s

    edu_cm_y = edu_cm.filter(confirm="Y").count()
    if edu_cm_y is not None:
        conf_tot_y += edu_cm_y

    exp_clg = WorkColleague.objects.filter(colleague_name=talent)
    exp_clg_r = exp_clg.filter(confirm="R").count()
    if exp_clg_r is not None:
        conf_tot_r += exp_clg_r

    exp_clg_y = exp_clg.filter(confirm="Y").count()
    if exp_clg_y is not None:
        conf_tot_y += exp_clg_y

    exp_clg_c = exp_clg.filter(confirm="C").count()
    if exp_clg_c is not None:
        conf_tot_c += exp_clg_c

    exp_clg_s = exp_clg.filter(confirm="S").count()
    if exp_clg_s is not None:
        conf_tot_s += exp_clg_s

    exp_clg_y = exp_clg.filter(confirm="Y").count()
    if exp_clg_y is not None:
        conf_tot_y += exp_clg_y

    exp_sup = Superior.objects.filter(superior_name=talent)

    exp_sup_r = exp_sup.filter(confirm="R").count()
    if exp_sup_r is not None:
        conf_tot_r += exp_sup_r

    exp_sup_y = exp_sup.filter(confirm="Y").count()
    if exp_sup_y is not None:
        conf_tot_y += exp_sup_y

    exp_sup_c = exp_sup.filter(confirm="C").count()
    if exp_sup_c is not None:
        conf_tot_c += exp_sup_c

    exp_sup_s = exp_sup.filter(confirm="S").count()
    if exp_sup_s is not None:
        conf_tot_s += exp_sup_s

    exp_sup_y = exp_sup.filter(confirm="Y").count()
    if exp_sup_y is not None:
        conf_tot_y += exp_sup_y


    exp_clt = WorkClient.objects.filter(client_name=talent)

    exp_clt_r = exp_clt.filter(confirm="R").count()
    if exp_clt_r is not None:
        conf_tot_r += exp_clt_r

    exp_clt_y = exp_clt.filter(confirm="Y").count()
    if exp_clt_y is not None:
        conf_tot_y += exp_clt_y

    exp_clt_c = exp_clt.filter(confirm="C").count()
    if exp_clt_c is not None:
        conf_tot_c += exp_clt_c

    exp_clt_s = exp_clt.filter(confirm="S").count()
    if exp_clt_s is not None:
        conf_tot_s += exp_clt_s

    exp_clt_y = exp_clt.filter(confirm="Y").count()
    if exp_clt_y is not None:
        conf_tot_y += exp_clt_y

    exp_cbr = WorkCollaborator.objects.filter(collaborator_name=talent)

    exp_cbr_r = exp_cbr.filter(confirm="R").count()
    if exp_cbr_r is not None:
        conf_tot_r += exp_cbr_r

    exp_cbr_y = exp_cbr.filter(confirm="Y").count()
    if exp_cbr_y is not None:
        conf_tot_y += exp_cbr_y

    exp_cbr_c = exp_cbr.filter(confirm="C").count()
    if exp_cbr_c is not None:
        conf_tot_c += exp_cbr_c

    exp_cbr_s = exp_cbr.filter(confirm="S").count()
    if exp_cbr_s is not None:
        conf_tot_s += exp_cbr_s

    exp_cbr_y = exp_cbr.filter(confirm="Y").count()
    if exp_cbr_y is not None:
        conf_tot_y += exp_cbr_y
    #As Confirmer<<<

    #>>>As Requestioner
    req_tot_c = int(0)
    req_tot_r = int(0)
    req_tot_y = int(0)
    req_tot_s = int(0)
    req_tot_y = int(0)

    edu_req_lect = Lecturer.objects.filter(education__talent=talent)

    edu_req_lect_r = edu_req_lect.filter(confirm="R").count()
    if edu_req_lect_r is not None:
        req_tot_r += edu_req_lect_r

    edu_req_lect_y = edu_req_lect.filter(confirm="Y").count()
    if edu_req_lect_y is not None:
        req_tot_y += edu_req_lect_y

    edu_req_lect_c = edu_req_lect.filter(confirm="C").count()
    if edu_req_lect_c is not None:
        req_tot_c += edu_req_lect_c

    edu_req_lect_s = edu_req_lect.filter(confirm="S").count()
    if edu_req_lect_s is not None:
        req_tot_s += edu_req_lect_s

    edu_req_lect_y = edu_req_lect.filter(confirm="Y").count()
    if edu_req_lect_y is not None:
        req_tot_y += edu_req_lect_y


    edu_req_cm = ClassMates.objects.filter(education__talent=talent)
    edu_req_cm_r = edu_req_cm.filter(confirm="R").count()
    if edu_req_cm_r is not None:
        req_tot_r += edu_req_cm_r

    edu_req_cm_y = edu_req_cm.filter(confirm="Y").count()
    if edu_req_cm_y is not None:
        req_tot_y += edu_req_cm_y

    edu_req_cm_c = edu_req_cm.filter(confirm="C").count()
    if edu_req_cm_c is not None:
        req_tot_c += edu_req_cm_c

    edu_req_cm_s = edu_req_cm.filter(confirm="S").count()
    if edu_req_cm_s is not None:
        req_tot_s += edu_req_cm_s

    edu_req_cm_y = edu_req_cm.filter(confirm="Y").count()
    if edu_req_cm_y is not None:
        req_tot_y += edu_req_cm_y


    exp_req_clg = WorkColleague.objects.filter(experience__talent=talent)
    exp_req_clg_r = exp_req_clg.filter(confirm="R").count()
    if exp_req_clg_r is not None:
        req_tot_r += exp_req_clg_r

    exp_req_clg_y = exp_req_clg.filter(confirm="Y").count()
    if exp_req_clg_y is not None:
        req_tot_y += exp_req_clg_y

    exp_req_clg_c = exp_req_clg.filter(confirm="C").count()
    if exp_req_clg_c is not None:
        req_tot_c += exp_req_clg_c

    exp_req_clg_s = exp_req_clg.filter(confirm="S").count()
    if exp_req_clg_s is not None:
        req_tot_s += exp_req_clg_s

    exp_req_clg_y = exp_req_clg.filter(confirm="Y").count()
    if exp_req_clg_y is not None:
        req_tot_y += exp_req_clg_y


    exp_req_sup = Superior.objects.filter(experience__talent=talent)
    exp_req_sup_r = exp_req_sup.filter(confirm="R").count()
    if exp_req_sup_r is not None:
        req_tot_r += exp_req_sup_r

    exp_req_sup_y = exp_req_sup.filter(confirm="Y").count()
    if exp_req_sup_y is not None:
        req_tot_y += exp_req_sup_y

    exp_req_sup_c = exp_req_sup.filter(confirm="C").count()
    if exp_req_sup_c is not None:
        req_tot_c += exp_req_sup_c

    exp_req_sup_s = exp_req_sup.filter(confirm="S").count()
    if exp_req_sup_s is not None:
        req_tot_s += exp_req_sup_s

    exp_req_sup_y = exp_req_sup.filter(confirm="Y").count()
    if exp_req_sup_y is not None:
        req_tot_y += exp_req_sup_y


    exp_req_clt = WorkClient.objects.filter(experience__talent=talent)

    exp_req_clt_y = exp_req_clt.filter(confirm="R").count()
    if exp_req_clt_y is not None:
        req_tot_y += exp_req_clt_y

    exp_req_clt_r = exp_req_clt.filter(confirm="Y").count()
    if exp_req_clt_r is not None:
        req_tot_r += exp_req_clt_r

    exp_req_clt_c = exp_req_clt.filter(confirm="C").count()
    if exp_req_clt_c is not None:
        req_tot_c += exp_req_clt_c

    exp_req_clt_s = exp_req_clt.filter(confirm="S").count()
    if exp_req_clt_s is not None:
        req_tot_s += exp_req_clt_s

    exp_req_clt_y = exp_req_clt.filter(confirm="Y").count()
    if exp_req_clt_y is not None:
        req_tot_y += exp_req_clt_y


    exp_req_cbr = WorkCollaborator.objects.filter(experience__talent=talent)
    exp_req_cbr_r = exp_req_cbr.filter(confirm="R").count()
    if exp_req_cbr_r is not None:
        req_tot_r += exp_req_cbr_r

    exp_req_cbr_y = exp_req_cbr.filter(confirm="Y").count()
    if exp_req_cbr_y is not None:
        req_tot_y += exp_req_cbr_y

    exp_req_cbr_c = exp_req_cbr.filter(confirm="C").count()
    if exp_req_cbr_c is not None:
        req_tot_c += exp_req_cbr_c

    exp_req_cbr_s = exp_req_cbr.filter(confirm="S").count()
    if exp_req_cbr_s is not None:
        req_tot_s += exp_req_cbr_s

    exp_req_cbr_y = exp_req_cbr.filter(confirm="Y").count()
    if exp_req_cbr_y is not None:
        req_tot_y += exp_req_cbr_y
    #As Requestioner<<<
    #Confirmation Summary<<<

    fm = request.user.free_month

    instance2 = ExpandedView.objects.get(talent=request.user)
    list_view = instance2.intro_walkthrough
    fse = instance2.trial_expired


    template = 'Profile/profile_home.html'
    context = {
    'wf1': wf1, 'tlt': tlt, 'pvr_count': pvr_count, 'total': total, 'interviews_tlt': interviews_tlt, 'interviews_emp': interviews_emp, 'interviews_empc': interviews_empc, 'interviews_tltc': interviews_tltc, 'assigned_tlt': assigned_tlt, 'assigned_emp': assigned_emp, 'assigned_tltc': assigned_empc, 'assigned_empc': assigned_tltc, 'open_assignments_tltc': open_assignments_tltc, 'open_assignments_empc': open_assignments_empc, 'lvl_1': lvl_1, 'lvl_2': lvl_2, 'lvl_3': lvl_3, 'lvl_4': lvl_4,'lvl_5': lvl_5, 'tot': tot, 'pfl': pfl, 'referral_code': referral_code, 'conf_tot_c': conf_tot_c, 'conf_tot_r': conf_tot_r, 'conf_tot_s': conf_tot_s, 'req_tot_c': req_tot_c, 'req_tot_r': req_tot_r, 'req_tot_s': req_tot_s, 'req_tot_y': req_tot_y, 'conf_tot_y': conf_tot_y, 'list_view': list_view, 'tlt_bil_qs_p': tlt_bil_qs_p, 'tlt_bil_qs_a': tlt_bil_qs_a, 'tlt_bil_qs_d': tlt_bil_qs_d, 'tlt_bil_qs_i': tlt_bil_qs_i, 'emp_bil_qs_p': emp_bil_qs_p, 'emp_bil_qs_a': emp_bil_qs_a, 'emp_bil_qs_d': emp_bil_qs_d, 'emp_bil_qs_i': emp_bil_qs_i,
    'emp_wit_p': emp_wit_p, 'emp_wit_a': emp_wit_a, 'emp_wit_d': emp_wit_d, 'emp_wit_c': emp_wit_c, 'emp_wit_s': emp_wit_s,
    'tlt_wit_p': tlt_wit_p, 'tlt_wit_a': tlt_wit_a, 'tlt_wit_d': tlt_wit_d, 'tlt_wit_c': tlt_wit_c, 'tlt_wit_s': tlt_wit_s,
    'fse': fse, "fm": fm,
    }
    return render(request, template, context)


@login_required()
def IntroCloseView(request):
    if request.method == 'POST':
        instance2 = ExpandedView.objects.get(talent=request.user)
        list_view = instance2.intro_walkthrough
        if list_view == True:
            instance2.intro_walkthrough = False
        elif list_view == False:
            instance2.intro_walkthrough = True
        instance2.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def FreeMonthExpiredView(request):
    if request.method == 'POST':
        instance2 = ExpandedView.objects.get(talent=request.user)
        list_view = instance2.trial_expired
        if list_view == False:
            instance2.trial_expired = True
        instance2.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
@subscription(1)
def AssignmentAcceptView(request, slug):
    assignment = WorkIssuedTo.objects.filter(slug=slug)
    assignment.update(tlt_response='A', tlt_response_date=timezone.now())#6

    tlt = assignment[0].talent
    vac = assignment[0].work

    TalentRequired.objects.filter(Q(ref_no=vac.ref_no)).update(vac_wkfl='A', offer_status='C')#5

    bsl_qs = BidShortList.objects.filter(scope=vac)
    bsl_qs.filter(talent=tlt).update(status='A')#3
    bsl_qs.filter(~Q(talent=tlt)).update(status='R')#4

    bil = BidInterviewList.objects.filter(Q(talent=tlt) & Q(scope=vac))
    if bil:
        bil.update(outcome='A', tlt_intcomplete=True, emp_intcomplete=True)#7
        if bil[0].tlt_response == 'P':
            bil.update(tlt_response = 'Z')

    wb_qs = WorkBid.objects.filter(Q(work=vac))
    if wb_qs:
        wb_qs.filter(Q(talent=tlt)).update(bidreview='A')#1
        wb_qs.filter(~Q(talent=tlt)).update(bidreview='R')#2

    return redirect(reverse('Profile:ProfileHome')+'#Assignment')


@login_required()
@subscription(1)
def AssignmentDeclineView(request, slug):
    assignment = WorkIssuedTo.objects.filter(slug=slug)
    assignment.update(tlt_response='D', tlt_response_date=timezone.now())#5
    instance = get_object_or_404(WorkIssuedTo, slug=slug)

    tlt = assignment[0].talent
    vac = assignment[0].work

    form = AssignmentDeclineReasonsForm(request.POST or None, instance = instance)

    if request.method =='POST':
        if form.is_valid():
            new=form.save(commit=False)
            new.save()

            TalentRequired.objects.filter(Q(ref_no=vac.ref_no)).update(vac_wkfl='I', offer_status='O')#3
            BidShortList.objects.filter(Q(talent=tlt) & Q(scope=vac)).update(status='D')#2
            BidInterviewList.objects.filter(Q(talent=tlt) & Q(scope=vac)).update(outcome='D')#5

            wb_qs = WorkBid.objects.filter(Q(talent=tlt) & Q(work=vac))
            if wb_qs:
                wb_qs.update(bidreview='D')#1

            return redirect(reverse('Profile:ProfileHome')+'#Assignments')
    else:
        template = 'marketplace/assignment_decline_reasons.html'
        context = {'instance': instance, 'form': form,}
        return render(request, template, context)


@login_required()
@subscription(2)
def AssignmentReAssign(request, slug):
    assignment = WorkIssuedTo.objects.filter(slug=slug).update(assignment_complete_emp=True)
    instance = WorkIssuedTo.objects.get(slug=slug)

    return redirect(reverse('MarketPlace:InterviewList', kwargs={'vac':instance.work.ref_no}))


@login_required()
@subscription(1)
def AssignmentClarifyView(request, wit):
    assignment = WorkIssuedTo.objects.filter(slug=wit)
    assignment.update(tlt_response='C', tlt_response_date=timezone.now())
    instance = get_object_or_404(WorkIssuedTo, slug=wit)

    form = AssignmentClarifyForm(request.POST or None, instance = instance)

    if request.method =='POST':
        if form.is_valid():
            new=form.save(commit=False)
            new.save()

            #>>>email
            context = {'form': form, 'instance': instance, 'user_email': instance.work.requested_by.email }
            html_message = render_to_string('Profile/email_vac_clarification_text.html', context).strip()

            message = Mail(
                from_email = (settings.SENDGRID_FROM_EMAIL, 'MyWeXlog Clarification Required'),
                to_emails = instance.work.requested_by.email,
                subject = f"{instance.work.title}: Clarification Requested from {instance.talent.alias}",
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
            #template = 'Profile/email_vac_clarification.html'
            #return render(request, template, context)
            #<<<email
            return  redirect(reverse('Profile:ProfileHome')+'#Assignments')
    else:
        template = 'marketplace/assignment_clarification.html'
        context = {'instance': instance, 'form': form,}
        return render(request, template, context)


@login_required()
@subscription(1)
def InterviewAcceptView(request, int_id):
    bil_qs = BidInterviewList.objects.filter(pk=int_id)
    bil_qs.update(tlt_response='A', tlt_reponded=timezone.now())#1

    tlt = bil_qs[0].talent
    vac = bil_qs[0].scope

    wb_qs = WorkBid.objects.filter(Q(talent=tlt) & Q(work=vac))
    if wb_qs:
        wb_qs.update(bidreview='I')#2

    return redirect(reverse('Profile:ProfileHome')+ '#Interview')


@login_required()
@subscription(1)
def int_accept(request, int_id):
    '''View for button in the candidate history template'''
    bil_qs = BidInterviewList.objects.filter(pk=int_id)
    bil_qs.update(tlt_response='A', tlt_reponded=timezone.now())#1

    tlt = bil_qs[0].talent
    vac = bil_qs[0].scope
    als = tlt.alias

    wb_qs = WorkBid.objects.filter(Q(talent=tlt) & Q(work=vac))
    if wb_qs:
        wb_qs.update(bidreview='I')#2

    return redirect(reverse('MarketPlace:TalentInterviewHistory', kwargs={'tlt':als}))

@login_required()
@subscription(1)
def InterviewDeclineView(request, int_id):
    bil_qs = BidInterviewList.objects.filter(pk=int_id)
    bil_qs.update(tlt_response='D', tlt_intcomplete=True, tlt_reponded=timezone.now(), outcome='D')#1

    tlt = bil_qs[0].talent
    vac = bil_qs[0].scope
    wb_qs = WorkBid.objects.filter(Q(talent=tlt) & Q(work=vac))#3
    BidShortList.objects.filter(Q(talent=tlt) & Q(scope=vac)).update(status='D')

    if wb_qs:
        wb_qs.update(bidreview='D')#2

    return redirect(reverse('MarketPlace:InterviewDecline', kwargs={'int_id':int_id}))


@login_required()
@subscription(1)
def int_decline(request, int_id):
    '''Button in the Candidate History to Decline an Interview'''
    bil_qs = BidInterviewList.objects.filter(pk=int_id)
    bil_qs.update(tlt_response='D', tlt_intcomplete=True, tlt_reponded=timezone.now(), outcome='D')#1

    tlt = bil_qs[0].talent
    als = tlt.alias
    vac = bil_qs[0].scope
    wb_qs = WorkBid.objects.filter(Q(talent=tlt) & Q(work=vac))#3
    BidShortList.objects.filter(Q(talent=tlt) & Q(scope=vac)).update(status='D')

    if wb_qs:
        wb_qs.update(bidreview='D')#2

    return redirect(reverse('MarketPlace:TalentInterviewHistory', kwargs={'tlt':als}))


@login_required()
@subscription(2)
def InterviewTltRemove(request, tlt):
    interview = BidInterviewList.objects.filter(talent__alias=tlt).update(emp_intcomplete=True, outcome='D')

    return redirect(reverse('Profile:ProfileHome')+'#Interview')


@login_required()
@subscription(2)
def InterviewTltComplete(request, int_id):
    interview = BidInterviewList.objects.filter(pk=int_id).update(tlt_intcomplete=True)

    return redirect(reverse('Profile:ProfileHome')+ '#Interview')


@login_required()
@csp_exempt
def BriefCareerHistoryView(request):
    talent=request.user

    skills_list = SkillTag.objects.filter(skills_utilised__talent=talent).distinct('skill').order_by('skill')

    form = BriefCareerHistoryForm(request.POST or None)

    history = BriefCareerHistory.objects.filter(talent=talent)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.save()
            form.save_m2m()
            if 'another' in request.POST:
                response = redirect('Profile:History')
                return response
            elif 'done' in request.POST:
                response = redirect(reverse('Profile:ProfileView')+'#History')
                return response
        else:
            template = 'Profile/brief_career_history.html'
            context = {'form': form, 'history': history, 'skills_list': skills_list}
            response = render(request, template, context)
            return response
    else:
        template = 'Profile/brief_career_history.html'
        context = {'form': form, 'history': history, 'skills_list': skills_list}
        response = render(request, template, context)
        return response


@login_required()
@csp_exempt
def BriefHistoryEditView(request, bch):
    talent=request.user
    instance = BriefCareerHistory.objects.get(slug=bch)

    skills_list = SkillTag.objects.filter(skills_utilised__talent=talent).distinct('skill').order_by('skill')

    form = BriefCareerHistoryForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.save()
            form.save_m2m()
            response = redirect(reverse('Profile:ProfileView')+"#History")
            return response

    else:
        template = 'Profile/brief_career_history_edit.html'
        context = {'form': form, 'bch': bch, 'skills_list': skills_list, 'instance': instance}
        response = render(request, template, context)
        return response


@login_required()
def BriefHistoryDeleteView(request, bch):
    talent=request.user
    instance = BriefCareerHistory.objects.get(slug=bch)

    if instance.talent == request.user:
        if request.method =='POST':
            instance.delete()
            return redirect(reverse('Profile:ProfileView')+'#History')
    else:
        raise PermissionDenied


@login_required()
def BriefHistoryAddDeleteView(request, bch):
    talent=request.user
    instance = BriefCareerHistory.objects.get(slug=bch)

    if instance.talent == request.user:
        if request.method =='POST':
            instance.delete()
            return redirect(reverse('Profile:History')+'#History')
    else:
        raise PermissionDenied


@login_required()
def ResignedView(request, bch, tlt):
    r_from = get_object_or_404(BriefCareerHistory, slug=bch)
    form = ResignedForm(request.POST or None, instance=r_from)
    if request.method == 'POST':
        new = form.save(commit=False)
        new.save()
        return redirect(reverse('Profile:ProfileView')+'#History')

    else:
        template = 'Profile/brief_career_resigned.html'
        context = {'form': form}
        return render (request, template, context)


@login_required()
def ConfirmView(request):

    if app_config.switch_confirmation == 'off':
        wf1 = Lecturer.objects.filter(confirm__exact='S')
        cm1 = ClassMates.objects.filter(confirm__exact='S')
        wk1 = WorkColleague.objects.filter(confirm__exact='S')
        spr1 = Superior.objects.filter(confirm__exact='S')
        wclr1 = WorkCollaborator.objects.filter(confirm__exact='S')
        wc1 = WorkClient.objects.filter(confirm__exact='S')
    else:
        talent = request.user
        wf1 = Lecturer.objects.filter(Q(lecturer=talent) & Q(confirm__exact='S'))
        cm1 = ClassMates.objects.filter(Q(colleague=talent) & Q(confirm__exact='S'))
        wk1 = WorkColleague.objects.filter(Q(colleague_name=talent) & Q(confirm__exact='S'))
        spr1 = Superior.objects.filter(Q(superior_name=talent) & Q(confirm__exact='S'))
        wclr1 = WorkCollaborator.objects.filter(Q(collaborator_name=talent) & Q(confirm__exact='S'))
        wc1 = WorkClient.objects.filter(Q(client_name=talent) & Q(confirm__exact='S'))

    template = 'Profile/experience_confirm.html'
    context = {
            'wf1': wf1, 'cm1': cm1, 'wk1': wk1, 'spr1': spr1, 'wclr1': wclr1, 'wc1': wc1
    }
    return render(request, template, context)


#>>>Education-Lecturer
@login_required()
def LecturerConfirmView(request, pk):
    if request.method == 'POST':
        info = Lecturer.objects.get(pk=pk)
        info.confirm = 'C'
        info.date_confirmed = timezone.now().date()
        info.save()
        edu = WorkExperience.objects.get(pk=info.education.id)
        edu.score += lecturer_score
        edu.save()
    return redirect(reverse('Profile:Confirm')+'#Lecturer')


@login_required()
def LecturerRejectView(request, pk):
    if request.method == 'POST':
        info = Lecturer.objects.get(pk=pk)
        info.confirm = 'R'
        info.date_confirmed = timezone.now().date()
        info.save()
    return redirect(reverse('Profile:Confirm')+'#Lecturer')


@login_required()
def LecturerWrongPersonView(request, pk):
    if request.method == 'POST':
        info = Lecturer.objects.get(pk=pk)
        info.date_confirmed = timezone.now().date()
        info.confirm = 'Y'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#Lecturer')


@login_required()
def LecturerCommentView(request, lct):
    info = get_object_or_404(Lecturer, slug=lct)
    form = LecturerCommentForm(request.POST or None, instance=info)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.date_confirmed = timezone.now().date()
            new.save()
            if new.confirm == 'C':
                edu = WorkExperience.objects.get(pk=info.education.id)
                edu.score += lecturer_score
                edu.save()
            else:
                pass
            return redirect(reverse('Profile:Confirm')+'#Lecturer')
        else:
            template ='talenttrack/confirm_comments.html'
            context = {'form': form, 'info': info}
            return render(request, template, context)
    else:
        template ='talenttrack/confirm_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)

@login_required()
def LecturerEditView(request, lct):
    info = get_object_or_404(Lecturer, slug=lct)
    form = LecturerCommentForm(request.POST or None, instance=info)

    original = info.confirm

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.date_confirmed = timezone.now().date()
            new.save()
            if new.confirm == original:
                pass
            elif original =='S':
                if new.confirm == "R":
                    pass
                else:
                    edu = WorkExperience.objects.get(pk=info.education.id)
                    edu.score += lecturer_score
                    edu.save()
            elif original != 'S':
                if new.confirm == 'C':
                    edu = WorkExperience.objects.get(pk=info.education.id)
                    edu.score += lecturer_score
                    edu.save()
                else:
                    edu = WorkExperience.objects.get(pk=info.education.id)
                    edu.score -= lecturer_score
                    edu.save()
            return redirect(reverse('Talent:CAsLectList'))
        else:
            template ='talenttrack/confirm_comments.html'
            context = {'form': form, 'info': info}
            return render(request, template, context)
    else:
        template ='talenttrack/confirm_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)
#>>>Education-Lecturer


#>>>Education-ClassMate
@login_required()
def ClassMatesConfirmView(request, pk):
    if request.method == 'POST':
        info = ClassMates.objects.get(pk=pk)
        info.confirm = 'C'
        info.save()
        edu = WorkExperience.objects.get(pk=info.education.id)
        edu.score += classmate_score
        edu.save()
    return redirect(reverse('Profile:Confirm')+'#ClassMates')


@login_required()
def ClassMatesRejectView(request, pk):
    if request.method == 'POST':
        info = ClassMates.objects.get(pk=pk)
        info.confirm = 'R'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#ClassMates')


@login_required()
def ClassMatesCommentView(request, cmt):
    info = get_object_or_404(ClassMates, slug=cmt)
    form = ClassMatesCommentForm(request.POST or None, instance=info)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            if new.confirm == 'C':
                edu = WorkExperience.objects.get(pk=info.education.id)
                edu.score += classmate_score
                edu.save()
            else:
                pass
            return redirect(reverse('Profile:Confirm')+'#ClassMates')
        else:
            template ='talenttrack/confirm_comments.html'
            context = {'form': form, 'info': info}
            return render(request, template, context)
    else:
        template ='talenttrack/confirm_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)


@login_required()
def ClassMatesEditView(request, cmt):
    info = get_object_or_404(ClassMates, slug=cmt)
    form = ClassMatesCommentForm(request.POST or None, instance=info)

    original = info.confirm

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.date_confirmed = timezone.now().date()
            new.save()
            if new.confirm == original:
                pass
            elif original =='S':
                if new.confirm == "R":
                    pass
                else:
                    edu = WorkExperience.objects.get(pk=info.education.id)
                    edu.score += classmate_score
                    edu.save()
            elif original != 'S':
                if new.confirm == 'C':
                    edu = WorkExperience.objects.get(pk=info.education.id)
                    edu.score += classmate_score
                    edu.save()
                else:
                    edu = WorkExperience.objects.get(pk=info.education.id)
                    edu.score -= classmate_score
                    edu.save()
            return redirect(reverse('Talent:CAsCmList'))
        else:
            template ='talenttrack/confirm_comments.html'
            context = {'form': form, 'info': info}
            return render(request, template, context)
    else:
        template ='talenttrack/confirm_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)


@login_required()
def ClassMatesWrongPersonView(request, pk):
    if request.method == 'POST':
        info = ClassMates.objects.get(pk=pk)
        info.confirm = 'Y'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#ClassMates')
#<<<Education-ClassMate


#>>>Experience: Colleague
@login_required()
def ColleagueConfirmView(request, pk):
    if request.method == 'POST':
        info = WorkColleague.objects.get(pk=pk)
        info.confirm = 'C'
        info.save()
        exp = WorkExperience.objects.get(pk=info.experience.id)
        exp.score += colleague_score
        exp.save()

    return redirect(reverse('Profile:Confirm')+'#Colleague')


@login_required()
def ColleagueRejectView(request, pk):
    if request.method == 'POST':
        info = WorkColleague.objects.get(pk=pk)
        info.confirm = 'R'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#Colleague')


@login_required()
def ColleagueWrongPersonView(request, pk):
    if request.method == 'POST':
        info = WorkColleague.objects.get(pk=pk)
        info.confirm = 'Y'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#Colleague')


@login_required()
def ColleagueCommentView(request, clg):
    info = get_object_or_404(WorkColleague, slug=clg)
    form = WorkColleagueConfirmForm(request.POST or None, instance=info)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            if new.confirm == 'C':
                exp = WorkExperience.objects.get(pk=info.experience.id)
                exp.score += colleague_score
                exp.save()
            else:
                pass
            return redirect(reverse('Profile:Confirm')+'#Colleague')
        else:
            template ='talenttrack/confirm_exp_comments.html'
            context = {'form': form, 'info': info}
            return render(request, template, context)
    else:
        template ='talenttrack/confirm_exp_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)


@login_required()
def ColleagueEditView(request, clg):
    info = get_object_or_404(WorkColleague, slug=clg)
    form = WorkColleagueConfirmForm(request.POST or None, instance=info)

    original = info.confirm

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.date_confirmed = timezone.now().date()
            new.save()
            if new.confirm == original:
                pass
            elif original =='S':
                if new.confirm == "R":
                    pass
                else:
                    edu = WorkExperience.objects.get(pk=info.experience.id)
                    edu.score += classmate_score
                    edu.save()
            elif original != 'S':
                if new.confirm == 'C':
                    edu = WorkExperience.objects.get(pk=info.experience.id)
                    edu.score += classmate_score
                    edu.save()
                else:
                    edu = WorkExperience.objects.get(pk=info.experience.id)
                    edu.score -= classmate_score
                    edu.save()
            return redirect(reverse('Talent:CAsClgList'))
        else:
            template ='talenttrack/confirm_exp_comments.html'
            context = {'form': form, 'info': info}
            return render(request, template, context)
    else:
        template ='talenttrack/confirm_exp_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)
#>>>Experience: Colleague


#>>>Experience: Superior
@login_required()
def SuperiorConfirmView(request, pk):
    if request.method == 'POST':
        info = Superior.objects.get(pk=pk)
        info.confirm = 'C'
        info.save()
        exp = WorkExperience.objects.get(pk=info.experience.id)
        exp.score += superior_score
        exp.save()

    return redirect(reverse('Profile:Confirm')+'#Superior')


@login_required()
def SuperiorRejectView(request, pk):
    if request.method == 'POST':
        info = Superior.objects.get(pk=pk)
        info.confirm = 'R'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#Superior')


@login_required()
def SuperiorCommentView(request, spr):
    info = get_object_or_404(Superior, slug=spr)
    form = SuperiorConfirmForm(request.POST or None, instance=info)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            if new.confirm == 'C':
                exp = WorkExperience.objects.get(pk=info.experience.id)
                exp.score += superior_score
                exp.save()
            else:
                pass
            return redirect(reverse('Profile:Confirm')+'#Superior')
        else:
            template ='talenttrack/confirm_exp_comments.html'
            context = {'form': form, 'info': info}
            return render(request, template, context)
    else:
        template ='talenttrack/confirm_exp_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)


@login_required()
def SuperiorEditView(request, spr):
    info = get_object_or_404(Superior, slug=spr)
    form = SuperiorConfirmForm(request.POST or None, instance=info)

    original = info.confirm

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.date_confirmed = timezone.now().date()
            new.save()
            if new.confirm == original:
                pass
            elif original =='S':
                if new.confirm == "R":
                    pass
                else:
                    edu = WorkExperience.objects.get(pk=info.experience.id)
                    edu.score += superior_score
                    edu.save()
            elif original != 'S':
                if new.confirm == 'C':
                    edu = WorkExperience.objects.get(pk=info.experience.id)
                    edu.score += superior_score
                    edu.save()
                else:
                    edu = WorkExperience.objects.get(pk=info.experience.id)
                    edu.score -= superior_score
                    edu.save()
            return redirect(reverse('Talent:CAsSupList'))
        else:
            template ='talenttrack/confirm_exp_comments.html'
            context = {'form': form, 'info': info}
            return render(request, template, context)
    else:
        template ='talenttrack/confirm_exp_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)


@login_required()
def SuperiorWrongPersonView(request, pk):
    if request.method == 'POST':
        info = Superior.objects.get(pk=pk)
        info.confirm = 'Y'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#Superior')
#<<<Experience:Superior


#>>>Experience:Collaborator
@login_required()
def CollaboratorConfirmView(request, pk):
    if request.method == 'POST':
        info = WorkCollaborator.objects.get(pk=pk)
        info.confirm = 'C'
        info.save()
        exp = WorkExperience.objects.get(pk=info.experience.id)
        exp.score += collaborator_score
        exp.save()

    return redirect(reverse('Profile:Confirm')+'#Collaborator')


@login_required()
def CollaboratorRejectView(request, pk):
    if request.method == 'POST':
        info = WorkCollaborator.objects.get(pk=pk)
        info.confirm = 'R'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#Collaborator')


@login_required()
def CollaboratorCommentView(request, clb):
    info = get_object_or_404(WorkCollaborator, slug=clb)
    form = WorkCollaboratorConfirmForm(request.POST or None, instance=info)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            if new.confirm == 'C':
                exp = WorkExperience.objects.get(pk=info.experience.id)
                exp.score += collaborator_score
                exp.save()
            else:
                pass
            return redirect(reverse('Profile:Confirm')+'#Collaborator')
        else:
            template ='talenttrack/confirm_exp_comments.html'
            context = {'form': form, 'info': info}
            return render(request, template, context)
    else:
        template ='talenttrack/confirm_exp_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)


@login_required()
def CollaboratorEditView(request, clb):
    info = get_object_or_404(WorkCollaborator, slug=clb)
    form = WorkCollaboratorConfirmForm(request.POST or None, instance=info)

    original = info.confirm

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.date_confirmed = timezone.now().date()
            new.save()
            if new.confirm == original:
                pass
            elif original =='S':
                if new.confirm == "R":
                    pass
                else:
                    edu = WorkExperience.objects.get(pk=info.experience.id)
                    edu.score += collaborator_score
                    edu.save()
            elif original != 'S':
                if new.confirm == 'C':
                    edu = WorkExperience.objects.get(pk=info.experience.id)
                    edu.score += collaborator_score
                    edu.save()
                else:
                    edu = WorkExperience.objects.get(pk=info.experience.id)
                    edu.score -= collaborator_score
                    edu.save()
            return redirect(reverse('Talent:CAsCbrList'))
        else:
            template ='talenttrack/confirm_exp_comments.html'
            context = {'form': form, 'info': info}
            return render(request, template, context)
    else:
        template ='talenttrack/confirm_exp_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)


@login_required()
def CollaboratorWrongPersonView(request, pk):
    if request.method == 'POST':
        info = WorkCollaborator.objects.get(pk=pk)
        info.confirm = 'Y'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#Collaborator')
#<<<Experience: Collaborator


#>>> Experience: Client
@login_required()
def ClientConfirmView(request, pk):
    if request.method == 'POST':
        info = WorkClient.objects.get(pk=pk)
        info.confirm = 'C'
        info.save()
        exp = WorkExperience.objects.get(pk=info.experience.id)
        exp.score += client_score
        exp.save()

    return redirect(reverse('Profile:Confirm')+'#Client')


@login_required()
def ClientRejectView(request, pk):
    if request.method == 'POST':
        info = WorkClient.objects.get(pk=pk)
        info.confirm = 'R'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#Client')


@login_required()
def ClientCommentView(request, wkc):
    info = get_object_or_404(WorkClient, slug=wkc)
    form = WorkClientConfirmForm(request.POST or None, instance=info)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            if new.confirm == 'C':
                exp = WorkExperience.objects.get(pk=info.experience.id)
                exp.score += client_score
                exp.save()
            else:
                pass
            return redirect(reverse('Profile:Confirm')+'#Client')
        else:
            template ='talenttrack/confirm_exp_comments.html'
            context = {'form': form, 'info': info}
            return render(request, template, context)
    else:
        template ='talenttrack/confirm_exp_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)


@login_required()
def ClientEditView(request, wkc):
    info = get_object_or_404(WorkClient, slug=wkc)
    form = WorkClientConfirmForm(request.POST or None, instance=info)

    original = info.confirm

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.date_confirmed = timezone.now().date()
            new.save()
            if new.confirm == original:
                pass
            elif original =='S':
                if new.confirm == "R":
                    pass
                else:
                    edu = WorkExperience.objects.get(pk=info.experience.id)
                    edu.score += client_score
                    edu.save()
            elif original != 'S':
                if new.confirm == 'C':
                    edu = WorkExperience.objects.get(pk=info.experience.id)
                    edu.score += client_score
                    edu.save()
                else:
                    edu = WorkExperience.objects.get(pk=info.experience.id)
                    edu.score -= client_score
                    edu.save()
            return redirect(reverse('Talent:CAsCltList'))
        else:
            template ='talenttrack/confirm_exp_comments.html'
            context = {'form': form, 'info': info}
            return render(request, template, context)
    else:
        template ='talenttrack/confirm_exp_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)


@login_required()
def ClientWrongPersonView(request, pk):
    if request.method == 'POST':
        info = WorkClient.objects.get(pk=pk)
        info.confirm = 'Y'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#Client')
#<<< Experience: Client


#>>> Pre-Experience: Confirm
@login_required()
def PreColleagueConfirmView(request, pk):
    if request.method == 'POST':
        info = WorkClient.objects.get(pk=pk)
        info.confirm = 'C'
        info.save()
        exp = PreLoggedExperience.objects.get(pk=info.pre_experience.id)
        exp.score += colleague_score
        exp.save()

    return redirect(reverse('Profile:Confirm')+'#PreColleague')


@login_required()
def PreColleagueRejectView(request, pk):
    if request.method == 'POST':
        info = PreColleague.objects.get(pk=pk)
        info.confirm = 'R'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#PreColleague')


@login_required()
def PreColleagueCommentView(request, pk):
    info = get_object_or_404(PreColleague, pk=pk)
    form = ClassMatesCommentForm(request.POST or None, instance=info)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            if new.confirm == 'C':
                exp = PreLoggedExperience.objects.get(pk=info.pre_experience.id)
                exp.score += pre_colleague_score
                exp.save()
            else:
                pass

            return redirect(reverse('Profile:Confirm')+'#PreColleague')

    else:
        template ='talenttrack/confirm_exp_comments.html'
        context = {'form': form, 'info': info}
        return render(request, template, context)


@login_required()
def PreColleagueWrongPersonView(request, pk):
    if request.method == 'POST':
        info = PreColleague.objects.get(pk=pk)
        info.confirm = 'Y'
        info.save()
    return redirect(reverse('Profile:Confirm')+'#PreColleague')
#<<< Pre-Experience: Confirm


@login_required()
def OnlineDelete(request, pk, tlt):
    if request.method == 'POST':
        site = OnlineRegistrations.objects.get(pk=pk)
        site.delete()
    return redirect(reverse('Profile:ProfileView')+'#online')


@login_required()
def PassportAddView(request):
    tlt = request.user.alias
    detail = Profile.objects.get(alias=tlt)
    if detail.talent == request.user:
        form = PassportDetailForm(request.POST or None)
        if request.method =='POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView')+'#passport')
        else:
            template = 'Profile/passport_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def PassportDeleteView(request, pk, tlt):
    info = PassportDetail.objects.get(pk=pk)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Profile:ProfileView')+'#passport')
    else:
        raise PermissionDenied


@login_required()
def PassportEditView(request, psp, tlt):
    info = PassportDetail.objects.get(slug=psp)
    if info.talent == request.user:
        form = PassportDetailForm(request.POST or None, instance=info)
        if request.method =='POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView')+'#passport')
        else:
            template = 'Profile/passport_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


#>>>Language Views
@csp_exempt
@login_required()
def LanguageAddView(request, tlt):
    detail = Profile.objects.get(alias=tlt)
    if detail.talent == request.user:
        form = LanguageTrackForm(request.POST or None)
        if request.method =='POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView'))
            else:
                template = 'Profile/language_add.html'
                context = {'form': form}
                return render(request, template, context)
        else:
            template = 'Profile/language_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def LanguageEditView(request, tlt, lang):
    detail = Profile.objects.get(alias=tlt)
    info = LanguageTrack.objects.get(slug=lang)
    if detail.talent == request.user:
        form = LanguageTrackForm(request.POST or None, instance=info)
        if request.method =='POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView'))
        else:
            template = 'Profile/language_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def LanguageDeleteView(request, lang_id, tlt):
    info = LanguageTrack.objects.get(pk=lang_id)
    if info.talent == request.user:
        if request.method =='POST':
            info.delete()
            return redirect(reverse('Profile:ProfileView')+'#language')
    else:
        raise PermissionDenied


@csp_exempt
@login_required()
def LanguagePopup(request):
    form = LanguageListForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_language");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'Profile/language_popup.html'
            return render(request, template, context)
    else:
        context = {'form':form,}
        template = 'Profile/language_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_language_id(request):
    if request.is_ajax():
        language = request.Get['language']
        language_id = SiteName.objects.get(language = language).id
        data = {'language_id':language_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Language Views


@csp_exempt
@login_required()
def IdentificationView(request):
    tlt = request.user.alias
    detail = Profile.objects.get(alias=tlt)
    info = IdentificationDetail.objects.get(talent__alias=tlt)
    if detail.talent == request.user:
        form = IdentificationDetailForm(request.POST or None, instance=info)
        if request.method =='POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView'))
        else:
            template = 'Profile/id_edit.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


#>>>Id Popup
@login_required()
@csp_exempt
def IdTypePopup(request):
    form = IdTypeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_id_type");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template = 'Profile/id_type_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_IdType_id(request):
    if request.is_ajax():
        type = request.Get['type']
        type_id = SiteName.objects.get(type = type).id
        data = {'type_id':type_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Id Popup


@login_required()
def FileUploadView(request):
    tlt = request.user.alias
    detail = Profile.objects.get(alias=tlt)
    if detail.talent == request.user:
        form = FileUploadForm(request.POST, request.FILES)
        if request.method =='POST':
            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView')+'#Upload')
            else:
                template = 'Profile/file_upload.html'
                context = {'form': form}
                return render(request, template, context)
        else:
            template = 'Profile/file_upload.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


login_required()
def FileDelete(request, pk):
    tlt=request.user.alias
    detail = FileUpload.objects.get(pk=pk)
    if detail.talent == request.user:
        if request.method =='POST':
            detail.delete()
            return redirect(reverse('Profile:ProfileView')+'#Upload')
    else:
        raise PermissionDenied


login_required()
def EmailDelete(request, pk, tlt):
    detail = Email.objects.get(pk=pk)
    if detail.talent == request.user:
        if request.method =='POST':
            detail.delete()
            return redirect(reverse('Profile:ProfileView')+'#email')
    else:
        raise PermissionDenied


login_required()
def not_wtr(request, wtr):
    '''Function to remove the country if talent no longer wishes to go there'''
    wtr_qs = WillingToRelocate.objects.get(slug=wtr)
    if wtr_qs.talent == request.user:
        if request.method =='POST':
            wtr_qs.delete()
            return redirect(reverse('Profile:ProfileView')+'#WTR')
    else:
        raise PermissionDenied


login_required()
def wtr_doc_status(request, wtr):
    '''Changes the status of the possetion of documents needed to work in a country'''
    wtr_qs = WillingToRelocate.objects.filter(slug=wtr)

    if request.method =='POST':
        if 'yes' in request.POST:
            print(True)
            wtr_qs.update(documents=True)
        elif 'no' in request.POST:
            print(False)
            wtr_qs.update(documents=False)

        return redirect(reverse('Profile:ProfileView')+'#WTR')


@login_required()
def ProfileView(request):
    tlt = request.user.alias
    usr = CustomUser.objects.get(alias=tlt)
    detail = Profile.objects.get(alias=tlt)

    tlt_id = request.user.id
    if detail.talent == request.user:
        info = Profile.objects.filter(alias=tlt)
        try:
            profile_pic = ProfileImages.objects.get(talent__alias=tlt).profile_pic
        except:
            profile_pic=None
        try:
            background_pic = ProfileImages.objects.get(talent__alias=tlt).profile_background
        except:
            background_pic=None
        email = Email.objects.filter(talent__alias=tlt)
        physical = PhysicalAddress.objects.get(talent__alias=tlt)
        postal = PostalAddress.objects.get(talent__alias=tlt)
        pnumbers = PhoneNumber.objects.filter(talent__alias=tlt)
        online = OnlineRegistrations.objects.filter(talent__alias=tlt)
        id = IdentificationDetail.objects.filter(talent__alias=tlt)
        passport = PassportDetail.objects.filter(talent__alias=tlt)
        speak = LanguageTrack.objects.filter(talent__alias=tlt)
        history = BriefCareerHistory.objects.filter(talent__alias=tlt).order_by('-date_from')
        user_info = CustomUser.objects.get(pk=tlt_id)
        achievement = Achievements.objects.filter(talent=tlt_id).order_by('-date_achieved')
        award = Awards.objects.filter(talent=tlt_id).order_by('-date_achieved')
        publication = Publications.objects.filter(talent=tlt_id).order_by('-date_published')
        lcm_qs = LicenseCertification.objects.filter(talent=tlt_id).order_by('-issue_date')
        upload = FileUpload.objects.filter(talent__alias=tlt)
        relocate = WillingToRelocate.objects.filter(talent__alias=tlt)

        template = 'Profile/profile_view.html'
        context = {
            'info':info, 'email':email, 'physical':physical, 'postal': postal, 'pnumbers': pnumbers, 'online': online, 'id': id, 'passport': passport, 'speak': speak, 'history': history, 'user_info': user_info, 'tlt': tlt, 'relocate': relocate,
            'upload': upload, 'lcm_qs': lcm_qs,'achievement': achievement, 'award': award, 'publication': publication, 'profile_pic': profile_pic,  'background_pic': background_pic,
            }

        return render(request, template, context)
    else:
        raise PermissionDenied

#this better work
@login_required()
def ProfileEditView(request, tlt):
    talent_id = request.user.id
    detail = CustomUser.objects.get(id=talent_id)
    #work-around to get first and last names into fields. THere must be a better way for people smarter than me to fix! (JK)
    fn = detail.first_name
    ln = detail.last_name

    Profile.objects.filter(talent=talent_id).update(f_name=fn, l_name=ln)

    pfl = Profile.objects.get(talent=talent_id)
    if detail.id == talent_id:
        form = ProfileForm(request.POST or None, instance=pfl)

        if request.method =='POST':
            next_url=request.POST.get('next','/')

            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()

                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Profile:ProfileView')
                return HttpResponseRedirect(next_url)
            else:
                template = 'Profile/profile_edit.html'
                context = {'form': form,}
                return render(request, template, context)
        else:
            template = 'Profile/profile_edit.html'
            context = {'form': form,}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def PublicProfileNameEditView(request, tlt):
    talent_id = request.user.alias

    pfl = CustomUser.objects.get(alias=talent_id)
    form = PublicProfileNameForm(request.POST or None, instance=pfl)

    if request.method =='POST':
        next_url=request.POST.get('next','/')
        if form.is_valid():
            new = form.save(commit=False)
            new.save()

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Profile:ProfileView')
            return HttpResponseRedirect(next_url)
        else:
            template = 'Profile/public_profile_name_edit.html'
            context = {'form': form,}
            return render(request, template, context)
    else:
        template = 'Profile/public_profile_name_edit.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def PublicProfileIntroEditView(request, tlt):
    talent_id = request.user.alias

    pfl = Profile.objects.get(alias=talent_id)
    form = PublicProfileIntroForm(request.POST or None, instance=pfl)

    if request.method =='POST':
        next_url=request.POST.get('next','/')
        if form.is_valid():
            new = form.save(commit=False)
            new.save()

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Profile:ProfileView')
            return HttpResponseRedirect(next_url)
        else:
            template = 'Profile/public_profile_intro_edit.html'
            context = {'form': form,}
            return render(request, template, context)
    else:
        template = 'Profile/public_profile_intro_edit.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def ProfilePicEditView(request, tlt):
    instance, _ = ProfileImages.objects.get_or_create(talent__alias=tlt)
#    instance = get_object_or_404(ProfileImages, talent__alias=tlt)

    if request.method =='POST':
        next_url=request.POST.get('next','/')
        form = UploadProfilePicForm(data=request.POST, files=request.FILES, instance=instance)
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.save()

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Profile:ProfileView')+'#pics'
            return HttpResponseRedirect(next_url)
    else:
        form = UploadProfilePicForm(instance=instance)
        template = 'Profile/profile_pic_edit.html'
        context = {'form': form,}
        return render(request, template, context)


@login_required()
def ProfileBackgroundPicEditView(request, tlt):
    instance, _ = ProfileImages.objects.get_or_create(talent__alias=tlt)

    form = UploadProfileBackgroundPicForm(data=request.POST, files=request.FILES, instance=instance)

    if request.method =='POST':
        next_url=request.POST.get('next','/')

        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.save()

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Profile:ProfileView')+'#pics'
            return HttpResponseRedirect(next_url)
    else:
        template = 'Profile/profile_background_pic_edit.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
def ProfileBackgroundEditView(request, tlt):
    talent = request.user.id
    detail = Profile.objects.get(alias=tlt)

    if detail.talent == request.user:
        form = ProfileBackgroundForm(request.POST or None, request.FILES or None, instance=detail)

        if request.method =='POST':
            next_url=request.POST.get('next','/')

            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()

                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Profile:ProfileView')+'#background'
                return HttpResponseRedirect(next_url)
        else:
            template = 'Profile/profile_background_edit.html'
            context = {'form': form,}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def ProfileMotivationEditView(request, tlt):
    talent = request.user.id
    detail = Profile.objects.get(alias=tlt)

    if detail.talent == request.user:
        form = ProfileMotivationForm(request.POST or None, instance=detail)

        if request.method =='POST':
            next_url=request.POST.get('next','/')

            if form.is_valid():
                new = form.save(commit=False)
                new.talent = request.user
                new.save()

                if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    next_url = reverse('Profile:ProfileView')+'#motivation'
                return HttpResponseRedirect(next_url)
        else:
            template = 'Profile/profile_motivation_edit.html'
            context = {'form': form,}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def EmailEditView(request, tlt):
    detail = get_object_or_404(Profile, alias=tlt)
    if detail.talent == request.user:
        form = EmailForm(request.POST or None)
        if request.method =='POST':
            next_url=request.POST.get('next','/')
            if form.is_valid():
                new=form.save(commit=False)
                new.talent = request.user
                new.save()
                if 'Done' in request.POST:
                    if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                        next_url = reverse('Profile:ProfileView')
                    return HttpResponseRedirect(next_url)
                elif 'Another' in request.POST:
                    form=EmailForm()
        else:
            form=EmailForm()
        template = 'Profile/email_edit.html'
        context = {'form': form}
        return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def EmailStatusView(request, tlt, eml):
    detail = Profile.objects.get(alias=tlt)
    detail2 = get_object_or_404(Email, slug=eml)
    if detail.talent == request.user:
        form = EmailStatusForm(request.POST or None, instance=detail2)
        if request.method =='POST':
            next_url=request.POST.get('next','/')
            if form.is_valid():
                new=form.save(commit=False)
                new.save()
                return redirect(reverse('Profile:ProfileView'))

        else:
            template = 'Profile/email_status.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def PhysicalAddressView(request):
    tlt = request.user.alias
    detail = Profile.objects.get(alias=tlt)
    if detail.talent == request.user:
        info = get_object_or_404(PhysicalAddress, talent__alias=tlt)
        form = PhysicalAddressForm(request.POST or None, instance=info)
        if request.method =='POST':
            if form.is_valid():
                new=form.save(commit=False)
                new.talent = request.user
                new.save()
                response = redirect(reverse('Profile:ProfileView')+'#phone')

                return response
        else:
            template = 'Profile/physical_address_add.html'
            context = {'form': form}
            response = render(request, template, context)
            return response
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def PostalAddressView(request):
    tlt = request.user.alias
    detail = Profile.objects.get(alias=tlt)
    if detail.talent == request.user:
        info = get_object_or_404(PostalAddress, talent__alias=tlt)
        form = PostalAddressForm(request.POST or None, instance=info)
        if request.method =='POST':
            if form.is_valid():
                new=form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView')+'#phone')
        else:
            template = 'Profile/postal_address_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def PhoneNumberAdd(request):
    tlt = request.user.alias
    detail = Profile.objects.get(alias=tlt)
    if detail.talent == request.user:
        form =PhoneNumberForm(request.POST or None)
        if request.method =='POST':
            if form.is_valid():
                new=form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView')+'#phone')
            else:
                template = 'Profile/phone_number_add.html'
                context = {'form': form}
                return render(request, template, context)
        else:
            template = 'Profile/phone_number_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def PhoneNumberDelete(request, pk):
    detail = PhoneNumber.objects.get(pk=pk)
    tlt = detail.talent.alias
    if detail.talent == request.user:
        if request.method =='POST':
            detail.delete()
            return redirect(reverse('Profile:ProfileView')+'#phone')
    else:
        raise PermissionDenied


@login_required()
@csp_exempt
def OnlineProfileAdd(request, tlt):
    detail = Profile.objects.get(alias=tlt)
    if detail.talent == request.user:
        form = OnlineProfileForm(request.POST or None)
        if request.method =='POST':
            if form.is_valid():
                new=form.save(commit=False)
                new.talent = request.user
                new.save()
                return redirect(reverse('Profile:ProfileView')+'#online')
        else:
            template = 'Profile/online_profile_add.html'
            context = {'form': form}
            return render(request, template, context)
    else:
        raise PermissionDenied


#>>>Site Type Popup
@login_required()
@csp_exempt
def ProfileTypePopup(request):
    form = ProfileTypeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_sitename");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template = 'Profile/site_type_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_SiteType_id(request):
    if request.is_ajax():
        type = request.Get['site']
        site_id = SiteName.objects.get(site = site).id
        data = {'site_id':site_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< SiteType Popup


@login_required()
def HelpDesktopNetworkView(request):
    template_name = 'Profile/help_desktop_network.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpDesktopWorkflowView(request):
    template_name = 'Profile/help_desktop_workflow.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpDesktopWorkshopView(request):
    template_name = 'Profile/help_desktop_workshop.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpDesktopInformationView(request):
    template_name = 'Profile/help_desktop_information.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpDesktopPendingInterviewsView(request):
    template_name = 'Profile/help_desktop_pending_interviews.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpDesktopAssignmentsView(request):
    template_name = 'Profile/help_desktop_assignments.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpLecturerCommentView(request):
    template_name = 'Profile/help_lecturer_comment.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpLecturerConfirmView(request):
    template_name = 'Profile/help_confirm_lecturer.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpClassmateConfirmView(request):
    template_name = 'Profile/help_confirm_classmate.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpColleqagueConfirmView(request):
    template_name = 'Profile/help_confirm_colleague.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpSubordinateConfirmView(request):
    template_name = 'Profile/help_confirm_subordinate.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpCoworkerConfirmView(request):
    template_name = 'Profile/help_confirm_coworker.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpContractorConfirmView(request):
    template_name = 'Profile/help_confirm_contractor.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpTalentWorkshopView(request):
    template_name = 'Profile/help_workshop_tlt.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpEmployerWorkshopView(request):
    template_name = 'Profile/help_workshop_employer.html'
    context = {}
    return render(request, template_name, context)
