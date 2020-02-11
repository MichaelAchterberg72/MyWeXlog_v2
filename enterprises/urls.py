from django.urls import path


from .import views
from .views import *

app_name = 'Enterprise'

urlpatterns = [
    path('home/', views.EnterpriseHome, name="EnterpriseHome"),
    #pop-ups
    path('popup/add/', views.EnterpriseAddPopup, name="EnterpriseAddPop"),
    path('add/', views.EnterpriseAddView, name="EnterpriseAdd"),
    path('popup/ajax/get_enterprise_id/', views.get_enterprise_id, name="AJAX_GetEnterpriseID"),
    path('popup/industry/add/', views.IndustryAddPopup, name="IndustryAddPop"),
    path('popup/ajax/get_industry_id/', views.get_industry_id, name="AJAX_GetIndustryID"),
    path('popup/branchtype/add/', views.BranchTypeAddPopup, name="BranchTypeAddPop"),
    path('popup/ajax/get_branchtype_id/', views.get_branchtype_id, name="AJAX_GetBranchTypeID"),
    path('branch/popadd/', views.BranchAddPopView, name="BranchAddPop"),
    path('popup/ajax/get_branch_id/', views.get_branch_id, name="AJAX_GetBranchID"),

    path('add/branch/<slug:cmp>/', views.BranchAddView, name="AddBranch"),
    path('edit/branch/<slug:bch>/', views.BranchEditView, name="EditBranch"),
    path('branches/<slug:cmp>/', views.BranchListView, name='BranchList'),
    path('branches/detail/<slug:bch>/', views.BranchDetailView, name='BranchDetail'),
    path('branch/add/', views.FullBranchAddView, name="FullBranchAdd"),

]
