from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Messages(models.Model):
    ##m_from = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_from')
    #m_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_to')
    date_sent = models.DateTimeField(auto_now_add=True)
    date_viewed = models.DateTimeField(auto_now=True)
    message = models.TextField()
    message_trace = models.CharField(max_length=30, null=True)
    #viewed = models.Bo
