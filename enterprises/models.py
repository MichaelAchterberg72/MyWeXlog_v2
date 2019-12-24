from django.db import models


from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


from locations.models import Region, City, Suburb
from db_flatten.models import PhoneNumberType


class Industry(models.Model):
    industry = models.CharField(max_length=60, unique=True)

    def clean(self):
        self.industry = self.industry.capitalize()

    def __str__(self):
        return self.industry

class Enterprise(models.Model):
    name = models.CharField('Enterprise name', max_length=250, unique=True)
    description = models.TextField('Enterprise description')
    website = models.URLField('Website (begin with "http://")', blank=True, null=True)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name

class BranchType(models.Model):
    type = models.CharField(max_length=60, unique=True)

    def clean(self):
        self.type = self.type.capitalize()

    def __str__(self):
        return self.type

class Branch(models.Model):
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT)
    name = models.CharField('Branch or Division Name', max_length=100)
    type = models.ForeignKey(BranchType, on_delete=models.PROTECT)
    phy_address_line1 = models.CharField('Physical address line 1', max_length=150, blank=True, null=True)
    phy_address_line2 = models.CharField('Physical address line 2', max_length=150, blank=True, null=True)
    country = CountryField()
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    suburb = models.ForeignKey(Suburb, on_delete=models.PROTECT)
    code = models.CharField('Post Code', max_length=12)
    industry = models.ManyToManyField(Industry)

    class Meta:
        unique_together = (('company','name', 'city'),)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return '{}, {}, {}'.format(self.company, self.name, self.city)

class PhoneNumber(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    phone = PhoneNumberField()
    type = models.ForeignKey(PhoneNumberType, on_delete=models.SET_NULL, null=True, related_name='Number_type')
    existing = models.BooleanField('Number in use')

    def __str__(self):
        return '{}: {}({})'.format(self.branch, self.phone, self.type)
