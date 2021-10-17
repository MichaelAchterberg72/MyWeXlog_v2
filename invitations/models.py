from django.conf import settings
from django.db import models
from tinymce.models import HTMLField

from enterprises.models import Branch
from talenttrack.models import WorkExperience


class Invitation(models.Model):
    WREL = (
        ('LR','Lecturer'),
        ('CM','Class Mate'),
        ('WC','Colleague'),
        ('WS','Superior'),
        ('WL','Collaborator'),
        ('WT','Client'),
        ('PC','Colleague'),
        ('AF','Acqaintance / Friend'),
    )
    name = models.CharField('First Name', max_length=45)
    surname = models.CharField('Surname', max_length=45)
    experience = models.ForeignKey(WorkExperience, on_delete=models.SET_NULL, null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.SET_NULL, verbose_name='Who did they work for at the time', null=True)
    relationship = models.CharField(max_length=2, choices=WREL, null=True)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    message = HTMLField(blank=True, null=True)
    email = models.EmailField(unique=True)
    date_invited = models.DateTimeField(auto_now_add=True)
    accpeted = models.BooleanField(null=True, default=False)
    date_accepted = models.DateTimeField(auto_now=True)
    assigned = models.BooleanField('Assigned since registration', default=False)

    def __str__(self):
        return f"{self.name} {self.surname} invited by {self.invited_by} on {self.date_invited} - {self.date_accepted}"
