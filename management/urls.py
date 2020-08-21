from django.urls import path


from .import views

app_name = 'Management'

urlpatterns = [
    path('dashboard/', views.ManagementDashboardView, name="ManagementDashboard"),
#    path('flatinvite/', views.FlatInviteview, name="FlatInvite"),
#    path('profile_2_pdf/', views.profile_2_pdf, name="Profile2PDF"),
]
