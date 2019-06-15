from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
import json


from csp.decorators import csp_exempt


from . models import (
        Region, City, Suburb, Currency
)


from .forms import (
    RegionForm, CityForm, SuburbForm,
)

#>>> Region Popup
@login_required()
def RegionAddPopup(request):
    form = RegionForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            messages.success(request, 'Region added!', extra_tags='None')
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_region");</script>' % (new.pk, new))

    else:
        context = {'form': form}
        template = 'locations/region_popup.html'
        return render(request, template, context)

@csrf_exempt
def get_region_id(request):
    if request.is_ajax():
        region = request.Get['region']
        region_id = Region.objects.get(name = region).id
        data = {'region_id':region_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#Region Popup <<<


#>>> City Popup
@login_required()
def CityAddPopup(request):
    form = CityForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            messages.success(request, 'City added!', extra_tags='None')
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_city");</script>' % (new.pk, new))

    else:
        context = {'form': form}
        template = 'locations/city_popup.html'
        return render(request, template, context)

@csrf_exempt
def get_city_id(request):
    if request.is_ajax():
        city = request.Get['city']
        city_id = City.objects.get(name = city).id
        data1 = {'city_id':city_id,}
        return HttpResponse(json.dumps(data1), content_type='application/json')
    return HttpResponse("/")
#City Popup <<<


#>>> City Popup
@login_required()
def SuburbAddPopup(request):
    form = SuburbForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_suburb");</script>' % (new.pk, new))

    else:
        context = {'form': form}
        template = 'locations/suburb_popup.html'
        return render(request, template, context)

@csrf_exempt
def get_suburb_id(request):
    if request.is_ajax():
        suburb = request.Get['city']
        suburb_id = Suburb.objects.get(name = suburb).id
        data1 = {'suburb_id':suburb_id,}
        return HttpResponse(json.dumps(data1), content_type='application/json')
    return HttpResponse("/")
#Suburb Popup <<<
