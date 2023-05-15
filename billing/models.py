from django.db import models
from django.conf import settings


from project.models import ProjectPersonalDetails, ProjectPersonalDetailsTask
from enterprises.models import Branch
from talenttrack.models import WorkExperience
# Create your models here.

REPEAT  = (
    ('H','Doesn\'t repeat'),
    ('D','Daily'),
    ('W','Weekly'),
    ('M','Monthly'),
    ('A','Annualy'),
    ('L','Every weekday (Monday to Friday)'),
    ('C','Custom'),
)

BUSY = (
    ('B','Busy'),
    ('F','Free'),
)

NOTIFICATION = (
    ('E','Email'),
    ('N','Notification'),
)

DURATION = (
    ('M','minutes'),
    ('H','hours'),
    ('D','days'),
    ('W','weeks'),
)

class Timesheet(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    work_experience = models.ForeignKey(WorkExperience, on_delete=models.SET_NULL, null=True)
    date_captured = models.DateField(auto_now_add=True)
    date = models.DateField()
    client = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, verbose_name="Client")
    project = models.ForeignKey(ProjectPersonalDetails, on_delete=models.SET_NULL, null=True)
    task = models.ForeignKey(ProjectPersonalDetailsTask, on_delete=models.SET_NULL, null=True, verbose_name="Tasks")
    details = models.TextField(blank=True, null=True)
    time_from = models.DateTimeField()
    time_to = models.DateTimeField()
    location = models.CharField(max_length=30, blank=True, null=True)
    out_of_office = models.BooleanField(default=False)
    notification = models.CharField(max_length=1, choices=NOTIFICATION, default='N')
    notification_time = models.CharField(max_length=1, blank=True, null=True)
    notification_duration = models.CharField(max_length=1, choices=DURATION, default='M')
    busy = models.CharField(max_length=1, choices=BUSY, default='B')
    repeat = models.CharField(max_length=1, choices=REPEAT, default='H')
    include_for_certificate = models.BooleanField(default=False)
    include_for_invoice = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {}'.format(self.time_from, self.task)
