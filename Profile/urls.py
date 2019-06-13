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
]
