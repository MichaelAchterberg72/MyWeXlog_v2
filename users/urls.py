from django.urls import path

from . import views

app_name = 'Users'

urlpatterns = [
#        path('home/', views.HomeView, name='Home'),
#        path('user/add/', views.AddUser, name='AddUser'),
#        path('user/list/', views.ListUsers, name='ListUser'),
#        path('user/edit/<int:pk>/', views.EditUser, name='EditUser'),
        path('settings/', views.CustomUserSettingsView, name='CustomUserSettings'),
        path('account-delete/', views.ProfileDeleteView, name='DeleteUser'),
        path('right-to-say-no/', views.RightToSayNoView, name='RightToSayNo'),
        path('user-agreement/', views.UserAgreementView, name='UserAgreement'),
        path('privacy-policy/', views.PrivacyPolicyView, name='PrivacyPolicy'),
        path('login-user-agreement/', views.LoginUserAgreementView, name='LoginUserAgreement'),
        path('login-privacy-policy/', views.LoginPrivacyView, name='LoginPrivacyPolicy'),
        path('login-cookie-policy/', views.LoginCookieView, name='LoginCookiePolicy'),
]
