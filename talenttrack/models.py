from django.db import models
from django.conf import settings
from django.utils import timezone
from time import time
from random import random
from django.db.models.signals import post_save


from enterprises.models import Enterprise, Industry, Branch
from project.models import ProjectData
from db_flatten.models import SkillTag

CONFIRM = (
    ('S','Select'),
    ('C','Confirm'),
    ('R','Reject'),
    ('Y','Wrong Person'),
)


class Result(models.Model):#What you receive when completing the course
    type = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.type


class CourseType(models.Model):
    type = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.type


class Course(models.Model):
    name = models.CharField('Course name', max_length=150, unique=True)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, verbose_name="Institution")
    course_type = models.ForeignKey(CourseType, on_delete=models.PROTECT)
    website = models.URLField(blank=True, null=True)
    certification = models.ForeignKey(Result, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('name','company'),)

    def __str__(self):
        return '{}, {} ({})'.format(self.name, self.company, self.course_type)


class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    topic = models.CharField(max_length=60, unique=True)
    skills = models.ManyToManyField(SkillTag)
    hours = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return '{} - {}'.format (self.course, self.topic)


#Function to randomise filename for Profile Upload
def EduFilename(instance, filename):
	ext = filename.split('.')[-1]
	return "education\%s_%s.%s" % (str(time()).replace('.','_'), random(), ext)

class Education(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    date_captured = models.DateField(auto_now_add=True)
    date_from = models.DateField()
    date_to = models.DateField()
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, blank=True, null=True, verbose_name="subject")
    file = models.FileField(upload_to=EduFilename, blank=True, null=True)
    score = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = (('talent','course','topic'),)

    def __str__(self):
        return '{}: {} ({})'.format(self.talent, self.course, self.topic)


class Lecturer(models.Model):
        #Captured by talent
    education = models.ForeignKey(Education, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now=True)
        #Captured by lecturer
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S', null=True)
    comments = models.TextField(blank=True, null=True)
        #Captured by talent
    response = models.TextField('My Response', blank=True, null=True)

    class Meta:
        unique_together = (('education','lecturer','date_captured'),)

    def __str__(self):
        return "Lecturer for {}".format(self.education)


class ClassMates(models.Model):
        #Captured by talent
    education = models.ForeignKey(Education, on_delete=models.CASCADE)
    colleague = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now=True)
        #Captured by colleague
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
        #Captured by talent
    response = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('education','colleague','date_captured'),)

    def __str__(self):
        return "ClassMate for {}".format(self.education)


class Designation(models.Model):
    name = models.CharField('Designation', max_length=60, unique=True)

    def __str__(self):
        return self.name


#Function to randomise filename for Profile Upload
def ExpFilename(instance, filename):
	ext = filename.split('.')[-1]
	return "experience\%s_%s.%s" % (str(time()).replace('.','_'), random(), ext)


class WorkExperience(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    date_from = models.DateField()
    date_to = models.DateField(default=timezone.now)
    date_captured = models.DateField(auto_now_add=True)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, verbose_name='Company')
    estimated = models.BooleanField(default=False)
    project = models.ForeignKey(
        ProjectData, on_delete=models.PROTECT, verbose_name='On Project', blank=True, null=True
    )
    industry = models.ForeignKey(Industry, on_delete=models.PROTECT)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    comment = models.TextField(blank=True, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
    upload = models.FileField(upload_to=ExpFilename, blank=True, null=True)
    skills = models.ManyToManyField(SkillTag)
    score = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = (('talent','hours_worked','date_from','project', 'date_to'),)

    def __str__(self):
        return '{} between {} & {} as {}'.format(
                    self.talent, self.date_from, self.date_to, self.designation
                    )


class WorkColleague(models.Model):
        #Captured by talent
    experience = models.ForeignKey(WorkExperience, on_delete=models.CASCADE)
    colleague_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now=True)
        #Captured by colleague
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
        #Captured by talent
    response = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('experience','colleague_name','date_captured'),)

    def __str__(self):
        return "WorkColleague for {} on {}".format(
            self.experience.talent, self.experience
        )


class Superior(models.Model):
        #Captured by talent
    experience = models.ForeignKey(WorkExperience, on_delete=models.PROTECT)
    superior_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now=True)
        #Captured by superior
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
        #Captured by talent
    response = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('experience','superior_name','date_captured'),)

    def __str__(self):
        return "WorkSuperior for {} on {}".format(
            self.experience.talent, self.experience
        )


class WorkCollaborator(models.Model):
        #Captured by talent
    experience = models.ForeignKey(WorkExperience, on_delete=models.PROTECT)
    collaborator_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    company = models.ForeignKey(Branch, on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now=True)
        #Captured by collaborator
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
        #Captured by talent
    response = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('experience','collaborator_name','date_captured'),)

    def __str__(self):
        return "WorkCollaborator for {} on {}".format(
            self.experience.talent, self.experience
        )

class WorkClient(models.Model):
        #Captured by talent
    experience = models.ForeignKey(WorkExperience, on_delete=models.PROTECT)
    client_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
    company = models.ForeignKey(Branch, on_delete=models.PROTECT)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now=True)
        #Captured by collaborator
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S')
    comments = models.TextField(blank=True, null=True)
        #Captured by talent
    response = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('experience','client_name','date_captured'),)

    def __str__(self):
        return "WorkCollaborator for {} on {}".format(
            self.experience.talent, self.experience
        )

class PreLoggedExperience(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    date_from = models.DateField()
    date_to = models.DateField(default=timezone.now)
    date_captured = models.DateField(auto_now_add=True)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT)
    project = models.ForeignKey(
        ProjectData, on_delete=models.PROTECT, verbose_name='On Project', blank=True, null=True
    )
    industry = models.ForeignKey(Industry, on_delete=models.PROTECT)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    comment = models.TextField(blank=True, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
    upload = models.FileField(upload_to=ExpFilename, blank=True, null=True)
    skills = models.ManyToManyField(SkillTag, related_name='logskill')
    score = models.SmallIntegerField(default=0)
    
    class Meta:
        unique_together = (('talent','hours_worked','date_from','project', 'date_to'),)

    def __str__(self):
        return '{} between {} & {} as {}'.format(
                    self.talent, self.date_from, self.date_to, self.designation
                    )


class PreColleague(models.Model):
        #Captured by talent
    pre_experience = models.ForeignKey(PreLoggedExperience, on_delete=models.PROTECT)
    colleague_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
        #AutoCaptured
    date_captured = models.DateField(auto_now_add=True)
    date_confirmed = models.DateField(auto_now=True)
        #Captured by colleague
    confirm = models.CharField(max_length=1, choices=CONFIRM, default='S', null=True)
    comments = models.TextField(blank=True, null=True)
        #Captured by talent
    response = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('pre_experience','colleague_name','date_captured'),)

    def __str__(self):
        return "WorkColleague for {} on {}".format(
            self.pre_experience.talent, self.pre_experience
        )
