from django.shortcuts import render
from django.urls import reverse
from csp.decorators import csp_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from datetime import datetime

from django.views.generic import (
        TemplateView
)
from django.views.decorators.csrf import csrf_exempt

from paypal.standard.forms import PayPalPaymentsForm
from payments.forms import (
        ExtPayPalPaymentsForm,
        ExtPayPalEncryptedPaymentsForm,
        ExtPayPalSharedSecretEncryptedPaymentsForm
)
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class PayPalSubscriptionReturnView(TemplateView):

    template_name = 'subscription_payments/subscription_successful_return.html'


class PayPalSubscriptionCancelReturnView(TemplateView):
    template_name = 'subscription_payments/subscription_cancel_return.html'


class AustraliaSubscriptionView(TemplateView):
    template_name = 'subscription_payments/australia_subscription.html'


def PayPalAustraliaPassive(request):
    paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "USD",
            "a3": "3.30",                      # monthly price
            "tax_rate": "0.10",                # tax rate (confirm works with subscribe button)
            "p3": "1",                         # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "srt": "12",                       # number of times the payment will recur
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
    # Create the instance.
    form = ExtPayPalPaymentsForm(initial=paypal_dict, button_type="subscribe")
    context = {"form": form.render()}  # set sandbox to render() for production
    template = "subscription_payments/australia_passive_subscription.html"
    return render(request, template, context)


class CanadaQuebecSubscriptionView(TemplateView):
    template_name = 'subscription_payments/canada_quebec_subscription.html'


class CanadaSaskatchewanSubscriptionView(TemplateView):
    template_name = 'subscription_payments/canada_saskatchewan_subscription.html'


class NewZealandSubscriptionView(TemplateView):
    template_name = 'subscription_payments/new_zealand_subscription.html'


class SouthAfricaSubscriptionView(TemplateView):
    template_name = 'subscription_payments/south_africa_subscription.html'
