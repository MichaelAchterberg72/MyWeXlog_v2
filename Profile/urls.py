from django.urls import path

from .import views

app_name = 'Profile'

urlpatterns = [
        path('', views.ProfileHome.as_view(), name="ProfileHome"),
        path('view/<int:profile_id>/', views.ProfileView, name="ProfileView"),
        path('edit/<int:profile_id>/', views.ProfileEditView, name="ProfileEdit"),
        path('email/<int:profile_id>/', views.EmailEditView, name='EmailEdit'),
        #>>>Company popup
        path('popup/company/', views.CompanyAddPopup, name="CompanyAddPop"),
        path('popup/ajax/get_company_id/', views.get_company_id, name="AJAX_GetCompanyID"),
        #<<<Company Popup
]
