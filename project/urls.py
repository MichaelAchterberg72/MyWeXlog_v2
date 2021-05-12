from django.urls import path


from . import views
from .views import *

app_name = 'Project'

urlpatterns = [
    path('home/', views.ProjectHome, name='ProjectHome'),
    path('full-list/', views.ProjectListHome, name='ProjectList'),
    path('personal-details/<slug:prj>/<slug:co>/<slug:bch>/', views.ProjectPersonalDetailsView, name='ProjectPersonal'),

    path('help/project-home/', views.HelpPersonalProjectView, name='HelpPersonalProject'),
    path('help/project-overview/', views.HelpProjectOverviewView, name='HelpProjectOverview'),
    path('help/project-list/', views.HelpProjectHomeView, name='HelpProjectHome'),
    path('help/project-add', views.HelpProjectAddView, name='HelpProjectAdd'),
    path('help/project-search/', views.HelpProjectSearchView, name='HelpProjectSearch'),
    path('help/project-detail/', views.HelpProjectDetailView, name='HelpProjectDetail'),

    path('detail/<slug:prj>/', views.ProjectDetailView, name='ProjectDetail'),
    path('add/', views.ProjectAddView, name='ProjectAdd'),
    path('edit/project/<slug:prj>/', views.ProjectEditView, name="EditProject"),
    path('hours/<slug:prj>/', views.HoursWorkedOnProject, name='HoursOnProject'),
    path('talent/<slug:prj>/<slug:corp>/', views.EmployeesOnProject, name='TltOnProject'),
    path('experience/detail/<slug:prj>/', views.WorkExperienceDetail, name='DetailExperienceOnProject'),

#    path('list/', views.ProjectListView, name='ProjectList'),
    path('search/', views.ProjectSearch, name='Project-Search'),
    path('popup/project/add/', views.ProjectAddPopup, name="ProjectAddPop"),
    path('popup/ajax/get_project_id/', views.get_project_id, name="AJAX_GetProjectID"),

    path('experience/detail/message/<int:pk>/', views.AutofillMessage, name="DetailMessage"),

    #Project Task
    path('task/list/<slug:ppds>/<slug:prj>/<slug:co>/<slug:bch>/', views.action_project_tasks, name="ProjectTaskList"),
    path('action-project-task/<int:pb>/<slug:ppds>/<slug:prj>/<slug:co>/<slug:bch>/', views.action_current_task, name='ActionProjectTask'),
    path('add/task/<slug:ppd>/', views.ProjectTaskAddView, name="AddProjectTask"),
    path('add/task/billing/<slug:ppdt>/', views.ProjectTaskBillingAddView, name="AddProjectTaskBilling"),
    path('not-current-project-task/<int:pb>/<slug:prj>/<slug:co>/<slug:bch>/', views.not_current_task, name='NotCurrentProjectTask'),
    path('edit-project-task-billing/<int:pb>/<slug:ppdts>/<slug:prj>/<slug:co>/<slug:bch>/', views.edit_billing_rate_pd, name='EditProjectTaskBilling'),
    path('edit-project-task-billing-full-list/<int:pb>/<slug:ppds>/<slug:ppdts>/<slug:prj>/<slug:co>/<slug:bch>/', views.edit_billing_rate_fl, name='EditProjectTaskBillingFL'),
]
