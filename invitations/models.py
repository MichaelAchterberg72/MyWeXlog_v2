from django.conf import settings
from django.db import models
from tinymce.models import HTMLField

from enterprises.models import Branch
from talenttrack.models import WorkExperience

from Profile.utils import create_code9

from utils.utils import update_model

from django.contrib.auth import get_user_model

User = get_user_model()


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
    slug = models.SlugField(max_length=9, unique=True, null=True)
    
    def __str__(self):
        return f"{self.name} {self.surname} invited by {self.invited_by} on {self.date_invited} - {self.date_accepted}"

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(Invitation, self).save(*args, **kwargs)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        invited_by = kwargs.pop('invited_by', None)
        experience = kwargs.pop('experience', None)
        companybranch = kwargs.pop('companybranch', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if invited_by:
            instance.invited_by = User.objects.get(alias=invited_by.alias)
            
        if experience:
            instance.experience = WorkExperience.update_or_create(slug=experience.slug, **experience)
            
        if companybranch:
            instance.companybranch = Branch.update_or_create(slug=companybranch.slug, **companybranch)
        
        instance.save()
            
        return instance