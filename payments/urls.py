from django.urls import path


from . import views

app_name = 'Payments'

urlpatterns = [
#    path('home/', views.PaymentsHome, name='PaymentsHome'),
    path('subscription/country-select/', views.SubscriptionCountrySelectView.as_view(), name='SubscriptionCountrySelect'),
    path('subscription/select/', views.SubscriptionSelectView.as_view(), name='SubscriptionSelect'),
    path('subscription/successful/', views.PayPalSubscriptionReturnView.as_view(), name='paypal-return-view'),
    path('subscription/cancel/', views.PayPalSubscriptionCancelReturnView.as_view(), name='paypal-cancel-view'),
    path('subscription/passive-cancel/', views.PayPalPassiveSubscriptionCancelReturnView.as_view(), name='passive-paypal-cancel-view'),
    path('subscription/active-cancel/', views.PayPalActiveSubscriptionCancelReturnView.as_view(), name='active-paypal-cancel-view'),
    path('subscription/passive/', views.GeneralPassiveSubscriptionView, name='PassiveSubscription'),
    path('subscription/active/', views.GeneralActiveSubscriptionView, name='ActiveSubscription'),
    path('subscription/australia/', views.AustraliaSubscriptionView, name='SubscriptionAustralia'),
    path('subscription/canada-quebec/', views.CanadaQuebecSubscriptionView, name='SubscriptionCanadaQuebec'),
    path('subscription/canada-saskatchewan/', views.CanadaSaskatchewanSubscriptionView.as_view(), name='SubscriptionCanadaSaskatchewan'),
    path('subscription/new-zealand/', views.NewZealandSubscriptionView, name='SubscriptionNewZealand'),
    path('subscription/south-africa/', views.SouthAfricaSubscriptionView, name='SubscriptionSouthAfrica'),

]
