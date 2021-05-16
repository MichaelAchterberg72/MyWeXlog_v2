from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from .forms import CalendarDetailForm

from .models import Timesheet

# Create your views here.
@login_required()
def create_calendar_entry_view(request, bil, tlt):
    instance = BidInterviewList.objects.get(slug=bil)

    form = CalendarDetailForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_calendar_item");</script>' % (instance.pk, instance))
        else:
            context = {'form':form,}
            template = 'billing/add_calendar_entry_popup.html'
            return render(request, template, context)
    else:
        context = {'form':form,}
        template = 'billing/add_calendar_entry_popup.html'
        return render(request, template, context)
