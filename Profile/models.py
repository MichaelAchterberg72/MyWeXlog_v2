from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from time import time
from random import random
from django.urls import reverse
from django.db.models.signals import post_save


from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from users.models import CustomUser
from locations.models import Region, City, Suburb
from db_flatten.models import PhoneNumberType
from enterprises.models import Enterprise
from pinax.referrals.models import Referral

class SiteName(models.Model):
    site = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.site

class OnlineRegistrations(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profileurl = models.URLField()
    sitename = models.ForeignKey(SiteName, on_delete=models.PROTECT, related_name='Site_Name')

    class Meta:
        unique_together = (('profileurl', 'sitename'),)

    def __str__(self):
        return '{}'.format(self.sitename)

class Profile(models.Model):
    MENTOR = (
        ('Y','Yes'),
        ('N','No'),
        )
    talent = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birth_date = models.DateField('Date of Birth', null=True)
    background = models.TextField()
    mentor = models.CharField('Do you wish to be a mentor?', max_length=1, choices=MENTOR, default='N')#Opt in to be a mentor to other people
    middle_name = models.CharField(max_length=60, null=True, blank=True)
    synonym = models.CharField(max_length=15, null=True)
    referral_code = models.OneToOneField(Referral, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.talent)

    def create_profile(sender, **kwargs):
        if kwargs['created']:
            create_profile = Profile.objects.create(talent=kwargs['instance'])

    post_save.connect(create_profile, sender=CustomUser)


class IdType(models.Model):
    type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.type


class IdentificationDetail(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    identification = models.CharField('Identification number', max_length=20, unique=True, null=True)
    id_type = models.ForeignKey(IdType, on_delete=models.PROTECT, verbose_name='Identification_type', null=True)

    class Meta:
        unique_together = (('talent','identification'),)

    def __str__(self):
        return '{}-{} ({})'.format(self.talent, self.identification, self.id_type)

    def create_id(sender, **kwargs):
        if kwargs['created']:
            create_profile = IdentificationDetail.objects.create(talent=kwargs['instance'])

            #Create personal referral code
            '''
            referral = Referral.create(
                user = kwargs['instance'],
                redirect_to = '/accounts/signup/'
            )
            CustomUser.objects.filter(username=kwargs['instance']).update(referral_code=referral)'''

            #send email to new used with link

    post_save.connect(create_id, sender=CustomUser)


class PassportDetail(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    passport_number = models.CharField(max_length = 20, unique=True, blank=True, null=True)
    issue = CountryField('Country issued in', null=True)
    expiry_date = models.DateField(null=True)

    class Meta:
        unique_together = (('talent','passport_number'),)

    def create_passport(sender, **kwargs):
        if kwargs['created']:
            create_profile = PassportDetail.objects.create(talent=kwargs['instance'])
    post_save.connect(create_passport, sender=CustomUser)

    def __str__(self):
        return '{}-{}'.format(self.talent, self.passport_number)


class LanguageList(models.Model):
    language = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.language


class LanguageTrack(models.Model):
    LVL = (
        ('B','Basic'),
        ('G','Good'),
        ('F','Fluent'),
        ('H','Home Language'),
    )
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    language = models.ForeignKey(LanguageList, on_delete=models.PROTECT)
    level = models.CharField(max_length=1, choices=LVL, default="B")

    class Meta:
        unique_together = (('talent','language'),)

    def __str__(self):
        return '{} - {} ({})'.format(self.talent, self.language, self.level)


class Email(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='Customuser_email')
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=False)
    company = models.ForeignKey(Enterprise, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = (('talent','email'),)

    def __str__(self):
        return self.email

class PhysicalAddress(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    line1 = models.CharField('Address Line 1', max_length=100, null=True)
    line2 = models.CharField('Address Line 2', max_length=100, blank=True, null=True)
    line3 = models.CharField('Address Line 3', max_length=100, blank=True, null=True)
    country = CountryField(null=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True)
    suburb = models.ForeignKey(Suburb, on_delete=models.PROTECT, null=True)
    code = models.CharField('Postal Code', max_length=12, blank=True, null=True)

    def __str__(self):
        return '{}: {}, {}, {},{}'.format(self.talent, self.line1, self.line2, self.line3, self.country)

    def create_physical_add(sender, **kwargs):
        if kwargs['created']:
            create_physical_add = PhysicalAddress.objects.create(talent=kwargs['instance'])
    post_save.connect(create_physical_add, sender=CustomUser)

class PostalAddress(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    line1 = models.CharField('Address Line 1', max_length=100)
    line2 = models.CharField('Address Line 2', max_length=100, blank=True, null=True)
    line3 = models.CharField('Address Line 3', max_length=100, blank=True, null=True)
    country = CountryField()
    region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True)
    suburb = models.ForeignKey(Suburb, on_delete=models.PROTECT, null=True)
    code = models.CharField('Postal Code', max_length=12, blank=True, null=True)

    def __str__(self):
        return '{}: {}, {}, {},{}'.format(self.talent, self.line1, self.line2, self.line3, self.country)

    def create_postal_add(sender, **kwargs):
        if kwargs['created']:
            create_postal_add = PostalAddress.objects.create(talent=kwargs['instance'])
    post_save.connect(create_postal_add, sender=CustomUser)

#Function to randomise filename for Profile Upload
def ExtFilename(instance, filename):
	ext = filename.split('.')[-1]
	return "profile\%s_%s.%s" % (str(time()).replace('.','_'), random(), ext)

class FileUpload(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=150)
    file = models.FileField(upload_to=ExtFilename)

    def __str__(self):
        return '{}: {}'.format(self.talent, self.title)

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)


class PhoneNumber(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    number = PhoneNumberField()
    type = models.ForeignKey(PhoneNumberType, on_delete=models.SET_NULL, null=True)
    current = models.BooleanField()

    def __str__(self):
        return '{}: {}({})'.format(self.talent, self.number, self.type)
