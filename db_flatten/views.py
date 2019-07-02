from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
import json


from csp.decorators import csp_exempt


from . models import PhoneNumberType, SkillTag

from . forms import (
        PhoneNumberForm, SkillForm,
)

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

@csrf_exempt
def get_skill_id(request):
    if request.is_ajax():
        skill = request.Get['skill']
        skill_id = Skill.objects.get(skill = skill).id
        data = {'skill_id':skill_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
