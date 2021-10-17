from django.contrib import admin

from .models import Author, BookList, Format, Genre, Publisher, ReadBy


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    pass


@admin.register(BookList)
class BookListAdmin(admin.ModelAdmin):
    pass


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    pass


@admin.register(ReadBy)
class ReadByAdmin(admin.ModelAdmin):
    pass
