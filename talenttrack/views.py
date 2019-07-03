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
        TopicForm, ResultForm, CourseTypeForm, CourseForm, DesignationForm, ClassMatesSelectForm, ClassMatesConfirmForm, LecturerSelectForm, LecturerConfirmForm, EducationForm, WorkExperienceForm, WorkColleagueSelectForm, WorkColleagueConfirmForm, WorkColleagueResponseForm, ClassMatesResponseForm, LecturerResponseForm, SuperiorSelectForm, WorkCollaboratorResponseForm, WorkCollaboratorConfirmForm, WorkCollaboratorSelectForm, WorkClientResponseForm, WorkClientConfirmForm, WorkClientSelectForm, PreColleagueResponseForm, PreColleagueConfirmForm, PreColleagueSelectForm, PreLoggedExperienceForm, TopicPopForm, LecturerRespondForm, ClassMatesRespondForm
)

from .models import (
        Education, Lecturer, Course, ClassMates
)


@login_required()
def ExperienceHome(request):
        train = Education.objects.filter(talent=request.user).order_by('-date_from')
        train_sum = Education.objects.filter(talent=request.user).aggregate(Edu_sum=Sum('hours_worked'))
        template = 'talenttrack/track_home.html'
        context = {'train': train, 'train_sum': train_sum}
        return render(request, template, context)


@login_required()
@csp_exempt
def WorkExperienceCaptureView(request):
    form = WorkExperienceForm(request.POST or None)
    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            form.save_m2m()
            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Talent:Home')
            return HttpResponseRedirect(next_url)
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
def EducationCaptureView(request):
    form = EducationForm(request.POST or None)
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
