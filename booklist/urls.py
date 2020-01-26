from django.urls import path


from . import views

app_name = 'BookList'

urlpatterns = [
    path('home/', views.BookListHome, name='BookListHome'),
    path('books/', views.BookListView, name='books-list'),
    path('books/search/', views.BookSearch, name='book-search'),
    path('books/detail/<int:book_id>/', views.BookDetailView, name='BookDetail'),
    path('books/read/', views.BookReadListView, name='books-read-list'),
    path('popup/author/', views.AuthorCreatePopupView, name='AuthorCreatePopup'),
    path('add/author/', views.AuthorAddView, name='AuthorCreate'),
    path('popup/publisher/', views.PublisherCreatePopupView, name='PublisherCreatePopup'),
    path('add/publisher/', views.PublisherAddView, name='PublisherCreate'),
    path('popup/skilltag/', views.TagCreatePopupView, name='TagCreatePopup'),
    path('popup/ajax/get_author_id', views.get_author_id, name='get_author_id'),
    path('popup/ajax/get_publisher_id', views.get_publisher_id, name='get_publisher_id'),
    path('popup/ajax/get_format_id', views.get_format_id, name='get_format_id'),
    path('add/books/', views.BookAddView, name='books-new'),
    path('popup/add/books/', views.BookAddPopupView, name='booksNewPopup'),
    path('add/books-read/', views.AddBookReadView, name='books-read-new'),
    path('add/book-type/', views.FormatAddView, name='FormatCreate'),
    path('popup/book-type/', views.FormatCreatePopupView, name='FormatCreatePopup'),
    path('booklist/<slug:tlt>/', views.ProfileBookList, name='VPBL'),
    path('booklist-back/', views.ProfileBackView, name='BLB'),
    path('popup/genre/', views.GenreAddPopup, name='GenreCreatePopup'),
    path('popup/ajax/get_genre_id', views.get_genre_id, name='get_genre_id'),

]
