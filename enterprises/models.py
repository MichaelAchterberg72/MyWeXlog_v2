from decimal import Decimal, getcontext

from django.db import models
from django.db.models.signals import post_save
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from db_flatten.models import PhoneNumberType
from locations.models import City, Region, Suburb
from Profile.utils import create_code9


# Industries: Mining & Metals: Process, Mining & Metals:Underground, Mining & Metals:Open Pit, PetroChem, FMCG, Food & Beverage, Agriculture, Retail, Aviation,
class Industry(models.Model):
    industry = models.CharField(max_length=60, unique=True)

    def clean(self):
        self.industry = self.industry.title()

    def __str__(self):
        return self.industry

    class Meta:
        ordering = ['industry',]


class Enterprise(models.Model):
    FC = (
        ('P','Public'),
        ('S','System'),
    )
    ename = models.CharField('Enterprise name', max_length=250, unique=True)
    slug = models.SlugField(max_length=60, blank=True, null=True, unique=True)
    description = models.TextField('Enterprise description')
    website = models.URLField(blank=True, null=True)
    filter_class = models.CharField(max_length=1, choices=FC, default='P')
    rate_1 = models.FloatField(null=True, default=0)#Average score from marketplace.models.TalentRate (rate_1)
    rate_2 = models.FloatField(null=True, default=0)#Average score from marketplace.models.TalentRate (rate_2)
    rate_3 = models.FloatField(null=True, default=0)#Average score from marketplace.models.TalentRate (rate_3)
    rate_4 = models.FloatField(null=True, default=0)#Average score from marketplace.models.TalentRate (payment_time)
    rate_count = models.IntegerField(null=True, default=0)

    def avg_rate(self):
        if self.rate_count is not None:
            sum = self.rate_1+self.rate_2+self.rate_3+self.rate_4
        else:
            sum=0

        return round(Decimal(sum/400),2)
    average = property(avg_rate)

    def clean(self):
        self.ename = self.ename.title()

    def __str__(self):
        return self.ename

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(Enterprise, self).save(*args, **kwargs)

    class Meta:
        ordering = ['ename',]


class BranchType(models.Model):
    type = models.CharField(max_length=70, unique=True)

    def clean(self):
        self.type = self.type.title()

    def __str__(self):
        return self.type

    class Meta:
        ordering = ['type',]


class Branch(models.Model):
    SZE = (
        ('A','1-10'),
        ('B','11-50'),
        ('C','51-150'),
        ('D','151-500'),
        ('E','501-1 000'),
        ('F','1 001-10 000'),
        ('G','10 001+'),
    )
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT)
    name = models.CharField('Branch or Division Name', max_length=100)
    type = models.ForeignKey(BranchType, on_delete=models.PROTECT, null=True)
    size = models.CharField('Branch Size', max_length=1, choices = SZE, default='A', null=True)
    phy_address_line1 = models.CharField('Physical address line 1', max_length=150, blank=True, null=True)
    phy_address_line2 = models.CharField('Physical address line 2', max_length=150, blank=True, null=True)
    country = CountryField(null=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, blank=True)
    suburb = models.ForeignKey(Suburb, on_delete=models.PROTECT, null=True, blank=True)
    code = models.CharField('Post Code', max_length=12, null=True)
    industry = models.ManyToManyField(Industry)
    slug = models.SlugField(max_length=60, unique=True, blank=True, null=True)
    rate_1 = models.FloatField(null=True, default=0)#Average score from marketplace.models.TalentRate (rate_1)
    rate_2 = models.FloatField(null=True, default=0)#Average score from marketplace.models.TalentRate (rate_2)
    rate_3 = models.FloatField(null=True, default=0)#Average score from marketplace.models.TalentRate (rate_3)
    rate_4 = models.FloatField(null=True, default=0)#Average score from marketplace.models.TalentRate (payment_time)
    rate_count = models.IntegerField(null=True, default=0)

    class Meta:
        unique_together = (('company','name', 'city'),)
        ordering = ['name',]

    def avg_rate(self):
        if self.rate_count is not None:
            sum = self.rate_1+self.rate_2+self.rate_3+self.rate_4
        else:
            sum=0
        return round(Decimal(sum/400),2)
    average = property(avg_rate)

    def clean(self):
        self.name = self.name.title()

    def __str__(self):
        return f'{self.company}, {self.name}, {self.type}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(Branch, self).save(*args, **kwargs)


class PhoneNumber(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    phone = PhoneNumberField()
    type = models.ForeignKey(PhoneNumberType, on_delete=models.SET_NULL, null=True, related_name='Number_type')
    existing = models.BooleanField('Number in use')

    def __str__(self):
        return '{}: {}({})'.format(self.branch, self.phone, self.type)
