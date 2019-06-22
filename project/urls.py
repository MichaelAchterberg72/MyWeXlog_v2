from django.urls import path


from . import views
from .views import *

app_name = 'Project'

urlpatterns = [
    path('home/', views.ProjectHomeView.as_view(), name='ProjectHome'),
    path('add/', views.ProjectAddView, name='ProjectAdd'),
    path('list/', views.ProjectListView, name='ProjectList'),
    path('search/', views.ProjectSearch, name='Project-Search'),
]
