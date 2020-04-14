from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.http import is_safe_url
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import PermissionDenied

from django.utils import timezone
from core.decorators import subscription
from django.contrib.auth.decorators import login_required
from csp.decorators import csp_exempt

from .models import FeedBack
from .forms import FeedBackForm


@login_required()
@csp_exempt
def FeedBackView(request):
    form = FeedBackForm(request.POST or None)

    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.save()
            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                next_url = reverse('Profile:Home')
            return HttpResponseRedirect(next_url)

    else:
        template = 'feedback/feedback_form.html'
        context = {'form': form,}
        return render(request, template, context)
