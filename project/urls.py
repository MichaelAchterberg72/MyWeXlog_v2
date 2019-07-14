from django.urls import path


from . import views
from .views import *

app_name = 'Project'

urlpatterns = [
    path('home/', views.ProjectListHome, name='ProjectHome'),
    path('detail/<int:project_id>/', views.ProjectDetailView, name='ProjectDetail'),
    path('add/', views.ProjectAddView, name='ProjectAdd'),
    path('edit/project/<int:e_id>/', views.ProjectEditView, name="EditProject"),
    path('hours/<int:project_id>/', views.HoursWorkedOnProject, name='HoursOnProject'),
    path('experience/detail/<int:workexperience_id>/', views.WorkExperienceDetail, name='DetailExperienceOnProject'),
    path('list/', views.ProjectListView, name='ProjectList'),
    path('search/', views.ProjectSearch, name='Project-Search'),
    path('popup/project/add/', views.ProjectAddPopup, name="ProjectAddPop"),
    path('popup/ajax/get_project_id/', views.get_project_id, name="AJAX_GetProjectID"),
    path('experience/detail/message/<int:pk>/', views.AutofillMessage, name="DetailMessage"),
]
