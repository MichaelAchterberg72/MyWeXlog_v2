from django.urls import path


from . import views
from .views import *

app_name = 'Project'

urlpatterns = [
    path('home/', views.ProjectListHome, name='ProjectHome'),

    path('help/project-home/', views.HelpProjectHomeView, name='HelpProjectHome'),
    path('help/project-add', views.HelpProjectAddView, name='HelpProjectAdd'),
    path('help/project-search/', views.HelpProjectSearchView, name='HelpProjectSearch'),
    path('help/project-detail/', views.HelpProjectDetailView, name='HelpProjectDetail'),

    path('detail/<slug:prj>/', views.ProjectDetailView, name='ProjectDetail'),
    path('add/', views.ProjectAddView, name='ProjectAdd'),
    path('edit/project/<slug:prj>/', views.ProjectEditView, name="EditProject"),
    path('hours/<slug:prj>/', views.HoursWorkedOnProject, name='HoursOnProject'),
    path('talent/<slug:prj>/<slug:corp>/', views.EmployeesOnProject, name='TltOnProject'),
    path('experience/detail/<slug:prj>/', views.WorkExperienceDetail, name='DetailExperienceOnProject'),

    path('list/', views.ProjectListView, name='ProjectList'),
    path('search/', views.ProjectSearch, name='Project-Search'),
    path('popup/project/add/', views.ProjectAddPopup, name="ProjectAddPop"),
    path('popup/ajax/get_project_id/', views.get_project_id, name="AJAX_GetProjectID"),

    path('experience/detail/message/<int:pk>/', views.AutofillMessage, name="DetailMessage"),
]
