from django.db import models

from django_countries.fields import CountryField

from enterprises.models import Enterprise, Industry, Branch
from locations.models import City, Region


from Profile.utils import create_code9


class ProjectData(models.Model):
    name = models.CharField('Project name', max_length=250, unique=True)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, verbose_name="Owner", null=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name='Branch Managing the Project', null=True)
    country = CountryField()
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    industry = models.ForeignKey(Industry, on_delete=models.PROTECT)
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return '{} - {}'.format(self.company, self.name)

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(ProjectData, self).save(*args, **kwargs)
