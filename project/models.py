from django.db import models

from django_countries.fields import CountryField

from enterprises.models import Enterprise, Industry, Branch
from locations.models import City, Region

class ProjectData(models.Model):
    name = models.CharField('Project name', max_length=250, unique=True)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, verbose_name="Owner", null=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name='Project Site', null=True)
    country = CountryField()
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    industry = models.ForeignKey(Industry, on_delete=models.PROTECT)

    def __str__(self):
        return '{} - {}'.format(self.company, self.name)
