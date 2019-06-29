from django.urls import path


from . import views
from .views import *

app_name = 'Project'

urlpatterns = [
    path('home/', views.ProjectListHome, name='ProjectHome'),
    path('books/detail/<int:project_id>/', views.ProjectDetailView, name='ProjectDetail'),
    path('add/', views.ProjectAddView, name='ProjectAdd'),
    path('edit/project/<int:e_id>/', views.ProjectEditView, name="EditProject"),
    path('list/', views.ProjectListView, name='ProjectList'),
    path('search/', views.ProjectSearch, name='Project-Search'),
]
