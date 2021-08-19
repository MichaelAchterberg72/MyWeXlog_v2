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
    list = SkillTag.objects.all().order_by('skill')
    count = list.count()

    #sum all hours logged to a skill
    skill_set = {}
    for s in list:
        #summing the skills
        i = list.get(skill=s)
        e = i.experience.all()
        e_sum = e.aggregate(sum_t=Sum('hours_worked'))
        e_float = e_sum.get('sum_t')
        e_count = e.count()
        skill_set[s] = [e_count, e_float]

    #demand calculation
    demand_set = {}
    for d in list:
        j = list.get(skill=d)
        f = j.skillrequired_set.all()
        d_count = f.count()
        demand_set[d] = d_count

    template = 'db_flatten/skill_list.html'
    context = {'list': list, 'count': count, 'skill_set': skill_set, 'demand_set': demand_set,}
    return render(request, template, context)
