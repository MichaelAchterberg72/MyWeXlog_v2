from csp.decorators import csp_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import is_safe_url

from core.decorators import subscription
from users.models import CustomUser

from .forms import (FeedBackForm, FeedBackRespondForm, NoticeForm,
                    NoticeReadForm)
from .models import FeedBack, FeedBackActions, NoticeRead, Notices


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

@login_required()
@subscription(3)
def feedback_list(request):
    actions_qs = FeedBack.objects.all().order_by('-date_captured')

    template = 'feedback/feedback_list.html'
    context = {'actions_qs': actions_qs, }
    return render(request, template, context)


@login_required()
@subscription(3)
def feedback_detail(request, fbd):
    detail_qs = FeedBack.objects.get(slug=fbd)
    response_qs = FeedBackActions.objects.filter(item__slug=fbd).order_by('-date_reviewed')

    template = 'feedback/feedback_detail.html'
    context = {'detail_qs': detail_qs, 'response_qs': response_qs, }
    return render(request, template, context)


@login_required()
@subscription(3)
def feedback_respond(request, fbd):
    feedback = get_object_or_404(FeedBack, slug=fbd)

    form = FeedBackRespondForm(request.POST or None)

    if request.method =='POST':
        if form.is_valid():
            new=form.save(commit=False)
            new.item = feedback
            new.review_by = request.user
            new.save()

            feedback.responded = True
            feedback.save()

            return redirect(reverse('Feedback:FeedbackDetail', kwargs={'fbd':fbd}))
        template = 'feedback/feedback_respond.html'
        context = {'form': form, 'feedback': feedback,}
        return render(request, template, context)

    template = 'feedback/feedback_respond.html'
    context = {'form': form, 'feedback': feedback,}
    return render(request, template, context)
