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


from .models import (
            Industry, Enterprise, BranchType, Branch, PhoneNumber,
            )


from .forms import (
    EnterprisePopupForm,
)


#>>>Company Popup
@login_required()
@csp_exempt
def EnterpriseAddPopup(request):
    form = EnterprisePopupForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_company");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template = 'enterprises/enterprise_popup.html'
        return render(request, template, context)

@csp_exempt
@csrf_exempt
def get_enterprise_id(request):
    if request.is_ajax():
        company = request.Get['company']
        company_id = Enterprise.objects.get(name = enterprise).id
        data = {'company_id':company_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< Company Popup
