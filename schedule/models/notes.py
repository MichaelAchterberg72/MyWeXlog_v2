from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import datetime
from django.db.models import Q
from django.template.defaultfilters import date
from django.urls import reverse
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django.utils.translation import gettext, gettext_lazy as _

from Profile.utils import create_code7, create_code9

from tinymce.models import HTMLField

from schedule.models.calendars import Calendar
from schedule.models.rules import Rule
from schedule.utils import OccurrenceReplacer

from schedule.models import Calendar, Event, Occurrence
from enterprises.models import Branch
from project.models import ProjectPersonalDetails, ProjectPersonalDetailsTask
from db_flatten.models import SkillTag

from utils.utils import update_model

from django.contrib.auth import get_user_model

User = get_user_model()


class NotePad(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    occurrence_id = models.ForeignKey(Occurrence, on_delete=models.SET_NULL, blank=True, null=True)
    event_id = models.ForeignKey(Event, on_delete=models.SET_NULL, blank=True, null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Branch Working for on Project')
    project_data = models.ForeignKey(ProjectPersonalDetails, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Personal Project Details')
    task = models.ForeignKey(ProjectPersonalDetailsTask, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Tasks")
    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    updated_on = models.DateTimeField(_("updated on"), auto_now=True)
    heading = models.CharField(max_length=240, null=True)
    note_pad = HTMLField(blank=True, null=True)
    date_due = models.DateTimeField(_("due on"), blank=True, null=True)
    complete = models.BooleanField(default=False)
    date_complete = models.DateTimeField(_("completed on"), blank=True, null=True)
    slug = models.SlugField(max_length=15, blank=True, null=True, unique=True)
    
    def __str__(self):
        return f'{self.talent} - {self.created_on}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(NotePad, self).save(*args, **kwargs)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        occurrence_id = kwargs.pop('occurrence_id', None)
        event_id = kwargs.pop('event_id', None)
        companybranch = kwargs.pop('companybranch', None)
        project_data = kwargs.pop('project_data', None)
        task = kwargs.pop('task', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if talent:
            instance.talent = User.objects.get(alias=talent.alias)
            
        if occurrence_id:
            instance.occurrence_id = Occurrence.update_or_create(id=occurrence_id.id, **occurrence_id)
            
        if event_id:
            instance.event_id = Event.update_or_create(id=event_id.id, **event_id)
            
        if companybranch:
            instance.companybranch = Branch.update_or_create(slug=companybranch.slug, **companybranch)

        if project_data:
            instance.project_data = ProjectPersonalDetails.update_or_create(slug=project_data.slug, **project_data)

        if task:
            instance.task = ProjectPersonalDetailsTask.update_or_create(slug=task.slug, **task)
        
        instance.save()
            
        return instance
    

def NotePad_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = f'b{instance.talent.id}{instance.id}h'

pre_save.connect(NotePad_slug, sender=NotePad)


class NotePadRelatedProject(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notepad_id = models.ForeignKey(NotePad, on_delete=models.SET_NULL, null=True)
    project_data = models.ForeignKey(ProjectPersonalDetails, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Personal Project Details')

    def __str__(self):
        return f'{self.talent} - {self.notepad_id}'
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        notepad_id = kwargs.pop('notepad_id', None)
        project_data = kwargs.pop('project_data', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(alias=talent.alias)
            
        if notepad_id:
            instance.notepad_id = NotePad.update_or_create(slug=notepad_id.slug, **notepad_id)
        
        if project_data:
            instance.project_data = ProjectPersonalDetails.update_or_create(slug=project_data.slug, **project_data)

        instance.save()
            
        return instance


class NotePadRelatedTask(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notepad_id = models.ForeignKey(NotePad, on_delete=models.SET_NULL, null=True)
    related_notepad_id = models.ForeignKey(NotePad, related_name='related_notepad', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.talent} - {self.notepad_id}'
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        notepad_id = kwargs.pop('notepad_id', None)
        related_notepad_id = kwargs.pop('related_notepad_id', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if notepad_id:
            instance.notepad_id = NotePad.update_or_create(slug=notepad_id.slug, **notepad_id)
        
        if related_notepad_id:
            instance.related_notepad_id = NotePad.update_or_create(slug=related_notepad_id.slug, **related_notepad_id)
        
        instance.save()
            
        return instance


class NotePadRelatedEvent(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notepad_id = models.ForeignKey(NotePad, on_delete=models.SET_NULL, null=True)
    related_event_id = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.talent} - {self.notepad_id}'
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        notepad_id = kwargs.pop('notepad_id', None)
        related_event_id = kwargs.pop('related_event_id', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(alias=talent.alias)
            
        if notepad_id:
            instance.notepad_id = NotePad.update_or_create(slug=notepad_id.slug, **notepad_id)
        
        if related_event_id:
            instance.related_event_id = NotePad.update_or_create(slug=related_event_id.slug, **related_event_id)
        
        instance.save()
            
        return instance
    

class NotePadRelatedOccurrence(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notepad_id = models.ForeignKey(NotePad, on_delete=models.SET_NULL, null=True)
    related_occurrence_id = models.ForeignKey(Occurrence, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.talent} - {self.notepad_id}'
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        notepad_id = kwargs.pop('notepad_id', None)
        related_occurrence_id = kwargs.pop('related_occurrence_id', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(alias=talent.alias)
            
        if notepad_id:
            instance.notepad_id = NotePad.update_or_create(slug=notepad_id.slug, **notepad_id)
        
        if related_occurrence_id:
            instance.related_occurrence_id = NotePad.update_or_create(slug=related_occurrence_id.slug, **related_occurrence_id)
        
        instance.save()
            
        return instance