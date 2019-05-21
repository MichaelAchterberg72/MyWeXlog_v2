from django.db import models

from django_countries.fields import CountryField

class Region(models.Model):
    country = CountryField()
    region = models.CharField('Region / State / etc.', max_length=80)

    class Meta:
        unique_together = (('country','region'),)

    def __str__(self):
        return '{}-{}'.format(self.country, self.region)

class City(models.Model):
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    city = models.CharField(max_length=80)

    class Meta:
        unique_together = (('region','city'),)

    def __str__(self):
        return '{}-{}'.format(self.region, self.city)

class Suburb(models.Model):
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    suburb = models.CharField(max_length=80)

    class Meta:
        unique_together = (('suburb','city'),)

    def __str__(self):
        return '{}-{}'.format(self.city, self.suburb)
