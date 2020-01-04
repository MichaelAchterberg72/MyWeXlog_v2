from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Message(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username}'

    def last_15_messages():
        return Message.objects.order_by('-timestamp').all()[:15]
