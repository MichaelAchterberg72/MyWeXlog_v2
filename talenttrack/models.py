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
from booklist.handle import handle_publisher
from db_flatten.models import SkillTag
from enterprises.models import Branch, Enterprise, Industry
from locations.models import Region
from Profile.utils import create_code9
from project.models import ProjectData, ProjectPersonalDetails
from WeXlog.storage_backends import PrivateMediaStorage

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
        
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(pk=id)

        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        return instance
    
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
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(pk=id)
            
        tag = kwargs.pop('tag', [])

        if instance:
            for field, value in kwargs.items():
                if field != "talent" or "tag":
                    setattr(instance, field, value)
            instance.save()
        else:
            kwargs.pop('tag', None)
            instance = cls.objects.create(**kwargs)
            
        if tag:
            instance = handle_m2m_relationship(
                instance=instance, 
                related_models_data=tag
            )
            
        return instance

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
    
    def update_or_create(cls, id=None, instance=None, **kwargs):
        talent = kwargs.pop("talent", None)
        publisher = kwargs.pop("publisher", None)
        author = kwargs.pop("author", [])
        tag = kwargs.pop("tag", [])
        genre = kwargs.pop("genre", [])

        if id and not instance:
            instance = cls.objects.get(pk=id)
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        # if talent:
        #     instance.talent = CustomUser.update_or_create(
        #         instance=instance.talent,
        #         **talent,
        #     )

        if publisher:
            instance.publisher = handle_publisher(instance, **publisher)

        # if author:
            

        # if tag:
            

        # if genre:
            

                     

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


class Result(models.Model):#What you receive when completing the course
    type = models.CharField(max_length=100, unique=True)

    def clean(self):
        self.type = self.type.title()

    def __str__(self):
        return self.type


class CourseType(models.Model):#What type of course (online, Attend lectures, etc.)
    type = models.CharField(max_length=60, unique=True)

    def clean(self):
        self.type = self.type.title()

    def __str__(self):
        return self.type


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


class Course(models.Model):
    name = models.CharField('Course name', max_length=150, unique=True)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, verbose_name="Institution")
    course_type = models.ForeignKey(CourseType, on_delete=models.PROTECT)
    website = models.URLField(blank=True, null=True)
    certification = models.ForeignKey(Result, on_delete=models.PROTECT, verbose_name = 'Result')

    def clean(self):
        self.name = self.name.title()

    class Meta:
        unique_together = (('name','company'),)

    def __str__(self):
        return '{}, {} ({})'.format(self.name, self.company, self.course_type)


class Topic(models.Model):
    topic = models.CharField(max_length=60, unique=True)
    skills = models.ManyToManyField(SkillTag)
    hours = models.DecimalField(max_digits=5, decimal_places=2)

    def clean(self):
        self.topic = self.topic.title()

    def __str__(self):
        return '{}'.format(self.topic)


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


class Designation(models.Model):
    name = models.CharField('Designation', max_length=60, unique=True)

    def clean(self):
        self.name = self.name.title()

    def __str__(self):
        return self.name


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


class WorkColleague(models.Model):
        #Captured by talent
    experience = models.ForeignKey(WorkExperience, on_delete=models.PROTECT)
    colleague_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
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
        unique_together = (('experience','colleague_name','date_captured'),)

    def __str__(self):
        return f'{self.colleague_name} on {self.experience.talent}, captured {self.date_captured} - responded {self.date_confirmed}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(WorkColleague, self).save(*args, **kwargs)


class Superior(models.Model):
        #Captured by talent
    experience = models.ForeignKey(WorkExperience, on_delete=models.CASCADE)
    superior_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now_add=True)
    locked = models.BooleanField(default=False)
        #Captured by superior
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
        unique_together = (('experience','superior_name','date_captured'),)

    def __str__(self):
        return "WorkSuperior for {} on {}".format(
            self.experience.talent, self.experience
        )

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(Superior, self).save(*args, **kwargs)

class WorkCollaborator(models.Model):
        #Captured by talent
    experience = models.ForeignKey(WorkExperience, on_delete=models.CASCADE)
    collaborator_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now_add=True)
    locked = models.BooleanField(default=False)
        #Captured by collaborator
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
    publish_comment = models.BooleanField(default=False)
    #skills rating
    quality = models.DecimalField(max_digits=5, decimal_places=2, choices=D_RATING, blank=True, null=True)
    time_taken = models.DecimalField(max_digits=5, decimal_places=2, choices=D_RATING, blank=True, null=True)
    complexity = models.DecimalField(max_digits=5, decimal_places=2, choices=D_RATING, blank=True, null=True)
        #Captured by talent
    response = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=9, unique=True, null=True, blank=True)

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


class WorkClient(models.Model):
        #Captured by talent
    experience = models.ForeignKey(WorkExperience, on_delete=models.CASCADE)
    client_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.PROTECT)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now_add=True)
    locked = models.BooleanField(default=False)
        #Captured by collaborator
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
    publish_comment = models.BooleanField(default=False)
    #skills rating
    quality = models.DecimalField(max_digits=5, decimal_places=2, choices=D_RATING, blank=True, null=True)
    time_taken = models.DecimalField(max_digits=5, decimal_places=2, choices=D_RATING, blank=True, null=True)
    complexity = models.DecimalField(max_digits=5, decimal_places=2, choices=D_RATING, blank=True, null=True)
        #Captured by talent
    response = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=20, unique=True, null=True)

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

class EmailRemindValidate(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_to', on_delete=models.SET_NULL, blank=True, null=True)
    subject = models.CharField(max_length=240, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    date_sent= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} sent to {self.recipient} on {self.date_sent}"
