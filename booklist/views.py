from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import FormView, TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from csp.decorators import csp_exempt
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
import operator
from django.db.models import Q
import json
from django.views.generic import (
        ListView,
        DetailView,
        CreateView,
        UpdateView,
        TemplateView
)
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
import json


from .models import BookList, Author, ReadBy, Format, Publisher
from .forms import *

# Create your views here.

class BookListHomeView(TemplateView):
    template_name = 'booklist/home.html'


@login_required
def BookListView(request):
    list = BookList.objects.all().order_by('title')
    template_name = 'booklist/books_list.html'
    paginate_by = 10  # if pagination is desired'
    context = {
            'list': list,
    }
    return render(request, template_name, context)

"""
class BookSearchListView(ListView):
    model = BookList
    paginate_by = 10

    def get_queryset(self):
        qs = BookList.objects.all()

        keywords = self.request.GET.get('q')
        if keywords:
            query = SearchQuery(keywords)
            vector = SearchVector('title', 'tag', 'author', 'publisher')
            qs = qs.annotate(search=vector).filter(search=query)
            qs = qs.annotate(rank=SearchRank(vector, query)).order_by('-rank')

        return qs
"""

def BookSearch(request):
    form = BookSearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = BookSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = BookList.objects.annotate(
                search=SearchVector('title', 'tag', 'author', 'publisher'),
            ).filter(search=query)

    template_name= 'booklist/book_search.html'
    context = {
            'form': form,
            'query': query,
            'results': results
    }
    return render(request, template_name, context)

@login_required
def BookReadListView(request):
    list = ReadBy.objects.all().order_by('date')
    template_name = 'booklist/books_read_list.html'
    paginate_by = 10  # if pagination is desired'
    context = {
            'list': list,
    }
    return render(request, template_name, context)


@csp_exempt
@login_required
def BookAddView(request):
    if request.method == 'POST':
        form = BookAddForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
#            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
#                    next_url = reverse('BookListView:books_list')
#            return HttpResponseRedirect(next_url)
            return redirect(reverse('BookList:books-read-new'))
    else:
        form = BookAddForm()

    context = {'form': form}
    template_name = 'booklist/create_new_book.html'
    return render(request, template_name, context)


@login_required
@csp_exempt
def AuthorCreatePopupView(request):
    form = AuthorAddForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance=form.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_author");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template_name = 'booklist/create_new_author_popup.html'
        return render(request, template_name, context)


@login_required
@csp_exempt
def PublisherCreatePopupView(request):
    form = PublisherAddForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance=form.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_publisher");</script>' % (instance.pk, instance))

    else:
        context = {'form':form,}
        template_name = 'booklist/create_new_publisher_popup.html'
        return render(request, template_name, context)


@login_required
@csp_exempt
def FormatCreatePopupView(request):
    form = FormatAddForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance=form.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_format");</script>' % (instance.pk, instance))

    else:
        context = {'form':form,}
        template_name = 'booklist/create_new_format_popup.html'
        return render(request, template_name, context)


@login_required
@csp_exempt
def TagCreatePopupView(request):
    form = TagAddForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance=form.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_tag");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template_name = 'booklist/create_new_tag_popup.html'
        return render(request, template_name, context)


@login_required
@csrf_exempt
def get_author_id(request):
	if request.is_ajax():
		author_name = request.GET['author_name']
		author_id = Author.objects.get(name = author_name).id
		data = {'author_id':author_id,}
		return HttpResponse(json.dumps(data), content_type='application/json')
	return HttpResponse("/")


@login_required
@csrf_exempt
def get_publisher_id(request):
	if request.is_ajax():
		publisher_publisher = request.GET['publisher_publisher']
		publisher_id = Publisher.objects.get(name = publisher_publisher).id
		data = {'publisher_id':publisher_id,}
		return HttpResponse(json.dumps(data), content_type='application/json')
	return HttpResponse("/")


@login_required
@csrf_exempt
def get_format_id(request):
	if request.is_ajax():
		format_format = request.GET['format_format']
		format_id = Format.objects.get(name = format_format).id
		data = {'format_id':format_id,}
		return HttpResponse(json.dumps(data), content_type='application/json')
	return HttpResponse("/")


@login_required
def AuthorAddView(request):
    if request.method == 'POST':
        form = AuthorAddForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
            return redirect(reverse('BookList:BookListHome'))
    else:
        form = AuthorAddForm()

    context = {'form':form}
    template_name = 'booklist/create_new_author.html'
    return render(request, template_name, context)


@login_required
def PublisherAddView(request):
    if request.method == 'POST':
        form = PublisherAddForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()

            return redirect(reverse('BookList:BookListHome'))
    else:
        form = PublisherAddForm()

    context = {'form': form}
    template_name = 'booklist/create_new_publisher.html'
    return render(request, template_name, context)


@login_required
def FormatAddView(request):
    if request.method == 'POST':
        form = FormatAddForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()

            return redirect(reverse('BookList:BookListHome'))
    else:
        form = FormatAddForm()

    context = {'form': form,}
    template_name = 'booklist/create_new_format.html'
    return render(request, template_name, context)


@login_required
@csp_exempt
def AddBookReadView(request):
    if request.method == 'POST':
        form = AddBookReadForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
#            if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
#                    next_url = reverse('BookListView:books_list')
#            return HttpResponseRedirect(next_url)
            return redirect(reverse('BookList:books-read-list'))
    else:
        form = AddBookReadForm()

    context = {'form': form}
    template_name = 'booklist/create_new_book_read.html'
    return render(request, template_name, context)
