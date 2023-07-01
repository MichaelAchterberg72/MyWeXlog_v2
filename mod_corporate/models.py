from django.conf import settings
from django.db import models
from django.utils import timezone

from AppControl.models import CorporateHR
from marketplace.models import WorkLocation
from Profile.utils import create_code9
from talenttrack.models import Designation

from utils.utils import update_model

from django.contrib.auth import get_user_model

User = get_user_model()


class OrgStructure(models.Model):
    corporate = models.ForeignKey(CorporateHR, on_delete=models.CASCADE)
    level_name = models.CharField(max_length=100)
    parent = models.ForeignKey('OrgStructure', on_delete=models.CASCADE, related_name='parentdept', blank=True, null=True)

    class Meta:
        unique_together = (('corporate','level_name'),)
        
    def __str__(self):
        return f'{self.level_name}'
        
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        instance.save()
            
        return instance


class CorporateStaff(models.Model):
    '''Department Head can only see stats for the departments. They cannot add or remove people.'''
    USER_TYPE = (
        (3,'Administrator'),
        (2,'Controller'),
        (1,'Department Head'),
        (0,'Staff'),
        )
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    corp_access = models.SmallIntegerField(choices=USER_TYPE, default=0)
    type = models.ForeignKey(WorkLocation, on_delete=models.PROTECT)
    department = models.ForeignKey(OrgStructure, on_delete=models.PROTECT)
    corporate = models.ForeignKey(CorporateHR, on_delete=models.CASCADE)
    #admin = models.BooleanField('Admin Status', default=False)#admin status
    status = models.BooleanField('Admin / Staff', default=False)#available for admin duty
    hide = models.BooleanField('Ignore', default=False)#hides people from the list if they are not staff - must not count entries that are hidden in the fee.
    date_add = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    unlocked = models.BooleanField(default=False)
    resigned = models.BooleanField(default=False)
    slug = models.CharField(max_length=9, blank=True)
    date_from = models.DateField()
    date_to = models.DateField(blank=True, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True)

    class Meta:
        verbose_name_plural = "Corporate Staff"
        
    def __str__(self):
        return f'{self.corporate}: {self.talent} ({self.status})'
    
    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(CorporateStaff, self).save(*args, **kwargs)
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        type = kwargs.pop('type', None)
        department = kwargs.pop('department', None)
        corporate = kwargs.pop('corporate', None)
        designation = kwargs.pop('designation', None)
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if talent:
            instance.talent = User.objects.get(alias=talent.alias)
            
        if type:
            instance.type = WorkLocation.update_or_create(id=type.id, **type)

        if department:
            instance.department = OrgStructure.update_or_create(id=department.id, **department)

        if corporate:
            instance.corporate = CorporateHR.update_or_create(id=corporate.id, **corporate)

        if designation:
            instance.designation = Designation.update_or_create(id=designation.id, **designation)

        instance.save()
            
        return instance

    @property
    def tenure(self):
        today = timezone.now().date()
        if self.date_to:
            tenure = self.date_to - self.date_from
        else:
            tenure = today - self.date_from

        months = tenure.days/(365/12)
        years = months/12

        return years


class RequiredSkills(models.Model):
    department = models.ForeignKey(OrgStructure, on_delete=models.CASCADE)
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        department = kwargs.pop('department', None)
            
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
            
        if department:
            instance.department = OrgStructure.update_or_create(id=department.id, **department)
        
        instance.save()
            
        return instance
