from django.db import models
from django.conf import settings


from project.models import ProjectPersonalDetails, ProjectPersonalDetailsTask
from enterprises.models import Branch
from talenttrack.models import WorkExperience

from utils.utils import update_model, handle_m2m_relationship

from django.contrib.auth import get_user_model

User = get_user_model()


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
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        try:
            if id and not instance:
                instance = cls.objects.get(id=id)
            
            talent = kwargs.pop('talent', None)
            work_experience = kwargs.pop('work_experience', None)
            client = kwargs.pop('client', None)
            project = kwargs.pop('project', None)
            task = kwargs.pop('task', None)
            
            if instance:
                update_model(instance, **kwargs)
                instance.save()
            else:
                instance = cls.objects.create(**kwargs)
                
            if talent:
                instance.talent = User.objects.filter(slug=talent.slug)
                
            if work_experience:
                instance.work_experience = WorkExperience.update_or_create(slug=work_experience.slug, **work_experience)
                
            if client:
                instance.client = Branch.update_or_create(id=client.id, **client)
                
            if project:
                instance.project = ProjectPersonalDetails.update_or_create(slug=project.slug, **project)
                
            if task:
                instance.task = ProjectPersonalDetailsTask.update_or_create(slug=task.slug, **task)
                
            instance.save()
            
            return instance
        
        except Exception as e:
            print('Error: ', e)
            raise e
            
    def __str__(self):
        return '{} - {}'.format(self.time_from, self.task)
