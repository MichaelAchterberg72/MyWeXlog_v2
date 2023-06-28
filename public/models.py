from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField

from utils.utils import update_model

# Create your models here.


class ContactUs(models.Model):
    date = models.DateTimeField(null=False, blank=False, default=timezone.now)
    name = models.CharField(max_length=60, null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    comments = models.TextField(null=True, blank=True)

    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        instance.save()
            
        return instance


class Suggestions(models.Model):
    date = models.DateTimeField(null=False, blank=False, default=timezone.now)
    name = models.CharField(max_length=60, null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    comments = models.TextField('Comments / Suggestions', null=True, blank=True)

    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        instance.save()
            
        return instance


class DataProtection(models.Model):
    date = models.DateTimeField(null=False, blank=False, default=timezone.now)
    name = models.CharField(max_length=60, null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    comments = models.TextField(null=True, blank=True)

    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        instance.save()
            
        return instance