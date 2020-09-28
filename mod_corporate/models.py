from django.db import models
from django.conf import settings


from Profile.utils import create_code9


from AppControl.models import (
    CorporateHR,
)

from marketplace.models import (
    WorkLocation,
)


class OrgStructure(models.Model):
    corporate = models.ForeignKey(CorporateHR, on_delete=models.CASCADE)
    level_name = models.CharField(max_length=100)
    level = models.ForeignKey('OrgStructure', on_delete=models.CASCADE, related_name='parent', blank=True, null=True)

    def __str__(self):
        return f'{self.corporate}-{self.level_name}'

    class Meta:
        unique_together = (('corporate','level_name'),)


class CorporateStaff(models.Model):
    USER_TYPE = (
        (2,'Administrator'),
        (1,'Controller'),
        (0,'Staff'),
        )
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    corp_access = models.SmallIntegerField(choices=USER_TYPE, default=0)
    type = models.ForeignKey(WorkLocation, on_delete=models.PROTECT)
    corporate = models.ForeignKey(CorporateHR, on_delete=models.CASCADE)
    admin = models.BooleanField('Admin Status', default=False)#admin status
    status = models.BooleanField('Admin / Staff', default=False)#available for admin duty
    date_add = models.DateField(auto_now_add=True)
    unlocked = models.BooleanField(default=False)
    slug = models.CharField(max_length=9, blank=True)

    class Meta:
        verbose_name_plural = "Corporate Staff"
        unique_together = (('corporate','talent'),)

    def __str__(self):
        return f'{self.corporate}: {self.talent} ({self.status})'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(CorporateStaff, self).save(*args, **kwargs)
