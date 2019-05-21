from django.db import models
from django.conf import settings

from enterprises.models import Enterprise

class Topic(models.Model):
    topic = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.topic

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
    institution = models.ForeignKey(Enterprise, on_delete=models.PROTECT)
    course_type = models.ForeignKey(CourseType, on_delete=models.PROTECT)
    website = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = (('name','institution'),)

    def __str__(self):
        return '{}, {} ({})'.format(self.name, self.institution, self.course_type)

#Function to randomise filename for Profile Upload
def ExtFilename(instance, filename):
	ext = filename.split('.')[-1]
	return "education\%s_%s.%s" % (str(time()).replace('.','_'), random(), ext)

class Education(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    date_from = models.DateField()
    date_to = models.DateField()
    subject = models.ForeignKey(Topic, on_delete=models.PROTECT, blank=True, null=True)
    certification = models.ForeignKey(Result, on_delete=models.PROTECT)
    file = models.FileField(upload_to=ExtFilename)

    class Meta:
        unique_together = (('talent','course','subject'),)

    def __str__(self):
        return '{}: {} ({})'.format(self.talent, self.course, self.subject)
