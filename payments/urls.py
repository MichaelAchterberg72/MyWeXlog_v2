from django.urls import path


from . import views

app_name = 'Payments'

urlpatterns = [
#    path('home/', views.PaymentsHome, name='PaymentsHome'),
    path('subscription/successful/', views.PayPalSubscriptionReturnView.as_view(), name='paypal-return-view'),
    path('subscription/cancel/', views.PayPalSubscriptionCancelReturnView.as_view(), name='paypal-cancel-view'),
    path('subscription/passive-cancel/', views.PayPalPassiveSubscriptionCancelReturnView.as_view(), name='passive-paypal-cancel-view'),
    path('subscription/active-cancel/', views.PayPalActiveSubscriptionCancelReturnView.as_view(), name='active-paypal-cancel-view'),
    path('subscription/passive/', views.GeneralPassiveSubscriptionView, name='PassiveSubscription'),
    path('subscription/active/', views.GeneralActiveSubscriptionView, name='ActiveSubscription'),
    path('subscription/upgrade/active/', views.PassiveUpgradeActiveSubscriptionView, name='PassiveUpgradeSubscription'),
    path('subscription/beta/passive/', views.BetaGeneralPassiveSubscriptionView, name='BetaPassiveSubscription'),
    path('subscription/beta/active/', views.BetaGeneralActiveSubscriptionView, name='BetaActiveSubscription'),
]
