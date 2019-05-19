from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


from django_countries.fields import CountryField
#from Location.models import Region, City, Suburb
#from enterprise.models import enterprise




class SiteName(models.Model):
    site = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.site

class OnlineRegistrations(models.Model):
    profileurl = models.URLField()
    sitename = models.ForeignKey(SiteName, on_delete=models.PROTECT, related_name='Site_Name')

    class Meta:
        unique_together = (('profileurl', 'sitename'),)

    def __str__(self):
        return self.sitename

class Profile(models.Model):
    talent = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birth_date = models.DateField('Date of Birth')
    background = models.TextField()
    mentor = models.BooleanField(default=False)#Opt in to be a mentor to other people
    onlineprofiles = models.ForeignKey(OnlineRegistrations, on_delete=models.CASCADE)

    def __str__(self):
        return self.talent

class Email(models.Model):
    talent = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=False)
    #company = models.ForeignKey(Enterprise, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.email

class PhysicalAddress(models.Model):
    talent = models.ForeignKey(Profile, on_delete=models.CASCADE)
    line1 = models.CharField('Address Line 1', max_length=100)
    line2 = models.CharField('Address Line 2', max_length=100, blank=True, null=True)
    line3 = models.CharField('Address Line 3', max_length=100, blank=True, null=True)
    country = CountryField()
    #region = models.ForeignKey(Region, on_delete=models.PROTECT)
    #city = models.ForeignKey(City, on_delete=models.PROTECT)
    #suburb = models.ForeignKey(Suburb, on_delete=models.PROTECT)
    code = models.CharField('Postal Code', max_length=12, blank=True, null=True)

    def __str__(self):
        return '{}, {}, {},{}'.format(self.line1, self.line2, self.line3, self.country)
