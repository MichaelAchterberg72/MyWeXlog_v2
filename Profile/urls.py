from django.urls import path

from .import views

app_name = 'Profile'

urlpatterns = [
        path('', views.ProfileHome.as_view(), name="ProfileHome"),
        path('view/<int:pk>/', views.ProfileView, name="ProfileView"),
]
