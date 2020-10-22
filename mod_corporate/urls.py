from django.urls import path


from .import views

app_name = 'Corporate'

urlpatterns = [
    path('dashboard/', views.dashboard_corporate, name='DashCorp'),
    path('org-view/', views.org_structure_view, name='OrgView'),
    path('<slug:cor>/org-add/', views.org_structure_add, name='OrgAdd'),
    #Staff
    path('<slug:cor>/org-staff/', views.staff_manage, name='StaffManage'),
    path('<slug:cor>/org/<slug:tlt>/', views.staff_include, name='StaffInclude'),
    path('<slug:cor>/staff/current/', views.staff_current, name='StaffCurrent'),
    path('<slug:cor>/staff-search/', views.staff_search, name='StaffSearch'),
    path('<slug:cor>/staff/Admin/', views.staff_admin, name='StaffAdmn'),
    path('<slug:cstf>/staff-mka/', views.staff_makeadmin, name='StaffMkAdmn'),
    path('<slug:cstf>/staff-rem/', views.staff_remove, name='StaffRemove'),
    path('<slug:cor>/admin/', views.admin_staff, name='CorpAdmin'),
    path('admin-permission/', views.admin_permission, name='AdminPerm'),
    #Departments
    path('<slug:cor>/<str:dept>/department-dashboard/', views.org_department_dashboard, name='OrgDepartment'),
]
