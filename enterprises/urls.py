from django.urls import path


from .import views
from .views import *

app_name = 'Enterprise'

urlpatterns = [
    path('home/', views.EnterpriseHomeView.as_view(), name='EnterpriseHome'),
    path('popup/enterprise/', views.EnterpriseCreatePopupView, name='EnterpriseCreatePopup'),
    path('popup/branch-type/', views.BranchTypeCreatePopupView, name='BranchTypeCreatePopup'),
    path('popup/industry/', views.IndustryCreatePopupView, name='IndustryCreatePopup'),
    path('list/', views.EnterpriseListView, name='EnterpriseList'),
    path('branch/add/', views.BranchAddView, name='BranchAdd'),
    path('enterprise/search/', views.EnterpriseSearch, name='enterprise-search'),
    path('branch/search/', views.BranchSearch, name='branch-search'),
]
