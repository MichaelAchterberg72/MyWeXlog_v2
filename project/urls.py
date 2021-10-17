from django.urls import path

from . import views
from .views import *

app_name = 'Project'

urlpatterns = [
    path('home/', views.ProjectDashboard, name='ProjectDashboard'),
    path('personal-projects/', views.ProjectHome, name='ProjectHome'),
    path('full-list/', views.ProjectListHome, name='ProjectList'),
    path('personal-details/<slug:prj>/<slug:co>/<slug:bch>/', views.ProjectPersonalDetailsView, name='ProjectPersonal'),
    path('personal-project/add/', views.ProjectPersonalDetailsAddView, name='ProjectPersonalAdd'),
    path('personal-project/project-list/add/<slug:prj>', views.ProjectPersonalDetailsAddPopulatedView, name='ProjectPersonalAddPopulated'),
    path('personal-project/delete/<int:ppj>', views.PersonalProejctDeleteView, name='ProjectPersonalDelete'),

    path('help/project-home/', views.HelpProjectHomeView, name='HelpProjectHome'),
    path('help/project-add', views.HelpProjectAddView, name='HelpProjectAdd'),
    path('help/project-search/', views.HelpProjectSearchView, name='HelpProjectSearch'),
    path('help/project-detail/', views.HelpProjectDetailView, name='HelpProjectDetail'),

    path('detail/<slug:prj>/', views.ProjectDetailView, name='ProjectDetail'),
    path('project-associated-skill-stats/<slug:prj>/<int:skl>/', views.project_associated_skill_stats, name='ProjectAssociatedSkillStats'),
    path('add/', views.ProjectAddView, name='ProjectAdd'),
    path('edit/project/<slug:prj>/', views.ProjectEditView, name="EditProject"),
    path('hours/<slug:prj>/', views.HoursWorkedOnProject, name='HoursOnProject'),
    path('talent/<slug:prj>/<slug:corp>/', views.EmployeesOnProject, name='TltOnProject'),
    path('experience/detail/<slug:prj>/', views.WorkExperienceDetail, name='DetailExperienceOnProject'),

#    path('list/', views.ProjectListView, name='ProjectList'),
    path('search/', views.ProjectSearch, name='Project-Search'),
    path('popup/project/add/', views.ProjectAddPopup, name="ProjectAddPop"),
    path('popup/project-full/add/', views.ProjectFullAddPopup, name="ProjectFullAddPop"),

     path('popup/personal-project/add/', views.ProjectPersonalDetailsAddPopupView, name='ProjectPersonalAddPop'),
    path('popup/ajax/get_p_project_id/', views.get_p_project_id, name="AJAX_GetPprojectID"),

     path('personal-project/add/', views.ProjectPersonalDetailsAddView, name='ProjectPersonalAdd'),

    path('experience/detail/message/<int:pk>/', views.AutofillMessage, name="DetailMessage"),
    # Ajax
    path('fields/project_data.json',
        ProjectDataJsonView.as_view(), name="project_data_json"),
]
