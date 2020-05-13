from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from time import time
import datetime
from random import random
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Count, Sum, F, Q


from Profile.utils import create_code9


from enterprises.models import Enterprise, Industry, Branch
from project.models import ProjectData
from db_flatten.models import SkillTag
from django_countries.fields import CountryField
from locations.models import Region


CONFIRM = (
    ('S','Select'),
    ('C','Confirm'),
    ('R','Reject'),
    ('Y','Wrong Person'),
)


class Achievements(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    achievement = models.CharField(max_length=500)
    date_achieved = models.DateField()
    description = models.TextField('Describe the Achievement')
    slug = models.SlugField(max_length=15, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['-date_achieved']
        unique_together = (('talent', 'achievement', 'date_achieved'),)

    def __str__(self):
        return f'{self.talent}: {self.achievement} ({self.date_achieved})'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(Achievements, self).save(*args, **kwargs)


class Result(models.Model):#What you receive when completing the course
    type = models.CharField(max_length=100, unique=True)

    def clean(self):
        self.type = self.type.capitalize()

    def __str__(self):
        return self.type


class CourseType(models.Model):#What type of course (online, Attend lectures, etc.)
    type = models.CharField(max_length=60, unique=True)

    def clean(self):
        self.type = self.type.capitalize()

    def __str__(self):
        return self.type


class LicenseCertification(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    certification = models.ForeignKey(Result, on_delete=models.PROTECT, verbose_name='Proffessional Memberships / Certification name')
    country = CountryField()
    region = models.ForeignKey(Region, on_delete=models.PROTECT, blank=True, null=True)
    cm_no = models.CharField('Membership / Credential Number', max_length=40)
    companybranch = models.ForeignKey(Enterprise, on_delete=models.PROTECT, verbose_name='Issued By')
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
        self.name = self.name.capitalize()

    class Meta:
        unique_together = (('name','company'),)

    def __str__(self):
        return '{}, {} ({})'.format(self.name, self.company, self.course_type)


class Topic(models.Model):
    topic = models.CharField(max_length=60, unique=True)
    skills = models.ManyToManyField(SkillTag)
    hours = models.DecimalField(max_digits=5, decimal_places=2)

    def clean(self):
        self.topic = self.topic.capitalize()

    def __str__(self):
        return '{}'.format(self.topic)


class Lecturer(models.Model):
        #Captured by talent
    education = models.ForeignKey('WorkExperience', on_delete=models.CASCADE)
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Subject")
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now=True)
        #Captured by lecturer
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S', null=True)
    comments = models.TextField(blank=True, null=True)
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
    colleague = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='ClassMate')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, verbose_name="Subject")
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now=True)
        #Captured by colleague
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
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
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name


#Function to randomise filename for Profile Upload
def ExpFilename(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/experience\%s_%s.%s" % (instance.talent.id, str(time()).replace('.','_'), random(), ext)


class WorkExperience(models.Model):
    #Common Fields
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()
    date_captured = models.DateField(auto_now_add=True)
    upload = models.FileField(upload_to=ExpFilename, blank=True, null=True, validators=[FileExtensionValidator(['pdf'])])
    score = models.SmallIntegerField(default=0)
    comment = models.TextField(blank=True, null=True)
    #Work Experience Fields (Captured & Pre-Experience)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, verbose_name='Company', null=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name='Company Branch', null=True)
    estimated = models.BooleanField(default=False)
    prelog = models.BooleanField(default=False)
    wexp = models.BooleanField(default=False)
    project = models.ForeignKey(
        ProjectData, on_delete=models.PROTECT, verbose_name='On Project', blank=True, null=True
    )
    industry = models.ForeignKey(Industry, on_delete=models.PROTECT, null=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True)
    skills = models.ManyToManyField(SkillTag, related_name='experience')
    #Fields for Education & Training
    edt = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, null=True, verbose_name="Subject")
    slug = models.SlugField(max_length=30, blank=True, null=True, unique=True)

    class Meta:
        unique_together = (('talent','hours_worked','date_from', 'date_to'),)

    def __str__(self):
        return f'{self.talent} between {self.date_from} & {self.date_to}'

    #script to check wheter experience is estimated or not
    def save(self, *args, **kwargs):
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
    colleague_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now=True)
        #Captured by colleague
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
        #Captured by talent
    response = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=9, unique=True, null=True)

    class Meta:
        unique_together = (('experience','colleague_name','date_captured'),)

    def __str__(self):
        return "WorkColleague for {} on {}".format(
            self.experience.talent, self.experience
        )

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(WorkColleague, self).save(*args, **kwargs)


class Superior(models.Model):
        #Captured by talent
    experience = models.ForeignKey(WorkExperience, on_delete=models.CASCADE)
    superior_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now=True)
        #Captured by superior
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
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
    collaborator_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now=True)
        #Captured by collaborator
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
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
    client_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now=True)
        #Captured by collaborator
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
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
