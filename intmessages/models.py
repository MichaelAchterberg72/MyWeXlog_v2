from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Contact(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friends')
    friends = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return f'{self.username}'

class Message(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.contact.user.username}'



class Chat(models.Model):
    participants = models.ManyToManyField(Contact, related_name='chats')
    messages = models.ManyToManyField(Message, blank=True)

    def last_15_messages(self):
        return self.messages.objects.order_by('-timestamp').all()[:15]

    def __str__(self):
        return f'{self.pk}'
