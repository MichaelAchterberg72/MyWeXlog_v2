from django.db import models
from django_countries.fields import CountryField

from utils.utils import update_model


class Region(models.Model):
    country = CountryField()
    region = models.CharField('Region / State / etc.', max_length=80)

    class Meta:
        unique_together = (('country','region'),)
        ordering = ['region',]
        
    def __str__(self):
        return f'{self.region}'
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        instance.save()
            
        return instance

    def clean(self):
        self.region = self.region.title()
    

class City(models.Model):
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    city = models.CharField('City, Town, or Place', max_length=80)

    class Meta:
        unique_together = (('region','city'),)
        ordering = ['city',]
    
    def __str__(self):
        return f'{self.city}'
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        instance.save()
            
        return instance

    def clean(self):
        self.city = self.city.title()


class Suburb(models.Model):
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    suburb = models.CharField(max_length=80)
    
    class Meta:
        unique_together = (('suburb','city'),)
        ordering = ['suburb',]
        
    def __str__(self):
        return f'{self.suburb}'
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        instance.save()
            
        return instance

    def clean(self):
        self.suburb = self.suburb.title()


class Currency(models.Model):
    country = CountryField()
    currency_name = models.CharField('Currency', max_length=150)
    currency_abv = models.CharField('Abbreviation', max_length=3, unique=True)
    
    class Meta:
        unique_together = (('country','currency_name'),)
        
    def __str__(self):
        return '{} {}'.format(self.country, self.currency_name)
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        instance.save()
            
        return instance

    def clean(self):
        self.currency_name = self.currency_name.title()