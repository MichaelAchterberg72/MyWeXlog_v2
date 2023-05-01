from decimal import Decimal, getcontext
from random import random
from time import time

from django.db import models
from django.db.models.signals import post_save
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from WeXlog.storage_backends import PrivateMediaStorage

from utils.utils import update_model, handle_m2m_relationship

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


def EnterpriseLogoPic(instance, filename):
	ext = filename.split('.')[-1]
	return "%s/enterprise-logo\%s_%s.%s" % (instance.id, str(time()).replace('.','_'), random(), ext)

class Enterprise(models.Model):
    FC = (
        ('P','Public'),
        ('S','System'),
    )
    ename = models.CharField('Enterprise name', max_length=250, unique=True)
    slug = models.SlugField(max_length=60, blank=True, null=True, unique=True)
    description = models.TextField('Enterprise description')
    logo = models.ImageField(storage=PrivateMediaStorage(), upload_to=EnterpriseLogoPic, blank=True, null=True)
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
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = Branch.objects.get(slug=slug)
            
        company = kwargs.pop('company', None)
        region = kwargs.pop('region', None)
        city = kwargs.pop('city', None)
        suburb = kwargs.pop('suburb', None)
        industry = kwargs.pop('industry', [])

        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = Branch.objects.create(**kwargs)
            
        if company:
            instance, created = Enterprise.objects.update_or_create(**company)
        
        if region:
            instance, created = Region.objects.update_or_create(**region)
        
        if city:
            instance, created = City.objects.update_or_create(**city)
        
        if suburb:
            instance, created = Suburb.objects.update_or_create(**suburb)

        if industry:
            industry_related_models_data = {
                'industry': (Industry, cls.industry, ['industry']),
            }
            instance = handle_m2m_relationship(instance, industry_related_models_data)

        return instance

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
