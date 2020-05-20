from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.task import task
from celery.task import Task
from celery.decorators import task
from celery import shared_task
from tasks.celery import app as celery_app

import celery

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import get_template

import sendgrid
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Subject, To, ReplyTo, SendAt, Content, From, CustomArg, Header)


from users.models import CustomUserSettings, CustomUser

#from paypal.standard.ipn.models import PayPalIPN
from paypal.standard.models import PayPalStandardBase

from datetime import datetime
from datetime import date


@celery_app.task(name="payments.SubscriptionExpiredTask")
@shared_task
def SubscriptionExpiredTask(tlt):

    username = CustomUser.objects.get(pk=tlt)
    context = {'user': username.first_name, 'user_email': username.email }
    html_message = render_to_string('email_templates/email_subscription_expired.html', context)

    message = Mail(
        from_email = settings.SENDGRID_FROM_EMAIL,
        to_emails = username.email,
        subject = 'Your Subscription has Expired',
        plain_text_content = strip_tags(html_message),
        html_content = html_message)

    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(e)


@celery_app.task(name="payments.SubscriptionAmountDifferentTask")
@shared_task
def SubscriptionAmountDifferentTask(tlt):

    username = CustomUser.objects.get(pk=tlt)
    context = {'user': username.first_name, 'user_email': username.email }
    html_message = render_to_string('email_templates/email_subscription_amount_different.html', context)

    message = Mail(
        from_email = settings.SENDGRID_FROM_EMAIL,
        to_emails = username.email,
        subject = 'Your Subscription has Expired',
        plain_text_content = strip_tags(html_message),
        html_content = html_message)

    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(e)


@celery_app.task(name="payments.SubscriptionCancelledTask")
@shared_task
def SubscriptionCancelledTask(tlt):

    username = CustomUser.objects.get(pk=tlt)
    context = {'user': username.first_name, 'user_email': username.email }
    html_message = render_to_string('email_templates/email_subscription_cancelled.html', context)

    message = Mail(
        from_email = settings.SENDGRID_FROM_EMAIL,
        to_emails = username.email,
        subject = 'Your Subscription has been Cancelled',
        plain_text_content = strip_tags(html_message),
        html_content = html_message)

    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(e)


@celery_app.task(name="payments.SubscriptionFailedTask")
@shared_task
def SubscriptionFailedTask(tlt):

    username = CustomUser.objects.get(pk=tlt)
    context = {'user': username.first_name, 'user_email': username.email }
    html_message = render_to_string('email_templates/email_subscription_failed.html', context)

    message = Mail(
        from_email = settings.SENDGRID_FROM_EMAIL,
        to_emails = username.email,
        subject = 'Your Subscription failed to be processed',
        plain_text_content = strip_tags(html_message),
        html_content = html_message)

    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(e)


@celery_app.task(name="payments.SubscriptionSignupTask")
@shared_task
def SubscriptionSignupTask(tlt):

    username = CustomUser.objects.get(pk=tlt)
    context = {'user': username.first_name, 'user_email': username.email }
    html_message = render_to_string('email_templates/email_subscription_signup.html', context)

    message = Mail(
        from_email = settings.SENDGRID_FROM_EMAIL,
        to_emails = username.email,
        subject = 'MyWeXlog Sign-up Confirmation',
        plain_text_content = strip_tags(html_message),
        html_content = html_message)

    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(e)


@celery_app.task(name="payments.SubscriptionRefundTask")
@shared_task
def SubscriptionRefundTask(tlt, refundamount, payment_txn_id):

    username = CustomUser.objects.get(pk=tlt)
    context = {'user': username, 'refundamount': refundamount, 'txn_id': payment_txn_id, 'user_email': username.email }
    html_message = render_to_string('email_templates/email_subscription_upgrade_refund.html', context)

    message = Mail(
        from_email = settings.SENDGRID_FROM_EMAIL,
        to_emails = settings.ACCOUNTS_EMAIL,
        subject = 'Subscriber Upgrade Refund',
        plain_text_content = strip_tags(html_message),
        html_content = html_message)

    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(e)


@celery_app.task(name="payments.RemindDeleteOldSubscription")
@shared_task
def RemindDeleteOldSubscription(tlt, payment_txn_id):

    username = CustomUser.objects.get(pk=tlt)
    context = {'user': username.first_name, 'txn_id': payment_txn_id, 'user_email': username.email }
    html_message = render_to_string('email_templates/email_reminder_old_subscription_delete.html', context)

    message = Mail(
        from_email = settings.SENDGRID_FROM_EMAIL,
        to_emails = username.email,
        subject = 'MyWeXlog Sign-up Confirmation',
        plain_text_content = strip_tags(html_message),
        html_content = html_message)

    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(e)


@celery_app.task(name="payments.SubscriptionUpgradeRefund")
def SubscriptionUpgradeRefund(tlt, useremail):

    p = PayPalStandardBase.objects.filter(custom=tlt.custom)
    q = p.filter(flag = True).order_by(-payment_date)
    subscriber = q[1]
    useremail = user.email

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
        SubscriptionRefundTask.delay(useremail, refundamount, payment_txn_id)
        RemindDeleteOldSubscription.delay(useremail, payment_txn_id)
    else:
        pass
