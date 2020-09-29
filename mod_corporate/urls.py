from django.urls import path


from .import views

app_name = 'Corporate'

urlpatterns = [
    path('dashboard/', views.dashboard_corporate, name='DashCorp'),
    path('org-view/', views.org_structure_view, name='OrgView'),
    path('org-add/<slug:cor>/', views.org_structure_add, name='OrgAdd'),
]
