from django.db import models
from django.conf import settings

from django.utils import timezone

from Profile.utils import create_code9


from AppControl.models import (
    CorporateHR,
)

from marketplace.models import (
    WorkLocation,
)

from talenttrack.models import(
        Designation
        )

class OrgStructure(models.Model):
    corporate = models.ForeignKey(CorporateHR, on_delete=models.CASCADE)
    level_name = models.CharField(max_length=100)
    parent = models.ForeignKey('OrgStructure', on_delete=models.CASCADE, related_name='parentdept', blank=True, null=True)

    def __str__(self):
        return f'{self.level_name}'

    class Meta:
        unique_together = (('corporate','level_name'),)


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

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(CorporateStaff, self).save(*args, **kwargs)


class RequiredSkills(models.Model):
    department = models.ForeignKey(OrgStructure, on_delete=models.CASCADE)
