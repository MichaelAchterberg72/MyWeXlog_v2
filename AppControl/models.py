from django.db import models
from django.conf import settings


from Profile.utils import create_code9
from enterprises.models import Branch, Enterprise


USER_TYPE = (
    ('A','Administrator'),
    ('U','Standard User'),
    )


class CorporateHR(models.Model):
    companybranch = models.ForeignKey(Branch, on_delete=models.CASCADE, blank=True, null=True)
    company = models.ForeignKey(Enterprise, on_delete=models.CASCADE, blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    expiry = models.DateField(blank=True)
    slug = models.CharField(max_length=9, blank=True)

    class Meta:
        verbose_name_plural = "Corporate HR"

    def __str__(self):
        if self.companybranch is not None:
            return f'{self.companybranch}'
        else:
            return f'{self.company}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(CorporateHR, self).save(*args, **kwargs)


class CorporateStaff(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=USER_TYPE, default='U')
    corporate = models.ForeignKey(CorporateHR, on_delete=models.CASCADE)
    status = models.BooleanField('Active', default=False)
    slug = models.CharField(max_length=9, blank=True)

    class Meta:
        verbose_name_plural = "Corporate Staff"

    def __str__(self):
        return f'{self.corporate}: {self.talent} ({self.status})'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(CorporateStaff, self).save(*args, **kwargs)
