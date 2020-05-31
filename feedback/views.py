from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.http import is_safe_url
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import PermissionDenied

from django.utils import timezone
from core.decorators import subscription
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from csp.decorators import csp_exempt

from .models import FeedBack, Notices, NoticeRead
from .forms import FeedBackForm, NoticeForm, NoticeReadForm

from users.models import CustomUser

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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


@login_required()
@csp_exempt
def NoticeListView(request):
    reg_date = request.user.date_joined
    notice = Notices.objects.filter(notice_date__gte = reg_date).order_by('-notice_date')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(notice, 20)

    try:
        pageitems = paginator.page(page)
    except PageNotAnInteger:
        pageitems = paginator.page(1)
    except EmptyPage:
        pageitems = paginator.page(paginator.num_pages)

    index = pageitems.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 3 if index >= 3 else 0
    end_index = index + 3 if index <= max_index - 3 else max_index
    page_range = list(paginator.page_range)[start_index:end_index]

    template = 'feedback/notice_list.html'
    context = {'notice': notice, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template, context)


@login_required()
@csp_exempt
def NoticeReadView(request, nt):
    qs = get_object_or_404(Notices, slug=nt)
#    tlt = request.user
    tlt = request.user
    qs2 = NoticeRead.objects.filter(Q(notice__slug=nt) & Q(talent=tlt)).exists()

    form = NoticeReadForm(request.POST or None)

    if request.method == 'POST':
        next_url=request.POST.get('next', '/')
        if form.is_valid():
            new = form.save(commit=False)
            new.notice = qs
            new.talent = request.user
            new.notice_read = True
            new.save()

            return redirect(reverse('Feedback:NoticesList'))

        else:
            template = 'feedback/notice_read_form.html'
            context = {'form': form, 'qs': qs, 'qs2': qs2}
            return render(request, template, context)

    else:
        template = 'feedback/notice_read_form.html'
        context = {'form': form, 'qs': qs, 'qs2': qs2}
        return render(request, template, context)
