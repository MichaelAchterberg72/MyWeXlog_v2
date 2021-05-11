from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from .forms import CalendarDetailForm

from .models import Timesheet

# Create your views here.
@login_required()
def TltIntCommentView(request, bil, tlt):
    instance = BidInterviewList.objects.get(slug=bil)

    form = CalendarDetailForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.tlt_reponded = timezone.now()
            new.save()

            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('MarketPlace:Entrance')
            return HttpResponseRedirect(next_url)
    else:
        template = 'marketplace/talent_interview_comment.html'
        context={'form': form, 'instance': instance,}
        return render(request, template, context)
