from datetime import datetime

from csp.decorators import csp_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from payments.forms import (ActiveSubscriptionChoiceForm,
                            ExtPayPalEncryptedPaymentsForm,
                            ExtPayPalPaymentsForm,
                            ExtPayPalSharedSecretEncryptedPaymentsForm,
                            PassiveSubscriptionChoiceForm)
from paypal.standard.forms import (PayPalEncryptedPaymentsForm,
                                   PayPalPaymentsForm)
from paypal.standard.ipn.signals import (invalid_ipn_received,
                                         valid_ipn_received)

from .tasks import SubscriptionUpgradeRefund


@method_decorator(csrf_exempt, name='dispatch')
class PayPalSubscriptionReturnView(TemplateView):
    template_name = 'subscription_payments/wexlog_home_3/subscription_successful_return.html'


@method_decorator(csrf_exempt, name='dispatch')
class PayPalSubscriptionCancelReturnView(TemplateView):
    template_name = 'subscription_payments/wexlog_home_3/subscription_cancel_return.html'


@method_decorator(csrf_exempt, name='dispatch')
class PayPalPassiveSubscriptionCancelReturnView(TemplateView):
    template_name = 'subscription_payments/wexlog_home_3/passive_subscription_cancel_return.html'


@method_decorator(csrf_exempt, name='dispatch')
class PayPalActiveSubscriptionCancelReturnView(TemplateView):
    template_name = 'subscription_payments/wexlog_home_3/active_subscription_cancel_return.html'


@method_decorator(csrf_exempt, name='dispatch')
class PayPalPackageBennefitsView(TemplateView):
    template_name = 'subscription_payments/package_bennefits.html'


@login_required
def GeneralPassiveSubscriptionView(request):

    passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "4.99",                      # monthly price
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog Monthly Passive Subscription",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:passive-paypal-cancel-view')),
    }

    six_passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "28.44",                      # monthly price
            "p3": "6",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog 6 Month Passive Subscription",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:passive-paypal-cancel-view')),
    }

    twelve_passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "56.58",                      # monthly price
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "Y",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog 12 Month Passive Subscription",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:passive-paypal-cancel-view')),
    }

    # Create the instance.
    passive_form = PayPalEncryptedPaymentsForm(initial=passive_paypal_dict, button_type="subscribe")
    six_passive_form = PayPalEncryptedPaymentsForm(initial=six_passive_paypal_dict, button_type="subscribe")
    twelve_passive_form = PayPalEncryptedPaymentsForm(initial=twelve_passive_paypal_dict, button_type="subscribe")
    context = {
            "passive_form": passive_form,
            "six_passive_form": six_passive_form,
            "twelve_passive_form": twelve_passive_form,
    }
    template = 'subscription_payments/wexlog_home_3/passive_subscription.html'
    return render(request, template, context)


@login_required
def GeneralActiveSubscriptionView(request):

    month_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "9.75",                      # monthly price
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "0",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog Monthly Active Subscription",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:active-paypal-cancel-view')),
    }

    active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "6.89",                      # monthly price
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog Monthly Active Subscription",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:active-paypal-cancel-view')),
    }

    six_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "39.84",                      # monthly price
            "p3": "6",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog 6 Month Active Subscription",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:active-paypal-cancel-view')),
    }

    twelve_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "79.38",                      # monthly price
            "tax_rate": "0.10",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "Y",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog 12 Month Active Subscription",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:active-paypal-cancel-view')),
    }
    # Create the instance.
    month_active_form = PayPalEncryptedPaymentsForm(initial=month_active_paypal_dict, button_type="subscribe")
    active_form = PayPalEncryptedPaymentsForm(initial=active_paypal_dict, button_type="subscribe")
    six_active_form = PayPalEncryptedPaymentsForm(initial=six_active_paypal_dict, button_type="subscribe")
    twelve_active_form = PayPalEncryptedPaymentsForm(initial=twelve_active_paypal_dict, button_type="subscribe")
    context = {
            "month_active_form": month_active_form,
            "active_form": active_form,
            "six_active_form": six_active_form,
            "twelve_active_form": twelve_active_form,
    }
    template = 'subscription_payments/wexlog_home_3/active_subscription.html'
    return render(request, template, context)


@login_required
def BetaGeneralPassiveSubscriptionView(request):

    beta_passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a1": "0.00",                      # trial period monthly price
            "p1": "12",                        # number months trial period
            "t1": "M",                         # duration of unit ('M' for months)
            "a3": "4.99",                      # monthly price
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog Monthly Passive Subscription - Beta",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:passive-paypal-cancel-view')),
    }

    beta_six_passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a1": "0.00",                      # trial period monthly price
            "p1": "12",                        # number months trial period
            "t1": "M",                         # duration of unit ('M' for months)
            "a3": "28.44",                      # monthly price
            "p3": "6",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog 6 Month Passive Subscription - Beta",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:passive-paypal-cancel-view')),
    }

    beta_twelve_passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a1": "0.00",                      # trial period monthly price
            "p1": "1",                        # number months trial period
            "t1": "Y",                         # duration of unit ('M' for months)
            "a3": "56.58",                      # monthly price
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "Y",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog 12 Month Passive Subscription - Beta",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:passive-paypal-cancel-view')),
    }

    # Create the instance.
    passive_form = PayPalEncryptedPaymentsForm(initial=beta_passive_paypal_dict, button_type="subscribe")
    six_passive_form = PayPalEncryptedPaymentsForm(initial=beta_six_passive_paypal_dict, button_type="subscribe")
    twelve_passive_form = PayPalEncryptedPaymentsForm(initial=beta_twelve_passive_paypal_dict, button_type="subscribe")
    context = {
            "passive_form": passive_form,
            "six_passive_form": six_passive_form,
            "twelve_passive_form": twelve_passive_form,
    }
    template = 'subscription_payments/beta_passive_subscription.html'
    return render(request, template, context)


@login_required
def BetaGeneralActiveSubscriptionView(request):

    beta_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a1": "0.00",                      # trial period monthly price
            "p1": "12",                        # number months trial period
            "t1": "M",                         # duration of unit ('M' for months)
            "a3": "6.89",                      # monthly price
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog Monthly Active Subscription - Beta",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:active-paypal-cancel-view')),
    }

    beta_six_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a1": "0.00",                      # trial period monthly price
            "p1": "12",                        # number months trial period
            "t1": "M",                         # duration of unit ('M' for months)
            "a3": "39.84",                      # monthly price
            "p3": "6",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog 6 Month Active Subscription - Beta",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:active-paypal-cancel-view')),
    }

    beta_twelve_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a1": "0.00",                      # trial period monthly price
            "p1": "1",                        # number months trial period
            "t1": "Y",                         # duration of unit ('M' for months)
            "a3": "79.38",                      # monthly price
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "Y",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog 12 Month Active Subscription - Beta",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:active-paypal-cancel-view')),
    }
    # Create the instance.
    active_form = PayPalEncryptedPaymentsForm(initial=beta_active_paypal_dict, button_type="subscribe")
    six_active_form = PayPalEncryptedPaymentsForm(initial=beta_six_active_paypal_dict, button_type="subscribe")
    twelve_active_form = PayPalEncryptedPaymentsForm(initial=beta_twelve_active_paypal_dict, button_type="subscribe")
    context = {
            "active_form": active_form,
            "six_active_form": six_active_form,
            "twelve_active_form": twelve_active_form,
    }
    template = 'subscription_payments/beta_active_subscription.html'
    return render(request, template, context)


@login_required
def PassiveUpgradeActiveSubscriptionView(request):

    month_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "9.75",                      # monthly price
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "0",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog Monthly Active Single Subscription",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:active-paypal-cancel-view')),
    }

    active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "6.89",                      # monthly price
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog Monthly Active Subscription Upgrade",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:active-paypal-cancel-view')),
    }

    six_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "39.84",                      # monthly price
            "p3": "6",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog 6 Month Active Subscription Upgrade",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:active-paypal-cancel-view')),
    }

    twelve_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "79.38",                      # monthly price
#            "tax_rate": "0.10",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "Y",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user.id,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "MyWeXlog 12 Month Active Subscription Upgrade",
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:active-paypal-cancel-view')),
    }
    # Create the instance.
    month_active_form = PayPalEncryptedPaymentsForm(initial=month_active_paypal_dict, button_type="subscribe")
    active_form = PayPalEncryptedPaymentsForm(initial=active_paypal_dict, button_type="subscribe")
    six_active_form = PayPalEncryptedPaymentsForm(initial=six_active_paypal_dict, button_type="subscribe")
    twelve_active_form = PayPalEncryptedPaymentsForm(initial=twelve_active_paypal_dict, button_type="subscribe")
    context = {
            "month_active_form": month_active_form,
            "active_form": active_form,
            "six_active_form": six_active_form,
            "twelve_active_form": twelve_active_form,
    }
    template = 'subscription_payments/wexlog_home_3/active_subscription_upgrade.html'
    return render(request, template, context)
