from django.db import models
from django.conf import settings

from django_countries.fields import CountryField

from enterprises.models import Enterprise, Industry, Branch
from locations.models import Currency, City, Region


from Profile.utils import create_code9


class ProjectData(models.Model):
    name = models.CharField('Project name', max_length=250)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, verbose_name="Owner", null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name='Branch Managing the Project', null=True)
    description = models.TextField(blank=True, null=True, verbose_name="Overall project description")
    country = CountryField()
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    industry = models.ForeignKey(Industry, on_delete=models.PROTECT)
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)

    class Meta:
        unique_together = (('name','companybranch'),)

    def __str__(self):
        return '{} - {}'.format(self.company, self.name)

    def clean(self):
        self.name = self.name.title()

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(ProjectData, self).save(*args, **kwargs)


class ProjectPersonalDetails(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(ProjectData, on_delete=models.CASCADE)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, verbose_name="Owner", null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name='Branch Working for on the Project', null=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return '{} - {}'.format(self.talent, self.project)

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(ProjectPersonalDetails, self).save(*args, **kwargs)


class ProjectPersonalDetailsTask(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ppd = models.ForeignKey(ProjectPersonalDetails, on_delete=models.CASCADE)
    company = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name="Company")
    client = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name="Client")
    task = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    date_create = models.DateField(auto_now_add=True)
    date_start = models.DateField(blank=True, null=True)
    date_end = models.DateField(blank=True, null=True)
    current = models.BooleanField(default=True)
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.ppd, self.task)

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(ProjectPersonalDetailsTask, self).save(*args, **kwargs)


RATE_UNIT = (
    ('H','per Hour'),
    ('D','per Day'),
    ('M','per Month'),
    ('L','Lump Sum'),
)

class ProjectTaskBilling(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ppdt = models.ForeignKey(ProjectPersonalDetailsTask, on_delete=models.CASCADE, verbose_name="Task")
    billing_rate = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    rate_unit = models.CharField(max_length=1, choices=RATE_UNIT, default='H')
    date_start = models.DateField(blank=True, null=True)
    date_end = models.DateField(blank=True, null=True)
    current = models.BooleanField(default=True)

    def __str__(self):
        return '{} {} {}'.format(self.ppdt.task, self.billing_rate, self.currency)
