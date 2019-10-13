from django.urls import path


from . import views
from .views import *

app_name = 'Public'

urlpatterns = [
    path('home/', views.LandingPageView.as_view(), name='LandingPage'),
    path('about/', views.AboutUsView.as_view(), name='AboutUs'),
    path('privacy/', views.PrivacyView.as_view(), name='Privacy'),
    path('user-agreement/', views.TermsConditionsView.as_view(), name='UserAgreement'),
    path('cookie/', views.CookieView.as_view(), name='Cookies'),
    path('disclaimer/', views.RightToSayNoView.as_view(), name='RightToSayNo'),
    path('contact/', views.ContactUsView, name='ContactUs'),
    path('contact/thank-you/', views.ThankContactView.as_view(), name='ThankContactUs'),
    path('suggestions/', views.SuggestionsView, name='Suggestions'),
    path('help-support/', views.HelpSupportView.as_view(), name='HelpSupport'),
    path('data-protection-officer/', views.DataProtectionView, name='DataProtection'),
]
