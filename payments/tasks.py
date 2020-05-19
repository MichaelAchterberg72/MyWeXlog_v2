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
from sendgrid.helpers.mail import Mail

from users.models import CustomUserSettings
#from paypal.standard.models import PayPalStandardBase

from datetime import datetime
from datetime import date

#from paypal.standard.models import PayPalStandardBase


@celery_app.task(name="payments.SubscriptionExpiredTask")
@shared_task
def SubscriptionExpiredTask(self, user):

    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(settings.CELERY_SYSTEM_EMAIL)
    to_email = To(user.email)
    subject = 'Your Subscription has Expired'
    context = {'user': user.first_name}
    content = get_template('email_templates/email_subscription_expired.html').render(context)
    plain_message = render_to_string('email_templates/email_subscription_expired_text.html', context)
    text_content = strip_tags(plain_message)
    html_content = Content("text/html", content)
    mail = Mail(from_email, to_email, subject, text_content, html_content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)


@celery_app.task(name="payments.SubscriptionAmountDifferentTask")
@shared_task
def SubscriptionAmountDifferentTask(self, user):

    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(settings.CELERY_SYSTEM_EMAIL)
    to_email = To(user.email)
    subject = 'Your Payment Amount with PayPal varies to the Subscription Amount'
    context = {'user': user.first_name}
    content = get_template('email_templates/email_subscription_amount_different.html').render(context)
    plain_message = render_to_string('email_templates/email_subscription_amount_different_text.html', context)
    text_content = strip_tags(plain_message)
    html_content = Content("text/html", content)
    mail = Mail(from_email, to_email, subject, text_content, html_content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)


@celery_app.task(name="payments.SubscriptionCancelledTask")
@shared_task
def SubscriptionCancelledTask(self, user):

    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(settings.CELERY_SYSTEM_EMAIL)
    to_email = To(user.email)
    subject = 'Your Subscription has been Cancelled'
    context = {'user': user.first_name}
    content = get_template('email_templates/email_subscription_cancelled.html').render(context)
    plain_message = render_to_string('email_templates/email_subscription_cancelled_text.html', context)
    text_content = strip_tags(plain_message)
    html_content = Content("text/html", content)
    mail = Mail(from_email, to_email, subject, text_content, html_content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)


@celery_app.task(name="payments.SubscriptionFailedTask")
@shared_task
def SubscriptionFailedTask(self, user):

    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(settings.CELERY_SYSTEM_EMAIL)
    to_email = To(user.email)
    subject = 'Your Subscription failed to be processed'
    context = {'user': user.first_name}
    content = get_template('email_templates/email_subscription_failed.html').render(context)
    plain_message = render_to_string('email_templates/email_subscription_failed_text.html', context)
    text_content = strip_tags(plain_message)
    html_content = Content("text/html", content)
    mail = Mail(from_email, to_email, subject, text_content, html_content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)


@celery_app.task(name="payments.SubscriptionSignupTask")
@shared_task
def SubscriptionSignupTask(tlt):
    from users.models import CustomUser

    username = CustomUser.objects.get(pk=tlt)
    context = {'user': username.first_name}
    html_message = render_to_string('email_templates/email_subscription_signup.html', context)
#    content = get_template('email_templates/email_subscription_signup.html').render(context)
#    plain_message = render_to_string('email_templates/email_subscription_signup_text.html' context)
#    text_content = strip_tags(plain_message)
    message = Mail(
        from_email = settings.CELERY_SYSTEM_EMAIL,
        to_emails = username.email,
        subject = 'MyWeXlog Sign-up Confirmation',
        html_content = html_message)

    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
#        response = sg.client.mail.send.post(request_body=mail.get())
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(e)

@celery_app.task(name="payments.SubscriptionRefundTask")
@shared_task
def SubscriptionRefundTask(self, user, refundamount, payment_txn_id):

    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(settings.CELERY_SYSTEM_EMAIL)
    to_email = To(settings.ACCOUNTS_EMAIL)
    subject = 'Subscriber Upgrade Refund'
    context = {'user': user, 'refundamount': refundamount, 'txn_id': payment_txn_id}
    content = get_template('email_templates/email_subscription_upgrade_refund.html').render(context)
    plain_message = render_to_string('email_templates/email_subscription_upgrade_refund_text.html', context)
    text_content = strip_tags(plain_message)
    html_content = Content("text/html", content)
    mail = Mail(from_email, to_email, subject, text_content, html_content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)


@celery_app.task(name="payments.RemindDeleteOldSubscription")
@shared_task
def RemindDeleteOldSubscription(self, user, payment_txn_id):

    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(settings.CELERY_SYSTEM_EMAIL)
    to_email = To(user.email)
    subject = 'MyWeXlog Subscription Reminder'
    context = {'user': user, 'txn_id': payment_txn_id}
    content = get_template('email_templates/email_reminder_old_subscription_delete.html').render(context)
    plain_message = render_to_string('email_templates/email_reminder_old_subscription_delete_text.html', context)
    text_content = strip_tags(plain_message)
    html_content = Content("text/html", content)
    mail = Mail(from_email, to_email, subject, text_content, html_content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)
# task.register(RemindDeleteOldSubscription())

@celery_app.task(name="payments.SubscriptionUpgradeRefund")
def SubscriptionUpgradeRefund(self, user, useremail):

    p = PayPalStandardBase.objects.filter(custom=user.custom)
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
