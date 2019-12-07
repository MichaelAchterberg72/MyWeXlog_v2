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

app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

@app.task
@shared_task
class SubscriptionExpiredTask(Task):
    if CustomUserSettings.talent == request.user:
        if CustomUserSettings.unsubscribe == True:
            pass

        if CustomUserSettings.subscription_notifications == False:
            pass

        else:
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
    if CustomUserSettings.talent == request.user:
        if CustomUserSettings.unsubscribe == True:
            pass

        if CustomUserSettings.subscription_notifications == False:
            pass

        else:

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
    if CustomUserSettings.talent == request.user:
        if CustomUserSettings.unsubscribe == True:
            pass

        if CustomUserSettings.subscription_notifications == False:
            pass

        else:

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
class SubscriptionSignupTask(Task):
    if CustomUserSettings.talent == request.user:
        if CustomUserSettings.unsubscribe == True:
            pass

        if CustomUserSettings.subscription_notifications == False:
            pass

        else:

            def run(self, user):

                subject, from_email, to = 'WexLog Sign-up Confirmation', settings.CELERY_SYSTEM_EMAIL, user.Email
                html_content = render_to_string('email_templates/email_subscription_signup.html', {'user': user.first_name})
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives(sunject, text_content, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

# task.register(SubscriptionSignupTask)
