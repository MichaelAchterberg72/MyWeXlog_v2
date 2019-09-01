from __future__ import absolute_import, unicode_literals
from .celery import app
from celery import Celery
from celery.task import Task
from celery.schedules import crontab

from django.conf import settings

from datetime import datetime
from datetime import timedelta

from payments.tasks import SubscriptionExpiredTask


@app.task
@periodic_task(run_every=(crontab(hour=23, minute=55)), name="UpdateSubscriptionPaidDate", ignore_result=True)
def UpdateSubscriptionPaidDate(Task):
monthly = timedelta(days=31, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0)
six_monthly = timedelta(days=183, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0)
twelve_monthly = timedelta(days=365, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0)
    if Users.paid_type == "1":
        if Users.paid_date <= datetime.now() - monthly:
            Users.objects.get(paid).update(paid=False)
            Users.objects.get(subscription).update(subscription="0")
            # send user an email to let them know the subscription has expired
            SubscriptionExpiredTask.delay(user)
        else:
            pass
    elif Users.paid_type == "2":
        if Users.paid_date <= datetime.now() - six_monthly:
            Users.objects.get(paid).update(paid=False)
            Users.objects.get(subscription).update(subscription="0")
            # send user an email to let them know the subscription has expired
            SubscriptionExpiredTask.delay(user)
        else:
            pass
    elif Users.paid_type == "3":
        if Users.paid_date <= datetime.now() - twelve_monthly:
            Users.objects.get(paid).update(paid=False)
            Users.objects.get(subscription).update(subscription="0")
            # send user an email to let them know the subscription has expired
            SubscriptionExpiredTask.delay(user)
        else:
            pass
    return
