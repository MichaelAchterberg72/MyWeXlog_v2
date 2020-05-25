from django.urls import path


from . import views
from .views import *

app_name = 'Public'

urlpatterns = [
    path('index/', views.HomePageView, name='WexlogHomeIndex'),
    path('site-stats/', views.SiteStatsView, name='WexlogHomeSiteStats'),
    path('about/', views.WexlogHomeAboutView, name='WexlogHomeAbout'),
    path('contact/', views.WexlogHomeContactView, name='WexlogHomeContact'),
    path('post-vacancy/', views.WexlogHomePostVacancyView.as_view(), name='WexlogHomePostVacancy'),
    path('search-candidates/', views.WexlogHomeSearchCandidatesView.as_view(), name='WexlogHomeSearchCandidates'),
    path('short-term/', views.WexlogHomeShortTermView.as_view(), name='WexlogHomeShortTerm'),
    path('permanent/', views.WexlogHomePermanentView.as_view(), name='WexlogHomePermanent'),
    path('market-skills/', views.WexlogHomeMarketSkillsView.as_view(), name='WexlogHomeMarketSkills'),
    path('find-client/', views.WexlogHomeFindClientView.as_view(), name='WexlogHomeFindClient'),
    path('benefits/', views.WexlogHomeBenefitsView.as_view(), name='WexlogHomeBenefits'),
    path('pricing/', views.WexlogHomePricingView.as_view(), name='WexlogHomePricing'),
    path('blog/', views.WexlogHomeBlogView.as_view(), name='WexlogHomeBlog'),
    path('privacy/', views.WexlogHomePrivacyView.as_view(), name='WexlogHomePrivacy'),
    path('user-agreement/', views.WexlogHomeUserAgreementView.as_view(), name='WexlogHomeUserAgreement'),
    path('cookie-policy/', views.WexlogHomeCookiePolicyView.as_view(), name='WexlogHomeCookiePolicy'),
    path('right-to-say-no/', views.WexlogHomeRightToSayNoView.as_view(), name='WexlogHomeRightToSayNo'),
    path('help-support/', views.WexlogHomeHelpSupportView.as_view(), name='WexlogHomeHelpSupport'),
    path('site-suggestions/', views.WexlogHomeSuggestionsView, name='WexlogHomeSuggestions'),
    path('data-protection-officer/', views.WexlogHomeDataPrivacyView, name='WexlogHomeDataPrivacy'),
    path('thank-contact/', views.WexlogHomeThankContactView.as_view(), name='WexlogHomeThankContact'),

#    path('home/', views.LandingPageHomePageView, name='LandingPage'),
#    path('test/', views.HtmlTestView.as_view(), name='Test'),
#    path('home3/', views.LandingPage3View.as_view(), name='LandingPage3'),
#    path('home4/', views.LandingPage4View.as_view(), name='LandingPage4'),
#    path('landing-page/about/', views.AboutUsView.as_view(), name='AboutUs'),
#    path('landing-page/privacy/', views.PrivacyView.as_view(), name='Privacy'),
#    path('landing-page/user-agreement/', views.TermsConditionsView.as_view(), name='UserAgreement'),
#    path('landing-page/cookie/', views.CookieView.as_view(), name='Cookies'),
#    path('landing-page/right-to-say-no/', views.RightToSayNoView.as_view(), name='RightToSayNo'),
    path('contact-us/', views.ContactUsView, name='ContactUs'),
    path('contact-us/thank-you/', views.ThankContactView.as_view(), name='ThankContactUs'),
#    path('landing-page/suggestions/', views.SuggestionsView, name='Suggestions'),
#    path('landing-page/help-support/', views.HelpSupportView.as_view(), name='HelpSupport'),
#    path('data-protection-officer/', views.DataProtectionView, name='DataProtection'),
#    path('landing-page/dpo-contact/', views.DataPrivacyView, name='DataPrivacy'),
#    path('landing-page/capture/', views.CaptureView.as_view(), name='Capture'),
#    path('landing-page/trust-passport/', views.TrustPassportView.as_view(), name='TrustPassport'),
#    path('landing-page/advertise/', views.AdvertiseView.as_view(), name='Advertise'),
#    path('landing-page/post-vacancy/', views.PostVacancyView.as_view(), name='PostVacancy'),
#    path('landing-page/search-candidates/', views.SearchCandidatesView.as_view(), name='SearchCandidates'),
#    path('landing-page/short-term/', views.ShortTermView.as_view(), name='ShortTerm'),
#    path('landing-page/permanent/', views.PermanentView.as_view(), name='Permanent'),
]
