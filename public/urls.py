from django.urls import path


from . import views
from .views import *

app_name = 'Public'

urlpatterns = [
    path('home/', views.HomePageView, name='LandingPage'),
    path('test/', views.HtmlTestView.as_view(), name='Test'),
    path('home3/', views.LandingPage3View.as_view(), name='LandingPage3'),
    path('home4/', views.LandingPage4View.as_view(), name='LandingPage4'),
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
    path('dpo-contact/', views.DataPrivacyView, name='DataPrivacy'),
    path('capture/', views.CaptureView.as_view(), name='Capture'),
    path('trust-passport/', views.TrustPassportView.as_view(), name='TrustPassport'),
    path('advertise/', views.AdvertiseView.as_view(), name='Advertise'),
    path('post-vacancy/', views.PostVacancyView.as_view(), name='PostVacancy'),
    path('search-candidates/', views.SearchCandidatesView.as_view(), name='SearchCandidates'),
    path('short-term/', views.ShortTermView.as_view(), name='ShortTerm'),
    path('permanent/', views.PermanentView.as_view(), name='Permanent'),
]
