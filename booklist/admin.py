from django.contrib import admin

from .models import Author, BookList, Format, Genre, Publisher, ReadBy


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    search_fields = ['publisher']


@admin.register(BookList)
class BookListAdmin(admin.ModelAdmin):
    search_fields = ['title', 'publisher__publisher', 'author__name', 'genre__name']


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    search_fields = ['format']


@admin.register(ReadBy)
class ReadByAdmin(admin.ModelAdmin):
    search_fields = ['talent__alias', 'book__title']
