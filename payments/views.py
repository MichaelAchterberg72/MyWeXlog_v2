from django.shortcuts import render, redirect
from django.urls import reverse
from csp.decorators import csp_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from datetime import datetime

from django.views.generic import (
        TemplateView
)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from paypal.standard.forms import PayPalPaymentsForm
from payments.forms import (
        ExtPayPalPaymentsForm,
        ExtPayPalEncryptedPaymentsForm,
        ExtPayPalSharedSecretEncryptedPaymentsForm,
        PassiveSubscriptionChoiceForm,
        ActiveSubscriptionChoiceForm
)

from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received


class SubscriptionCountrySelectView(TemplateView):
    template_name = 'subscription_payments/subscription_country_select.html'

@method_decorator(csrf_exempt, name='dispatch')
class PayPalSubscriptionReturnView(TemplateView):
    template_name = 'subscription_payments/subscription_successful_return.html'


@method_decorator(csrf_exempt, name='dispatch')
class PayPalSubscriptionCancelReturnView(TemplateView):
    template_name = 'subscription_payments/subscription_cancel_return.html'


@login_required
def AustraliaSubscriptionView(request):
    passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "3.30",                      # monthly price
            "tax_rate": "0.10",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "Passive Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    six_passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "18.15",                      # monthly price
            "tax_rate": "0.10",                # tax rate (confirm works with subscribe button)
            "p3": "6",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "6 Month Passive Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    twelve_passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "35.86",                      # monthly price
            "tax_rate": "0.10",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "Y",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "12 Month Passive Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "4.40",                      # monthly price
            "tax_rate": "0.10",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "Active Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    six_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "24.75",                      # monthly price
            "tax_rate": "0.10",                # tax rate (confirm works with subscribe button)
            "p3": "6",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "6 Month Active Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    twelve_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "49.06",                      # monthly price
            "tax_rate": "0.10",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "Y",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "12 Month Active Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }
    # Create the instance.
    passive_form = PayPalPaymentsForm(initial=passive_paypal_dict, button_type="subscribe")
    six_passive_form = PayPalPaymentsForm(initial=six_passive_paypal_dict, button_type="subscribe")
    twelve_passive_form = PayPalPaymentsForm(initial=twelve_passive_paypal_dict, button_type="subscribe")
    active_form = PayPalPaymentsForm(initial=active_paypal_dict, button_type="subscribe")
    six_active_form = PayPalPaymentsForm(initial=six_active_paypal_dict, button_type="subscribe")
    twelve_active_form = PayPalPaymentsForm(initial=twelve_active_paypal_dict, button_type="subscribe")
    context = {
            "passive_form": passive_form,
            "six_passive_form": six_passive_form,
            "twelve_passive_form": twelve_passive_form,
            "active_form": active_form,
            "six_active_form": six_active_form,
            "twelve_active_form": twelve_active_form,
    }
    template = 'subscription_payments/australia_subscription.html'
    return render(request, template, context)


@login_required
def CanadaQuebecSubscriptionView(request):
    passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "3.30",                      # monthly price
            "tax_rate": "0.9975",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "Passive Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    six_passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "18.15",                      # monthly price
            "tax_rate": "0.9975",                # tax rate (confirm works with subscribe button)
            "p3": "6",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "6 Month Passive Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    twelve_passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "35.85",                      # monthly price
            "tax_rate": "0.9975",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "Y",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "12 Month Passive Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "4.40",                      # monthly price
            "tax_rate": "0.9975",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "Active Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    six_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "24.74",                      # monthly price
            "tax_rate": "0.9975",                # tax rate (confirm works with subscribe button)
            "p3": "6",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "6 Month Active Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    twelve_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "49.05",                      # monthly price
            "tax_rate": "0.9975",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "Y",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "12 Month Active Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }
    # Create the instance.
    passive_form = PayPalPaymentsForm(initial=passive_paypal_dict, button_type="subscribe")
    six_passive_form = PayPalPaymentsForm(initial=six_passive_paypal_dict, button_type="subscribe")
    twelve_passive_form = PayPalPaymentsForm(initial=twelve_passive_paypal_dict, button_type="subscribe")
    active_form = PayPalPaymentsForm(initial=active_paypal_dict, button_type="subscribe")
    six_active_form = PayPalPaymentsForm(initial=six_active_paypal_dict, button_type="subscribe")
    twelve_active_form = PayPalPaymentsForm(initial=twelve_active_paypal_dict, button_type="subscribe")
    context = {
            "passive_form": passive_form,
            "six_passive_form": six_passive_form,
            "twelve_passive_form": twelve_passive_form,
            "active_form": active_form,
            "six_active_form": six_active_form,
            "twelve_active_form": twelve_active_form,
    }
    template = 'subscription_payments/canada_quebec_subscription.html'
    return render(request, template, context)


class CanadaSaskatchewanSubscriptionView(TemplateView):
    template_name = 'subscription_payments/canada_saskatchewan_subscription.html'


@login_required
def NewZealandSubscriptionView(request):
    passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "3.45",                      # monthly price
            "tax_rate": "0.15",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "Passive Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    six_passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "18.98",                      # monthly price
            "tax_rate": "0.15",                # tax rate (confirm works with subscribe button)
            "p3": "6",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "6 Month Passive Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    twelve_passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "37.49",                      # monthly price
            "tax_rate": "0.15",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "Y",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "12 Month Passive Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "4.60",                      # monthly price
            "tax_rate": "0.15",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "Active Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    six_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "25.88",                      # monthly price
            "tax_rate": "0.15",                # tax rate (confirm works with subscribe button)
            "p3": "6",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "6 Month Active Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    twelve_active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "51.29",                      # monthly price
            "tax_rate": "0.15",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "Y",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "12 Month Active Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }
    # Create the instance.
    passive_form = PayPalPaymentsForm(initial=passive_paypal_dict, button_type="subscribe")
    six_passive_form = PayPalPaymentsForm(initial=six_passive_paypal_dict, button_type="subscribe")
    twelve_passive_form = PayPalPaymentsForm(initial=twelve_passive_paypal_dict, button_type="subscribe")
    active_form = PayPalPaymentsForm(initial=active_paypal_dict, button_type="subscribe")
    six_active_form = PayPalPaymentsForm(initial=six_active_paypal_dict, button_type="subscribe")
    twelve_active_form = PayPalPaymentsForm(initial=twelve_active_paypal_dict, button_type="subscribe")
    context = {
            "passive_form": passive_form,
            "six_passive_form": six_passive_form,
            "twelve_passive_form": twelve_passive_form,
            "active_form": active_form,
            "six_active_form": six_active_form,
            "twelve_active_form": twelve_active_form,
    }
    template = 'subscription_payments/new_zealand_subscription.html'
    return render(request, template, context)


@login_required
def SouthAfricaSubscriptionView(request):
    passive_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "3.45",                      # monthly price
            "tax_rate": "0.15",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "Passive Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }

    active_paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "4.60",                      # monthly price
            "tax_rate": "0.15",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "custom": request.user,            # system member pk or braintree pk
            "on0": datetime.now(),             # optional field value (date of subscription)
            "item_name": "Active Subscription",
            "invoice": "12345678",             # invoice number
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('Payments:paypal-return-view')),
            "cancel_return": request.build_absolute_uri(reverse('Payments:paypal-cancel-view')),
    }
    # Create the instance.
    passive_form = PayPalPaymentsForm(initial=passive_paypal_dict, button_type="subscribe")
    active_form = PayPalPaymentsForm(initial=active_paypal_dict, button_type="subscribe")
    context = {"passive_form": passive_form, "active_form": active_form}
    template = "subscription_payments/south_africa_subscription.html"
    return render(request, template, context)
