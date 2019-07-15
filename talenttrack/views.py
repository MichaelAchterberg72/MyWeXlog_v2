from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
import json
from django.db.models import Count, Sum


from csp.decorators import csp_exempt


from .forms import (
        TopicForm, ResultForm, CourseTypeForm, CourseForm, DesignationForm, ClassMatesSelectForm, ClassMatesConfirmForm, LecturerSelectForm, LecturerConfirmForm, EducationForm, WorkExperienceForm, WorkColleagueSelectForm, WorkColleagueConfirmForm, WorkColleagueResponseForm, ClassMatesResponseForm, LecturerResponseForm, SuperiorSelectForm, WorkCollaboratorResponseForm, WorkCollaboratorConfirmForm, WorkCollaboratorSelectForm, WorkClientResponseForm, WorkClientConfirmForm, WorkClientSelectForm, PreColleagueResponseForm, PreColleagueConfirmForm, PreColleagueSelectForm, PreLoggedExperienceForm, TopicPopForm, LecturerRespondForm, ClassMatesRespondForm, WorkColleagueSelectForm, SuperiorSelectForm, WorkCollaboratorSelectForm
)

from .models import (
        Education, Lecturer, Course, ClassMates, WorkExperience, Superior, WorkCollaborator, WorkClient, WorkColleague, PreLoggedExperience, PreColleague
)


@login_required()
def ExperienceHome(request):
        train = Education.objects.filter(talent=request.user).order_by('-date_from')
        train_sum = train.aggregate(Edu_sum=Sum('hours_worked'))

        experience = WorkExperience.objects.filter(talent=request.user).order_by('-date_from')
        exp_sum = experience.aggregate(we_sum=Sum('hours_worked'))

        prelog = PreLoggedExperience.objects.filter(talent=request.user).order_by('-date_from')
        pre_sum = prelog.aggregate(p_sum=Sum('hours_worked'))

        template = 'talenttrack/track_home.html'
        context = {'train': train, 'train_sum': train_sum, 'experience': experience, 'exp_sum': exp_sum, 'prelog': prelog, 'pre_sum': pre_sum}
        return render(request, template, context)


@login_required()
@csp_exempt
def PreLoggedExperienceCaptureView(request):
    form = PreLoggedExperienceForm(request.POST or None, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.save()
            form.save_m2m()
            return redirect('Talent:PreColleagueSelect')
    else:
        template = 'talenttrack/prelogged_capture.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
def PreColleagueSelectView(request):
    instance = PreLoggedExperience.objects.filter(talent=request.user).latest('date_captured')
    form = PreColleagueSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.pre_experience = instance
            new.save()
            return redirect(reverse('Talent:Home'))
    else:
        template = 'talenttrack/prelogged_colleague_select.html'
        context = {'instance': instance, 'form': form}
        return render(request, template, context)


@login_required()
def PreLogDetailView(request, pre_id):
    check = PreLoggedExperience.objects.get(pk=pre_id)
    if check.talent == request.user:
        confirmed_l = PreColleague.objects.filter(pre_experience=pre_id)
        template = 'talenttrack/prelogged_detail.html'
        context = {'check': check, 'confirmed_l': confirmed_l}
        return render(request, template, context)
    else:
        raise PermissionDenied


@login_required()
def ClientSelectView(request, pk):
    instance = WorkExperience.objects.get(pk=pk)
    form = WorkClientSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                return redirect('Talent:ClientSelect', kwargs={'pk':pk})
            elif 'done' in request.POST:
                return redirect('Talent:Home')
    else:
        template = 'talenttrack/experience_client_select.html'
        context = {'instance': instance, 'form': form}
        return render(request, template, context)


@login_required()
def ClientAddView(request, pk):
    instance = get_object_or_404(WorkExperience, pk=pk)
    form = WorkClientSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                return redirect(reverse('Talent:ClientAdd', kwargs={'pk':pk}))
            elif 'done' in request.POST:
                return redirect(reverse('Talent:ExperienceDetail', kwargs={'exp_id': instance.id}))
    else:
        template = 'talenttrack/experience_client_add.html'
        context = {'instance': instance, 'form': form}
        return render(request, template, context)


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
def CollaboratorSelectView(request, pk):
    instance = WorkExperience.objects.get(pk=pk)
    form = WorkCollaboratorSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                return redirect('Talent:CollaboratorSelect', kwargs={'pk':pk})
            elif 'done' in request.POST:
                return redirect(reverse('Talent:ClientSelect', kwargs={'pk':pk}))
    else:
        template = 'talenttrack/experience_collaborator_select.html'
        context = {'instance': instance, 'form': form}
        return render(request, template, context)


@login_required()
def CollaboratorAddView(request, pk):
    instance = get_object_or_404(WorkExperience, pk=pk)
    form = WorkCollaboratorSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                return redirect(reverse('Talent:CollaboratorAdd', kwargs={'pk':pk}))
            elif 'done' in request.POST:
                return redirect(reverse('Talent:ExperienceDetail', kwargs={'exp_id': instance.id}))
    else:
        template = 'talenttrack/experience_collaborator_add.html'
        context = {'instance': instance, 'form': form}
        return render(request, template, context)


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
def SuperiorSelectView(request, pk):
    instance = WorkExperience.objects.get(pk=pk)
    form = SuperiorSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                return redirect('Talent:SuperiorSelect', kwargs={'pk':pk})
            elif 'done' in request.POST:
                return redirect(reverse('Talent:CollaboratorSelect', kwargs={'pk':pk}))
    else:
        template = 'talenttrack/experience_superior_select.html'
        context = {'instance': instance, 'form': form}
        return render(request, template, context)


@login_required()
def SuperiorAddView(request, pk):
    instance = get_object_or_404(WorkExperience, pk=pk)
    form = SuperiorSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                return redirect('Talent:SuperiorAdd', kwargs={'pk':pk})
            elif 'done' in request.POST:
                return redirect(reverse('Talent:ExperienceDetail', kwargs={'exp_id': instance.id}))
    else:
        template = 'talenttrack/experience_superior_add.html'
        context = {'instance': instance, 'form': form}
        return render(request, template, context)


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
def ColleagueSelectView(request):
    instance = WorkExperience.objects.filter(talent=request.user).latest('date_captured')
    form = WorkColleagueSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                return redirect('Talent:ColleagueSelect')
            elif 'done' in request.POST:
                return redirect(reverse('Talent:SuperiorSelect', kwargs={'pk':instance.id}))
    else:
        template = 'talenttrack/experience_colleague_select.html'
        context = {'instance': instance, 'form': form}
        return render(request, template, context)


def ColleagueAddView(request, pk):
    instance = get_object_or_404(WorkExperience, pk=pk)
    form = WorkColleagueSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.experience = instance
            new.save()
            if 'another' in request.POST:
                return redirect(reverse('Talent:ColleagueAdd', kwargs={'pk':pk}))
            elif 'done' in request.POST:
                return redirect(reverse('Talent:ExperienceDetail', kwargs={'exp_id':instance.id}))
    else:
        template = 'talenttrack/experience_colleague_add.html'
        context = {'instance': instance, 'form': form}
        return render(request, template, context)


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
    check = WorkExperience.objects.get(pk=exp_id)
    if check.talent == request.user:
        sum = WorkExperience.objects.filter(talent=request.user)
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
            new.save()
            form.save_m2m()
            return redirect('Talent:ColleagueSelect')
    else:
        template = 'talenttrack/work_experience_capture.html'
        context = {'form': form}
        return render(request, template, context)


@login_required()
def EducationDetail(request, edu_id):
    check = Education.objects.get(pk=edu_id)
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
    instance = Education.objects.filter(talent=request.user).latest('date_captured')
    form = LecturerSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.save()
            if 'another' in request.POST:
                return redirect('Talent:LecturerSelect')
            elif 'done' in request.POST:
                return redirect('Talent:ClassMatesSelect')
    else:
        template = 'talenttrack/lecturer_select.html'
        context = {'instance': instance, 'form': form}
        return render(request, template, context)


@login_required()
@csp_exempt
def LecturerAddView(request, pk):
    instance = get_object_or_404(Education, pk=pk)
    form = LecturerSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.save()
            if 'another' in request.POST:
                return redirect('Talent:LecturerAdd', kwargs={'pk': pk})
            elif 'done' in request.POST:
                return redirect(reverse('Talent:EducationDetail', kwargs={'edu_id': instance.id}))
    else:
        template = 'talenttrack/lecturer_select.html'
        context = {'instance': instance, 'form': form}
        return render(request, template, context)


@login_required()
@csp_exempt
def ClassMateSelectView(request):
    instance = Education.objects.filter(talent=request.user).latest('date_captured')
    form = ClassMatesSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.save()
            if 'another' in request.POST:
                return redirect('Talent:ClassMatesSelect')
            elif 'done' in request.POST:
                return redirect(reverse('Talent:Home'))
    else:
        template = 'talenttrack/classmate_select.html'
        context = {'instance': instance, 'form': form}
        return render(request, template, context)


@login_required()
@csp_exempt
def ClassMateAddView(request, pk):
    instance = get_object_or_404(Education, pk=pk)
    form = ClassMatesSelectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.education = instance
            new.save()
            if 'another' in request.POST:
                return redirect(reverse('Talent:ClassMatesAdd', kwargs={'pk': pk}))
            elif 'done' in request.POST:
                return redirect(reverse('Talent:EducationDetail', kwargs={'edu_id': instance.id}))
    else:
        template = 'talenttrack/classmate_select.html'
        context = {'instance': instance, 'form': form}
        return render(request, template, context)


@login_required()
@csp_exempt
def EducationCaptureView(request):
    form = EducationForm(request.POST or None, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            new=form.save(commit=False)
            new.talent = request.user
            new.save()
            form.save_m2m()
            return redirect(reverse('Talent:LecturerSelect'))
    else:
        template = 'talenttrack/talent_education.html'
        context = {'form': form}
        return render(request, template, context)


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


@csrf_exempt
def get_result_id(request):
    if request.is_ajax():
        result = request.Get['result']
        result_id = Result.objects.get(type = result).id
        data = {'result_id':result_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Result Popup

#>>>Result Popup
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


@csrf_exempt
def get_designation_id(request):
    if request.is_ajax():
        designation = request.Get['designation']
        designation_id = Designation.objects.get(name = designation).id
        data = {'designation_id':designation_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Designation Popup
