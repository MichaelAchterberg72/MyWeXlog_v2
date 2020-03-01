from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from time import time
from random import random
from django.urls import reverse
from django.db.models.signals import post_save, pre_save


from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from .utils import create_code7, create_code9

from users.models import CustomUser
from locations.models import Region, City, Suburb, Currency
from db_flatten.models import PhoneNumberType
from enterprises.models import Enterprise, Branch
from pinax.referrals.models import Referral
from marketplace.models import WorkLocation, SkillLevel
from talenttrack.models import Designation


class BriefCareerHistory(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    work_configeration = models.ForeignKey(WorkLocation, on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name="Home_Base")
    current = models.BooleanField(default=False)
    date_captured = models.DateField(auto_now_add=True)
    date_from = models.DateField()
    date_to = models.DateField(blank=True, null=True)
    slug = models.SlugField(max_length=15, blank=True, null=True, unique=True)

    def __str__(self):
        if self.date_to:
            return f'{self.talent}, {self.work_configeration}: {self.companybranch}, from: {self.date_from}, to: {self.date_to}'
        else:
            return f'{self.talent}, {self.work_configeration}: {self.companybranch}, from: {self.date_from} (Currently Employed Here)'

    def save(self, *args, **kwargs):
        if self.date_to:
            self.current = False

        else:
            self.current = True
            inject = f'{self.companybranch} ({self.designation})'
            CustomUser.objects.filter(pk=self.talent.id).update(display_text=inject)

        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(BriefCareerHistory, self).save(*args, **kwargs)

def BriefCareerHistory_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = f'b{instance.talent.id}{instance.id}h'

pre_save.connect(BriefCareerHistory_slug, sender=BriefCareerHistory)


#website for online registrations
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
    RATE_UNIT = (
        ('H','per Hour'),
        ('D','per Day'),
        ('M','per Month'),
        ('L','Lump Sum'),
    )
    talent = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    f_name = models.CharField(max_length=30, null=True)
    l_name = models.CharField(max_length=30, null=True)
    alias = models.CharField(max_length=30, null=True)
    birth_date = models.DateField('Date of Birth', null=True)
    background = models.TextField()
    mentor = models.CharField('Do you wish to be a mentor?', max_length=1, choices=MENTOR, default='N')#Opt in to be a mentor to other people
    referral_code = models.OneToOneField(Referral, on_delete=models.SET_NULL, null=True)
    std_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True)
    rate_unit = models.CharField(max_length=1, choices=RATE_UNIT, default='H')
    motivation = models.TextField(blank=True, null=True)
    exp_lvl = models.ForeignKey(SkillLevel, on_delete=models.PROTECT, related_name='profile_tenure', null=True)

    def __str__(self):
        return str(self.talent)

    def save(self, *args, **kwargs):
        if self.alias is None or self.alias == "":
            self.alias = create_code7(self)

        inject_fn = f'{self.f_name}'
        inject_ln = f'{self.l_name}'
        inject_al = f'{self.alias}'
        target = CustomUser.objects.filter(pk=self.talent.id)
        if self.f_name is None or self.f_name =="":
            target.update(alias=inject_al, alphanum=inject_al)
        else:
            target.update(alias=inject_al, first_name=inject_fn, last_name=inject_ln)
        super(Profile, self).save(*args, **kwargs)

    def create_profile(sender, **kwargs):
        if kwargs['created']:
            create_profile = Profile.objects.create(talent=kwargs['instance'])

    post_save.connect(create_profile, sender=CustomUser)


class IdType(models.Model):
    type = models.CharField(max_length=50, unique=True)

    def clean(self):
        self.type = self.type.capitalize()

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

    post_save.connect(create_id, sender=CustomUser)


class PassportDetail(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    passport_number = models.CharField(max_length = 20, unique=True, blank=True, null=True)
    issue = CountryField('Country issued in', null=True)
    expiry_date = models.DateField(null=True)
    slug = models.SlugField(max_length=20, blank=True, null=True, unique=True)

    class Meta:
        unique_together = (('talent','passport_number'),)

    def create_passport(sender, **kwargs):
        if kwargs['created']:
            create_profile = PassportDetail.objects.create(talent=kwargs['instance'])
    post_save.connect(create_passport, sender=CustomUser)

    def __str__(self):
        return '{}-{}'.format(self.talent, self.passport_number)


    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(PassportDetail, self).save(*args, **kwargs)


class LanguageList(models.Model):
    language = models.CharField(max_length=30, unique=True)

    def clean(self):
        self.language = self.language.capitalize()

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
    slug = models.SlugField(max_length=15, blank=True, null=True)

    class Meta:
        unique_together = (('talent','language'),)

    def __str__(self):
        return '{} - {} ({})'.format(self.talent, self.language, self.level)


def Language_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = f'{instance.talent.id}{instance.language.id}'

pre_save.connect(Language_slug, sender=LanguageTrack)


class Email(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='Customuser_email')
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=False)
    company = models.ForeignKey(Enterprise, on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField(max_length=50, null=True, unique=True, blank=True)

    class Meta:
        unique_together = (('talent','email'),)

    def clean(self):
        self.email = self.email.lower()

    def __str__(self):
        return self.email


    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(Email, self).save(*args, **kwargs)


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
