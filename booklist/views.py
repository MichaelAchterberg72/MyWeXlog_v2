from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import FormView, TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.http import is_safe_url


from django.views.decorators.csrf import csrf_exempt
from csp.decorators import csp_exempt
from django.db.models import Count
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
import operator
from django.db.models import Q
import json
from django.views.generic import (
        TemplateView
)
from django.views.decorators.csrf import csrf_exempt
from core.decorators import subscription

from django.views import generic
import json

from Profile.models import Profile
from .models import BookList, Author, ReadBy, Format, Publisher
from .forms import *

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


#@login_required()
#class BookListHomeView(TemplateView):
    #template_name = 'booklist/home.html'


@login_required()
def add_to_my_list(request, bks):
    book_qs = get_object_or_404(BookList, slug=bks)

    form = AddFromListForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.book = book_qs
            new.talent = request.user
            new.save()
            return redirect(reverse('BookList:BookListHome'))
        else:
            context = {'form': form, 'book_qs': book_qs,}
            template_name = 'booklist/Book_add_from_list.html'
            return render(request, template_name, context)
    else:
        context = {'form': form, 'book_qs': book_qs,}
        template_name = 'booklist/Book_add_from_list.html'
        return render(request, template_name, context)


@login_required()
def BookListHome(request, profile_id=None):
    profile_id = request.user
    ecount = ReadBy.objects.filter(talent=profile_id).aggregate(sum_e=Count('book'))
    books = ReadBy.objects.filter(talent=profile_id).order_by('-date')

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(books, 20)

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

    template_name = 'booklist/booklist_home.html'
    context = {'ecount': ecount, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template_name, context)


@login_required()
def HelpBookListHomeView(request):

    template_name = 'booklist/help_booklist_home.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpBookListView(request):

    template_name = 'booklist/help_booklist.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpBookListSearchView(request):

    template_name = 'booklist/help_booklist_search.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpBookListAddBookReadView(request):

    template_name = 'booklist/help_booklist_add.html'
    context = {}
    return render(request, template_name, context)


@login_required()
def HelpAddBookView(request):

    template_name = 'booklist/help_add_book.html'
    context = {}
    return render(request, template_name, context)


@csp_exempt
#This view is for the profile to display the complete list of books read.
def ProfileBookList(request, tlt):
    info = get_object_or_404(Profile, talent__alias=tlt)
    bkl = ReadBy.objects.filter(talent__alias=tlt).order_by('-date')
    bkl_count = bkl.count()
    tlt = tlt

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(bkl, 20)

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

    template_name = 'booklist/vac_profile_list.html'
    context = {'info': info, 'bkl_count': bkl_count, 'tlt': tlt, 'pageitems': pageitems, 'page_range': page_range}
    return render(request, template_name, context)


def ProfileBackView(request):
    if request.method =='POST':
        next_url=request.POST.get('next', '/')

        if not next_url or not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
           next_url = reverse('MarketPlace:Entrance')

        return HttpResponseRedirect(next_url)


@login_required()
def BookDetailView(request, book):
    info = get_object_or_404(BookList, slug=book)
    detail = BookList.objects.filter(slug=book)
    b_id = detail[:1]
    bk = ReadBy.objects.filter(talent=request.user)
    rbk = bk.filter(book=b_id)

    template_name = 'booklist/book_detail.html'
    context = {'detail': detail, 'info': info, 'rbk': rbk,}
    return render(request, template_name, context)


@login_required()
def BookListView(request):
    bk_obj = BookList.objects.all().order_by('title')
    bcount = bk_obj.aggregate(sum_b=Count('title'))

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    paginator = Paginator(bk_obj, 20)

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

    template_name = 'booklist/books_list.html'
    context = {
             'bcount': bcount,
             'pageitems': pageitems,
             'page_range': page_range
    }
    return render(request, template_name, context)


def BookSearch(request):
    form = BookSearchForm()
    query = None
    results = []
    count = 0
    if 'query' in request.GET:
        form = BookSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = set(BookList.objects.annotate(
                search=SearchVector('title',
                                    'tag__skill',
                                    'author__name',
                                    'publisher__publisher'),
            ).filter(search=query).order_by('title'))

            for q in results:
                count += 1


    template_name= 'booklist/book_search.html'
    context = {
            'form': form,
            'query': query,
            'results': results,
            'count': count,
    }
    return render(request, template_name, context)


@login_required()
def BookReadListView(request):
    list = ReadBy.objects.all().order_by('date')

    template_name = 'booklist/books_read_list.html'
    context = {
            'list': list,
    }
    return render(request, template_name, context)


@csp_exempt
@login_required()
def BookAddView(request):
    if request.method == 'POST':
        form = BookAddForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
            return redirect(reverse('BookList:books-read-new'))
    else:
        form = BookAddForm()

    context = {'form': form}
    template_name = 'booklist/create_new_book.html'
    return render(request, template_name, context)


@csp_exempt
@login_required()
def AddBookView(request):
    if request.method == 'POST':
        form = BookAddForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
            return redirect(reverse('BookList:books-read-new'))
    else:
        form = BookAddForm()

    context = {'form': form}
    template_name = 'booklist/add_new_book.html'
    return render(request, template_name, context)


@login_required()
@csp_exempt
def BookAddPopupView(request):
    form = BookAddForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance=form.save()
            form.save_m2m()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_book");</script>' % (instance.pk, instance))
    else:
        context = {'form':form,}
        template_name = 'booklist/create_new_book.html'
        return render(request, template_name, context)


@login_required()
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


@login_required()
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


@login_required()
@csp_exempt
def FormatCreatePopupView(request):
    form = FormatAddForm(request.POST or None)
    if request.method =='POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance=form.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_type");</script>' % (instance.pk, instance))

    else:
        context = {'form':form,}
        template_name = 'booklist/create_new_format_popup.html'
        return render(request, template_name, context)


@login_required()
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

    else:
        context = {'form':form,}
        template_name = 'booklist/create_new_tag_popup.html'
        return render(request, template_name, context)


@login_required()
@csrf_exempt
def get_author_id(request):
	if request.is_ajax():
		author_name = request.GET['author_name']
		author_id = Author.objects.get(name = author_name).id
		data = {'author_id':author_id,}
		return HttpResponse(json.dumps(data), content_type='application/json')
	return HttpResponse("/")


@login_required()
@csrf_exempt
def get_publisher_id(request):
	if request.is_ajax():
		publisher_publisher = request.GET['publisher_publisher']
		publisher_id = Publisher.objects.get(name = publisher_publisher).id
		data = {'publisher_id':publisher_id,}
		return HttpResponse(json.dumps(data), content_type='application/json')
	return HttpResponse("/")


@login_required()
@csrf_exempt
def get_format_id(request):
	if request.is_ajax():
		format_format = request.GET['format_format']
		format_id = Format.objects.get(name = format_format).id
		data = {'format_id':format_id,}
		return HttpResponse(json.dumps(data), content_type='application/json')
	return HttpResponse("/")


@login_required()
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


@login_required()
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


@login_required()
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


@login_required()
@csp_exempt
def AddBookReadView(request):
    if request.method == 'POST':
        form = AddBookReadForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.talent = request.user
            new.save()
            return redirect(reverse('BookList:BookListHome'))
    else:
        form = AddBookReadForm()

    context = {'form': form}
    template_name = 'booklist/create_new_book_read.html'
    return render(request, template_name, context)

#>>>GenreAdd Popup
@login_required()
@csp_exempt
def GenreAddPopup(request):
    form = GenreAddForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_genre");</script>' % (instance.pk, instance))
        else:
                context = {'form':form,}
                template = 'booklist/genre_add.html'
                return render(request, template, context)

    else:
        context = {'form':form,}
        template = 'booklist/genre_add.html'
        return render(request, template, context)


@csrf_exempt
def get_genre_id(request):
    if request.is_ajax():
        name = request.Get['name']
        name_id = Genre.objects.get(genre = name).id
        data = {'name_id':name_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")
#<<< GenreAdd Popup
