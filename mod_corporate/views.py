from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from core.decorators import corp_permission, subscription


from .models import (
    CorporateStaff, OrgStructure
)

from AppControl.models import (
    CorporateHR
)

from .forms import (
    OrgStructureForm,
)

@login_required()
@corp_permission(1)
class OrgStructureView(request):
    '''A view of the levels in the corporate structure'''
    usr = request.user
    corp = CorporateStaff.objects.get(talent=usr)
    structure = OrgStructure.objects.filter(corporate=corp).order_by('parent')

    template = 'mod_corporate/org_structure_view.html'
    context = {'structure': structure, 'corp': corp,}
    return render(request, template, context)


@login_required()
@corp_permission(2)
class OrgStructureAdd(request, cor):
    '''View to capture the company structure - only corporate administrators can edit the structure '''
    corp = get_object_or_404(CorporateHR, slug=cor)

    form = OrgStructureForm(request.POST or None, fil=corp)

    if request.method = 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.corporate = corp
            new.save()
            return redirect(reverse(''))
        else:
            template = ''
            context = {'form': form,}
            return render(request, template, context)
    else:
        template = ''
        context = {'form': form,}
        return render(request, template, context)
