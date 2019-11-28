from django.urls import path


from .import views

app_name = 'Users'

urlpatterns = [
#        path('home/', views.HomeView, name='Home'),
#        path('user/add/', views.AddUser, name='AddUser'),
#        path('user/list/', views.ListUsers, name='ListUser'),
#        path('user/edit/<int:pk>/', views.EditUser, name='EditUser'),
        path('settings/', views.CustomUserSettingsView, name='CustomUserSettings'),
]
