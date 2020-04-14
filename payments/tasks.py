from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.task import task
from celery.task import Task
from celery.decorators import task
from celery import shared_task

import celery
from WeXlog.celery import app

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, send_mail

from users.models import CustomUserSettings

from datetime import datetime
from datetime import date

from paypal.standard.models import PayPalStandardBase


app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

@app.task
@shared_task
class SubscriptionExpiredTask(Task):

    def run(self, user):

        subject = 'Your Subscription has Expired'
        context = {'user': user.first_name}
        html_message = render_to_string('email_templates/email_subscription_expired.html', context)
        plain_message = strip_tags(html_message)
        from_email = settings.CELERY_SYSTEM_EMAIL
        send_to = user.Email
        send_mail(subject, html_message, from_email, [send_to,])


@app.task
@shared_task
class SubscriptionAmountDifferentTask(Task):

    def run(self, user):

        subject = 'Your Payment Amount with PayPal varies to the Subscription Amount'
        context = {'user': user.first_name}
        html_message = render_to_string('email_templates/email_subscription_amount_different.html', context)
        plain_message = strip_tags(html_message)
        send_to = user.Email
        send_mail(subject, html_message, settings.CELERY_SYSTEM_EMAIL, [send_to,])


@app.task
@shared_task
class SubscriptionCancelledTask(Task):

    def run(self, user):

        subject = 'Your Subscription has been Cancelled'
        context = {'user': user.first_name}
        html_message = render_to_string('email_templates/email_subscription_cancelled.html', context)
        plain_message = strip_tags(html_message)
        send_to = user.Email
        send_mail(subject, html_message, settings.CELERY_SYSTEM_EMAIL, [send_to,])


@app.task
@shared_task
class SubscriptionFailedTask(Task):

    def run(self, user):

        subject = 'Your Subscription failed to be processed'
        context = {'user': user.first_name}
        html_message = render_to_string('email_templates/email_subscription_failed.html', context)
        plain_message = strip_tags(html_message)
        send_to = user.Email
        send_mail(subject, html_message, settings.CELERY_SYSTEM_EMAIL, [send_to,])


@app.task
@shared_task
class SubscriptionSignupTask(Task):

    def run(self, user):

        subject = 'WexLog Sign-up Confirmation'
        context = {'user': user.first_name}
        html_message = render_to_string('email_templates/email_subscription_signup.html', context)
        plain_message = strip_tags(html_message)
        send_to = user.Email
        send_mail(subject, html_message, settings.CELERY_SYSTEM_EMAIL, [send_to,])


@app.task
@shared_task
class SubscriptionRefundTask(Task):

    def run(self, user, refundamount, payment_txn_id):

        subject = 'Subscriber Upgrade Refund'
        context = {'user': user, 'refundamount': refundamount, 'txn_id': payment_txn_id}
        html_message = render_to_string('email_templates/email_subscription_upgrade_refund.html', context)
        plain_message = strip_tags(html_message)
        send_to = settings.ACCOUNTS_EMAIL
        send_mail(subject, html_message, settings.CELERY_SYSTEM_EMAIL, [send_to,])


@app.task
@shared_task
class RemindDeleteOldSubscription(Task):

    def run(self, user, payment_txn_id):

        subject = 'WeXlog Subscription Reminder'
        context = {'user': user, 'txn_id': payment_txn_id}
        html_message = render_to_string('email_templates/email_reminder_old_subscription_delete.html', context)
        plain_message = strip_tags(html_message)
        from_email = settings.CELERY_SYSTEM_EMAIL
        send_to = user.Email
        send_mail(subject, html_message, from_email, [send_to,])
# task.register(RemindDeleteOldSubscription())


def SubscriptionUpgradeRefund():

    def run(self, user):

        q = PayPalStandardBase.objects.filter(custom=user).order_by(-payment_date)
        subscriber = q[1]
        useremail = subscriber.custom

        npd = subscriber.next_payment_date
        npdd = npd.strftime('%d/%m/%Y')
        cd = date.today().strftime('%d/%m/%Y')
        nsd = cd - npd
        daysdelta = nsd.days

        opd = subscriber.payment_date
        opdd = opd.strftime('%d/%m/%Y')
        sd = npdd - opdd
        subscriptiondaysdelta = sd.days

        amp = subscriber.amount1
        subscriptionperday = amp / subscriptiondaysdelta
        refundamount = subscriptionperday * daysdelta

        payment_txn_id = subscriber.txn_id

        if refundamount >= 0:
            SubscriptionRefundTask(useremail, refundamount, payment_txn_id)
            RemindDeleteOldSubscription(useremail, payment_txn_id)
        else:
            pass
