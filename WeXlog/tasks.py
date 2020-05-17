from __future__ import absolute_import, unicode_literals
#from .celery import app
from celery import Celery
from celery.task import Task
from celery.schedules import crontab
from tasks.celery import app as celery_app

from django.conf import settings
from celery.task.schedules import crontab
from celery.decorators import periodic_task
#from django.contrib.auth.models import User

from datetime import datetime
from datetime import timedelta

#from payments.tasks import SubscriptionExpiredTask

from users.models import CustomUser


@celery_app.task(name="UpdateSubscriptionPaidDate")
@periodic_task(run_every=(crontab(hour=0, minute=5)), name="UpdateSubscriptionPaidDate", ignore_result=True)
def UpdateSubscriptionPaidDate():
    #monthly = timedelta(days=31, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0)
    monthly = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=1)

    six_monthly = timedelta(days=183, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0)
    twelve_monthly = timedelta(days=365, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0)

    users = CustomUser.objects.all()

    for u in users:
        username = CustomUser.objects.get(pk=u)
        if username.paid_type == 1:
            if username.paid_date <= datetime.now() - monthly:
                username.paid = False
                username.subscription = 0
                # send user an email to let them know the subscription has expired
#                SubscriptionExpiredTask.delay(username)

        elif username.paid_type == 2:
            if username.paid_date <= datetime.now() - six_monthly:
                username.paid = False
                username.subscription = 0
                # send user an email to let them know the subscription has expired
#                SubscriptionExpiredTask.delay(username)

        elif username.paid_type == 3:
            if username.paid_date <= datetime.now() - twelve_monthly:
                username.paid = False
                username.subscription = 0
                # send user an email to let them know the subscription has expired
#                SubscriptionExpiredTask.delay(username)
