import json

from csp.decorators import csp_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import is_safe_url
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from .forms import CityForm, CurrencyForm, RegionForm, SuburbForm, VacCityForm
from .models import City, Currency, Region, Suburb


#>>> Region Popup
@login_required()
@csp_exempt
def RegionAddPopup(request):

    form = RegionForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            response = HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_region");</script>' % (instance.pk, instance))
            response.delete_cookie('dataC')
            return response
        else:
            context = {'form': form}
            template = 'locations/region_popup.html'
            return render(request, template, context)

    else:
        context = {'form': form}
        template = 'locations/region_popup.html'
        return render(request, template, context)

@csrf_exempt
def get_region_id(request):
    if request.is_ajax():
        new_region = request.Get['region']
        region_id = Region.objects.get(region = new_region).id
        data = {'region_id':region_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#Region Popup <<<


#>>> City Popup
@login_required()
@csp_exempt
def CityAddPopup(request):

    data=json.loads(request.COOKIES['region'])
    qs = Region.objects.get(id=data)

    form = CityForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.region = qs
            new.save()
            response = HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_city");</script>' % (new.pk, new))
            response.delete_cookie('region')
            return response
        else:
            context = {'form': form,}
            template = 'locations/city_popup.html'
            return render(request, template, context)

    else:
        context = {'form': form}
        template = 'locations/city_popup.html'
        return render(request, template, context)

@csrf_exempt
def get_city_id(request):
    if request.is_ajax():
        city = request.Get['city']
        city_id = City.objects.get(city = city).id
        data1 = {'city_id':city_id,}
        return HttpResponse(json.dumps(data1), content_type='application/json')
    return HttpResponse("/")


@login_required()
@csp_exempt
def CityVacPopup(request):
    '''view to add a city to the vacancy view - as no region is shown in that page'''

    form = VacCityForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            response = HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_city");</script>' % (new.pk, new))
            return response
        else:
            context = {'form': form,}
            template = 'locations/city_vac_add_popup.html'
            return render(request, template, context)
    else:
        context = {'form': form}
        template = 'locations/city_vac_add_popup.html'
        return render(request, template, context)
#City Popup <<<


#>>> Suburb Popup
@login_required()
@csp_exempt
def SuburbAddPopup(request):

    data=json.loads(request.COOKIES['city'])
    qs = City.objects.get(id=data)

    form = SuburbForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.city=qs
            new.save()
            response = HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_suburb");</script>' % (new.pk, new))
            response.delete_cookie("city")
            return response
        else:
            context = {'form': form}
            template = 'locations/suburb_popup.html'
            return render(request, template, context)

    else:
        context = {'form': form}
        template = 'locations/suburb_popup.html'
        return render(request, template, context)

@csrf_exempt
def get_suburb_id(request):
    if request.is_ajax():
        suburb = request.Get['city']
        suburb_id = Suburb.objects.get(suburb = suburb).id
        data1 = {'suburb_id':suburb_id,}
        return HttpResponse(json.dumps(data1), content_type='application/json')
    return HttpResponse("/")
#Suburb Popup <<<


#>>> Currency Popup
@login_required()
@csp_exempt
def CurrencyAddPopup(request):
    form = CurrencyForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_currency");</script>' % (instance.pk, instance))
        else:
            context = {'form': form}
            template = 'locations/currency_popup.html'
            return render(request, template, context)

    else:
        context = {'form': form}
        template = 'locations/currency_popup.html'
        return render(request, template, context)

@csrf_exempt
def get_currency_id(request):
    if request.is_ajax():
        new_currency = request.Get['currency']
        currency_id = Currency.objects.get(currency = new_currency).id
        data = {'currency_id':currency_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#Currency Popup <<<
