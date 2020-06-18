from __future__ import absolute_import, unicode_literals
#from .celery import app
from celery import Celery
from celery.task import Task
from celery.schedules import crontab
from tasks.celery import app as celery_app

from django.conf import settings
from django.utils import timezone

from celery.task.schedules import crontab
from celery.task import periodic_task

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.template.loader import get_template

import sendgrid
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Subject, To, ReplyTo, SendAt, Content, From, CustomArg, Header)

import datetime
from datetime import timedelta

#from payments.tasks import SubscriptionExpiredTask

from users.models import CustomUser


@celery_app.task(name="UpdateSubscriptionPaidDate")
@periodic_task(run_every=(crontab(hour=0, minute=0)), name="UpdateSubscriptionPaidDate", ignore_result=True)
def UpdateSubscriptionPaidDate():

    monthly = datetime.timedelta(days=31, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0)
    six_monthly = datetime.timedelta(days=183, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0)
    twelve_monthly = datetime.timedelta(days=366, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0)

    users = CustomUser.objects.all()

    for u in users:
        username = CustomUser.objects.get(pk=u.id)
        if username.paid == True:
            if username.paid_type == 1:
                if username.paid_date <= timezone.now() - monthly:
                    username.paid = False
                    username.subscription = 0
                    username.save()
                    # send user an email to let them know the subscription has expired
    #                SubscriptionExpiredTask.delay(username)

            elif username.paid_type == 2:
                if username.paid_date <= datetime.now() - six_monthly:
                    username.paid = False
                    username.subscription = 0
                    username.save()
                    # send user an email to let them know the subscription has expired
    #                SubscriptionExpiredTask.delay(username)

            elif username.paid_type == 3:
                if username.paid_date <= datetime.now() - twelve_monthly:
                    username.paid = False
                    username.subscription = 0
                    username.save()
                    # send user an email to let them know the subscription has expired
    #                SubscriptionExpiredTask.delay(username)
        username.save()


def UpgradeRefunds():
    from paypal.standard.ipn.models import PayPalIPN

    monthly = datetime.timedelta(days=31)
    mda = datetime.today() - monthly  #.strftime('%d/%m/%Y')

    qs = PayPalIPN.objects.filter(Q(txn_type='subscr_signup') & Q(item_name__icontains='Upgrade'))
    item = qs.filter(subscr_date__gte=mda).values_list('payer_id', flat=True)

#    for r in item:
#        username = CustomUser.objects.get(pk=r.custom)
#        useremail = username.email
#        tlt = username.pk

#        p = PayPalIPN.objects.filter(custom=r.custom)
#        q = p.filter(flag = True).order_by(-payment_date)
#        subscriber = q[1]

#        npd = subscriber.next_payment_date
#        npdd = npd.strftime('%d/%m/%Y')
#        cd = date.today().strftime('%d/%m/%Y')
#        nsd = cd - npd
#        daysdelta = nsd.days

#        opd = subscriber.payment_date
#        opdd = opd.strftime('%d/%m/%Y')
#        sd = npdd - opdd
#        subscriptiondaysdelta = sd.days

#        amp = subscriber.amount1
#        subscriptionperday = amp / subscriptiondaysdelta
#        refundamount = subscriptionperday * daysdelta

#        payment_txn_id = subscriber.txn_id

#        if refundamount > 0.48:
#            SubscriptionRefundTask.delay(username, useremail, refundamount, payment_txn_id)
#            RemindDeleteOldSubscription.delay(useremail, payment_txn_id)


    subject = f"Refunds for MyWeXlog Upgrades"
    context = {'item': item }
    html_message = render_to_string('payments/email_subscription_subscription_refund.html', context).strip()
    plain_message = strip_tags(html_message)

    message = Mail(
        from_email = settings.SENDGRID_FROM_EMAIL,
        to_emails = settings.ACCOUNTS_EMAIL,
        subject = subject,
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
