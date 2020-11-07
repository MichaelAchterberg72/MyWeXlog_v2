from django.urls import path


from .import views

app_name = 'Corporate'

urlpatterns = [
    path('select/', views.corporate_select, name='CorpSelect'),
    path('<slug:cor>/dashboard/', views.dashboard_corporate, name='DashCorp'),
    path('org-view/', views.org_structure_view, name='OrgView'),
    path('<slug:cor>/org-add/', views.org_structure_add, name='OrgAdd'),
    #Staff
    path('<slug:cor>/org-staff/', views.staff_manage, name='StaffManage'),
    path('<slug:cor>/org/<slug:tlt>/<slug:bch>/', views.staff_include, name='StaffInclude'),
    path('<slug:cor>/staff-add/', views.staff_add, name='StaffAdd'),
    path('<slug:cor>/staff/current/', views.staff_current, name='StaffCurrent'),
    path('<slug:cor>/staff-search/', views.staff_search, name='StaffSearch'),
    path('staff-actions/', views.staff_actions, name='StaffActions'),
    path('<slug:cor>/admin/', views.admin_staff, name='CorpAdmin'),
    path('admin-permission/', views.admin_permission, name='AdminPerm'),
    path('<slug:cor>/user-hidden/', views.talent_hidden, name='Hidden'),
    path('hidden-actions/', views.hidden_actions, name='HiddenActions'),
    path('<slug:cor>/staff-past/', views.past_staff, name='StaffPast'),

    #Departments
    path('<slug:cor>/<str:dept>/department-dashboard/', views.org_department_dashboard, name='OrgDepartment'),
    #Department Skills
    path('<slug:cor>/<str:dept>/department-skills-current/', views.dept_skills_current, name='DeptSkillsCurrent'),
    path('<slug:cor>/<str:dept>/department-skills-resigned/', views.dept_skills_resigned, name='DeptSkillsResigned'),
    path('<slug:cor>/<str:dept>/department-skills-freelance/', views.dept_skills_freelance, name='DeptSkillsFreelance'),
    path('<slug:cor>/<str:dept>/department-skills-not-utilised/', views.dept_skills_not_utilised, name='DeptSkillsNotUtilised'),
    #skills detail page
    path('<slug:cor>/<str:dept>/<int:skl>/department-skill-detail/', views.dept_skill_dashboard, name='DeptSkillDashboard'),
    path('<slug:cor>/<str:dept>/<int:skl>/department-skill-current-staff/', views.dept_skill_current_staff, name='DeptSkillCurrentStaff'),
    path('<slug:cor>/<str:dept>/<int:skl>/department-skill-past-staff/', views.dept_skill_past_staff, name='DeptSkillPastStaff'),
    #Help pages
    path('dashboard-staff/', views.help_dash_staff, name='HelpDashStaff'),
]
