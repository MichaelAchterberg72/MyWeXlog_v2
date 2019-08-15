from django.urls import path


from . import views

app_name = 'Payments'

urlpatterns = [
#    path('home/', views.PaymentsHome, name='PaymentsHome'),
    path('subscription/successful/', views.PayPalSubscriptionReturnView.as_view(), name='paypal-return-view'),
    path('subscription/cancel/', views.PayPalSubscriptionCancelReturnView.as_view(), name='paypal-cancel-view'),
    path('subscription/australia/', views.AustraliaSubscriptionView.as_view(), name='SubscriptionAustralia'),
    path('subscription/australia/passive/', views.PayPalAustraliaPassive, name='SubscriptionPassiveAustralia'),
    path('subscription/canada-quebec/', views.CanadaQuebecSubscriptionView.as_view(), name='SubscriptionCanadaQuebec'),
    path('subscription/canada-saskatchewan/', views.CanadaSaskatchewanSubscriptionView.as_view(), name='SubscriptionCanadaSaskatchewan'),
    path('subscription/new-zealand/', views.NewZealandSubscriptionView.as_view(), name='SubscriptionNewZealand'),
    path('subscription/south-africa/', views.SouthAfricaSubscriptionView.as_view(), name='SubscriptionSouthAfrica'),
]
