from django.urls import path


from .import views

app_name = 'Trust'

urlpatterns = [
    path('home/', views.TrustHomeView.as_view(), name='TrustHome'),
    path('enterprise/add/', views.EnterpriseTrustAddView, name='EnterpriseTrustAdd'),
    path('talent/add/', views.TalentTrustAddView, name='TalentTrustAdd'),
]
