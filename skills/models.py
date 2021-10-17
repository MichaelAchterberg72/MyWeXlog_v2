from django.db import models


from django_countries.fields import CountryField


class SkillFilter(models.Model):
    country = CountryField(blank=True, blank_label='Select country (Optional)')
    region = models.CharField('Region (Optional)', max_length=250, blank=True)
    skill1 = models.CharField('Skill 1', max_length=150)
    skill2 = models.CharField('Skill 2 (Optional)', max_length=150, blank=True)
    skill3 = models.CharField('Skill 3 (Optional)', max_length=150, blank=True)
    skill4 = models.CharField('Skill 4 (Optional)', max_length=150, blank=True)
