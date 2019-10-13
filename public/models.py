from django.db import models
from datetime import datetime

from django_countries.fields import CountryField

# Create your models here.


class ContactUs(models.Model):
    date = models.DateTimeField(null=False, blank=False, default=datetime.now())
    name = models.CharField(max_length=60, null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    comments = models.TextField(null=True, blank=True)


class Suggestions(models.Model):
    date = models.DateTimeField(null=False, blank=False, default=datetime.now())
    name = models.CharField(max_length=60, null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    comments = models.TextField(null=True, blank=True)


class DataPrivacy(models.Model):
    date = models.DateTimeField(null=False, blank=False, default=datetime.now())
    name = models.CharField(max_length=60, null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    comments = models.TextField(null=True, blank=True)
