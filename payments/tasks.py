from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.task import task
from celery.task import Task
from celery.decorators import task
from celery import shared_task

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

from users.models import CustomUserSettings

from datetime import datetime
from datetime import date

from paypal.standard.models import PayPalStandardBase


app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

@app.task
@shared_task
class SubscriptionExpiredTask(Task):

    def run(self, user):

        subject, from_email, to = 'Your Subscription has Expired', settings.CELERY_SYSTEM_EMAIL, user.Email
        html_content = render_to_string('email_templates/email_subscription_expired.html', {'user': user.first_name})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(sunject, text_content, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

# task.register(SubscriptionExpiredTask)


@app.task
@shared_task
class SubscriptionAmountDifferentTask(Task):

    def run(self, user):

        subject, from_email, to = 'Your Payment Amount with PayPal varies to the Subscription Amount', settings.CELERY_SYSTEM_EMAIL, user.Email
        html_content = render_to_string('email_templates/email_subscription_amount_different.html', {'user': user.first_name})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(sunject, text_content, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

# task.register(SubscriptionAmountDifferentTask)


@app.task
@shared_task
class SubscriptionCancelledTask(Task):

    def run(self, user):

        subject, from_email, to = 'Your Subscription has been Cancelled', settings.CELERY_SYSTEM_EMAIL, user.Email
        html_content = render_to_string('email_templates/email_subscription_cancelled.html', {'user': user.first_name})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(sunject, text_content, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

# task.register(SubscriptionCancelledTask)


@app.task
@shared_task
class SubscriptionFailedTask(Task):

    def run(self, user):

        subject, from_email, to = 'Your Subscription failed to be processed', settings.CELERY_SYSTEM_EMAIL, user.Email
        html_content = render_to_string('email_templates/email_subscription_failed.html', {'user': user.first_name})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(sunject, text_content, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

# task.register(SubscriptionCFailedTask)


@app.task
@shared_task
class SubscriptionSignupTask(Task):

    def run(self, user):

        subject, from_email, to = 'WexLog Sign-up Confirmation', settings.CELERY_SYSTEM_EMAIL, user.Email
        html_content = render_to_string('email_templates/email_subscription_signup.html', {'user': user.first_name})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(sunject, text_content, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

# task.register(SubscriptionSignupTask)


@app.task
@shared_task
class SubscriptionRefundTask(Task):

    def run(self, user, refundamount, payment_txn_id):

        subject, from_email, to = 'Refund Subscriber Upgrade', settings.CELERY_SYSTEM_EMAIL, settings.ACCOUNTS_EMAIL
        html_content = render_to_string('email_templates/email_subscription_upgrade_refund.html', {'user': user, 'refundamount': refundamount, 'txn_id': payment_txn_id})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(sunject, text_content, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

# task.register(SubscriptionExpiredTask)


def SubscriptionUpgradeRefund():

    def run(self, user):

        q = PayPalStandardBase.objects.get(custom=user).order_by(-payment_date)
        subscriber = q[1]

        npd = subscriber.next_payment_date
        cd = date.today()
        nsd = cd - npd
        daysdelta = nsd.days

        npd = subscriber.next_payment_date
        opd = subscriber.payment_date
        sd = npd - opd
        subscriptiondaysdelta = sd.days

        amp = subscriber.amount1
        subscriptionperday = amp / subscriptiondaysdelta
        refundamount = subscriptionperday * daysdelta

        payment_txn_id = subscriber.txn_id

        if refundamount >= 0:
            SubscriptionRefundTask(subscriber, refundamount, payment_txn_id)
        else:
            pass
