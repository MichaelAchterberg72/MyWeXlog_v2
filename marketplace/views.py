from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
import json
from django.db.models import Count, Sum
from django.utils import timezone


from csp.decorators import csp_exempt


from .forms import (
        TalentAvailabillityForm, SkillRequiredForm, SkillLevelForm, DeliverablesForm, TalentRequiredForm, WorkLocationForm
)

from .models import(
    TalentRequired, SkillRequired, Deliverables, TalentAvailabillity
)


@login_required()
def MarketHome(request):
    ipost = TalentRequired.objects.filter(requested_by=request.user, offer_status__iexact='O').order_by('-date_entered')[:5]
    capacity = TalentAvailabillity.objects.filter(talent=request.user, date_to__gte=timezone.now()).order_by('-date_to')[:5]

    template = 'marketplace/vacancy_home.html'
    context ={'ipost': ipost, 'capacity': capacity}
    return render(request, template, context)



@login_required()
def TalentAvailabillityView(request):
    form = TalentAvailabillityForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.save()
            return redirect(reverse('MarketPlace:Entrance')+'#Availabillity')
    else:
        template = 'marketplace/talent_availabillity.html'
        context = {'form':form}
        return render(request, template, context)

@login_required()
def VacancyEditView(request, pk):
    instance = get_object_or_404(TalentRequired, pk=pk)
    skille = SkillRequired.objects.filter(scope=pk)
    delivere = Deliverables.objects.filter(scope=pk)

    form = TalentRequiredForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return redirect(reverse('MarketPlace:VacancyEdit', kwargs={'pk': pk}))
    else:
        template = 'marketplace/vacancy_edit.html'
        context = {'form': form, 'instance': instance, 'skille': skille, 'delivere': delivere}
        return render(request, template, context)



@login_required()
def VacancySkillsAddView(request, pk):
    instance = get_object_or_404(TalentRequired, pk=pk)
    form = SkillRequiredForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.scope = instance
            new.save()
            if 'another' in request.POST:
                return redirect(reverse('MarketPlace:Skills', kwargs={'pk': pk}))
            elif 'done' in request.POST:
                return redirect(reverse('MarketPlace:Entrance'))
    else:
        template = 'marketplace/vacancy_skills.html'
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


@login_required()
def VacancySkillsAdd2View(request, pk):
    instance = get_object_or_404(TalentRequired, pk=pk)
    form = SkillRequiredForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.scope = instance
            new.save()
            return redirect(reverse('MarketPlace:VacancyEdit', kwargs={'pk': pk})+'#deliverables')
    else:
        template = 'marketplace/vacancy_skills2.html'
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


@login_required()
def SkillDeleteView(request, pk):
    if request.method == 'POST':
        skilld = SkillRequired.objects.get(pk=pk)
        skilld.delete()
        return redirect(reverse('MarketPlace:VacancyEdit', kwargs={'pk':skilld.scope.id})+'#skills')


@login_required()
def DeliverablesEditView(request, pk):
    instance = get_object_or_404(Deliverables, pk=pk)
    form = DeliverablesForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return redirect(reverse('MarketPlace:VacancyEdit', kwargs={'pk': instance.scope.id})+'#deliverables')
    else:
        template = 'marketplace/vacancy_deliverables_edit.html'
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


@login_required()
def DeliverablesAdd2View(request, pk):
    instance = get_object_or_404(TalentRequired, pk=pk)
    form = DeliverablesForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.scope = instance
            new.save()
            return redirect(reverse('MarketPlace:VacancyEdit', kwargs={'pk': pk})+'#deliverables')
    else:
        template = 'marketplace/vacancy_deliverables_edit.html'
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


@login_required()
def DeliverableDeleteView(request, pk):
    if request.method == 'POST':
        deld = Deliverables.objects.get(pk=pk)
        deld.delete()
    return redirect(reverse('MarketPlace:VacancyEdit', kwargs={'pk':deld.scope.id})+'#deliverables')


@login_required()
def DeliverablesAddView(request, pk):
    instance = get_object_or_404(TalentRequired, pk=pk)
    form = DeliverablesForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.scope = instance
            new.save()
            if 'another' in request.POST:
                return redirect(reverse('MarketPlace:Deliverables', kwargs={'pk': pk}))
            elif 'done' in request.POST:
                return redirect(reverse('MarketPlace:Skills', kwargs={'pk': pk}))
    else:
        template = 'marketplace/vacancy_deliverables.html'
        context = {'form': form, 'instance': instance}
        return render(request, template, context)


@login_required()
@csp_exempt
def VacancyView(request):
    form = TalentRequiredForm(request.POST or None, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.requested_by = request.user
            new.save()
            form.save_m2m()
            return redirect(reverse('MarketPlace:Deliverables', kwargs={'pk':new.id}))
    else:
        template = 'marketplace/vacancy.html'
        context = {'form': form}
        return render(request, template, context)


#>>> WorkLocation Popup
@login_required()
@csp_exempt
def WorkLocationAddPopup(request):
    form = WorkLocationForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_worklocation");</script>' % (instance.pk, instance))

    else:
        context = {'form': form}
        template = 'marketplace/worklocation_popup.html'
        return render(request, template, context)

@csrf_exempt
def get_worklocation_id(request):
    if request.is_ajax():
        new_worklocation = request.Get['worklocation']
        worklocation_id = WorkLocation.objects.get(worklocation = new_worklocation).id
        data = {'worklocation_id':worklocation_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#WorkLocation Popup <<<


#>>>SkillLevel Popup
@login_required()
@csp_exempt
def SkillLevelAddPopup(request):
    form = SkillLevelForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_experience_level");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template = 'marketplace/skilllevel_popup.html'
        return render(request, template, context)


@csrf_exempt
def get_skilllevel_id(request):
    if request.is_ajax():
        skilllevel = request.Get['skilllevel']
        skilllevel_id = SkillLevel.objects.get(name = skilllevel).id
        data = {'skilllevel_id':skilllevel_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< SkillLevel Popup
