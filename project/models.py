from django.conf import settings
from django.utils.translation import gettext, gettext_lazy as _

from tinymce.models import HTMLField

from django.db import models
from django_countries.fields import CountryField
from tinymce.models import HTMLField

from enterprises.models import Enterprise, Industry, Branch
from locations.models import Currency, City, Region
from db_flatten.models import SkillTag

from Profile.utils import create_code9

from utils.utils import update_model, handle_m2m_relationship

from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectData(models.Model):
    name = models.CharField('Project name', max_length=250)
    company = models.ForeignKey(Enterprise, on_delete=models.PROTECT, verbose_name="Owner", null=True)
    companybranch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name='Branch Managing the Project', null=True)
    description = HTMLField(blank=True, null=True, verbose_name="Overall project description")
    country = CountryField()
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    industry = models.ForeignKey(Industry, on_delete=models.PROTECT)
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)

    class Meta:
        unique_together = (('name','companybranch'),)
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        company = kwargs.pop('company', None)
        companybranch = kwargs.pop('companybranch', None)
        region = kwargs.pop('region', None)
        city = kwargs.pop('city', None)
        industry = kwargs.pop('industry', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if company:
            instance.company = Enterprise.update_or_create(slug=company.slug, **company)

        if companybranch:
            instance.companybranch = Branch.update_or_create(slug=companybranch.slug, **companybranch)

        if region:
            instance.region = Region.update_or_create(id=region.id, **region)

        if city:
            instance.city = City.update_or_create(id=city.id, **city)

        if industry:
            instance.industry = Industry.update_or_create(id=industry.id, **industry)
        
        instance.save()
            
        return instance

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
    description = HTMLField(verbose_name='Personal responsibilities description', blank=True, null=True)
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)

    class Meta:
        unique_together = (('talent', 'project', 'company', 'companybranch'),)
        
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        project = kwargs.pop('project', None)
        company = kwargs.pop('company', None)
        companybranch = kwargs.pop('companybranch', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if project:
            instance.project = ProjectData.update_or_create(slug=project.slug, **project)

        if company:
            instance.company = Enterprise.update_or_create(slug=company.slug, **company)

        if companybranch:
            instance.companybranch = Branch.update_or_create(slug=companybranch.slug, **companybranch)
        
        instance.save()
            
        return instance

    def __str__(self):
        return '{}'.format(self.project)

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(ProjectPersonalDetails, self).save(*args, **kwargs)


TASK_STATUS = (
      (0,'Due'),
      (1,'Pending'),
      (2,'Current'),
      (3,'Complete'),
  )

class ProjectPersonalDetailsTask(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ppd = models.ForeignKey(ProjectPersonalDetails, on_delete=models.CASCADE)
    company = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name="Company")
    client = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name="Client")
    task = models.CharField(max_length=50, null=True, blank=True)
    description = HTMLField(blank=True, null=True)
    skills = models.ManyToManyField(SkillTag, related_name='task_skills')
    date_create = models.DateField(auto_now_add=True)
    date_start = models.DateField(blank=True, null=True)
    date_end = models.DateField(blank=True, null=True)
    task_status = models.IntegerField(choices=TASK_STATUS, default=2)
    date_due = models.DateTimeField(_("due on"), blank=True, null=True)
    date_complete = models.DateTimeField(_("completed on"), blank=True, null=True)
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        ppd = kwargs.pop('ppd', None)
        company = kwargs.pop('company', None)
        client = kwargs.pop('client', None)
        skills = kwargs.pop('skills', [])
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if ppd:
            instance.ppd = ProjectPersonalDetails.update_or_create(slug=ppd.slug, **ppd)

        if company:
            instance.company = Branch.update_or_create(slug=company.slug, **company)

        if client:
            instance.client = Branch.update_or_create(slug=client.slug, **client)

        if skills:
            skills_related_models_data = {
                'model': SkillTag,
                'manager': 'skills',
                'fields': ['skill', 'code'],
                'data': skills_related_models_data,
            }
            instance = handle_m2m_relationship(instance, [skills_related_models_data])
        
        instance.save()
            
        return instance

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
    
    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)
            
        talent = kwargs.pop('talent', None)
        ppdt = kwargs.pop('ppdt', None)
        currency = kwargs.pop('currency', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(slug=talent.slug)
            
        if ppdt:
            instance.ppdt = ProjectPersonalDetailsTask.update_or_create(slug=ppdt.slug, **ppdt)

        if currency:
            instance.currency = Currency.update_or_create(id=currency.id, **currency)
        
        instance.save()
            
        return instance

    def __str__(self):
        return '{} {} {}'.format(self.ppdt.task, self.billing_rate, self.currency)
