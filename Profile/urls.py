from django.urls import path

from .import views

app_name = 'Profile'

urlpatterns = [
        path('', views.ProfileHome.as_view(), name="ProfileHome"),
        path('view/<int:profile_id>/', views.ProfileView, name="ProfileView"),
        path('edit/<int:profile_id>/', views.ProfileEditView, name="ProfileEdit"),
        path('email/<int:profile_id>/', views.EmailEditView, name='EmailEdit'),
        path('email/<int:profile_id>/<int:email_id>/', views.EmailStatusView, name='EmailStatus'),
        path('address/physical/<int:profile_id>/', views.PhysicalAddressView, name='PhysicalAddress'),
        path('address/postal/<int:profile_id>/', views.PostalAddressView, name='PostalAddress'),
        path('phone/add/<int:profile_id>/', views.PhoneNumberAdd, name='PhoneNumberAdd'),
        path('online/add/<int:profile_id>/', views.OnlineProfileAdd, name='OnlineProfileAdd'),
        path('popup/add/', views.ProfileTypePopup, name="ProfileTypeAddPop"),
        path('popup/ajax/get_site_id/', views.get_SiteType_id, name="AJAX_GetSiteTypeID"),
        path('file/<int:profile_id>/', views.FileUploadView, name='FileUploadView'),
]
