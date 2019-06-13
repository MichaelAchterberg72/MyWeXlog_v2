from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


from locations.models import Region, City, Suburb
from db_flatten.models import PhoneNumberType
from enterprises.models import Enterprise


class SiteName(models.Model):
    site = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.site

class OnlineRegistrations(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profileurl = models.URLField()
    sitename = models.ForeignKey(SiteName, on_delete=models.PROTECT, related_name='Site_Name')

    class Meta:
        unique_together = (('profileurl', 'sitename'),)

    def __str__(self):
        return self.sitename

class Profile(models.Model):
    MENTOR = (
        ('Y','Yes'),
        ('N','No'),
        )
    talent = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    synonym = models.CharField(max_length=15)
    birth_date = models.DateField('Date of Birth')
    background = models.TextField()
    mentor = models.CharField('Do you wish to be a mentor?', max_length=1, choices=MENTOR, default='N')#Opt in to be a mentor to other people

    def __str__(self):
        return str(self.talent)

class Email(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='Customuser_email')
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=False)
    company = models.ForeignKey(Enterprise, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = (('talent','email'),)

    def __str__(self):
        return self.email

class PhysicalAddress(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    line1 = models.CharField('Address Line 1', max_length=100, null=True)
    line2 = models.CharField('Address Line 2', max_length=100, blank=True, null=True)
    line3 = models.CharField('Address Line 3', max_length=100, blank=True, null=True)
    country = CountryField(null=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True)
    suburb = models.ForeignKey(Suburb, on_delete=models.PROTECT, null=True)
    code = models.CharField('Postal Code', max_length=12, blank=True, null=True)

    def __str__(self):
        return '{}: {}, {}, {},{}'.format(self.talent, self.line1, self.line2, self.line3, self.country)

class PostalAddress(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    line1 = models.CharField('Address Line 1', max_length=100)
    line2 = models.CharField('Address Line 2', max_length=100, blank=True, null=True)
    line3 = models.CharField('Address Line 3', max_length=100, blank=True, null=True)
    country = CountryField()
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    suburb = models.ForeignKey(Suburb, on_delete=models.PROTECT)
    code = models.CharField('Postal Code', max_length=12, blank=True, null=True)

    def __str__(self):
        return '{}: {}, {}, {},{}'.format(self.talent, self.line1, self.line2, self.line3, self.country)

#Function to randomise filename for Profile Upload
def ExtFilename(instance, filename):
	ext = filename.split('.')[-1]
	return "profile\%s_%s.%s" % (str(time()).replace('.','_'), random(), ext)

class FileUpload(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=150)
    file = models.FileField(upload_to=ExtFilename)

    def __str__(self):
        return '{}: {}'.format(self.talent, self.title)


class PhoneNumber(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    number = PhoneNumberField()
    type = models.ForeignKey(PhoneNumberType, on_delete=models.SET_NULL, null=True)
    current = models.BooleanField()

    def __str__(self):
        return '{}: {}({})'.format(self.talent, self.number, self.type)
