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
        path('id/<int:profile_id>/', views.IdentificationView, name='IdView'),
        path('popup/add/idtype/', views.IdTypePopup, name="IdTypeAddPop"),
        path('popup/ajax/get_IdType_id/', views.get_IdType_id, name="AJAX_GetIdTypeID"),
        path('passport/<int:profile_id>/', views.PassportAddView, name='PassportAddView'),
        path('passport/<int:p_id>/<int:profile_id>/edit/', views.PassportEditView, name='PassportEditView'),
        path('language/<int:profile_id>/', views.LanguageAddView, name='LanguageAdd'),
        path('popup/add/language/', views.LanguagePopup, name="LanguagePop"),
        path('popup/ajax/get_language_id/', views.get_language_id, name="AJAX_GetLanguageID"),
        path('language/<int:profile_id>/<int:lang_id>/', views.LanguageEditView, name='LanguageEdit'),
        path('online/delete/<int:pk>/', views.OnlineDelete, name='OnlineDelete'),
        path('passport/delete/<int:pk>/', views.PassportDeleteView, name='PassportDelete'),
        path('phonenumber/delete/<int:pk>/', views.PhoneNumberDelete, name='PhoneDelete'),
        path('file/delete/<int:pk>/', views.FileDelete, name='FileDelete'),
        path('email/delete/<int:pk>/', views.EmailDelete, name='EmailDelete'),
]
