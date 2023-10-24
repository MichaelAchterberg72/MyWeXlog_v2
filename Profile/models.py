import datetime
from decimal import Decimal, getcontext
from io import BytesIO, StringIO
from random import random
from time import time

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.urls import reverse
from django.utils import timezone
from django_countries.fields import CountryField
from pdf2image import convert_from_bytes, convert_from_path
from pdf2image.exceptions import (PDFInfoNotInstalledError, PDFPageCountError,
                                  PDFSyntaxError)
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image
from pinax.referrals.models import Referral
from tinymce.models import HTMLField

from db_flatten.models import LanguageList, PhoneNumberType
from enterprises.models import Branch, Enterprise
from db_flatten.models import SkillTag
from invitations.models import Invitation
from locations.models import City, Currency, Region, Suburb
from marketplace.models import SkillLevel, WorkLocation
from talenttrack.models import (ClassMates, Designation, Lecturer, Superior,
                                WorkClient, WorkCollaborator, WorkColleague)
from users.models import CustomUser
from WeXlog.storage_backends import PrivateMediaStorage

from .utils import create_code7, create_code9

from utils.utils import update_model, handle_m2m_relationship

from django.contrib.auth import get_user_model

User = get_user_model()


class BriefCareerHistory(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    work_configeration = models.ForeignKey(WorkLocation, on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name="Home_Base")
    description = HTMLField(blank=True, null=True)
    skills = models.ManyToManyField(SkillTag, related_name='skills_utilised')
    reason_for_leaving = models.TextField('Reason for leaving', blank=True, null=True)
    current = models.BooleanField(default=False)
    date_captured = models.DateField(auto_now_add=True)
    date_from = models.DateField()
    date_to = models.DateField(blank=True, null=True)
    slug = models.SlugField(max_length=15, blank=True, null=True, unique=True)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        work_configeration = kwargs.pop('work_configeration', None)
        designation = kwargs.pop('designation', None)
        companybranch = kwargs.pop('companybranch', None)
        skills = kwargs.pop('skills', [])
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if work_configeration:
            instance.work_configeration = WorkLocation.update_or_create(id=work_configeration.id, **work_configeration)

        if designation:
            instance.designation = Designation.update_or_create(id=designation.id, **designation)

        if companybranch:
            instance.companybranch = Branch.update_or_create(id=companybranch.id, **companybranch)

        if skills:
            skills_related_models_data = {
                'model': SkillTag,
                'manager': 'skills',
                'fields': ['skill', 'code'],
                'data': skills,
            }
            instance = handle_m2m_relationship(instance, [skills_related_models_data])
        
        instance.save()
            
        return instance

    def __str__(self):
        if self.date_to:
            return f'{self.talent}, {self.work_configeration}: {self.companybranch}, from: {self.date_from}, to: {self.date_to}'
        else:
            return f'{self.talent}, {self.work_configeration}: {self.companybranch}, from: {self.date_from} (Currently Employed Here)'

    @property
    def tenure(self):
        today = timezone.now().date()
        if self.date_to:
            tenure = self.date_to - self.date_from
        else:
            tenure = today - self.date_from

        months = tenure.days/(365/12)
        years = months/12

        return years

    def save(self, *args, **kwargs):
        if self.date_to:
            self.current = False

        else:
            self.current = True
            inject = f'{self.talent.first_name} {self.talent.last_name}: {self.companybranch} ({self.designation})'
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

    def __str__(self):
        return self.site


class OnlineRegistrations(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profileurl = models.URLField()
    sitename = models.ForeignKey(SiteName, on_delete=models.PROTECT, related_name='Site_Name')
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        sitename = kwargs.pop('sitename', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if sitename:
            instance.sitename = SiteName.update_or_create(id=sitename.id, **sitename)
        
        instance.save()
            
        return instance

    class Meta:
        unique_together = (('profileurl', 'sitename'),)

    def __str__(self):
        return '{}'.format(self.sitename)

#this better work!
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
    alias = models.CharField(max_length=30, null=True, unique=True)
    public_profile_intro = HTMLField(max_length=460, blank=True, null=True)
    birth_date = models.DateField('Date of Birth', null=True)
    background = HTMLField(blank=True, null=True)
    mentor = models.CharField('Do you wish to be a mentor?', max_length=1, choices=MENTOR, default='N')#Opt in to be a mentor to other people
    referral_code = models.OneToOneField(Referral, on_delete=models.SET_NULL, null=True)
    std_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True)
    rate_unit = models.CharField(max_length=1, choices=RATE_UNIT, default='H')
    motivation = HTMLField(blank=True, null=True)
    exp_lvl = models.ForeignKey(SkillLevel, on_delete=models.PROTECT, related_name='profile_tenure', null=True, default=1)
    rate_1 = models.FloatField(null=True, default=0)#average for marketplace.models.VacancyRate
    rate_2 = models.FloatField(null=True, default=0)#average for marketplace.models.VacancyRate
    rate_3 = models.FloatField(null=True, default=0)#average for marketplace.models.VacancyRate
    rate_count = models.IntegerField(null=True, default=0)#count for marketplace.models.VacancyRate
    confirm_check = models.BooleanField(null=True, default=False)
    accepted_terms = models.BooleanField(default=False)
    age_accept = models.BooleanField(default=False, null=True)
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        referral_code = kwargs.pop('referral_code', None)
        currency = kwargs.pop('currency', None)
        exp_lvl = kwargs.pop('exp_lvl', [])
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        # if referral_code:
        #     instance.referral_code = .update_or_create(id=referral_code.id, **referral_code)
            
        if currency:
            instance.currency = Currency.update_or_create(id=currency.id, **currency)
            
        if exp_lvl:
            exp_lvl_related_models_data = {
                'model': SkillLevel,
                'manager': 'exp_lvl',
                'fields': ['level', 'min_hours', 'description'],
                'data': exp_lvl,
            }
            instance = handle_m2m_relationship(instance, [exp_lvl_related_models_data])
        
        instance.save()
            
        return instance

    def __str__(self):
        return str(self.talent)

    def avg_rate(self):
        if self.rate_count is not None:
            sum = self.rate_1+self.rate_2+self.rate_3
        else:
            sum=0
        return round(Decimal(sum/300),2)
    average = property(avg_rate)

    @property
    def age(self):
        '''Age at last birthday'''
        today = timezone.now().date()
        age = relativedelta(today, self.birth_date).years
        return age

    def save(self, *args, **kwargs):
        if self.alias is None or self.alias == "":
            self.alias = create_code7(self)

        fullname = f'{self.talent.first_name} {self.talent.last_name} - Profile incomplete'

        inject_fn = f'{self.f_name}'
        inject_ln = f'{self.l_name}'
        inject_al = f'{self.alias}'
        target = CustomUser.objects.filter(pk=self.talent.id)
        if self.f_name is None or self.f_name =="":
            target.update(alias=inject_al, alphanum=inject_al, display_text=fullname)
        else:
            target.update(alias=inject_al, first_name=inject_fn, last_name=inject_ln)

        #check for confirmations once registering
        if self.confirm_check == False:
            tlt = self.talent.email
            eml_i = Invitation.objects.filter(email=tlt)
            self.confirm_check = True
            eml_i.update(accpeted = True)


            if eml_i:
                eml_i = eml_i.get(email=tlt)
                rel = eml_i.relationship
                if rel == 'LR':
                    lct = Lecturer(
                                   education = eml_i.experience,
                                   lecturer=self.talent,
                                   topic=eml_i.experience.topic)
                    lct.save()
                if rel == 'CM':
                    cm = ClassMates(
                                    education = eml_i.experience,
                                    colleague=self.talent,
                                    topic=eml_i.experience.topic)
                    cm.save()
                if rel == 'WC':
                    wc = WorkColleague(
                                       experience = eml_i.experience,
                                       colleague_name=self.talent)
                    wc.save()
                if rel == 'PC':
                    wc = WorkColleague(
                                       experience = eml_i.experience,
                                       colleague_name=self.talent)
                    wc.save()
                if rel == 'WS':
                    ws = Superior(
                                  experience = eml_i.experience,
                                  superior_name=self.talent)
                    ws.save()
                if rel == 'WL':
                    wl = WorkCollaborator(
                                          experience = eml_i.experience,
                                          collaborator_name=self.talent,
                                          company=eml_i.companybranch.company,
                                          companybranch=eml_i.companybranch)
                    wl.save()
                if rel == 'WT':
                    wt = WorkClient(
                                    experience = eml_i.experience,
                                    client_name=self.talent,
                                    company=eml_i.companybranch.company,
                                    companybranch=eml_i.companybranch)
                    wt.save()
            else:
                pass

        super(Profile, self).save(*args, **kwargs)

    def create_profile(sender, **kwargs):
        if kwargs['created']:
            create_profile = Profile.objects.create(talent=kwargs['instance'], accepted_terms=True, age_accept=True)

    post_save.connect(create_profile, sender=CustomUser)

def ProfilePic(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/profile\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)

def BackgroundPic(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/profile\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)

class ProfileImages(models.Model):
    talent = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_pic = models.ImageField(storage=PrivateMediaStorage(), upload_to=ProfilePic, blank=True, null=True)
    profile_background = models.ImageField(storage=PrivateMediaStorage(), upload_to=BackgroundPic, blank=True, null=True)

    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
        
        instance.save()
            
        return instance
    
    def __str__(self):
        return str(self.talent)

    def create_settings(sender, **kwargs):
        if kwargs['created']:
            create_settings = ProfileImages.objects.create(talent=kwargs['instance'])

    post_save.connect(create_settings, sender=CustomUser)


class IdType(models.Model):
    type = models.CharField(max_length=50, unique=True)
    
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

    def clean(self):
        self.type = self.type.title()

    def __str__(self):
        return self.type


class IdentificationDetail(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    identification = models.CharField('Identification number', max_length=20, unique=True, null=True)
    id_type = models.ForeignKey(IdType, on_delete=models.PROTECT, verbose_name='Identification_type', null=True)

    class Meta:
        unique_together = (('talent','identification'),)
        
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
        
        instance.save()
            
        return instance

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
        
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
        
        instance.save()
            
        return instance

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
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        language = kwargs.pop('language', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if language:
            instance.language = LanguageList.update_or_create(id=language.id, **language)
        
        instance.save()
            
        return instance

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
    slug = models.SlugField(max_length=9, null=True, unique=True, blank=True)

    class Meta:
        unique_together = (('talent','email'),)
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        company = kwargs.pop('company', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if company:
            instance.company = Enterprise.update_or_create(slug=company.slug, **company)
        
        instance.save()
            
        return instance

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
    line1 = models.CharField('Address Line 1', max_length=250, null=True, blank=True)
    line2 = models.CharField('Address Line 2', max_length=250, blank=True, null=True)
    line3 = models.CharField('Address Line 3', max_length=100, blank=True, null=True)
    country = CountryField(null=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True)
    suburb = models.ForeignKey(Suburb, on_delete=models.PROTECT, null=True, blank=True)
    code = models.CharField('Postal Code', max_length=12, null=True)
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        region = kwargs.pop('region', None)
        city = kwargs.pop('city', None)
        suburb = kwargs.pop('suburb', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if region:
            instance.region = Region.update_or_create(id=region.id, **region)

        if city:
            instance.city = City.update_or_create(id=city.id, **city)

        if suburb:
            instance.suburb = Suburb.update_or_create(id=suburb.id, **suburb)
        
        instance.save()
            
        return instance

    def __str__(self):
        return f'{self.talent}: {self.country}'

    def create_physical_add(sender, **kwargs):
        if kwargs['created']:
            create_physical_add = PhysicalAddress.objects.create(talent=kwargs['instance'])

    post_save.connect(create_physical_add, sender=CustomUser)


class PostalAddress(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    line1 = models.CharField('Address Line 1', max_length=100, blank=True, null=True)
    line2 = models.CharField('Address Line 2', max_length=100, blank=True, null=True)
    line3 = models.CharField('Address Line 3', max_length=100, blank=True, null=True)
    country = CountryField()
    region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True)
    suburb = models.ForeignKey(Suburb, on_delete=models.PROTECT, null=True, blank=True)
    code = models.CharField('Postal Code', max_length=12, null=True)
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        region = kwargs.pop('region', None)
        city = kwargs.pop('city', None)
        suburb = kwargs.pop('suburb', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if region:
            instance.region = Region.update_or_create(id=region.id, **region)

        if city:
            instance.city = City.update_or_create(id=city.id, **city)

        if suburb:
            instance.suburb = Suburb.update_or_create(id=suburb.id, **suburb)
        
        instance.save()
            
        return instance

    def __str__(self):
        return f'{self.talent}: {self.country}'

    def create_postal_add(sender, **kwargs):
        if kwargs['created']:
            create_postal_add = PostalAddress.objects.create(talent=kwargs['instance'])
    post_save.connect(create_postal_add, sender=CustomUser)

#Function to randomise filename for Profile Upload
def ExtFilename(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/profile\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)

def ExtThumbnail(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/profile\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)

class FileUpload(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=150)
    file = models.FileField(storage=PrivateMediaStorage(), upload_to=ExtFilename, validators=[FileExtensionValidator(['pdf'])])
    thumbnail = models.ImageField(storage=PrivateMediaStorage(), upload_to=ExtThumbnail, blank=True, null=True)

    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
        
        instance.save()
            
        return instance
    
    def __str__(self):
        return '{}: {}'.format(self.talent, self.title)

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.file:
            cache_path = self.file
            bytes_file = bytes(cache_path.open(mode='rb').read())

            images = convert_from_bytes(bytes_file)[0]
            image = images.resize((int(260), int(360)), Image.ANTIALIAS)

            quality_val = 90
            thumb_io = BytesIO()
            image.save(thumb_io, format='JPEG', quality=quality_val)

            thumb_file = InMemoryUploadedFile(thumb_io, None, 'foo.jpg', 'image/jpeg', thumb_io.__sizeof__(), None)

            self.thumbnail = thumb_file

        super(FileUpload, self).save(*args, **kwargs)

class PhoneNumber(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    number = PhoneNumberField()
    type = models.ForeignKey(PhoneNumberType, on_delete=models.SET_NULL, null=True)
    current = models.BooleanField()
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        type = kwargs.pop('type', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if type:
            instance.type = PhoneNumberType.update_or_create(id=type.id, **type)
        
        instance.save()
            
        return instance

    def __str__(self):
        return '{}: {}({})'.format(self.talent, self.number, self.type)


class WillingToRelocate(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    country = CountryField()
    documents = models.BooleanField(default=False)#All documents required to work are in place.
    slug = models.SlugField(max_length=9, null=True, unique=True, blank=True)

    class Meta:
        unique_together = (('talent', 'country'),)
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
        
        instance.save()
            
        return instance

    def __str__(self):
        return f'{self.talent.alias} - {self.country}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(WillingToRelocate, self).save(*args, **kwargs)
