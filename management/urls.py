from django.urls import path

from . import views

app_name = 'Management'

urlpatterns = [
    path('dashboard/', views.ManagementDashboardView, name="ManagementDashboard"),
    path('vacancies/', views.all_open_vacancies, name="AllVacancies"),
    path('bids/', views.all_bids, name="AllBids"),
    path('issued/', views.work_issued, name="WorkIssued"),
    path('expanded_views/', views.ExpandedViewPercentageView, name="ExpandedViews"),
#    path('flatinvite/', views.FlatInviteview, name="FlatInvite"),
#    path('profile_2_pdf/', views.profile_2_pdf, name="Profile2PDF"),
]
