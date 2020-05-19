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
