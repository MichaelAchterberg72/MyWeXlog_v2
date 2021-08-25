import json

from csp.decorators import csp_exempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import is_safe_url
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from .forms import PhoneNumberForm, SkillForm
from .models import PhoneNumberType, SkillTag


@login_required()
@csp_exempt
def PhoneNumberTypeAddPopup(request):
    form = PhoneNumberForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_type");</script>' % (new.pk, new))
        else:
            context = {'form':form,}
            template = 'db_flatten/phone_number_type_popup.html'
            return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'db_flatten/phone_number_type_popup.html'
        return render(request, template, context)

@csrf_exempt
def get_numbertype_id(request):
    if request.is_ajax():
        type = request.Get['type']
        type_id = PhoneNumberType.objects.get(type = type).id
        data = {'type_id':type_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")


@login_required()
@csp_exempt
def SkillAddPopup(request):
    form = SkillForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_skills");</script>' % (new.pk, new))
        else:
            context = {'form':form,}
            template = 'db_flatten/skill_popup.html'
            return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'db_flatten/skill_popup.html'
        return render(request, template, context)

@csrf_exempt
def get_skill_id(request):
    if request.is_ajax():
        skill = request.Get['skill']
        skill_id = Skill.objects.get(skill = skill).id
        data = {'skill_id':skill_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")

@login_required()
def ListTagsView(request):
    '''List sorted alphabetically for both demand and confirmed hours '''
    list = SkillTag.objects.all().order_by('skill')
    tally = list.count()

    hours = list.filter(experience__score__gte=3).annotate(
                                                           hours_sum = Sum('experience__hours_worked')
                                                           )
    total_hours = list.filter(experience__score__gte=3).aggregate(
                                                                  total_sum=Sum('experience__hours_worked')
                                                                  )
    demand = list.annotate(
                           demand_count = Count('skillrequired__scope')
                           )
    order = "alphabetically"

    template = 'db_flatten/skill_list.html'
    context = {'list': list, 'hours': hours, 'tally': tally, 'demand': demand, 'total_hours': total_hours, 'order': order}
    return render(request, template, context)


@login_required()
def ListTagsSortView(request):
    '''List sorted from max to min for both demand and confirmed hours '''
    list = SkillTag.objects.all()
    tally = list.count()

    hours = list.filter(experience__score__gte=3).annotate(
                                                           hours_sum = Sum('experience__hours_worked')
                                                           ).order_by("-hours_sum")
    total_hours = list.filter(experience__score__gte=3).aggregate(
                                                                  total_sum=Sum('experience__hours_worked')
                                                                  )
    demand = list.annotate(
                           demand_count = Count('skillrequired__scope')
                           ).order_by("-demand_count")
    order = "from Max to Min"

    template = 'db_flatten/skill_list.html'
    context = {'list': list, 'hours': hours, 'tally': tally, 'demand': demand, 'total_hours': total_hours, 'order': order}
    return render(request, template, context)
