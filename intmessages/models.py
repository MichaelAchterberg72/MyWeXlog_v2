from django.db import models
from users.models import CustomUser
from django.contrib.auth.models import User
from django.conf import settings

from Profile.utils import create_code9

from utils.utils import update_model, handle_m2m_relationship

from Profile.utils import create_code9

from django.contrib.auth import get_user_model

User = get_user_model()


class ChatGroup(models.Model):
    room_name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(max_length=50, null=True, blank=True, unique=True)
    description = models.TextField(blank=True, null=True, help_text='Add a description for the group!')
    date_created = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        instance.save()
            
        return instance

    def __str__(self):
        return '{}, {}'.format(self.room_name, self.date_created)

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)
        super(ChatGroup, self).save(*args, **kwargs)


class ChatRoomMembers(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    chat_group = models.ForeignKey(ChatGroup, on_delete=models.PROTECT, null=True)
    room_name = models.CharField(max_length=200, null=True)
    mute_notifications = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        chat_group = kwargs.pop('chat_group', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if chat_group:
            instance.chat_group = ChatGroup.update_or_create(slug=chat_group.slug, **chat_group)
        
        instance.save()
            
        return instance

    def __str__(self):
        return '{}, {}'.format(self.room_name, self.talent)


class Message(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='author_messages', on_delete=models.SET_NULL, null=True)
    room_name = models.CharField(max_length=200, null=True)
    message_read = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="message_read_user", blank=True) # , through=MessageRead
    content = models.TextField()
    reply_pk = models.CharField(max_length=20, null=True, blank=True)
    initial_members_count = models.CharField(max_length=20, null=True)
    message_deleted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        author = kwargs.pop('author', None)
        message_read = kwargs.pop('message_read', [])
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if author:
            instance.author = User.objects.get(slug=author.slug)
            
        if message_read:
            message_read_related_models_data = {
                'model': User,
                'manager': 'message_read',
                'fields': ['slug'],
                'data': message_read,
            }
            instance = handle_m2m_relationship(instance, [message_read_related_models_data])
        
        instance.save()
            
        return instance

    def __str__(self):
        return self.author.username

    def last_30_messages():
        return Message.objects.order_by('-timestamp').all()[:30]

class MessageRead(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True)
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    chat_group = models.ForeignKey(ChatGroup, on_delete=models.PROTECT, null=True)
    message_read = models.BooleanField(null=True, default=False)
    read_date = models.DateTimeField(auto_now=True)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        message = kwargs.pop('message', None)
        chat_group = kwargs.pop('chat_group', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if message:
            instance.message = Message.update_or_create(id=message.id, **message)

        if chat_group:
            instance.chat_group = ChatGroup.update_or_create(slug=chat_group.slug, **chat_group)

        instance.save()
            
        return instance

    def __str__(self):
        return '{}, {} {}'.format(self.chat_group, self.talent, self.message_read)
