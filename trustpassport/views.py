from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from django.views.generic import (
        TemplateView
)

from csp.decorators import csp_exempt

from .forms import *

# Create your views here.
class TrustHomeView(TemplateView):
    template_name = 'trustpassport/home.html'


@login_required()
@csp_exempt
def EnterpriseTrustAddView(request):
    if request.method =='POST':
        form = EnterpriseTrustAddForm(request.POST or None)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return redirect(reverse('Trust:TrustHome'))
    else:
        form = EnterpriseTrustAddForm()

    template_name = 'trustpassport/enterprise_trust_add.html'
    context = {'form': form}
    return render(request, template_name, context)


@login_required()
@csp_exempt
def TalentTrustAddView(request):
    if request.method =='POST':
        form = TalentTrustAddForm(request.POST or None)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            return redirect(reverse('Trust:TrustHome'))
    else:
        form = TalentTrustAddForm()

    template_name = 'trustpassport/talent_trust_add.html'
    context = {'form': form}
    return render(request, template_name, context)
