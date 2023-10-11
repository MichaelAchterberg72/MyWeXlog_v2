from django.conf import settings
from django.db import models

from utils.utils import update_model

from enterprises.models import Branch, Enterprise
from Profile.utils import create_code9


class CorporateHR(models.Model):
    SUB = (
    (0, 'Light'),
    (1, 'Medium'),
    (2, 'Heavy'),
    )
    
    companybranch = models.ForeignKey(Branch, on_delete=models.CASCADE, blank=True, null=True)
    company = models.ForeignKey(Enterprise, on_delete=models.CASCADE)
    subscription = models.SmallIntegerField(choices=SUB, default=0)
    date_created = models.DateField(auto_now_add=True)
    expiry = models.DateField(blank=True)
    slug = models.CharField(max_length=9, blank=True)

    @classmethod
    def update_or_create(cls, slug=None, instance=None, **kwargs):
        if slug and not instance:
            instance = cls.objects.get(slug=slug)

        companybranch = kwargs.pop('companybranch', None)
        company = kwargs.pop('company', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)

        if companybranch:
            instance.companybranch = Branch.update_or_create(slug=companybranch.slug, **companybranch)

        if company:
            instance.company = Enterprise.update_or_create(slug=company.slug, **company)
        
        instance.save()
            
        return instance

    class Meta:
        verbose_name_plural = "Corporate HR"

    def __str__(self):
        if self.companybranch is not None:
            return f'{self.companybranch}'
        else:
            return f'{self.company}'

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(CorporateHR, self).save(*args, **kwargs)
