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



class NotePad(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    occurrence_id = models.ForeignKey(Occurrence, on_delete=models.SET_NULL, null=True)
    event_id = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Branch Working for on Project')
    project_data = models.ForeignKey(ProjectPersonalDetails, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Personal Project Details')
    task = models.ForeignKey(ProjectPersonalDetailsTask, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Tasks")
    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    updated_on = models.DateTimeField(_("updated on"), auto_now=True)
    heading = models.CharField(max_length=240, null=True)
    note_pad = HTMLField(blank=True, null=True)
    date_due = models.DateTimeField(_("due on"), blank=True, null=True)
    complete = models.BooleanField('Is Completed', default=False)
    date_complete = models.DateTimeField(_("completed on"), auto_now=True)
    slug = models.SlugField(max_length=15, blank=True, null=True, unique=True)

    def __str__(self):
        return f'{self.talent} - {self.date_captured}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(NotePad, self).save(*args, **kwargs)

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


class NotePadRelatedTask(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notepad_id = models.ForeignKey(NotePad, on_delete=models.SET_NULL, null=True)
    related_notepad_id = models.ForeignKey(NotePad, related_name='related_notepad', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.talent} - {self.notepad_id}'


class NotePadRelatedEvent(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notepad_id = models.ForeignKey(NotePad, on_delete=models.SET_NULL, null=True)
    related_event_id = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.talent} - {self.notepad_id}'


class NotePadRelatedOccurrence(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notepad_id = models.ForeignKey(NotePad, on_delete=models.SET_NULL, null=True)
    related_occurrence_id = models.ForeignKey(Occurrence, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.talent} - {self.notepad_id}'
