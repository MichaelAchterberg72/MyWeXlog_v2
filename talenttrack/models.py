import datetime
from decimal import Decimal
from io import BytesIO, StringIO
from random import random
from time import time

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Count, F, Q, Sum
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django_countries.fields import CountryField
from pdf2image import convert_from_bytes, convert_from_path
from pdf2image.exceptions import (PDFInfoNotInstalledError, PDFPageCountError,
                                  PDFSyntaxError)
from PIL import Image
from smartfields import dependencies, fields
from smartfields.dependencies import FileDependency
from smartfields.processors import ImageProcessor

from WeXlog.utils import update_model, handle_m2m_relationship

from booklist.models import Author, Genre, Publisher
# from booklist.handle import handle_publisher
from db_flatten.models import SkillTag
from enterprises.models import Branch, Enterprise, Industry
from locations.models import Region
from Profile.utils import create_code9
from project.models import ProjectData, ProjectPersonalDetails
from WeXlog.storage_backends import PrivateMediaStorage
from users.models import CustomUser

from django.contrib.auth import get_user_model

User = get_user_model()


CONFIRM = (
    ('S','Select'),
    ('C','Confirm'),
    ('R','Reject'),
    ('Y','Wrong Person'),
)
RATING=(
    ('1','basic'),
    ('2','working'),
    ('3','good'),
    ('4','master'),
    ('5','grand master'),
)

D_RATING = [
    (Decimal("1.0"), "basic"),
    (Decimal("2.0"), "working"),
    (Decimal("3.0"), "good"),
    (Decimal("4.0"), "master"),
    (Decimal("5.0"), "grand master"),
]

#Function to randomise filename for Profile Upload
def AchFilename(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/ach\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)

def AchThumbnail(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/ach\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)

class Achievements(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    achievement = models.CharField(max_length=500)
    date_achieved = models.DateField()
    description = models.TextField('Describe the Achievement')
    upload = models.FileField(storage=PrivateMediaStorage(), upload_to=AchFilename, blank=True, null=True, validators=[FileExtensionValidator(['pdf'])])
    thumbnail = models.ImageField(storage=PrivateMediaStorage(), upload_to=AchThumbnail, blank=True, null=True)
    slug = models.SlugField(max_length=15, unique=True, null=True, blank=True)
        
    def __str__(self):
        return f'{self.talent}: {self.achievement} ({self.date_achieved})'

    class Meta:
        ordering = ['-date_achieved']
        unique_together = (('talent', 'achievement', 'date_achieved'),)
        
    def save(self, *args, **kwargs):
        if self.upload:
            cache_path = self.upload
            bytes_file = bytes(cache_path.open(mode='rb').read())

            images = convert_from_bytes(bytes_file)[0]
            image = images.resize((int(260), int(360)), Image.ANTIALIAS)

            quality_val = 90
            thumb_io = BytesIO()
            image.save(thumb_io, format='JPEG', quality=quality_val)

            thumb_file = InMemoryUploadedFile(thumb_io, None, 'foo.jpg', 'image/jpeg', thumb_io.__sizeof__(), None)

            self.thumbnail = thumb_file

        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(Achievements, self).save(*args, **kwargs)
        
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
            instance.talent = User.objects.get(alias=talent.alias)
        
        instance.save()
            
        return instance
    
#Function to randomise filename for Profile Awards Upload
def AwardFilename(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/award\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)

def AwardThumbnail(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/award\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)


class Awards(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    award = models.CharField(max_length=500)
    date_achieved = models.DateField()
    description = models.TextField('Describe the Award')
    tag = models.ManyToManyField(SkillTag, verbose_name='Tag / Associated Skill')
    upload = models.FileField(storage=PrivateMediaStorage(), upload_to=AwardFilename, blank=True, null=True, validators=[FileExtensionValidator(['pdf'])])
    thumbnail = models.ImageField(storage=PrivateMediaStorage(), upload_to=AwardThumbnail, blank=True, null=True)
    slug = models.SlugField(max_length=15, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['-date_achieved']
        unique_together = (('talent', 'award', 'date_achieved'),)

    def __str__(self):
        return f'{self.talent}: {self.award} ({self.date_achieved})'
    
    def save(self, *args, **kwargs):
        if self.upload:
            cache_path = self.upload
            bytes_file = bytes(cache_path.open(mode='rb').read())

            images = convert_from_bytes(bytes_file)[0]
            image = images.resize((int(260), int(360)), Image.ANTIALIAS)

            quality_val = 90
            thumb_io = BytesIO()
            image.save(thumb_io, format='JPEG', quality=quality_val)

            thumb_file = InMemoryUploadedFile(thumb_io, None, 'foo.jpg', 'image/jpeg', thumb_io.__sizeof__(), None)

            self.thumbnail = thumb_file

        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(Awards, self).save(*args, **kwargs)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        tag = kwargs.pop('tag', [])
        talent = kwargs.pop('talent', None)

        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if talent:
            instance.talent = User.objects.get(alias=talent.alias)
            
        if tag:
            tag_related_models_data = {
                'model': SkillTag,
                'manager': 'tag',
                'fields': ['skill', 'code'],
                'data': tag,
            }
            instance = handle_m2m_relationship(instance, [tag_related_models_data])

        instance.save()
            
        return instance


#Function to randomise filename for Profile Upload
def PublicationFilename(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/pub\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)

def PublicationThumbnail(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/pub-thumb\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)


class Publications(models.Model):
    CLASS=(
        ('F','Fiction'),
        ('N','Non-fiction'),
    )
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    type = models.CharField(max_length=1, choices=CLASS, default='F' )
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT)
    link = models.URLField('Publication URL', blank=True, null=True)
    author = models.ManyToManyField(Author)
    tag = models.ManyToManyField(SkillTag, verbose_name='Tag / Associated Skill')
    genre = models.ManyToManyField(Genre)
    date_published = models.DateField()
    description = models.TextField('Describe the Publication')
    upload = models.FileField(storage=PrivateMediaStorage(), upload_to=PublicationFilename, blank=True, null=True, validators=[FileExtensionValidator(['pdf'])])
    thumbnail = models.ImageField(storage=PrivateMediaStorage(), upload_to=PublicationThumbnail, blank=True, null=True)
    slug = models.SlugField(max_length=15, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['-date_published']
        unique_together = (('talent', 'title', 'date_published'),)

    def __str__(self):
        return f'{self.talent}: {self.title} ({self.date_published})'
    
    def save(self, *args, **kwargs):
        if self.upload:
            cache_path = self.upload
            bytes_file = bytes(cache_path.open(mode='rb').read())

            images = convert_from_bytes(bytes_file)[0]
            image = images.resize((int(260), int(360)), Image.ANTIALIAS)

            quality_val = 90
            thumb_io = BytesIO()
            image.save(thumb_io, format='JPEG', quality=quality_val)

            thumb_file = InMemoryUploadedFile(thumb_io, None, 'foo.jpg', 'image/jpeg', thumb_io.__sizeof__(), None)

            self.thumbnail = thumb_file

        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(Publications, self).save(*args, **kwargs)
    
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop("talent", None)
        publisher = kwargs.pop("publisher", None)
        author = kwargs.pop("author", [])
        tag = kwargs.pop("tag", [])
        genre = kwargs.pop("genre", [])
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if talent:
            instance.talent = User.objects.get(
                alias=instance.talent.alias,
            )

        if publisher:
            instance.publisher = Publisher.update_or_create(id=publisher.id, **publisher)

        if author:
            author_related_models_data = {
                'model': Author,
                'manager': 'author',
                'fields': ['name'],
                'data': author,
            }
            instance = handle_m2m_relationship(instance, [author_related_models_data])

        if tag:
            tag_related_models_data = {
                'model': SkillTag,
                'manager': 'tag',
                'fields': ['skill', 'code'],
                'data': tag,
            }
            instance = handle_m2m_relationship(instance, [tag_related_models_data])

        if genre:
            genre_related_models_data = {
                'model': Genre,
                'manager': 'genre',
                'fields': ['name'],
                'data': genre,
            }
            instance = handle_m2m_relationship(instance, [genre_related_models_data])
            
        instance.save()
        
        return instance


class Result(models.Model):#What you receive when completing the course
    type = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.type
    
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


class CourseType(models.Model):#What type of course (online, Attend lectures, etc.)
    type = models.CharField(max_length=60, unique=True)
    
    def __str__(self):
        return self.type
    
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

#Function to randomise filename for Profile Upload
def CertFilename(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/cert\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)

def CertThumbnail(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/cert\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)


class LicenseCertification(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    certification = models.ForeignKey(Result, on_delete=models.PROTECT, verbose_name='Proffessional Memberships / Certification type')
    cert_name = models.CharField(max_length=150, null=True)
    country = CountryField()
    region = models.ForeignKey(Region, on_delete=models.PROTECT, blank=True, null=True)
    cm_no = models.CharField('Membership / Credential Number', max_length=40, blank=True, null=True)
    companybranch = models.ForeignKey(Enterprise, on_delete=models.PROTECT, verbose_name='Issued By')
    upload = models.FileField(storage=PrivateMediaStorage(), upload_to=CertFilename, blank=True, null=True, validators=[FileExtensionValidator(['pdf'])])
    thumbnail = models.ImageField(storage=PrivateMediaStorage(), upload_to=CertThumbnail, blank=True, null=True)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    current = models.BooleanField('Is this current?', default = True)
    slug = models.SlugField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['-issue_date']
        unique_together = (('talent', 'cm_no'),)
        
    def __str__(self):
        return f'{self.talent}, {self.certification}: {self.current}'

    def save(self, *args, **kwargs):
        if self.upload:
            cache_path = self.upload
            bytes_file = bytes(cache_path.open(mode='rb').read())

            images = convert_from_bytes(bytes_file)[0]
            image = images.resize((int(260), int(360)), Image.ANTIALIAS)

            quality_val = 90
            thumb_io = BytesIO()
            image.save(thumb_io, format='JPEG', quality=quality_val)

            thumb_file = InMemoryUploadedFile(thumb_io, None, 'foo.jpg', 'image/jpeg', thumb_io.__sizeof__(), None)

            self.thumbnail = thumb_file

        if self.expiry_date:
            ed = self.expiry_date
            cd = datetime.date.today()
            dt = (ed-cd).days
            if dt >=0 :
                self.current=True
            else:
                self.current=False
        else:
            self.current=True

        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(LicenseCertification, self).save(*args, **kwargs)
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        certification = kwargs.pop('certification', None)
        region = kwargs.pop('region', None)
        companybranch = kwargs.pop('companybranch', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(alias=talent.alias)
            
        if certification:
            instance.certification = Result.update_or_create(id=certification.id, **certification)

        if region:
            instance.region = Region.update_or_create(id=region.id, **region)

        if companybranch:
            instance.companybranch = Enterprise.update_or_create(slug=companybranch.slug, **companybranch)
        
        instance.save()
            
        return instance


class Course(models.Model):
    name = models.CharField('Course name', max_length=150, unique=True)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, verbose_name="Institution")
    course_type = models.ForeignKey(CourseType, on_delete=models.PROTECT)
    website = models.URLField(blank=True, null=True)
    certification = models.ForeignKey(Result, on_delete=models.PROTECT, verbose_name = 'Result')

    class Meta:
        unique_together = (('name','company'),)

    def __str__(self):
        return '{}, {} ({})'.format(self.name, self.company, self.course_type)
        
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        company = kwargs.pop('company', None)
        course_type = kwargs.pop('course_type', None)
        certification = kwargs.pop('certification', None)
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if company:
            instance.company = Enterprise.update_or_create(slug=company.slug, **company)

        if course_type:
            instance.course_type = CourseType.update_or_create(id=course_type.id, **course_type)

        if certification:
            instance.certification = Result.update_or_create(id=certification.id, **certification)
        
        instance.save()
            
        return instance

    def clean(self):
            self.name = self.name.title()


class Topic(models.Model):
    topic = models.CharField(max_length=60, unique=True)
    skills = models.ManyToManyField(SkillTag)
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    
    def __str__(self):
        return '{}'.format(self.topic)
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        skills = kwargs.pop('tag', [])

        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if skills:
            tag_related_models_data = {
                'model': SkillTag,
                'manager': 'skills',
                'fields': ['skill', 'code'],
                'data': skills,
            }
            instance = handle_m2m_relationship(instance, [tag_related_models_data])
            
        instance.save()
        
        return instance

    def clean(self):
        self.topic = self.topic.title()


class Lecturer(models.Model):
        #Captured by talent
    education = models.ForeignKey('WorkExperience', on_delete=models.CASCADE)
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Subject")
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now_add=True)
    locked = models.BooleanField(default=False)
        #Captured by lecturer
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S', null=True)
    comments = models.TextField(blank=True, null=True)
    publish_comment = models.BooleanField(default=False)
        #Captured by talent
    response = models.TextField('My Response', blank=True, null=True)
    slug = models.SlugField(max_length=9, unique=True, null=True)
    
    class Meta:
        unique_together = (('education','lecturer','date_captured'),)

    def __str__(self):
        return f"Lecturer for {self.education}"

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(Lecturer, self).save(*args, **kwargs)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        lecturer = kwargs.pop('lecturer', None)
        education = kwargs.pop('education', None)
        topic = kwargs.pop('topic', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if lecturer:
            instance.lecturer = User.objects.get(alias=lecturer.alias)
            
        if education:
            instance.education = WorkExperience.update_or_create(slug=education.slug, **education)

        if topic:
            instance.topic = Topic.update_or_create(id=topic.id, **topic)

        instance.save()
            
        return instance


class ClassMates(models.Model):
        #Captured by talent
    education = models.ForeignKey('WorkExperience', on_delete=models.CASCADE)
    colleague = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, verbose_name='ClassMate')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, verbose_name="Subject")
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now_add=True)
    locked = models.BooleanField(default=False)
        #Captured by colleague
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
    publish_comment = models.BooleanField(default=False)
        #Captured by talent
    response = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=9, unique=True, null=True)
    
    class Meta:
        unique_together = (('education','colleague','date_captured'),)

    def __str__(self):
        return f"ClassMate for {self.education}"

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(ClassMates, self).save(*args, **kwargs)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        colleague = kwargs.pop('colleague', None)
        education = kwargs.pop('education', None)
        topic = kwargs.pop('topic', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if colleague:
            instance.colleague = User.objects.get(alias=lecturer.alias)
            
        if education:
            instance.education = WorkExperience.update_or_create(slug=education.slug, **education)

        if topic:
            instance.topic = Topic.update_or_create(id=topic.id, **topic)

        instance.save()
            
        return instance


class Designation(models.Model):
    name = models.CharField('Designation', max_length=60, unique=True)
    
    def __str__(self):
        return self.name
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        return instance

    def clean(self):
        self.name = self.name.title()

#Function to randomise filename for Profile Upload
def ExpFilename(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/experience\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)

def ExpThumbnail(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/experience\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)

class WorkExperience(models.Model):
    TYPE=(
        ('F','Freelance'),
        ('C','Contract'),
        ('T','Consultant'),
        ('E','Employee'),
        ('O','FIFO'),
    )
    #Common Fields
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()
    date_captured = models.DateField(auto_now_add=True)
    upload = models.FileField(storage=PrivateMediaStorage(), upload_to=ExpFilename, blank=True, null=True, validators=[FileExtensionValidator(['pdf'])])
    thumbnail = models.ImageField(storage=PrivateMediaStorage(), upload_to=ExpThumbnail, blank=True, null=True)
    score = models.SmallIntegerField(default=0)
    employment_type = models.CharField(max_length=1, choices=TYPE, default='F', blank=True, null=True)
    title = models.CharField(max_length=250, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    publish_comment = models.BooleanField(default=False)
    not_validated = models.BooleanField(default=False)
    #Work Experience Fields (Captured & Pre-Experience)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, verbose_name='Company', null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name='Company Branch', null=True)
    estimated = models.BooleanField(default=False)
    prelog = models.BooleanField(default=False)
    wexp = models.BooleanField(default=False)
    project = models.ForeignKey(
        ProjectData, on_delete=models.PROTECT, verbose_name='On Project', blank=True, null=True
    )
    project_data = models.ForeignKey(
        ProjectPersonalDetails, on_delete=models.PROTECT, verbose_name='Project', blank=True, null=True)
    industry = models.ForeignKey(Industry, on_delete=models.PROTECT, null=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True)
    skills = models.ManyToManyField(SkillTag, related_name='experience')
    #Fields for Education & Training
    edt = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, null=True, verbose_name="Subject")
    slug = models.SlugField(max_length=10, blank=True, null=True, unique=True)
    
    class Meta:
        unique_together = (('talent','hours_worked','date_from', 'date_to', 'course','topic', 'company'),)

    def __str__(self):
        return f'{self.talent} between {self.date_from} & {self.date_to}'

    #script to check wheter experience is estimated or not
    def save(self, *args, **kwargs):
        if self.upload:
            cache_path = self.upload
            bytes_file = bytes(cache_path.open(mode='rb').read())

            images = convert_from_bytes(bytes_file)[0]
            image = images.resize((int(260), int(360)), Image.ANTIALIAS)

            quality_val = 90
            thumb_io = BytesIO()
            image.save(thumb_io, format='JPEG', quality=quality_val)

            thumb_file = InMemoryUploadedFile(thumb_io, None, 'foo.jpg', 'image/jpeg', thumb_io.__sizeof__(), None)

            self.thumbnail = thumb_file

        if self.estimated == True:
            pass
        else:
            a = timezone.now().date()
            b = self.date_from

            dur_d = (a - b).days

            if dur_d >= 14:
                self.estimated = True
            else:
                pass

        if self.slug is None or self.slug == "":
                self.slug = create_code9(self)

        super(WorkExperience, self).save(*args, **kwargs)
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        company = kwargs.pop('company', None)
        companybranch = kwargs.pop('companybranch', None)
        project = kwargs.pop('project', None)
        project_data = kwargs.pop('project_data', None)
        industry = kwargs.pop('industry', None)
        designation = kwargs.pop('designation', None)
        course = kwargs.pop('course', None)
        topic = kwargs.pop('topic', None)
        skills = kwargs.pop('skills', [])

        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if company:
            instance.company = Enterprise.update_or_create(slug=company.slug,**company)

        if companybranch:
            instance.companybranch = Branch.update_or_create(slug=companybranch.slug, **companybranch)

        if project:
            instance.project = ProjectData.update_or_create(slug=project.slug, **project)

        if project_data:
            instance.project_data = ProjectPersonalDetails.update_or_create(slug=project_data.slug, **project_data)

        if industry:
            instance.industry = Industry.update_or_create(id=industry.id, **industry)

        if designation:
            instance.designation = Designation.update_or_create(id=designation.id, **designation)

        if course:
            instance.course = Course.update_or_create(id=course.id, **course)

        if topic:
            instance.topic = Topic.update_or_create(id=topic.id, **topic)
            
        if skills:
            tag_related_models_data = {
                'model': SkillTag,
                'manager': 'skills',
                'fields': ['skill', 'code'],
                'data': skills,
            }
            instance = handle_m2m_relationship(instance, [tag_related_models_data])
            
        instance.save()
        
        return instance


class CoWorkerMixin(models.Model):
        #Captured by talent
    experience = models.ForeignKey(WorkExperience, on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now_add=True)
    locked = models.BooleanField(default=False)
        #Captured by colleague
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
    publish_comment = models.BooleanField(default=False)
    #skills rating
    quality = models.DecimalField(max_digits=5, decimal_places=2, choices=D_RATING, blank=True, null=True)
    time_taken = models.DecimalField(max_digits=5, decimal_places=2, choices=D_RATING, blank=True, null=True)
    complexity = models.DecimalField(max_digits=5, decimal_places=2, choices=D_RATING, blank=True, null=True)
        #Captured by talent
    response = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=9, unique=True, null=True)

    class Meta:
        abstract = True
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        experience = kwargs.pop('experience', None)
        designation = kwargs.pop('designation', None)
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if experience:
            instance.experience = WorkExperience.update_or_create(slug=experience.slug, **experience)

        if designation:
            instance.designation = Designation.update_or_create(id=designation.id, **designation)
        
        instance.save()
            
        return instance
        
        
class WorkColleague(CoWorkerMixin):
    colleague_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = (('experience','colleague_name','date_captured'),)

    def __str__(self):
        return f'{self.colleague_name} on {self.experience.talent}, captured {self.date_captured} - responded {self.date_confirmed}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(WorkColleague, self).save(*args, **kwargs)
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        instance = super().update_or_create(slug=slug, instance=instance, **kwargs)
        
        colleague_name = kwargs.pop('colleague_name', None)
        
        if colleague_name:
            instance.colleague_name = User.objects.get(alias=colleague_name.alias)
        
        return instance


class Superior(CoWorkerMixin):
    superior_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = (('experience','superior_name','date_captured'),)

    def __str__(self):
        return "WorkSuperior for {} on {}".format(
            self.experience.talent, self.experience
        )

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(Superior, self).save(*args, **kwargs)
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        instance = super().update_or_create(slug=slug, instance=instance, **kwargs)
        
        superior_name = kwargs.pop('superior_name', None)
        
        if superior_name:
            instance.superior_name = User.objects.get(alias=superior_name.alias)
        
        return instance
    

class WorkCollaborator(CoWorkerMixin):
    collaborator_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('experience','collaborator_name','date_captured'),)

    def __str__(self):
        return "WorkCollaborator for {} on {}".format(
            self.experience.talent, self.experience
        )

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(WorkCollaborator, self).save(*args, **kwargs)
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        instance = super().update_or_create(slug=slug, instance=instance, **kwargs)
        
        collaborator_name = kwargs.pop('collaborator_name', None)
        company = kwargs.pop('company', None)
        companybranch = kwargs.pop('companybranch', None)
        
        if collaborator_name:
            instance.collaborator_name = User.objects.get(alias=collaborator_name.alias)
            
        if company:
            instance.company = Enterprise.update_or_create(slug=company.slug, **company)

        if companybranch:
            instance.companybranch = Branch.update_or_create(slug=companybranch.slug, **companybranch)
        
        return instance


class WorkClient(CoWorkerMixin):
    client_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('experience','client_name','date_captured'),)

    def __str__(self):
        return "WorkCollaborator for {} on {}".format(
            self.experience.talent, self.experience
        )

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(WorkClient, self).save(*args, **kwargs)
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        instance = super().update_or_create(slug=slug, instance=instance, **kwargs)
        
        client_name = kwargs.pop('client_name', None)
        company = kwargs.pop('company', None)
        companybranch = kwargs.pop('companybranch', None)
        
        if client_name:
            instance.client_name = User.objects.get(alias=client_name.alias)
            
        if company:
            instance.company = Enterprise.update_or_create(slug=company.slug, **company)

        if companybranch:
            instance.companybranch = Branch.update_or_create(slug=companybranch.slug, **companybranch)
        
        return instance
    

class EmailRemindValidate(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_to', on_delete=models.SET_NULL, blank=True, null=True)
    subject = models.CharField(max_length=240, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    date_sent= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} sent to {self.recipient} on {self.date_sent}"
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        sender = kwargs.pop('sender', None)
        recipient = kwargs.pop('recipient', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if sender:
            instance.sender = User.objects.get(alias=sender.alias)
        
        if recipient:
            instance.recipient = User.objects.get(alias=recipient.alias)
        
        instance.save()
            
        return instance
