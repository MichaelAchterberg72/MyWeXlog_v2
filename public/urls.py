from django.urls import path


from . import views
from .views import *

app_name = 'Public'

urlpatterns = [
    path('home/', views.LandingPageView.as_view(), name='LandingPage'),
    path('home3/', views.LandingPage3View.as_view(), name='LandingPage3'),
    path('home4/', views.LandingPage4View.as_view(), name='LandingPage4'),
    path('home5/', views.LandingPage5View.as_view(), name='LandingPage5'),
    path('home6/', views.LandingPage6View.as_view(), name='LandingPage6'),
    path('about/', views.AboutUsView.as_view(), name='AboutUs'),
    path('privacy/', views.PrivacyView.as_view(), name='Privacy'),
    path('user-agreement/', views.TermsConditionsView.as_view(), name='UserAgreement'),
    path('cookie/', views.CookieView.as_view(), name='Cookies'),
    path('right-to-say-no/', views.RightToSayNoView.as_view(), name='RightToSayNo'),
    path('contact/', views.ContactUsView, name='ContactUs'),
    path('contact/thank-you/', views.ThankContactView.as_view(), name='ThankContactUs'),
    path('suggestions/', views.SuggestionsView, name='Suggestions'),
    path('data-privacy/', views.DataPrivacyView, name='DataPrivacy'),
    path('help-support/', views.HelpSupportView.as_view(), name='HelpSupport'),
]
